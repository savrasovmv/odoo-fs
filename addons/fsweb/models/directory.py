# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


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

    # sequence = fields.Integer('Sequence', default=10)

    # _sql_constraints = [
    #     ('check_number_of_months', 'CHECK(number_of_months >= 0)', 'The number of month can\'t be negative.'),
    # ]