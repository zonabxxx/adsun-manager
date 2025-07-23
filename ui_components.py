#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN UI Components
UI render funkcie a pomocné funkcie
"""

import streamlit as st
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import sqlite3
import re

from ai_components import RealAIReasoningEngine
from database_components import DatabaseManager, get_sample_processes
from adsun_process_mapper_ai import ProcessContext
from adsun_knowledge_assistant import ADSUNKnowledgeAssistant
from airtable_connector import HybridDatabaseManager
from api_manager import render_api_settings, get_api_keys
from ui_styles import get_main_css

def init_streamlit_config():
    """Moderné nastavenia Streamlit aplikácie"""
    st.set_page_config(
        page_title="🎯 ADSUN Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Moderný CSS design z modulu
    st.markdown(get_main_css(), unsafe_allow_html=True)

def render_header():
    """Render hlavného headeru v štýle používateľa"""
    
    # Inicializácia hybrid DB managera ak neexistuje
    if 'hybrid_db_manager' not in st.session_state:
        st.session_state.hybrid_db_manager = HybridDatabaseManager()
    
    stats = st.session_state.hybrid_db_manager.get_process_statistics()
    
    st.markdown(f"""
    <div class="main-header">
        <div class="header-title">
            <span>🤖</span>
            ADSUN Assistant
        </div>
        <div class="header-subtitle">
            Kompletný systém firemných procesov
        </div>
        <div class="header-stats">
            <div class="stat-item">
                <span>📋</span>
                <span>{stats['process_count']} procesov načítaných</span>
            </div>
            <div class="stat-item">
                <span>📊</span>
                <span>{stats.get('sessions_count', 0)} sessions</span>
            </div>
            <div class="stat-item">
                <span>👥</span>
                <span>Dokumentátorov: {len(stats.get('top_documenters', []))}</span>
            </div>
            <div class="stat-item">
                <span>🎯</span>
                <span>ADSUN Management System v1.0</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_process_cards():
    """Render procesov ako karty v štýle používateľa"""
    
    # Inicializácia databázy ak neexistuje
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    
    processes = st.session_state.db_manager.get_all_processes()
    
    # Ak nie sú procesy, vytvor vzorové
    if not processes:
        processes = get_sample_processes()
    
    for process in processes:
        category = process.get('category', 'admin').lower()
        duration = process.get('duration_minutes', 0) or 0  # Fix: handle None values
        
        # Formatovanie času
        if duration >= 60:
            time_str = f"{duration//60}-{(duration//60)+1} hodín" if duration >= 120 else f"{duration//60} hodín"
        else:
            time_str = f"{duration} minút"
        
        # Kategória styling
        tag_class = f"tag-{category}"
        
        # Render karty procesu
        st.markdown(f"""
        <div class="process-card" onclick="selectProcess('{process['name']}')">
            <div class="process-title">{process['name']}</div>
            <div class="process-meta">
                <span><strong>{process.get('category', 'Admin').title()}</strong></span>
                <span>• {process.get('owner', 'Neurčený')}</span>
                <span>• {time_str}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_quick_questions():
    """Render rýchlych otázok v štýle používateľa"""
    
    st.markdown("""
    <div class="quick-questions">
        <div style="margin-bottom: 1rem; font-weight: 600; color: #2C3E50;">
            Rýchle otázky:
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Rýchle otázky v grid layout
    quick_questions = [
        "Ako naceniť polep auta?",
        "Kroky príjmu dopytu", 
        "Proces realizácie polepov",
        "Tvorba cenovej ponuky",
        "Kto za čo zodpovedá?",
        "Štatistiky procesov"
    ]
    
    cols = st.columns(3)
    for i, question in enumerate(quick_questions):
        with cols[i % 3]:
            if st.button(question, key=f"quick_{i}", use_container_width=True):
                st.session_state.selected_question = question
                st.session_state.show_assistant = True
                st.rerun()

def render_sidebar_config():
    """Render konfiguračného sidebaru - zjednodušená verzia"""
    with st.sidebar:
        # Automatické načítanie uložených kľúčov pri spustení
        if 'api_keys_loaded' not in st.session_state:
            stored_keys = get_api_keys()
            if stored_keys:
                if 'openai' in stored_keys:
                    st.session_state.openai_api_key = stored_keys['openai']
                    os.environ['OPENAI_API_KEY'] = stored_keys['openai']
                if 'airtable_key' in stored_keys:
                    st.session_state.airtable_api_key = stored_keys['airtable_key']
                if 'airtable_base' in stored_keys:
                    st.session_state.airtable_base_id = stored_keys['airtable_base']
            st.session_state.api_keys_loaded = True
        
        # Hlavna navigacia
        st.markdown("### 🎯 ADSUN Assistant")
        
        # Pouzivatel
        if 'documenter_name' not in st.session_state:
            st.session_state.documenter_name = ""
        
        documenter_name = st.text_input(
            "👤 Vaše meno:",
            value=st.session_state.documenter_name,
            help="Pre ukladanie dokumentácie"
        )
        
        if documenter_name != st.session_state.documenter_name:
            st.session_state.documenter_name = documenter_name
        
        # Hlavné režimy - veľké tlačidlá
        st.markdown("---")
        st.markdown("### 🚀 Hlavné funkcie")
        
        # Režim overview (domov)
        if st.button("🏠 Prehľad", use_container_width=True, help="Hlavná stránka s procesmi"):
            st.session_state.mode = "overview"
            st.rerun()
        
        # AI asistent  
        if st.button("🤖 AI Assistant", use_container_width=True, help="Inteligentné odpovede na otázky"):
            st.session_state.mode = "assistant"
            st.rerun()
        
        # Učenie procesov
        if st.button("📚 Učenie procesov", use_container_width=True, help="AI-asistované dokumentovanie"):
            st.session_state.mode = "learning"
            st.rerun()
        
        # Managment - rozbaľovacia sekcia
        st.markdown("---")
        with st.expander("🏢 **Business Management**", expanded=False):
            if st.button("📋 Procesy", use_container_width=True):
                st.session_state.mode = "process_management"
                st.rerun()
            
            if st.button("🏛️ Oddelenia", use_container_width=True):
                st.session_state.mode = "departments"
                st.rerun()
            
            if st.button("👥 Pozície", use_container_width=True):
                st.session_state.mode = "positions"
                st.rerun()
            
            if st.button("⚙️ Nastavenia firmy", use_container_width=True):
                st.session_state.mode = "company_settings"
                st.rerun()
        
        # Databáza a nastavenia - rozbaľovacia sekcia
        with st.expander("🗄️ **Databáza & Nastavenia**", expanded=False):
            if st.button("📊 Správa databázy", use_container_width=True):
                st.session_state.mode = "database_management"
                st.rerun()
            
            if st.button("🏗️ Schéma databázy", use_container_width=True):
                st.session_state.mode = "database_schema"
                st.rerun()
            
            # Databáza typ - kompaktné
            st.markdown("**Typ databázy:**")
            db_type = st.radio(
                "typ_db",
                ["SQLite", "Airtable"],
                help="Vyberte spôsob ukladania dát",
                label_visibility="collapsed"
            )
            
            use_airtable = db_type == "Airtable"
            
            if use_airtable:
                # Kompaktné Airtable nastavenia
                api_key = st.text_input(
                    "API Key:", 
                    value=st.session_state.get('airtable_api_key', ''),
                    type="password",
                    help="Airtable API token"
                )
                base_id = st.text_input(
                    "Base ID:", 
                    value=st.session_state.get('airtable_base_id', ''),
                    help="ID vašej Airtable base"
                )
                
                # Uloženie do session state
                if api_key != st.session_state.get('airtable_api_key', ''):
                    st.session_state.airtable_api_key = api_key
                if base_id != st.session_state.get('airtable_base_id', ''):
                    st.session_state.airtable_base_id = base_id
                
                if api_key and base_id:
                    if 'hybrid_db_manager' not in st.session_state:
                        st.session_state.hybrid_db_manager = HybridDatabaseManager(
                            use_airtable=True,
                            airtable_api_key=api_key,
                            airtable_base_id=base_id
                        )
        
        # AI nastavenia - rozbaľovacia sekcia  
        with st.expander("🤖 **AI Nastavenia**", expanded=False):
            # OpenAI API key
            openai_key = st.text_input(
                "OpenAI API Key:", 
                value=st.session_state.get('openai_api_key', ''),
                type="password",
                help="Pre AI reasoning a predikcie"
            )
            
            # Uloženie do session state a environment
            if openai_key != st.session_state.get('openai_api_key', ''):
                st.session_state.openai_api_key = openai_key
                if openai_key:
                    os.environ['OPENAI_API_KEY'] = openai_key
                    st.success("✅ AI aktivované!", icon="🤖")
            elif openai_key:
                st.success("✅ AI aktivované!", icon="🤖")
            
            # Jednoduché API nastavenia bez expandera
            st.markdown("**Pokročilé nastavenia:**")
            
            # API model selection
            model_options = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
            selected_model = st.selectbox(
                "AI Model:",
                model_options,
                index=0,
                help="Vyberte AI model pre reasoning"
            )
            st.session_state.ai_model = selected_model
            
            # Temperature setting
            temperature = st.slider(
                "Kreativita AI:",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="0 = konzervatívne, 1 = kreatívne"
            )
            st.session_state.ai_temperature = temperature
        
        # Status indikátory na spodku
        st.markdown("---")
        render_status_indicators()

def render_status_indicators():
    """Zobrazí status indikátory systému"""
    st.markdown("### 📊 Status")
    
    # AI status
    if st.session_state.get('openai_api_key'):
        st.success("🤖 AI aktívne", icon="✅")
    else:
        st.warning("🤖 AI neaktívne", icon="⚠️")
    
    # Databáza status
    if st.session_state.get('hybrid_db_manager'):
        if hasattr(st.session_state.hybrid_db_manager, 'connection_ok') and st.session_state.hybrid_db_manager.connection_ok:
            st.success("🗄️ Airtable pripojené", icon="☁️")
        else:
            st.info("🗄️ SQLite lokálne", icon="💾")
    else:
        st.info("🗄️ SQLite lokálne", icon="💾")
    
    # Dokumentátor
    if st.session_state.get('documenter_name'):
        st.info(f"👤 {st.session_state.documenter_name}", icon="✅")
    else:
        st.warning("👤 Nezadané meno", icon="⚠️")

def render_learning_mode():
    """Render režimu učenia procesov s AI asistentom"""
    from business_management import render_process_learning
    render_process_learning()

def render_assistant_mode():
    """Render AI Assistant režimu - Chat Interface"""
    st.markdown("## 💬 AI Chat Assistant")
    st.markdown("*Konverzácia s AI o vašich procesoch - pýtajte sa koľko chcete!*")
    
    # Inicializácia chat histórie
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        # Uvítacia správa
        welcome_msg = {
            'type': 'ai',
            'content': """👋 **Ahoj! Som váš AI asistent pre procesy.**

🎯 **Môžete sa ma pýtať:**
• "Koľko procesov mám?" - štatistiky a prehľad
• "Všetky procesy" - kompletný zoznam
• "Aké kategórie mám?" - typy procesov  
• "Kto za čo zodpovedá?" - organizácia
• "Ako naceniť polep auta?" - konkrétne procesy

💡 **Píšte prirodzene - rozumiem rôznym formuláciám!**""",
            'timestamp': datetime.now()
        }
        st.session_state.chat_history.append(welcome_msg)
    
    # Inicializácia knowledge assistant
    if 'knowledge_assistant' not in st.session_state:
        st.session_state.knowledge_assistant = ADSUNKnowledgeAssistant()
    
    # Chat container s históriou
    chat_container = st.container()
    
    with chat_container:
        # Zobrazenie chat histórie
        for msg in st.session_state.chat_history:
            if msg['type'] == 'user':
                # Používateľská správa - napravo, modré pozadie
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 10px 0;">
                    <div style="background-color: #007bff; color: white; padding: 12px 16px; border-radius: 18px 18px 4px 18px; max-width: 70%; word-wrap: break-word;">
                        <strong>👤 Vy:</strong><br>
                        {msg['content']}
                        <div style="font-size: 0.7em; opacity: 0.8; margin-top: 5px;">
                            {msg['timestamp'].strftime('%H:%M')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            else:  # AI správa
                # AI správa - naľavo, sivé pozadie
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 10px 0;">
                    <div style="background-color: #f1f3f4; color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 4px; max-width: 85%; word-wrap: break-word;">
                        <strong>🤖 AI Assistant:</strong><br>
                        {msg['content']}
                        <div style="font-size: 0.7em; opacity: 0.6; margin-top: 5px;">
                            {msg['timestamp'].strftime('%H:%M')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Separator
    st.markdown("---")
    
    # Input sekcia na spodku
    st.markdown("### 💬 Napíšte vašu otázku:")
    
    # Text input pre nové správy - Form pre lepšie spracovanie
    with st.form(key=f"chat_form_{len(st.session_state.chat_history)}", clear_on_submit=True):
        user_input = st.text_input(
            "Napíšte otázku:",
            placeholder="napr: Koľko procesov zatiaľ mám nahraných?",
            label_visibility="collapsed"
        )
        
        # Form submit tlačidlo
        submitted = st.form_submit_button("📤 Odoslať", type="primary", use_container_width=True)
    
    # Tlačidlá mimo formu
    col1, col2 = st.columns([1, 1])
    
    with col1:
        clear_button = st.button("🗑️ Vyčistiť chat", use_container_width=True)
    
    with col2:
        if st.button("⚡ Rýchle otázky", use_container_width=True):
            st.session_state.show_quick_questions = not st.session_state.get('show_quick_questions', False)
    
    # Zobrazenie rýchlych otázok ak je požadované
    if st.session_state.get('show_quick_questions', False):
        st.markdown("**⚡ Rýchle otázky:**")
        quick_questions = [
            "Koľko procesov mám?",
            "Všetky procesy", 
            "Aké kategórie mám?",
            "Kto za čo zodpovedá?",
            "Ako naceniť polep auta?",
            "Proces realizácie polepov"
        ]
        
        cols = st.columns(3)
        for i, question in enumerate(quick_questions):
            with cols[i % 3]:
                if st.button(question, key=f"quick_chat_{i}", use_container_width=True):
                    # Pridaj otázku ako používateľskú správu
                    user_msg = {
                        'type': 'user',
                        'content': question,
                        'timestamp': datetime.now()
                    }
                    st.session_state.chat_history.append(user_msg)
                    
                    # Získaj odpoveď od AI
                    with st.spinner("🤖 AI premýšľa..."):
                        ai_response = st.session_state.knowledge_assistant.answer_query(question)
                        ai_response = clean_ai_response(ai_response)  # Očisti od HTML
                    
                    # Pridaj AI odpoveď
                    ai_msg = {
                        'type': 'ai',
                        'content': ai_response,
                        'timestamp': datetime.now()
                    }
                    st.session_state.chat_history.append(ai_msg)
                    
                    # Skry rýchle otázky a refresh
                    st.session_state.show_quick_questions = False
                    st.rerun()
    
    # Spracovanie odoslanej správy z formu
    if submitted and user_input.strip():
        # Resetuj enter_pressed flag
        st.session_state.enter_pressed = False
        
        # Pridaj používateľskú správu
        user_msg = {
            'type': 'user',
            'content': user_input.strip(),
            'timestamp': datetime.now()
        }
        st.session_state.chat_history.append(user_msg)
        
        # Získaj odpoveď od AI
        with st.spinner("🤖 AI pripravuje odpoveď..."):
            try:
                ai_response = st.session_state.knowledge_assistant.answer_query(user_input.strip())
                ai_response = clean_ai_response(ai_response)  # Očisti od HTML
            except Exception as e:
                ai_response = f"❌ **Chyba:** {e}\n\n💡 **Skúste:** Napísať otázku inak alebo použiť 'Učenie procesov'"
        
        # Pridaj AI odpoveď
        ai_msg = {
            'type': 'ai', 
            'content': ai_response,
            'timestamp': datetime.now()
        }
        st.session_state.chat_history.append(ai_msg)
        
        # Refresh stránku (input sa vyčistí automaticky)
        st.rerun()
    
    # Vyčistenie chatu
    if clear_button:
        st.session_state.chat_history = []
        # Pridaj znova uvítaciu správu
        welcome_msg = {
            'type': 'ai',
            'content': """👋 **Chat vyčistený! Začnime znova.**

🎯 **Pýtajte sa ma na čokoľvek o vašich procesoch!**
• Štatistiky a počty
• Zoznamy procesov  
• Organizáciu a pozície
• Konkrétne postupy

💬 **Teraz máte čistý chat pre novú konverzáciu!**""",
            'timestamp': datetime.now()
        }
        st.session_state.chat_history.append(welcome_msg)
        st.rerun()
    
    # Štatistiky chatu v sidebari
    with st.sidebar:
        if len(st.session_state.chat_history) > 1:  # Viac ako len uvítacia správa
            st.markdown("### 📊 Chat štatistiky")
            total_messages = len(st.session_state.chat_history)
            user_messages = len([m for m in st.session_state.chat_history if m['type'] == 'user'])
            st.metric("💬 Celkom správ", total_messages)
            st.metric("❓ Vašich otázok", user_messages)
            
            if st.button("📥 Export chat", use_container_width=True):
                # Exportuj chat do textu
                chat_text = "# ADSUN AI Chat Export\n\n"
                for msg in st.session_state.chat_history:
                    sender = "👤 VY" if msg['type'] == 'user' else "🤖 AI"
                    time = msg['timestamp'].strftime('%H:%M')
                    chat_text += f"**{sender}** ({time}):\n{msg['content']}\n\n---\n\n"
                
                st.download_button(
                    label="💾 Stiahnuť chat",
                    data=chat_text,
                    file_name=f"adsun_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown"
                ) 

def clean_ai_response(response: str) -> str:
    """Očistí AI odpoveď od HTML tagov"""
    if not response:
        return response
    
    # Odstráni HTML tagy
    html_pattern = r'<[^>]+>'
    cleaned = re.sub(html_pattern, '', response)
    
    # Odstráni viacnásobné medzery a nova riadky
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    cleaned = re.sub(r' +', ' ', cleaned)
    
    return cleaned.strip()

def render_section_header(title: str, subtitle: str, icon: str = "📋", stats: Dict = None):
    """Render jednotného moderného headera pre všetky sekcie"""
    stats_html = ""
    if stats:
        stats_items = []
        for key, value in stats.items():
            if isinstance(value, dict) and 'icon' in value and 'text' in value:
                stats_items.append(f'<div class="stat-item"><span>{value["icon"]}</span><span>{value["text"]}</span></div>')
            else:
                stats_items.append(f'<div class="stat-item"><span>📊</span><span>{key}: {value}</span></div>')
        stats_html = f'<div class="header-stats">{"".join(stats_items)}</div>'
    
    st.markdown(f"""
    <div class="main-header">
        <div class="header-title">
            <span>{icon}</span>
            {title}
        </div>
        <div class="header-subtitle">
            {subtitle}
        </div>
        {stats_html}
    </div>
    """, unsafe_allow_html=True)

def render_action_buttons(actions: List[Dict], columns: int = 3):
    """Render jednotných akčných tlačidiel"""
    cols = st.columns(columns)
    for i, action in enumerate(actions):
        with cols[i % columns]:
            if st.button(
                f"{action.get('icon', '⚡')} {action['label']}", 
                key=action.get('key', f"action_{i}"),
                type=action.get('type', 'secondary'),
                use_container_width=True,
                help=action.get('help', '')
            ):
                if 'callback' in action:
                    action['callback']()
                if 'session_state' in action:
                    for key, value in action['session_state'].items():
                        st.session_state[key] = value
                if action.get('rerun', False):
                    st.rerun()

def render_modern_dataframe(data: List[Dict], columns: List[str] = None, actions: List[Dict] = None):
    """Render modernej tabuľky s akciami"""
    if not data:
        st.info("📋 Žiadne dáta na zobrazenie")
        return
    
    # Ak nie sú definované stĺpce, vezmi všetky
    if not columns:
        columns = list(data[0].keys())
    
    # Vyfiltruj len požadované stĺpce
    filtered_data = []
    for item in data:
        filtered_item = {col: item.get(col, '-') for col in columns}
        filtered_data.append(filtered_item)
    
    # Zobraz ako dataframe
    import pandas as pd
    df = pd.DataFrame(filtered_data)
    
    # Konvertuj všetky hodnoty na stringy pre PyArrow kompatibilitu
    for col in df.columns:
        df[col] = df[col].astype(str)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Akčné tlačidlá ak sú definované
    if actions:
        st.markdown("### ⚡ Akcie")
        render_action_buttons(actions) 