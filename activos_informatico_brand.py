# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ActivosInformaticoBrand(models.Model):
    _name = 'activos.informatico.brand'
    _description = 'Marca de activos fijos'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('Nuevo'),
        copy=False
    )

    category_ids = fields.Many2many(
        string='Categoría',
        comodel_name='activos.informatico.category',
        relation='activos_informatico_category_brand_rel',
        column1='category_id',
        column2='brand_id',
    )
    
    model_ids = fields.One2many(
        string='Modelos',
        comodel_name='activos.informatico.model',
        inverse_name='brand_id',
    )
    
    

    
