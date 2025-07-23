#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN AI Assistant - Hlavná aplikácia
Refaktorovaný modulárny systém pod 600 riadkov
"""

import streamlit as st

# Import všetkých modulov
from ui_components import (
    init_streamlit_config,
    render_header,
    render_process_cards,
    render_quick_questions,
    render_sidebar_config,
    render_learning_mode,
    render_assistant_mode
)

from business_management import (
    render_process_management,
    render_departments,
    render_positions,
    render_company_settings,
    render_edit_process,
    render_edit_department,
    render_edit_position,
    render_database_management,
    render_database_schema
)

def main():
    """Hlavná funkcia aplikácie"""
    init_streamlit_config()
    
    # Inicializácia session state
    if 'mode' not in st.session_state:
        st.session_state.mode = "assistant"
    if 'show_assistant' not in st.session_state:
        st.session_state.show_assistant = False
    
    # Sidebar konfigurácia
    render_sidebar_config()
    
    # Hlavný obsah podľa režimu
    if st.session_state.mode == "learning":
        render_learning_mode()
    elif st.session_state.mode == "assistant" or st.session_state.show_assistant:
        render_assistant_mode()
        st.session_state.show_assistant = False
    elif st.session_state.mode == "process_management":
        render_process_management()
    elif st.session_state.mode == "departments":
        render_departments()
    elif st.session_state.mode == "positions":
        render_positions()
    elif st.session_state.mode == "company_settings":
        render_company_settings()
    elif st.session_state.mode == "database_management":
        render_database_management()
    elif st.session_state.mode == "database_schema":
        render_database_schema()
    elif st.session_state.mode == "edit_process":
        render_edit_process()
    elif st.session_state.mode == "edit_department":
        render_edit_department()
    elif st.session_state.mode == "edit_position":
        render_edit_position()
    else:
        # Hlavný prehľad (podobný používateľovmu)
        render_header()
        render_process_cards()
        render_quick_questions()
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #6C757D; font-size: 0.9rem;">🎯 ADSUN AI Assistant - Kompletný Business Management systém</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 