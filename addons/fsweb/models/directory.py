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
    regname = fields.Char(u'Рег. имя sip')
    password = fields.Char(u'Пароль sip')
    number = fields.Char(u'Номер телефона', required=True)
    active = fields.Boolean('Active', default=True)
    fs_users_id = fields.Many2one("fs.users", string="Пользователь", required=True)
    domain_id = fields.Many2one("fs.domain", string="Домен", required=True, default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('domain_id')))
    context_id = fields.Many2one("fs.context", string="Контекст", required=True, default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('context_id')))
    is_transfer = fields.Boolean('Переадресовывать?', default=False)
    transfer_number = fields.Char(u'Номер переадресации')
    is_kerio = fields.Boolean('Зарегестрирован в kerio', default=False, readonly=True)
    kerio_user_guid = fields.Char(u'Id kerio пользователя', help=u'Идентификатор записи пользователя', readonly=True)
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

    @api.model
    def action_update_all(self, *arg):
        print("++++++++++++++++++++++++++++++ action_update_all ")
        return True

    
    def action_update_fs(self):
        print("++++++++++++ action_update_account ++++++++++++++++++")
        
        fs_host = self.env['ir.config_parameter'].sudo().get_param('fs_host')
        fs_port = self.env['ir.config_parameter'].sudo().get_param('fs_port')
        fs_password = self.env['ir.config_parameter'].sudo().get_param('fs_password')
        fs = greenswitch.InboundESL(host=fs_host, port=int(fs_port), password=fs_password)
        fs.connect()
        # r = fs.send('api sofia status')
        r = fs.send('api sofia profile external rescan')
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
                    if 'user_id' in res and 'sip_username' in res and  'number' in res and  'line_id' in res and 'group_id' in res and 'username' in res and 'password' in res:
                        self.is_kerio = True
                        self.kerio_user_guid = res["user_id"]
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

    def action_set_transfer_kerio(self):
        """Действие запускает функцию для Обновления записи переадресации в kerio"""
        res = self.set_transfer_kerio()
        # res = self.update_transfer_api(self.regname, True, '106')
        if res == True:
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
        else:
            if "error" in res:
                error = res["error"]
            else:
                error = "Неизвестная ошибка"
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': ('Ошибка'),
                    'message': error,
                    'type':'warning',  #types: success,warning,danger,info
                    'sticky': True,  #True/False will display for few seconds if false
                },
            }
        
        return notification


    def set_transfer_kerio(self):
        """Обновляет запись переадресации в kerio"""
        print("++++++++++++ set_transfer_kerio ++++++++++++++++++")
        if not self.is_kerio:
            return {"error": "Не зарегистрирован в Kerio"}
        if self.is_transfer == True and self.transfer_number == False:
            return {"error": "Не установлен номер для переадресации"}

        kerio_url = self.env['ir.config_parameter'].sudo().get_param('kerio_url')
        kerio_user = self.env['ir.config_parameter'].sudo().get_param('kerio_user')
        kerio_password = self.env['ir.config_parameter'].sudo().get_param('kerio_password')
        print('kerio_user', kerio_user)
        error = ""
        if self.kerio_user_guid and self.kerio_group_guid and self.number and kerio_url and kerio_user and kerio_password:

            kerio = kerio_api.KerioAPI(kerio_url, kerio_user, kerio_password)
            if kerio.session:
                print("kerio.session", kerio.session)
                res = kerio.update_transfer(    user_id = self.kerio_user_guid,
                                                group_id = self.kerio_group_guid,
                                                number = self.number,
                                                is_transfer = self.is_transfer,
                                                transfer_number = self.transfer_number
                )
                if res == True:
                    print("Запись переадресации Успех")
                    return True
                else:
                    print("Запись переадресации ОШИБКА")
                    return {"error": res}
                                
            else:
                error = "Не возможно подключиться к Kerio Operator"
        else:
            error = "Не установлены обязательные параметры: kerio_user_guid, kerio_group_guid, number, kerio_url, kerio_user, kerio_password"
        return {"error": error}
    
    @api.model
    def update_transfer_api(self, regname=False, is_transfer=False, transfer_number=False):
        """ 
            Внешнее дейсвие для обновления записи переадрессации 
        """
        print("++++++++++++++  update_transfer_api  ++++++++++++++++ ")
        if not regname or (is_transfer == True and transfer_number == False):
            return False
        
        search_dir = self.env['fs.directory'].sudo().search([('regname', '=', regname)], limit=1)
        print("search_dir", search_dir)
        if len(search_dir)>0:
            # Сохраняем старые значения переадресации
            old_is_transfer = search_dir.is_transfer
            old_transfer_number = search_dir.transfer_number

            # Устанавливаем новые значения
            search_dir.is_transfer = is_transfer
            search_dir.transfer_number = transfer_number

            res = search_dir.set_transfer_kerio()
            
            if res == True:
                return True
            else: 
                # Восстанавливаем старые значения, т.к обновление прошло не удачно
                print("Ошибка при обновлении переадресации", res)
                search_dir.is_transfer = old_is_transfer
                search_dir.transfer_number = old_transfer_number
                return res

        return False


