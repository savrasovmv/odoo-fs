# -*- coding: utf-8 -*-

from odoo import fields, models
from ldap3 import Server, Connection, SUBTREE, MODIFY_REPLACE, LEVEL
import json

#Подключение к ldap
LDAP_HOST = '10.100.100.5'
LDAP_PORT = 636
LDAP_USER = "LDAP@tmenergo.ru"
LDAP_PASS = 'TfFn7MfTlL'
LDAP_USERNAME = "LDAP"  #Для проверки поиска в AD

class FsUsers(models.Model):
    _name = "fs.users"
    _description = "Пользователи FS"
    _order = "name"

    name = fields.Char(u'ФИО', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    is_ldap = fields.Boolean('LDAP?', default=True)
    ip_phone = fields.Integer(u'Вн. номер')
    sAMAccountName = fields.Char(u'sAMAccountName')
    ou = fields.Char(u'Орг.единица (OU)')
    department = fields.Char(u'Департамент')
    title = fields.Char(u'Должность')

    def action_update_from_ldap(self):
        #Подключение к серверу AD
        ldap_server = Server(host=LDAP_HOST, port=LDAP_PORT, use_ssl=True, get_info='ALL')
        c = Connection(ldap_server, user=LDAP_USER, password=LDAP_PASS)
        c.bind()
        filter = '(&(objectClass=person)(sAMAccountName=' + self.sAMAccountName + '))'
        res = c.search(search_base='OU=UsersCorporate,DC=tmenergo,DC=ru',
                    search_filter=filter,
                    search_scope=SUBTREE,
                    attributes=['cn','department', 'title', 'ou', 'ipPhone', 'distinguishedName' ])
        print("------------------------------------")
        print(res)
        if res:
            emp = c.response[0]
            print(emp)
            atr = emp['attributes']
            dn = emp['dn']
            print(atr)
            department = atr['department']
            self.name = atr['cn']
            self.department = atr['department']
            self.title = atr['title']
            self.ou = dn.split(',OU=')[1]
            self.ip_phone = atr['ipPhone']
        return True