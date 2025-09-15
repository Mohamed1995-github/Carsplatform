# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class ServiceProvider(models.Model):
    _name = 'service.provider'
    _description = 'Service Provider'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Service Provider Name',
        required=True,
        tracking=True
    )
    
    ref = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('verification', 'Verification'),
        ('registered', 'Registered'),
        ('suspended', 'Suspended'),
        ('refused', 'Refused'),
    ], string='Status', default='draft', tracking=True, required=True)
    
    recommender_phone = fields.Char(
        string='Recommender Phone',
        help='Phone number of the contact who recommended this service provider'
    )
    
    provider_phone = fields.Char(
        string='Provider Phone',
        required=True,
        help='Phone number of the service provider (8 digits starting with 2, 3, or 4)'
    )
    
    nni = fields.Char(
        string='NNI',
        required=True,
        help='National Number Identifier (10 digits)'
    )
    
    contract_start_date = fields.Date(
        string='Contract Start Date',
        required=True,
        tracking=True
    )
    
    contract_expiry_date = fields.Date(
        string='Contract Expiry Date',
        required=True,
        tracking=True
    )
    
    service_domain_ids = fields.Many2many(
        'product.category',
        'service_provider_domain_rel',
        'provider_id',
        'category_id',
        string='Service Domains',
        required=True,
        help='Select service domains from product categories'
    )
    
    service_ids = fields.Many2many(
        'product.product',
        'service_provider_service_rel',
        'provider_id',
        'product_id',
        string='Services',
        domain="[('type', '=', 'service'), ('categ_id', 'in', service_domain_ids)]",
        help='Select services from the chosen service domains'
    )
    
    supplier_rank = fields.Boolean(
        string='Supplier Rank',
        default=True,
        help='Mark as supplier'
    )
    
    service_provider_rank = fields.Boolean(
        string='Service Provider Rank',
        default=True,
        help='Mark as service provider'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Related Contact',
        help='Contact record for this service provider'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Portal User',
        readonly=True,
        help='Portal user created when status becomes Registered'
    )

    @api.model
    def create(self, vals):
        if vals.get('ref', _('New')) == _('New'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('service.provider') or _('New')
        return super(ServiceProvider, self).create(vals)

    @api.constrains('provider_phone')
    def _check_provider_phone(self):
        for record in self:
            if record.provider_phone:
                # Remove any non-digit characters
                phone = re.sub(r'\D', '', record.provider_phone)
                if len(phone) != 8 or not phone.startswith(('2', '3', '4')):
                    raise ValidationError(
                        _('Provider phone must be 8 digits starting with 2, 3, or 4.')
                    )

    @api.constrains('nni')
    def _check_nni(self):
        for record in self:
            if record.nni:
                # Remove any non-digit characters
                nni = re.sub(r'\D', '', record.nni)
                if len(nni) != 10:
                    raise ValidationError(
                        _('NNI must be exactly 10 digits.')
                    )

    @api.constrains('contract_start_date', 'contract_expiry_date')
    def _check_contract_dates(self):
        for record in self:
            if record.contract_start_date and record.contract_expiry_date:
                if record.contract_start_date >= record.contract_expiry_date:
                    raise ValidationError(
                        _('Contract expiry date must be after the start date.')
                    )

    @api.onchange('service_domain_ids')
    def _onchange_service_domain_ids(self):
        """Clear services when service domains change"""
        if self.service_domain_ids:
            # Update domain for services
            return {
                'domain': {
                    'service_ids': [
                        ('type', '=', 'service'),
                        ('categ_id', 'in', self.service_domain_ids.ids)
                    ]
                }
            }
        else:
            self.service_ids = False
            return {
                'domain': {
                    'service_ids': [('id', '=', False)]
                }
            }

    def action_verify(self):
        """Move to verification status"""
        self.write({'status': 'verification'})

    def action_register(self):
        """Move to registered status and create portal user"""
        for record in self:
            record.write({'status': 'registered'})
            record._create_portal_user()

    def action_suspend(self):
        """Move to suspended status"""
        self.write({'status': 'suspended'})

    def action_refuse(self):
        """Move to refused status"""
        self.write({'status': 'refused'})

    def action_reset_to_draft(self):
        """Reset to draft status"""
        self.write({'status': 'draft'})

    def _create_portal_user(self):
        """Create portal user when status becomes registered"""
        for record in self:
            if not record.user_id and record.partner_id:
                # Create portal user
                user_vals = {
                    'name': record.name,
                    'login': record.provider_phone,
                    'partner_id': record.partner_id.id,
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                    'active': True,
                }
                
                user = self.env['res.users'].create(user_vals)
                record.write({'user_id': user.id})
                
                # Send welcome email
                template = self.env.ref('service_marketplace.email_template_service_provider_welcome', False)
                if template:
                    template.send_mail(record.id, force_send=True)

    def _create_partner(self):
        """Create or update partner record"""
        for record in self:
            if not record.partner_id:
                partner_vals = {
                    'name': record.name,
                    'phone': record.provider_phone,
                    'is_company': True,
                    'supplier_rank': record.supplier_rank,
                    'service_provider_rank': record.service_provider_rank,
                    'category_id': [(6, 0, [self.env.ref('service_marketplace.service_provider_category').id])],
                }
                
                partner = self.env['res.partner'].create(partner_vals)
                record.write({'partner_id': partner.id})
            else:
                # Update existing partner
                record.partner_id.write({
                    'name': record.name,
                    'phone': record.provider_phone,
                    'supplier_rank': record.supplier_rank,
                    'service_provider_rank': record.service_provider_rank,
                })

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to automatically create partner"""
        records = super().create(vals_list)
        for record in records:
            record._create_partner()
        return records

    def write(self, vals):
        """Override write to update partner when needed"""
        result = super().write(vals)
        for record in self:
            if any(field in vals for field in ['name', 'provider_phone', 'supplier_rank', 'service_provider_rank']):
                record._create_partner()
        return result


