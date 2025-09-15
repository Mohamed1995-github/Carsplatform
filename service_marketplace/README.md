# Service Marketplace Module for Odoo V17

## Overview
This module provides a comprehensive service marketplace solution for managing service providers, their registration, verification, and portal access.

## Features

### Service Provider Management
- **Reference ID**: Auto-generated sequence-based reference (SP0001, SP0002, etc.)
- **Status Management**: Draft → Verification → Registered → Suspended/Refused
- **Contact Information**: Phone validation (8 digits starting with 2, 3, or 4)
- **NNI Validation**: 10-digit National Number Identifier
- **Contract Management**: Start and expiry date tracking
- **Service Domains**: Multi-select from product categories
- **Services**: Multi-select services from chosen domains
- **Ranks**: Supplier and Service Provider rank management

### Contact Integration
- **Service Provider Rank**: New contact type for service providers
- **Automatic Partner Creation**: Creates/updates partner records
- **Portal User Creation**: Automatic portal access when status becomes "Registered"

### Security & Access Control
- **User Groups**: Marketplace User, Manager, and Portal groups
- **Access Rights**: Read/Write/Create/Delete permissions based on roles
- **Portal Access**: Service providers get portal access upon registration

## Installation

1. Copy the `service_marketplace` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Service Marketplace" module

## Usage

### Creating a Service Provider
1. Go to **Service Marketplace > Service Providers**
2. Click **Create**
3. Fill in the required information:
   - Service Provider Name
   - Provider Phone (8 digits starting with 2, 3, or 4)
   - NNI (10 digits)
   - Contract dates
   - Service domains and services
4. Save and send for verification

### Status Workflow
- **Draft**: Initial state, can be edited
- **Verification**: Sent for review, can be approved or refused
- **Registered**: Approved and active, portal user created
- **Suspended**: Temporarily disabled
- **Refused**: Rejected application

### Portal Access
When a service provider's status becomes "Registered":
- A portal user is automatically created
- Login credentials are sent via email
- The user can access their portal account

## Technical Details

### Models
- `service.provider`: Main service provider model
- `res.partner`: Extended with service_provider_rank field

### Dependencies
- `base`: Core Odoo functionality
- `portal`: Portal user management
- `product`: Product and category management
- `contacts`: Contact management

### Data Files
- `ir_sequence_data.xml`: Reference sequence configuration
- `res_partner_data.xml`: Service provider category
- `email_templates.xml`: Welcome email template

### Security
- Access rights defined in `ir.model.access.csv`
- Security groups in `security.xml`

## Customization

### Adding New Fields
To add new fields to the service provider model:
1. Add the field to `models/service_provider.py`
2. Update the form view in `views/service_provider_views.xml`
3. Add access rights if needed

### Custom Workflows
The module supports custom status transitions through the action methods:
- `action_verify()`
- `action_register()`
- `action_suspend()`
- `action_refuse()`
- `action_reset_to_draft()`

## Support
For support and customization requests, please contact your Odoo administrator.

## License
LGPL-3


