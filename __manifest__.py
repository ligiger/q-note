# -*- coding: utf-8 -*-
{
    'name': "q_note",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Getronic Engineering AG",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Quality Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','portal','product','project'],

    # always loaded
    'data': [ 
        'security/q_note_security.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
        #'views/templates.xml',
        'report/q_note_report.xml',
        'report/q_note_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}