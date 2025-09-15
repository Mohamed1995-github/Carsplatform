# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    service_provider_rank = fields.Boolean(
        string='Service Provider Rank',
        default=False,
        help='Check this if the contact is a service provider'
    )
    
    service_provider_ids = fields.One2many(
        'service.provider',
        'partner_id',
        string='Service Provider Records',
        help='Service provider records linked to this contact'
    )
    
    is_service_provider = fields.Boolean(
        string='Is Service Provider',
        compute='_compute_is_service_provider',
        store=True,
        help='True if this contact has service provider rank'
    )

    @api.depends('service_provider_rank')
    def _compute_is_service_provider(self):
        """Compute if partner is a service provider"""
        for partner in self:
            partner.is_service_provider = partner.service_provider_rank

    @api.model
    def _get_contact_type_ranking(self):
        """Override to include service provider rank"""
        ranking = super()._get_contact_type_ranking()
        ranking['service_provider'] = 10
        return ranking

    def _get_contact_type(self):
        """Override to include service provider type"""
        contact_type = super()._get_contact_type()
        if self.service_provider_rank:
            contact_type = 'service_provider'
        return contact_type


