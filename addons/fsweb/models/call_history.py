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

class CallHistory(models.Model):
    _name = "fs.call_history"
    _description = "History Calls"
    _order = "date"

    name = fields.Char(u'guid')
    from_num = fields.Char(string='Номер абонента')
    from_name = fields.Char(string='Имя абонента')
    from_type = fields.Char(string='Тип звонка')
    to_num = fields.Char(string='Номер адресата')
    to_name = fields.Char(string='Имя адресата')
    to_status = fields.Char(string='Статус')
    duration = fields.Integer(string='Длительность разговора')
    date = fields.Char(u'Дата')
    


