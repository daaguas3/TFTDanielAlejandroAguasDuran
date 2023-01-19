# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ActivosInformaticoMovement(models.Model):
    _name = 'activos.informatico.movement'
    _description = 'Kardex de activos informaticos'
    _table = 'activos_informatico_movement'

    _rec_name = 'name'
    _order = 'create_date ASC'

    name = fields.Char(
        string='Name',
        default=lambda self: _('Nuevo'),
        copy=False,
    )

    type = fields.Selection(
        string='Tipos',
        selection=[('assigment', 'Asignación'), ('refund', 'Devolución'),('decompose','Descomponer'),('optimization','Optimización')],
        related='request_id.category_id.type',
        store=True
    )    
    
    fixed_asset_id = fields.Many2one(
        string='Activo Fijo',
        comodel_name='activos.informatico.fixed.asset',
        ondelete='restrict',
    )

    category_fixed_asset_id = fields.Many2one(
        string='Categoría activo fijo',
        comodel_name='activos.informatico.category',
        related='fixed_asset_id.category_id'
    )

    current_employee_id = fields.Many2one(
        string='Custodio actual',
        comodel_name='hr.employee',
        ondelete='restrict',
    ) 

    apply_fixed_asset_id = fields.Many2one(
        string='Aplicado en',
        comodel_name='activos.informatico.fixed.asset',
        ondelete='restrict',
    )

    request_id = fields.Many2one(
        string='Solicitud',
        comodel_name='activos.informatico.request',
        ondelete='restrict',
    )

    @api.model_create_multi
    def create(self, values):
        """
            Create a new record for a model ActivosInformaticoMovement
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        result = super(ActivosInformaticoMovement, self).create(values)
        result.current_employee_id = result.fixed_asset_id.current_employee_id
        return result

    _sql_constraints = [
        ('fixed_asset_request_uniq', 'unique (fixed_asset_id,request_id,apply_fixed_asset_id)', 'No puede selecionar duplicar el registro')
    ]

    
