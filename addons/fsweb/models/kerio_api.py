# -*- coding: utf-8 -*-
import requests
import json
import pprint

class KerioAPI(object):
    """Класс для работы с API Kerio Operator"""
    def __init__(self, url, username, password):
        """Constructor"""
        self.url = url
        self.username = username
        self.password = password
        self.headers = {"Content-Type": "application/json"}
        self.session = self.session_login()
        if self.session:
            print("Connect")
            self.headers = {"Content-Type": "application/json", "X-Token": self.token}
        else:
            print("Connect FILED")


    def session_login(self):

        data = {
            "jsonrpc": "2.0",
            'id':  1,
            'method': 'Session.login',
            'params': {
                'userName': self.username,
                'password': self.password,
                'application': {
                'name': 'Sample app',
                'vendor': 'Kerio',
                'version': '1.0'
                }
            }
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data))
        res = json.loads(response.content)

        if "result" in res:
            if "token" in res["result"]:
                token = res["result"]["token"]
                cookies = response.cookies
                self.token = token
                self.cookies = cookies
                return True

        return False



    def print_object(self):
        print({
                "url": self.url,
                "username": self.username,
                "password": self.password,
                "session": self.session,
                "token": self.token,
                "cookies": self.cookies,
            }) 
      
    
    def search_sip_username(self, number, sip_username):
        """Поиск данных number - тел.номер, sip_username - регистрация"""
        if not self.session: return {"result": "error", "error" : "Not connect"}

        data = {
            "jsonrpc": "2.0",
            'id':  "1",
            'method': 'Extensions.get',
            'params': {
                "query": {
                    "combining": "And",
                    "conditions": [{
                        "comparator": "=",
                        "fieldName": "SEARCH",
                        "value": number
                    }]
                }
            }
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data), cookies=self.cookies)
        res = json.loads(response.content)
        pprint.pprint(res)
        if "error" in res:
            print("Ошибка: ", res['error'])
            return {"result": "error", "error": res['error']}

        if "result" in res:
            if "sipExtensionList" in res["result"]:
                ext_list = res["result"]["sipExtensionList"]
                sip_user = False
                for line in ext_list:
                    if "telNum" in line and "guid" in line and "USERNAME" in line:
                        
                        
                        telNum = line["telNum"]
                        print("Добавочный номер найден", telNum)
                        if  "parentId" in line and "sipUsername" in line:
                            sipUsername = line["sipUsername"]
                            if sipUsername == sip_username and telNum == number:
                                print("Регистрация найдена", sipUsername)
                                sip_user = {
                                    'sip_username': line["sipUsername"],
                                    'number': line["telNum"],
                                    'line_id': line["guid"],
                                    'group_id': line["parentId"],
                                    'username': line["USERNAME"],
                                }
                                return sip_user

                        if telNum == number and not "sipUsername" in line:
                            sip_user = {
                                'number': line["telNum"],
                                'group_id': line["guid"],
                                'USERNAME': line["USERNAME"],
                            }

                return sip_user

        return False


    def set_name_line(self, line_id, sip_username):
        """Переименует регистрацию для добавочного номер
            line_id - guid sip регистрации
            sip_username - регистрационное имя sip которое задаем
        """
        data = {
            "jsonrpc": "2.0",
            'id':  "1",
            'method': 'Extensions.set',
            'params': {
                "guids": [line_id], 
                "detail": {
                    "sipUsername": sip_username
                }
            }
        }
        print("set_name_line data", data)
        response = requests.post(self.url, headers=self.headers, data=json.dumps(data), cookies=self.cookies)
        res = json.loads(response.content)
        print("set_name_line res", res)
        if "result" in res:
            return True

        return False

    def get_password(self, line_id):
        """Возвращает пароль регистрации добавочного номер
            line_id - guid sip регистрации
        """
        data = {
            "jsonrpc": "2.0",
            'id':  "1",
            'method': 'Extensions.getSipPassword',
            'params': {
                "guid": line_id, 
            }
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(data), cookies=self.cookies)
        res = json.loads(response.content)
        if "result" in res:
            try:
                password = res["result"]["password"]
                return password
            except:
                return False

        return False


    def create_line(self, group_id):
        """Создает новую регистрацию для добавочного номер
            group_id - guid добавочного номра (например номер 100)
        """
        data = {
          "jsonrpc": "2.0",
          'id':  "1",
          'method': 'Extensions.createLine',
          'params': {"guid": group_id, "detail": {}}
        }

        response = requests.post(url, headers=self.headers, data=json.dumps(data), cookies=self.cookies)
        res = json.loads(response.content)
        print("create_line", res)
        if "result" in res:
            try:
                group_id = res["result"]["result"]["id"]["guidGroup"]
                line_id = res["result"]["result"]["id"]["guidLine"]
                

                return {
                        "group_id": group_id, 
                        "line_id": line_id, 
                    }
            except:
                return False

    def create_line_by_username(self, group_id, sip_username):
        """Создает новую регистрацию для добавочного номер с указанным именем регистрции
            group_id - guid добавочного номра (например номер 100)
            sip_username - имя регистрации
        """
        new_line = self.create_line(group_id)
        if new_line:
            res = self.set_name_line(new_line["line_id"], sip_username)
            if res:
                new_line["sip_username"] = sip_username
                password = self.get_password(new_line["line_id"])
                if password:
                    new_line["password"] = password
                    return new_line
                else:
                    return {"error": "Ошибка при получении пароля"}
            else:
                return {"error": "Ошибка при попытке назначить имя регистрации"}
        else:
            return {"error": "Ошибка при создании новой регистрации"}



    def update_or_create_line(self, number, sip_username):
        """Создает или обновляет регистрацию для добавочного номер
            number - тел.номер, sip_username - регистрация
        """
        line = self.search_sip_username(number, sip_username)
        if not line or "error" in line:
            return False

        # Если регистрация существует
        if "sip_username" in line:
            # Добавляеи пароль и возвращаем данные
            password = self.get_password(line["line_id"])
            line["password"] = password
            return line
        elif "group_id" in line:
            # т.е добавочный номер (группа) найден, но регистрация нет, тогда создаем новую регистрацию
            new_line = self.create_line_by_username(line["group_id"], sip_username)
            return new_line





if __name__ == "__main__":
    url = "https://sip3.fineapple.xyz:4021/admin/api/jsonrpc/";
    username = "admin00"
    password = "1qaz2WSX"

    kerio = KerioAPI(url, username, password)
    if kerio.session:
        sip_user = kerio.update_or_create_line('104', '104rc5555')
        print(sip_user)