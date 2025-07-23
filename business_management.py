#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Business Management UI
Správa procesov, oddelení, pozícií a nastavení firmy
Modulárny prístup - len importy z podmodulů
"""

# Import process management
from process_management import (
    render_process_management,
    render_edit_process,
    show_process_details,
    delete_process,
    render_process_learning
)

# Import departments management  
from departments_management import (
    render_departments,
    render_edit_department,
    render_department_learning
)

# Import positions management
from positions_management import (
    render_positions,
    render_edit_position,
    render_position_learning
)

# Import company settings
from company_settings import (
    render_company_settings,
    load_company_settings,
    get_default_settings
)

# Import database management
from database_management import (
    render_database_management
)

# Import database schema
from database_schema import (
    render_database_schema
)

# Re-export všetky funkcie pre backward compatibility
__all__ = [
    # Process management
    'render_process_management',
    'render_edit_process',
    'show_process_details', 
    'delete_process',
    'render_process_learning',
    
    # Departments management
    'render_departments',
    'render_edit_department',
    'render_department_learning',
    
    # Positions management
    'render_positions',
    'render_edit_position', 
    'render_position_learning',
    
    # Company settings
    'render_company_settings',
    'load_company_settings',
    'get_default_settings',
    
    # Database management
    'render_database_management',
    
    # Database schema
    'render_database_schema'
] 