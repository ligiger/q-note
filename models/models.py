# -*- coding: utf-8 -*-
from collections import defaultdict
import math

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare

class q_note(models.Model):
    _name = 'q_note'
    _description = 'Qualitätsmeldung'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    
    op_type = fields.Selection([
        ('product', 'Lagerprodukt'),
        ('process', 'Prozess'),
        ])
    
    product_we_id = fields.Many2one('stock.picking', string="Wareneingang Vorgang")
    move_line = fields.Many2one('stock.move.line', string="Betroffenes Produkt")
    lieferant = fields.Many2one(related='product_we_id.partner_id', string="Lieferant", readonly="true")
    bestellung = fields.Char(related='product_we_id.origin', string="Bestellnummer", readonly="true")
    ls_nummer = fields.Char(related='product_we_id.x_ls_nummer', string="Lieferscheinnummer", readonly="true")
    migo_nummer = fields.Char(related='product_we_id.x_migo_nr', string="Migo-Nummer", readonly="true")
    

    date_create = fields.Datetime(string='Erstelldatum', default=fields.Datetime.now, readonly="true")
    created_by = fields.Many2one('res.users', string="Erstellt durch", default=lambda self: self.env.user, readonly="true")

    date_confirmed = fields.Datetime(string='Eingereicht am', readonly="true")
    confirmed_by = fields.Many2one('res.users', string="Eingereicht durch", readonly="true")

    date_accepted = fields.Datetime(string='Bestätigt am:', readonly="true")
    accepted_by = fields.Many2one('res.users', string="Bestätigt durch", readonly="true")

    date_done = fields.Datetime(string='Abgeschlossen am:', readonly="true")
    done_by = fields.Many2one('res.users', string="Abgeschlossen durch", readonly="true")

    date_cancelled = fields.Datetime(string='Abgebrochen am:', readonly="true")
    cancelled_by = fields.Many2one('res.users', string="Abgebrochen durch", readonly="true")

    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('created', 'Eingereicht'),
        ('confirmed', 'Bestätigt'),
        ('done', 'Abgeschlossen'),
        ('cancel', 'Abgebrochen'),
        ])
    
    
    description = fields.Html('Beschreibung')
    analysis = fields.Html('Problemanalyse')

    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)

    @api.depends('value')
    def _value_pc(self):
        self.value2 = float(self.value) / 100

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    @api.multi
    def name_get(self):
        result=[]
        for record in self:
            if record.lot_name:
                lot = record.lot_name
            else:
                lot = '---'
            name = '[%s] %s' % (lot,record.product_id.name)
            result.append((record.id, name))
        return result
        '''
        # TDE: this could be cleaned a bit I think
        name = self.get('name', '')
        lot = self..get('lot_name', False) or False
        if lot:
            name = '[%s] %s' % (lot,name)
        return (self['id'], name)'''
        '''
        def _name_get(d):
            name = d.get('name', '')
            code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
            if code:
                name = '[%s] %s' % (code,name)
            return (d['id'], name)'''