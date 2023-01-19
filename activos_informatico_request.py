# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

REQUEST_CATEGORY_ASSIGMENT = "activos_informatico.request_category_assigment"
REQUEST_CATEGORY_OPTIMIZATION = "activos_informatico.request_category_optimization"
REQUEST_CATEGORY_REFUND = "activos_informatico.request_category_refund"
REQUEST_CATEGORY_DECOMPOSE = "activos_informatico.request_category_decompose"
FIXED_ASSET_CATEGORY_JOB_POSITION = "activos_informatico.category_job_positions"

class ActivosInformaticoRequestCategory(models.Model):
    _name = 'activos.informatico.request.category'
    _description = 'Categoria de solicitudes'

    _rec_name = 'name'
    _order = 'name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        default=lambda self: _('Nuevo'),
        copy=False
    )

    description = fields.Char(
        string='Descripción',
    )
    
   
    
    request_ids = fields.One2many(
        string='Custodio',
        comodel_name='activos.informatico.request',
        inverse_name='category_id',
    )

    type = fields.Selection(
        string='Tipos de movimeinto en kardex',
        selection=[('assigment', 'Asignación'), ('refund', 'Devolución'),('decompose','Descomponer'),('optimization','Optimización')],
        default='assigment',
        required=True
    )

    active = fields.Boolean(
        string='active',
        default=True
    )

    


