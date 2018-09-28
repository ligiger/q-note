# -*- coding: utf-8 -*-
from collections import defaultdict
import math

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare

class risk(models.Model):
    _name = 'q_note.risk'
    _description = 'Risiko'

    auswirkung = fields.Selection([
        ('1', 'Klein'),
        ('2', 'Mittel'),
        ('3', 'Gross'),
        ], string="Auswirkungen")
    probability = fields.Selection([
        ('1', 'Unwahrscheinlich'),
        ('2', 'Wahrscheinlich'),
        ('3', 'Sehr Wahrschenlich'),
        ], string="Wahrschenlichkeit des Auftretens")
    discovery = fields.Selection([
        ('3', 'Unwahrscheinlich'),
        ('2', 'Wahrscheinlich'),
        ('1', 'Sehr Wahrschenlich'),
        ], string="Entdeckungswahrscheinlichkeit")
    
    risikozahl = fields.Float(compute="_value_pc", store=True)

    @api.depends('discovery','probability','auswirkung')
    def _value_pc(self):
        for record in self:
            record.risikozahl = int(record.auswirkung) * int(record.probability) * int(record.discovery)

class q_note(models.Model):
    _name = 'q_note'
    _description = 'Qualitätsmeldung'
    _inherit = ['mail.thread', 'mail.activity.mixin','q_note.risk']

    name = fields.Char(default="Neue Abweichungsmeldung", readonly="true")
    
    op_type = fields.Selection([
        ('product', 'Lagerprodukt'),
        ('process', 'Prozess'),
    ], default="product", string="Meldungstyp")
    
    product_we_id = fields.Many2one('stock.picking', string="Wareneingang Vorgang")
    move_line = fields.Many2one('stock.move.line', string="Betroffenes Produkt")
    lieferant = fields.Many2one(related='product_we_id.partner_id', string="Lieferant", readonly="true")
    bestellung = fields.Char(related='product_we_id.origin', string="Bestellnummer", readonly="true")
    ls_nummer = fields.Char(related='product_we_id.x_ls_nummer', string="Lieferscheinnummer", readonly="true")
    migo_nummer = fields.Char(related='product_we_id.x_migo_nr', string="Migo-Nummer", readonly="true")

    process = fields.Char(string="Betroffener Prozess")
    

    date_create = fields.Datetime(string='Erstelldatum', default=fields.Datetime.now, readonly="true")
    created_by = fields.Many2one('res.users', string="Erstellt durch", default=lambda self: self.env.user, readonly="true")

    date_confirmed = fields.Datetime(string='Eingereicht am', readonly="true")
    confirmed_by = fields.Many2one('res.users', string="Eingereicht durch", readonly="true")

    date_accepted = fields.Datetime(string='Bestätigt am:', readonly="true")
    accepted_by = fields.Many2one('res.users', string="Bestätigt durch", readonly="true")

    date_validated = fields.Datetime(string='Validiert am:', readonly="true")
    validated_by = fields.Many2one('res.users', string="Validiert durch", readonly="true")

    date_done = fields.Datetime(string='Abgeschlossen am:', readonly="true")
    done_by = fields.Many2one('res.users', string="Abgeschlossen durch", readonly="true")

    date_cancelled = fields.Datetime(string='Abgebrochen am:', readonly="true")
    cancelled_by = fields.Many2one('res.users', string="Abgebrochen durch", readonly="true")

    tasks = fields.One2many('project.task','abweichung_id')

    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('created', 'Eingereicht'),
        ('confirmed', 'Bestätigt'),
        ('validated', 'Validiert'),
        ('done', 'Abgeschlossen'),
        ('cancel', 'Abgebrochen'),
        ], default="draft")
    
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].get('q_note') or '/'
        vals['name'] = seq
        return super(q_note, self).create(vals)
    
    @api.one
    def confirm(self):
        self.write({'state': 'created'})
        self.write({'date_create': fields.Datetime.now()})
        self.write({'created_by': self.env['res.users'].browse(self.env.uid).id})

    @api.one
    def accept(self):
        self.write({'state': 'confirmed'})
        self.write({'date_accepted': fields.Datetime.now()})
        self.write({'accepted_by': self.env['res.users'].browse(self.env.uid).id})

    @api.one
    def validate(self):
        self.write({'state': 'validated'})
        self.write({'date_validated': fields.Datetime.now()})
        self.write({'validated_by': self.env['res.users'].browse(self.env.uid).id})

    @api.one
    def done(self):
        self.write({'state': 'done'})
        self.write({'date_done': fields.Datetime.now()})
        self.write({'done_by': self.env['res.users'].browse(self.env.uid).id})

    @api.one
    def cancel(self):
        self.write({'state': 'cancel'})
        self.write({'date_cancelled': fields.Datetime.now()})
        self.write({'cancelled_by': self.env['res.users'].browse(self.env.uid).id})

    @api.one
    def edit(self):
        self.write({'state': 'draft'})

    description = fields.Html('Beschreibung')
    analysis = fields.Html('Problemanalyse')

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

class Picking(models.Model):
    _inherit = 'stock.picking'

    abweichungen = fields.One2many('q_note', 'product_we_id', string="Abweichungsmeldungen")

class Task(models.Model):
    _inherit = 'project.task'

    abweichung_id = fields.Many2one('q_note', string="Zu Abweichungsmeldung")