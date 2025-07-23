#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Airtable Manager - Čistý chat interface pre Airtable procesy
"""

import streamlit as st
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from airtable_connector import HybridDatabaseManager, AirtableConnector
from api_manager import APIKeyManager, get_api_keys

def init_airtable_ui():
    """Nastavenie clean Airtable UI"""
    st.set_page_config(
        page_title="ADSUN Airtable Manager",
        page_icon="🗄️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Clean blue/gray styling
    st.markdown("""
    <style>
    /* Clean styling podobný obrázku */
    .stApp {
        background-color: #FAFBFC;
    }
    
    /* Skrytie Streamlit elementov */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stRadio > div { flex-direction: row; gap: 1rem; }
    
    /* Header styling */
    .airtable-header {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #E1E8ED;
    }
    
    .header-title {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2C3E50;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    
    .header-subtitle {
        font-size: 1rem;
        color: #6C757D;
        margin: 0.3rem 0 0 0;
    }
    
    .status-badge {
        background: #D4EDDA;
        color: #155724;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        float: right;
        margin-top: -0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none;
        padding: 0.6rem 1.5rem;
    }
    
    .primary-btn {
        background: #4A90E2 !important;
        color: white !important;
    }
    
    .primary-btn:hover {
        background: #357ABD !important;
        transform: translateY(-1px);
    }
    
    .secondary-btn {
        background: #F8F9FA !important;
        color: #495057 !important;
        border: 1px solid #DEE2E6 !important;
    }
    
    .secondary-btn:hover {
        background: #E9ECEF !important;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #E1E8ED;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        min-height: 300px;
    }
    
    .chat-message {
        background: #F8F9FA;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #4A90E2;
    }
    
    .chat-response {
        background: #E3F2FD;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #2196F3;
    }
    
    /* Quick questions */
    .quick-questions {
        margin: 1.5rem 0;
    }
    
    .quick-btn {
        background: #F1F3F4;
        border: 1px solid #D1D5DB;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        font-size: 0.9rem;
        color: #374151;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-block;
    }
    
    .quick-btn:hover {
        background: #4A90E2;
        color: white;
        border-color: #4A90E2;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #D1D5DB !important;
        padding: 0.8rem !important;
        font-size: 0.95rem !important;
    }
    
    /* Status section */
    .status-section {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        margin-top: 2rem;
        border: 1px solid #E1E8ED;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .status-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #F1F3F4;
    }
    
    .status-item:last-child {
        border-bottom: none;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .airtable-header {
            padding: 1rem;
        }
        
        .header-title {
            font-size: 1.5rem;
        }
        
        .status-badge {
            float: none;
            margin-top: 0.5rem;
            display: inline-block;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def render_airtable_header():
    """Render header v štýle Airtable managera"""
    st.markdown("""
    <div class="airtable-header">
        <div class="status-badge">🟢 Pripravený</div>
        <div class="header-title">
            <span>🗄️</span>
            ADSUN Airtable Manager
        </div>
        <div class="header-subtitle">
            Ukladanie a načítavanie procesov
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_main_buttons():
    """Render hlavných tlačidiel"""
    col1, col2, col3 = st.columns([2, 2, 4])
    
    with col1:
        chat_btn = st.button("💬 Chat s dátami", key="chat_btn", use_container_width=True)
        if chat_btn:
            st.session_state.mode = "chat"
    
    with col2:
        add_btn = st.button("➕ Pridať proces", key="add_btn", use_container_width=True)
        if add_btn:
            st.session_state.mode = "add_process"
    
    return chat_btn, add_btn

def render_chat_interface():
    """Render chat interfacu"""
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Úvodná správa ak nie je konverzácia
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="chat-message">
            <strong>🚀 ADSUN Airtable Manager je pripravený!</strong><br>
            <em>9:31:57</em>
        </div>
        """, unsafe_allow_html=True)
    
    # Zobrazenie chat histórie
    for message in st.session_state.chat_history:
        if message['type'] == 'user':
            st.markdown(f"""
            <div class="chat-message">
                <strong>👤 Vy:</strong><br>
                {message['content']}<br>
                <em>{message['timestamp']}</em>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-response">
                <strong>🤖 Assistant:</strong><br>
                {message['content']}<br>
                <em>{message['timestamp']}</em>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_query_input():
    """Render input pre otázky"""
    
    # Query input a button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_input(
            "",
            placeholder="Spýtaj sa na svoje procesy... (napr. 'ukáž všetky procesy')",
            key="query_input",
            label_visibility="collapsed"
        )
    
    with col2:
        ask_btn = st.button("🔍 Pýtaj", key="ask_btn", use_container_width=True)
    
    return user_query, ask_btn

def render_quick_questions():
    """Render rýchlych otázok"""
    st.markdown("**Rýchle otázky:**")
    
    quick_questions = [
        "Ukáž všetky procesy",
        "Koľko procesov mám?", 
        "Obchodné procesy",
        "Štatistiky"
    ]
    
    # Render ako inline buttony
    cols = st.columns(len(quick_questions))
    for i, question in enumerate(quick_questions):
        with cols[i]:
            if st.button(question, key=f"quick_{i}", use_container_width=True):
                return question
    
    return None

def render_system_status():
    """Render stavu systému"""
    
    # Inicializácia DB managera
    if 'airtable_manager' not in st.session_state:
        st.session_state.airtable_manager = HybridDatabaseManager()
    
    # Získanie štatistík
    try:
        stats = st.session_state.airtable_manager.get_process_statistics()
        connection_status = "🟢 Pripojený" if stats['process_count'] >= 0 else "🔴 Odpojený"
    except:
        stats = {'process_count': 0, 'sessions_count': 0}
        connection_status = "🔴 Odpojený"
    
    st.markdown("""
    <div class="status-section">
        <div class="status-title">
            <span>✅</span>
            Stav systému
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Status metriky
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Databáza", connection_status)
    
    with col2:
        st.metric("Procesy", f"{stats['process_count']}")
    
    with col3:
        st.metric("Sessions", f"{stats.get('sessions_count', 0)}")

def process_chat_query(query: str) -> str:
    """Spracuje chat query a vráti odpoveď"""
    
    # Základné odpovede na časté otázky
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['všetky procesy', 'zoznam', 'procesy']):
        try:
            db_manager = st.session_state.airtable_manager
            processes = db_manager.get_all_processes()
            
            if not processes:
                return "📋 **Žiadne procesy nenájdené**\n\nMôžete pridať nový proces pomocou tlačidla 'Pridať proces'."
            
            response = f"📋 **Našiel som {len(processes)} procesov:**\n\n"
            for i, process in enumerate(processes[:10], 1):
                name = process.get('name', 'Bez názvu')
                category = process.get('category', 'Neurčené')
                owner = process.get('owner', 'Neurčený')
                response += f"{i}. **{name}** ({category}) - {owner}\n"
            
            if len(processes) > 10:
                response += f"\n... a ďalších {len(processes) - 10} procesov"
            
            return response
            
        except Exception as e:
            return f"❌ **Chyba pri načítavaní procesov**\n\n{str(e)}"
    
    elif any(word in query_lower for word in ['koľko', 'počet', 'stats', 'štatistiky']):
        try:
            stats = st.session_state.airtable_manager.get_process_statistics()
            
            return f"""📊 **Štatistiky systému:**

🔢 **Procesy:** {stats['process_count']}
📝 **Sessions:** {stats.get('sessions_count', 0)}
⚡ **Priemerná automatizácia:** {stats.get('avg_automation', 0):.1f}/5
👥 **Dokumentátori:** {len(stats.get('top_documenters', []))}

🎯 Systém je pripravený na prácu!"""
            
        except Exception as e:
            return f"❌ **Chyba pri načítavaní štatistík**\n\n{str(e)}"
    
    elif 'obchodné' in query_lower or 'obchod' in query_lower:
        try:
            db_manager = st.session_state.airtable_manager
            all_processes = db_manager.get_all_processes()
            business_processes = [p for p in all_processes if 'obchod' in str(p.get('category', '')).lower()]
            
            if not business_processes:
                return "🏢 **Žiadne obchodné procesy nenájdené**\n\nMôžete pridať nový obchodný proces pomocou tlačidla 'Pridať proces'."
            
            response = f"🏢 **Obchodné procesy ({len(business_processes)}):**\n\n"
            for i, process in enumerate(business_processes, 1):
                name = process.get('name', 'Bez názvu')
                owner = process.get('owner', 'Neurčený')
                duration = process.get('duration_minutes', 0)
                time_str = f"{duration} min" if duration else "Neurčené"
                response += f"{i}. **{name}** - {owner} ({time_str})\n"
            
            return response
            
        except Exception as e:
            return f"❌ **Chyba pri hľadaní obchodných procesov**\n\n{str(e)}"
    
    else:
        return f"""🤖 **Rozumiem vašej otázke:** "{query}"

Momentálne môžem pomôcť s:
• 📋 Zobrazenie všetkých procesov
• 📊 Štatistiky a počty  
• 🏢 Filtrovanie podľa kategórií
• ➕ Pridávanie nových procesov

Skúste niektorú z rýchlych otázok alebo zadajte konkrétny dotaz!"""

def main():
    """Hlavná funkcia Airtable Managera"""
    init_airtable_ui()
    
    # Automatické načítanie API kľúčov
    if 'api_keys_loaded' not in st.session_state:
        stored_keys = get_api_keys()
        if stored_keys:
            if 'airtable_key' in stored_keys and 'airtable_base' in stored_keys:
                st.session_state.airtable_manager = HybridDatabaseManager(
                    use_airtable=True,
                    airtable_api_key=stored_keys['airtable_key'],
                    airtable_base_id=stored_keys['airtable_base']
                )
        st.session_state.api_keys_loaded = True
    
    # Inicializácia session state
    if 'mode' not in st.session_state:
        st.session_state.mode = "chat"
    
    # Header
    render_airtable_header()
    
    # Main buttons
    chat_btn, add_btn = render_main_buttons()
    
    # Chat interface
    render_chat_interface()
    
    # Query input
    user_query, ask_btn = render_query_input()
    
    # Quick questions
    quick_question = render_quick_questions()
    
    # Spracovanie query
    query_to_process = None
    if ask_btn and user_query:
        query_to_process = user_query
    elif quick_question:
        query_to_process = quick_question
    
    if query_to_process:
        # Pridaj do histórie
        current_time = datetime.now().strftime("%H:%M:%S")
        
        st.session_state.chat_history.append({
            'type': 'user',
            'content': query_to_process,
            'timestamp': current_time
        })
        
        # Spracuj a pridaj odpoveď
        with st.spinner("🤖 Spracovávam..."):
            response = process_chat_query(query_to_process)
        
        st.session_state.chat_history.append({
            'type': 'bot', 
            'content': response,
            'timestamp': current_time
        })
        
        # Vyčisti input a rerun
        st.session_state.query_input = ""
        st.rerun()
    
    # System status
    render_system_status()
    
    # Sidebar s nastaveniami (skrytý ale dostupný)
    with st.sidebar:
        st.markdown("### ⚙️ Nastavenia")
        
        if st.button("🔄 Resetovať chat"):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("🗄️ Konfigurácia Airtable"):
            st.info("Pre nastavenie Airtable API kľúčov použite hlavnú aplikáciu")
        
        # API status
        has_airtable = bool(st.session_state.get('airtable_manager'))
        st.metric("Airtable", "✅ Pripojené" if has_airtable else "❌ Nie je nastavené")

if __name__ == "__main__":
    main() 