class ActivosInformaticoRequest(models.Model):
    _name = 'activos.informatico.request'
    _description = 'Solicitudes'

    _rec_name = 'name'
    _order = 'name ASC'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Número de solicitud',
        copy=False
    )

    category_id = fields.Many2one(
        string='Categoría',
        comodel_name='activos.informatico.request.category',
        ondelete='restrict',
        required=True
    )

    fixed_asset_id = fields.Many2one(
        string='Puesto de trabajo',
        comodel_name='activos.informatico.fixed.asset',
        domain="[('id','in',job_positions_allow_ids)]",
        ondelete='restrict',
    )

    job_positions_allow_ids = fields.One2many(
        string='Puestos de trabajo permitidos',
        comodel_name='activos.informatico.fixed.asset',
        compute='_compute_job_positions_allow_ids' ,
        help='Consulta todos los puestos de trabajos disponibles'
    )

    
    job_positions_allow_ids_count = fields.Integer(
        string='job_positions_allow_ids_count',
        compute='_compute_job_positions_allow_ids_count'
    )
        
    @api.depends('job_positions_allow_ids')
    def _compute_job_positions_allow_ids_count(self):
        for record in self:
            record.job_positions_allow_ids_count = len(record.job_positions_allow_ids)
        
    def _compute_job_positions_allow_ids(self):
        for record in self:
            
            domain=[
                ('category_id.parent_id','=',self.env.ref(FIXED_ASSET_CATEGORY_JOB_POSITION).id )
                ]
            if(self.category_id == self.env.ref(REQUEST_CATEGORY_ASSIGMENT)):
                #Agrega solo los puestos de trabajo que no esten asignado o libres
                domain.append(('current_employee_id','=',False))
            if(self.category_id == self.env.ref(REQUEST_CATEGORY_OPTIMIZATION) or self.category_id == self.env.ref(REQUEST_CATEGORY_REFUND) ):
                #agrega todos los equipos asignados
                domain.append(('current_employee_id','=',record.requester_employee_id.id))
            if(self.category_id == self.env.ref(REQUEST_CATEGORY_DECOMPOSE)):
                domain.append(('stage','=','available'))

            record.job_positions_allow_ids = self.env['activos.informatico.fixed.asset'].search(domain)
    
    
    requester_employee_id = fields.Many2one(
        string='Custodio',
        comodel_name='hr.employee',
        ondelete='restrict',
        help='El soliciante siempre es el custorio actual'
    )

    accountable_employee_id = fields.Many2one(
        string='Responsable',
        comodel_name='hr.employee',
        ondelete='restrict',
    )
    
    
    description = fields.Text(
        string='Detalle de la solicitud',
    )
    
    optimization_parts_ids= fields.Many2many(
        string='Partes',
        comodel_name='activos.informatico.fixed.asset',
        relation='activos_informatico_optimization_rel',
        column2='fixed_asset_id',
        column1='request_id',
    )

    stage = fields.Selection(
        string='Estado',
        selection=[('new', 'Nuevo'), ('process', 'Proceso'),('done','Terminado'),('cancel','Cancelado')],
        default='new'
    )
    
    active = fields.Boolean(
        string='active',
        default=True
    )

    @api.model
    def default_get(self, default_fields):
       
        rslt = super(ActivosInformaticoRequest, self).default_get(default_fields )
        rslt.update({
            'create_uid':self.env.uid
        })    
        return rslt 

    def _validated_done_optimization(self):
        if self.category_id == self.env.ref(REQUEST_CATEGORY_OPTIMIZATION):
            for part in self.optimization_parts_ids:
                if(part.stage !='available'):
                    raise ValidationError('Para continuar todas las partes deben estar disponibles')
            for part in self.optimization_parts_ids:
                part.stage = 'assigned'
                self.env['activos.informatico.movement'].create({
                'name':'Optimizar - Repuesto',
                'request_id':self.id,
                'apply_fixed_asset_id':self.fixed_asset_id.id,
                'fixed_asset_id':part.id,
                })
            #registro el movimiento del kardex
            self.env['activos.informatico.movement'].create({
                'name':'Optimizar - Puesto trabajo',
                'request_id':self.id,
                'fixed_asset_id':self.fixed_asset_id.id,
            })
    
    def _validated_done_assigment(self):
        if self.category_id == self.env.ref(REQUEST_CATEGORY_ASSIGMENT):
            if not self.fixed_asset_id.id:
                raise ValidationError('Para terminar debes asignar un puesto de trabajo')
            if self.fixed_asset_id.current_employee_id.id:
                raise ValidationError('El puesto de trabajo ya no esta disponible selecione otro')
            #asigno el puesto de trabajo    
            self.fixed_asset_id.current_employee_id = self.requester_employee_id
            self.fixed_asset_id.stage = 'assigned'
            #registro el movimiento del kardex
            self.env['activos.informatico.movement'].create({
                'name':'Asignación nueva',
                'request_id':self.id,
                'fixed_asset_id':self.fixed_asset_id.id,
            })
    
    def _validated_done_refund(self):
        if self.category_id == self.env.ref(REQUEST_CATEGORY_REFUND):
            if not self.fixed_asset_id.id:
                raise ValidationError('Para terminar debes asignar un puesto de trabajo')
            #registro el movimiento del kardex
            self.env['activos.informatico.movement'].create({
                'name':'Devolución',
                'request_id':self.id,
                'fixed_asset_id':self.fixed_asset_id.id,
            })
            #Libero
            self.fixed_asset_id.current_employee_id = False
            self.fixed_asset_id.stage = 'available'
    
    def _validated_done_decompose(self):
        if self.category_id == self.env.ref(REQUEST_CATEGORY_DECOMPOSE):
            if not self.fixed_asset_id.id:
                raise ValidationError('Para terminar debes asignar un puesto de trabajo')
            #registro el movimiento del kardex
            self.env['activos.informatico.movement'].create({
                'name':'Baja de equipo',
                'request_id':self.id,
                'fixed_asset_id':self.fixed_asset_id.id,
            })
            self.fixed_asset_id.active=False
            for part in self.optimization_parts_ids:
                part.stage = 'available'
                part.temp = False
                self.env['activos.informatico.movement'].create({
                'name':'Optimizar - Repuesto',
                'request_id':self.id,
                'apply_fixed_asset_id':self.fixed_asset_id.id,
                'fixed_asset_id':part.id,
                })
    
            


    def action_stage_change(self):
                  
        if(self.stage == 'process' and self.env.context['new_stage']=='done'):
            if not self.accountable_employee_id.id:
                raise ValidationError('Para continuar debes asignar un responsable')
            
            self._validated_done_optimization()
            self._validated_done_assigment()
            self._validated_done_refund()
            self._validated_done_decompose()
          

        self.stage = self.env.context['new_stage']


        
    
    def _add_stakeholders(self):
        for record in self:
            employees = [record.requester_employee_id,record.accountable_employee_id]
            for  employee in employees:
                if employee.user_id:
                    record.message_subscribe(partner_ids=employee.user_id.partner_id.ids)
    
    
    @api.onchange('requester_employee_id')
    def _onchange_requester_employee_id(self):
        if (self.category_id == self.env.ref(REQUEST_CATEGORY_OPTIMIZATION) or self.category_id == self.env.ref(REQUEST_CATEGORY_REFUND) ) and  self.requester_employee_id.id:
            
            domain=[('current_employee_id','=',self.requester_employee_id.id)]
            fixed_asset= self.env['activos.informatico.fixed.asset'].search(domain,limit=1)
            self.fixed_asset_id = fixed_asset
            self. _compute_job_positions_allow_ids()
    
    
    
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise
    
            @param values: dict of new values to be set
    
            @return: True on success, False otherwise
        """
    
        result = super(ActivosInformaticoRequest, self).write(values)

        if( 'requester_employee_id' in values or 'accountable_employee_id' in values):
            self._add_stakeholders()
    
        return result
    
    
    @api.model_create_multi
    def create(self, values):
        """
            Create a new record for a model ActivosInformaticoRequest
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
        for v in values:
            v['name'] = self.env['ir.sequence'].next_by_code('sequence.request.seq')

        result = super(ActivosInformaticoRequest, self).create(values)
        result._add_stakeholders()
        return result
    



   
        
        
        
    
    
    
    
    

    

    



