# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

import requests

import json

import greenswitch
# import subprocess
# try:
#     import ESL
# except ImportError:
#     from freeswitchESL import ESL
# from freeswitchESL import ESL

class Directory(models.Model):
    _name = "fs.directory"
    _description = "Directory FS"
    _order = "number"

    name = fields.Char(u'ФИО', required=True)
    cidr = fields.Char(u'cidr')
    regname = fields.Char(u'Рег. имя', required=True)
    password = fields.Char(u'Пароль', required=True)
    number = fields.Integer(u'Номер', required=True)
    active = fields.Boolean('Active', default=True)
    fs_users_id = fields.Many2one("fs.users", string="Пользователь")
    domain_id = fields.Many2one("fs.domain", string="Домен")
    context_id = fields.Many2one("fs.context", string="Контекст")
    is_transfer = fields.Boolean('Переадресовывать?', default=True)
    transfer_number = fields.Integer(u'Номер переадресации', required=True)
    kerio_number_guid = fields.Integer(u'Id kerio номера', help=u'Идентификатор записи добавочного номера')
    kerio_reg_guid = fields.Integer(u'Id kerio регистрации', help=u'Идентификатор записи регистрации')

    # sequence = fields.Integer('Sequence', default=10)

    # _sql_constraints = [
    #     ('check_number_of_months', 'CHECK(number_of_months >= 0)', 'The number of month can\'t be negative.'),
    # ]

    def action_update_all(self):
        print("++++++++++++++++++++++++++++++")

    
    def action_update_account(self):
        print("++++++++++++ action_update_account ++++++++++++++++++")
        # file_name = "/home/user/temp/%s.xml" % self.regname
        # f= open(file_name, "w+")
        # f.write("""
        #     <include>
        #         <gateway name="110rc">
        #             <param name="username" value="110rc"/>
        #             <param name="password" value="Gfhjkm12@"/>
        #             <param name="proxy" value="192.168.1.11"/>
        #             <param name="register" value="true"/>
        #         </gateway>
        #     </include>
        
        # """)
        # f.close() 
        # subprocess.run(["scp", file_name, "root@192.168.1.8:/etc/freeswitch/sip_profiles/external/"])
        # con = ESL.ESLconnection("192.168.1.8", "8021", "ClueCon")
        fs = greenswitch.InboundESL(host='192.168.1.8', port=8021, password='ClueCon')
        fs.connect()
        r = fs.send('api sofia status')
        print(r.data)
        return True

    def action_registration_kerio(self):
        print("++++++++++++ action_registration_kerio ++++++++++++++++++")
        url = "https://sip3.fineapple.xyz:4021/admin/api/jsonrpc/";
        reg_data = {
            "jsonrpc": "2.0",
            'id':  1,
            'method': 'Session.login',
            'params': {
                'userName': "admin00",
                'password': "1qaz2WSX",
                'application': {
                'name': 'Sample app',
                'vendor': 'Kerio',
                'version': '1.0'
                }
            }
        }
        json_reg_data = json.dumps(reg_data)
        headers_reg = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers_reg, data=json_reg_data)
        res = json.loads(response.content)
        token = res["result"]["token"]
        headers_dict = {
            "Content-Type": "application/json",
            "X-Token": token,
        }

        # Создание доп регистрации
        form_data = {
            "jsonrpc": "2.0",
            'id':  "1",
            'method': 'Extensions.createLine',
            'params': {"guid": 1247, "detail": {}}
        }
        json_object = json.dumps(form_data)
        response = requests.post(url, headers=headers_dict, data=json_object, cookies=response.cookies)

        # Переименование регистрации
        form_data = {
            "jsonrpc": "2.0",
            'id':  "1",
            'method': 'Extensions.set',
            'params': {
                    
                    "guids": [1819], 
                    
                    "detail": {
                        "sipUsername": self.regname
                    }
            }
        }

        response = requests.post(url, headers=headers_dict, data=json_object, cookies=response.cookies)