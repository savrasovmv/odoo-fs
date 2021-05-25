# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Domain(models.Model):
    _name = "fs.domain"
    _description = "Domain FS"
    _order = "name"

    name = fields.Char(u'Домен', required=True, help="sip.example.com")