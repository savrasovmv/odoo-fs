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
    ip_phone = fields.Char(u'Вн. номер')
    username = fields.Char(u'sAMAccountName')
    ou = fields.Char(u'Орг.единица (OU)')
    department = fields.Char(u'Департамент')
    title = fields.Char(u'Должность')

    def action_update_from_ldap(self):
        #Подключение к серверу AD
        LDAP_HOST = self.env['ir.config_parameter'].sudo().get_param('ldap_host')
        LDAP_PORT = self.env['ir.config_parameter'].sudo().get_param('ldap_port')
        LDAP_USER = self.env['ir.config_parameter'].sudo().get_param('ldap_user')
        LDAP_PASS = self.env['ir.config_parameter'].sudo().get_param('ldap_password')
        ldap_search_base = self.env['ir.config_parameter'].sudo().get_param('ldap_search_base')

        ldap_server = Server(host=LDAP_HOST, port=int(LDAP_PORT), use_ssl=True, get_info='ALL')
        c = Connection(ldap_server, user=LDAP_USER, password=LDAP_PASS)
        c.bind()
        filter = '(&(objectClass=person)(sAMAccountName=' + self.username + '))'
        res = c.search(search_base=ldap_search_base,
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

        # f= open("/home/user/temp/%src.xml" % self.ip_phone, "w+")
        # f.write("""
        #         <gateway name="110p2">
        #             <param name="username" value="110p2"/>
        #             <param name="password" value="Gfhjkm12@"/>
        #             <param name="proxy" value="192.168.1.11"/>
        #             <param name="register" value="false"/>
        #         </gateway>
        
        # """)
        # f.close() 
        return True