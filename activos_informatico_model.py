# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class ActivosInformaticoModel(models.Model):
    _name = 'activos.informatico.model'
    _description = 'Modelo'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('Nuevo'),
        copy=False
    )

    
    brand_id = fields.Many2one(
        string='brand',
        comodel_name='activos.informatico.brand',
        ondelete='restrict',
    )
    

    
