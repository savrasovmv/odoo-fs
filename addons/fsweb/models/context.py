# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Context(models.Model):
    _name = "fs.context"
    _description = "Context FS"
    _order = "name"

    name = fields.Char(u'Контекст', required=True, help="Например: public, default")