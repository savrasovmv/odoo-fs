# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class FsSettings(models.TransientModel):
    # _name = "fs.settings"
    _inherit = 'res.config.settings'


    rc_url = fields.Char(u'URL Rochet Chat')
    rc_prefix = fields.Char(u'Префикс рег. номера Rochet Chat', default='rc')
    rc_user = fields.Char(u'Пользователь Rochet Chat', default='')
    rc_password = fields.Char(u'Пароль Rochet Chat', default='')


    kerio_url = fields.Char(u'URL kerio operator')
    kerio_user = fields.Char(u'Пользователь kerio')
    kerio_password = fields.Char(u'Пароль kerio')

    domain_id = fields.Many2one("fs.domain", string="Домен по умолчанию")
    context_id = fields.Many2one("fs.context", string="Контекст по умолчанию")
    
    @api.model
    def get_values(self):
        res = super(FsSettings, self).get_values()
        conf = self.env['ir.config_parameter']
        res.update({
                'rc_url': conf.get_param('rc_url'),
                'rc_prefix': conf.get_param('rc_prefix'),
                'rc_user': conf.get_param('rc_user'),
                'rc_password': conf.get_param('rc_password'),
                'kerio_url': conf.get_param('kerio_url'),
                'kerio_user': conf.get_param('kerio_user'),
                'kerio_password': conf.get_param('kerio_password'),
                'domain_id': int(conf.get_param('domain_id')),
                'context_id': int(conf.get_param('context_id')),
        })
        return res


    def set_values(self):
        super(FsSettings, self).set_values()
        conf = self.env['ir.config_parameter']
        conf.set_param('rc_url', str(self.rc_url))
        conf.set_param('rc_prefix', str(self.rc_prefix))
        conf.set_param('rc_user', str(self.rc_user))
        conf.set_param('rc_password', str(self.rc_password))
        conf.set_param('kerio_url', str(self.kerio_url))
        conf.set_param('kerio_user', str(self.kerio_user))
        conf.set_param('kerio_password', str(self.kerio_password))
        conf.set_param('domain_id', int(self.domain_id))
        conf.set_param('context_id', int(self.context_id))
    #     """
    #     Method argument "fields" is a list of names
    #     of all available fields.
    #     """
    #     conf = self.env['ir.config_parameter']
    #     #company = self.env.user.company_id
    #     return {
    #         'rc_url': conf.get_param('rc_url'),
    #         'rc_prefix': conf.get_param('rc_prefix'),
    #         'rc_user': conf.get_param('rc_user'),
    #         'rc_password': conf.get_param('passworc_passwordrd_selex'),
    #         'kerio_url': conf.get_param('kerio_url'),
    #         'kerio_user': conf.get_param('kerio_user'),
    #         'kerio_password': conf.get_param('kerio_password'),
    #         'domain_id': int(conf.get_param('domain_id')),
    #         'context_id': int(conf.get_param('context_id')),
            
    #     }
    
