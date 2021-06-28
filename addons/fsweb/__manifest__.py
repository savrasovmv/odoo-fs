# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'freeswitch web',
    'version': '1',
    'category': 'freeswitch',
    'sequence': 15,
    'summary': 'Модуль управления пользователями FS',
    'description': "Модуль управления пользователями FS",
    'depends': [
        # 'base_setup',
        'base',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',

        
        'views/domain_views.xml',
        'views/context_views.xml',
        'views/directory_views.xml',
        'views/call_history_views.xml',
        'views/users_views.xml',
        'views/settings_view.xml',
        'views/fs_menu.xml',
        

    ],
    'installable': True,
    'application': True,
    'auto_install': False
}