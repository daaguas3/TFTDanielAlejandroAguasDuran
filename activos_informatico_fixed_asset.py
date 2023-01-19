# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError



class ActivosInformaticoTypeProcessor(models.Model):
    _name = 'activos.informatico.type.processor'
    _description = 'Tipos de procesadores'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('Nuevo'),
        copy=False
    )

class ActivosInformaticoTypeSo(models.Model):
    _name = 'activos.informatico.type.so'
    _description = 'Tipos de sistema operativo'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('Nuevo'),
        copy=False
    )


class ActivosInformaticoTag(models.Model):
    _name = 'activos.informatico.tag'
    _description = 'Etiqueta'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('New'),
        copy=False
    )



class ActivosInformaticoFixedAsset(models.Model):
    _name = 'activos.informatico.fixed.asset'
    _description = 'Activos fijos'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Código',
        required=True,
        default=lambda self: _('Nuevo'),
        copy=False,
        help="Código secuencial interno"
    )

    
    code_fixed_asset = fields.Char(
        string='Código único de activo fijo',
        help='Código de activo fijo de la empresa'
    )
    

    category_id = fields.Many2one(
        string='Categoría',
        comodel_name='activos.informatico.category',
        ondelete='restrict',
    )
    
    brand_id = fields.Many2one(
        string='Marca',
        comodel_name='activos.informatico.brand',
        ondelete='restrict',       
    )

    model_id = fields.Many2one(
        string='Modelo',
        comodel_name='activos.informatico.model',
        ondelete='restrict',
        domain="[('brand_id','=',brand_id)]"
    )

    active = fields.Boolean(
        string='active',
        default=True
    )

    serie = fields.Char(
        string='Serie',
    )
    
    processor_id = fields.Many2one(
        string='Procesador',
        comodel_name='activos.informatico.type.processor',
        ondelete='restrict',
    )


    ram = fields.Integer(
        string='Tamaño RAM',
    )
    
    ram_space = fields.Selection(
        string='Medida RAM',
        selection=[('mb', 'Mb'), ('gb', 'Gb')],
        default='gb'
    )

    disco = fields.Integer(
        string='Espacio de Disco',
    )
    
    disco_space = fields.Selection(
        string='Medida de Disco',
        selection=[('mb', 'Mb'), ('gb', 'Gb'),('tb', 'Tb')],
        default='gb'
    )

    disco_type = fields.Selection(
        string='Tipo de Disco',
        selection=[('hdd', 'Mecánico'), ('sd', 'Sólido')],
        default='sd'
    )
    
    hostname = fields.Char(
        string='Hostname',
    )

    so_id = fields.Many2one(
        string='Sistema Operativo',
        comodel_name='activos.informatico.type.so',
        ondelete='restrict',
    )

    domain = fields.Char(
        string='Dominio',
    )

    tag_ids = fields.Many2many(
        string='Etiqueta',
        comodel_name='activos.informatico.tag',
        relation='activos_informatico_tag_fixed_asset_rel',
        column1='tag_id',
        column2='fixed_asset_id',
    )
 
    stage = fields.Selection(
        string='Estado',
        selection=[('available', 'Disponible'), ('assigned', 'Asignado'),('repair','Reparáción')],
        default='available'
    )

    current_employee_id = fields.Many2one(
        string='Custodio actual',
        comodel_name='hr.employee',
        ondelete='restrict',
    )
    
    warranty = fields.Boolean(
        string='Garantia',
        default=True
    )

    date_warranty = fields.Date(
        string='Fecha vencimiento'
    )
    
    peripherals_ids = fields.One2many(
        string='Perifericos',
        comodel_name='activos.informatico.fixed.asset',
        inverse_name='composed_in_id',
        domain="[('id','in',peripherals_available_ids)]",
        help="Lista de periféricos quer esta formado el puesto de trabajo"
    )

    composed_in_id = fields.Many2one(
        string='Puesto de trabajo',
        comodel_name='activos.informatico.fixed.asset',
        ondelete='restrict',
        help='Puesto de trabajo que esta asignado'
    )
    
    peripherals_available_ids = fields.One2many(
        string='perifericos disponible',
        comodel_name='activos.informatico.fixed.asset',
        compute='_compute_peripherals_available_ids',
        help="Campo calculado que ayuda a filtrar los perificos disponibles"
    )
        
    def _compute_peripherals_available_ids(self):
        for record in self:
            domain=[('is_job_position','=',False),('stage','=','available'),('composed_in_id','=',False)]
            record.peripherals_available_ids = self.env['activos.informatico.fixed.asset'].search(domain)
        
    is_job_position = fields.Boolean(
        string='Es puesto de trabajo',
        compute='_compute_is_job_position',
        store=True
    )
        
    @api.depends('category_id','category_id.parent_id')
    def _compute_is_job_position(self):
            for record in self:
                record.is_job_position = record.category_id.parent_id == self.env.ref('activos_informatico.category_job_positions') 
        
    
    note = fields.Html(
        string='Nota',
    )

    
    movement_ids = fields.One2many(
        string='movement',
        comodel_name='activos.informatico.movement',
        inverse_name='fixed_asset_id',
        help='kardex'
    )

    
    movement_count = fields.Integer(
        string='N movimientos',
        compute='_compute_movement_count' 
    )

    
    temp = fields.Boolean(
        string='Temporal',
        help='Campo técnico que inidica que el activo es temporal y no se puede asignar',
        default=False,
        required=True
    )
    
        
    @api.depends('movement_ids')
    def _compute_movement_count(self):
        for record in self:
            record.movement_count = len(record.movement_ids)
    
    def action_open_movements(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "activos.informatico.movement",
            "domain": [('fixed_asset_id', '=', self.id)],
            
            "name": "Movimiento de inventario",
            "target": "current",
            'view_mode': 'tree',
        }
        return result
        
    @api.model_create_multi
    def create(self, values):
        """
            Create a new record for a model ActivosInformaticoFixedAsset
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for v in values:
            if 'category_id' in v:
                cat = self.env['activos.informatico.category'].browse(v['category_id'])
                seq = cat.sequence_id if cat.sequence_id.id else cat.parent_id.sequence_id
                if seq.id:
                    v['name'] = self.env['ir.sequence'].next_by_code(seq.code)

    
        result = super(ActivosInformaticoFixedAsset, self).create(values)
    
        return result
    
    _sql_constraints = [
        ('code_fixed_asset_uniq', 'unique (code_fixed_asset)', 'No se puede duplicar el código único de activo fijo !')
        ]
     
    
    
    


    
    
    
        
