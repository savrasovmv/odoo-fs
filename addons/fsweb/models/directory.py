# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, http
from odoo.http import request

import requests

import json

import greenswitch

from . import kerio_api
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

    name = fields.Char(u'ФИО')
    username = fields.Char(string='Имя пользователя')
    cidr = fields.Char(u'cidr')
    regname = fields.Char(u'Рег. имя')
    password = fields.Char(u'Пароль')
    number = fields.Integer(u'Номер', required=True)
    active = fields.Boolean('Active', default=True)
    fs_users_id = fields.Many2one("fs.users", string="Пользователь", required=True)
    domain_id = fields.Many2one("fs.domain", string="Домен", required=True, default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('domain_id')))
    context_id = fields.Many2one("fs.context", string="Контекст", required=True, default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('context_id')))
    is_transfer = fields.Boolean('Переадресовывать?', default=False)
    transfer_number = fields.Integer(u'Номер переадресации')
    is_kerio = fields.Boolean('Зарегестрирован в kerio', default=False, readonly=True)
    kerio_group_guid = fields.Char(u'Id kerio номера', help=u'Идентификатор записи добавочного номера', readonly=True)
    kerio_line_guid = fields.Char(u'Id kerio регистрации', help=u'Идентификатор записи регистрации', readonly=True)
    is_rocketchat = fields.Boolean(string='Зарегистрирован в RocketChat', default=False, readonly=True)
    rc_user_id = fields.Char(string='Id пользователя RocketChat', readonly=True)
    # sequence = fields.Integer('Sequence', default=10)

    # _sql_constraints = [
    #     ('check_number_of_months', 'CHECK(number_of_months >= 0)', 'The number of month can\'t be negative.'),
    # ]
    # @api.model
    # def create(self, vals):
    #     # Do some business logic, modify vals...
    #     ...
    #     # Then call super to execute the parent method
    #     return super().create(vals)


    @api.onchange("fs_users_id")
    def _onchange_from_users(self):
        for record in self:
            record.name = record.fs_users_id.name
            record.regname = str(record.fs_users_id.ip_phone) + 'rc'
            record.number = record.fs_users_id.ip_phone
            record.username = record.fs_users_id.username

    # @api.depends("fs_users_id")
    # def _compute_from_users(self):
    #     for record in self:
    #         # record.name = record.fs_users_id.name
    #         record.regname = str(record.fs_users_id.ip_phone) + 'rc'
    #         record.number = record.fs_users_id.ip_phone
    # def _inverse_number(self):
    #     for record in self:
    #         record.cidr = record.name


    def action_update_all(self):
        print("++++++++++++++++++++++++++++++")

    
    def action_update_fs(self):
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
        # r = fs.send('api sofia status')
        r = fs.send('api luarun /etc/freeswitch/scripts/gateway.lua')
        print(r.data)
        return True

    def action_registration_kerio(self):
        print("++++++++++++ action_registration_kerio ++++++++++++++++++")
        kerio_url = self.env['ir.config_parameter'].sudo().get_param('kerio_url')
        kerio_user = self.env['ir.config_parameter'].sudo().get_param('kerio_user')
        kerio_password = self.env['ir.config_parameter'].sudo().get_param('kerio_password')
        print('kerio_user', kerio_user)
        error = ""
        if self.username and self.regname and self.number and kerio_url and kerio_user and kerio_password:

            kerio = kerio_api.KerioAPI(kerio_url, kerio_user, kerio_password)
            if kerio.session:
                print("kerio.session", kerio.session)

                res = kerio.update_or_create_line(str(self.number), self.regname, self.username)
                print(res)
                if res:
                    if 'sip_username' in res and  'number' in res and  'line_id' in res and 'group_id' in res and 'username' in res and 'password' in res:
                        self.is_kerio = True
                        self.kerio_group_guid = res["group_id"]
                        self.kerio_line_guid = res["line_id"]
                        self.password = res["password"]
                        # raise UserError("You can't do that!") 
                        notification = {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': ('Успех'),
                                'message': 'Запись обновлена',
                                'type':'success',  #types: success,warning,danger,info
                                'sticky': False,  #True/False will display for few seconds if false
                            },
                        }
                        return notification
                    if "error" in res:
                        error = res["error"]
            else:
                error = "Не возможно подключиться к Kerio Operator"
        else:
            error = "Не установлены обязательные параметры: username, regname, number, kerio_url, kerio_user, kerio_password"
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': ('Ошибка'),
                'message': 'Запись не добавлена. %s' % error,
                'type':'warning',  #types: success,warning,danger,info
                'sticky': True,  #True/False will display for few seconds if false
            },
        }
        return notification


class DirectoryController(http.Controller):
    @http.route('/apidirectory', auth='public')
    def handler(self):
        dir_rec = request.env['fs.directory'].sudo().search([])
        print("+++++++dir_rec",dir_rec)
        spisok = []
        for rec in dir_rec:
            print("++++rec", rec)
            vals = {
                'id': rec.id,
                'regname': rec.regname,
                'password': rec.password,
                'username': rec.username,
            }
            print("+++val", vals)
            spisok.append(vals)
        print("++++spisok", spisok)

        data = {'status': 200, 'response': spisok, 'message': 'spisok returned'}
        print("++++data", data)

        return json.dumps(data)

class DirectoryController(http.Controller):
    @http.route('/api_get_directory/<username>', type='http', auth='user')
    def api_get_directory(self, username=False):
        if not username:
            data = {'status': 200, 'response': [], 'message': 'Not user name'}
            return json.dumps(data)
        else:
            domain = [('username', '=', username), ('active', '=', True)]


        dir_rec = request.env['fs.directory'].sudo().search(domain, limit=1)
        if len(dir_rec) > 0:
            print("+++++++dir_rec",dir_rec)
            vals = {
                'id': dir_rec.id,
                'regname': dir_rec.regname,
                'password': dir_rec.password,
                'username': dir_rec.username,
            }

        data = {'status': 200, 'response': vals, 'message': 'vals returned'}
        print("++++vals", vals)

        return json.dumps(data)