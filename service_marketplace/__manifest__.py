# -*- coding: utf-8 -*-
{
    'name': 'Service Marketplace',
    'version': '17.0.1.0.0',
    'category': 'Services',
    'summary': 'Service Marketplace for managing service providers',
    'description': """
        Service Marketplace Module
        =========================
        
        This module provides functionality to manage service providers including:
        - Service provider registration and verification
        - Contact management with service provider rank
        - Automatic portal user creation
        - Service domain and product management
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'portal',
        'product',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'data/res_partner_data.xml',
        'data/email_templates.xml',
        'views/service_provider_views.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
