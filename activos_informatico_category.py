# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ActivosInformaticoCategory(models.Model):
    _name = 'activos.informatico.category'
    _description = 'Categoria de activos informaticos'

    _rec_name = 'name'
    _order = 'parent_id ASC'

    name = fields.Char(
        string='Nombre',
        required=True,
        default=lambda self: _('Nuevo'),
        copy=False,
        
    )    

    children_ids = fields.One2many(
        string='Sub categorias',
        comodel_name='activos.informatico.category',
        inverse_name='parent_id',
    )

    parent_id = fields.Many2one(
        string='Categoría Padre',
        comodel_name='activos.informatico.category',
        ondelete='restrict',
    )
    
    parent_path = fields.Char(index=True, unaccent=False)

    active = fields.Boolean(
        string='active',
        default=True,
        required=True
    )

    sequence_id = fields.Many2one(
        string='Secuenca para el activo fijo',
        comodel_name='ir.sequence',
        ondelete='restrict',
    )
    
    
    
    
    
    
    
    

    

