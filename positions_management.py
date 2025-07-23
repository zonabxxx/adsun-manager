#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Positions Management
Správa pozícií s AI-driven vytváraním a automatickým dopĺňaním
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from ai_components import RealAIReasoningEngine
from ui_components import render_section_header, render_action_buttons, render_modern_dataframe

def load_existing_departments() -> List[str]:
    """Načíta existujúce oddelenia z databázy"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            
            # Pokús sa načítať z departments tabuľky
            try:
                cursor = conn.execute("SELECT DISTINCT name FROM departments ORDER BY name")
                departments = [row[0] for row in cursor.fetchall() if row[0]]
                if departments:
                    return departments
            except sqlite3.OperationalError:
                pass  # Tabuľka departments neexistuje
            
            # Fallback - načítaj z positions tabuľky
            try:
                cursor = conn.execute("SELECT DISTINCT department FROM positions WHERE department IS NOT NULL AND department != '' ORDER BY department")
                departments = [row[0] for row in cursor.fetchall() if row[0]]
                return departments
            except sqlite3.OperationalError:
                return []  # Ani positions tabuľka neexistuje
                
    except Exception as e:
        st.error(f"❌ Chyba načítavania oddelení: {e}")
        return []

def render_positions():
    """Render správy pozícií"""
    
    # Načítanie pozícií z databázy
    positions = load_positions_from_db()
    
    # Moderný header so štatistikami
    departments = list(set(pos.get('department', 'Neurčené') for pos in positions))
    levels = list(set(pos.get('level', 'Neurčené') for pos in positions))
    
    stats = {
        "positions": {"icon": "👥", "text": f"{len(positions)} pozícií"},
        "departments": {"icon": "🏢", "text": f"{len(departments)} oddelení"},
        "levels": {"icon": "📊", "text": f"{len(levels)} úrovní"}
    }
    
    render_section_header(
        title="Pozície",
        subtitle="Správa firemných pozícií s AI asistentom pre dopĺňanie",
        icon="👥",
        stats=stats
    )
    
    # DETAILY MIMO EXPANDERA - AK SÚ ZOBRAZENÉ
    if 'show_position_details' in st.session_state:
        position_id = st.session_state.show_position_details
        st.markdown("---")
        show_position_details(position_id)
        
        if st.button("❌ Zavrieť detaily", type="secondary"):
            del st.session_state.show_position_details
            st.rerun()
        
        st.markdown("---")
    
    # ZODPOVEDNOSTI MIMO EXPANDERA - AK SÚ ZOBRAZENÉ
    if 'show_position_responsibilities' in st.session_state:
        position_id = st.session_state.show_position_responsibilities
        st.markdown("---")
        show_position_responsibilities(position_id)
        
        if st.button("❌ Zavrieť zodpovednosti", type="secondary"):
            del st.session_state.show_position_responsibilities
            st.rerun()
        
        st.markdown("---")
    
    # Pridanie novej pozície
    with st.expander("➕ Pridať novú pozíciu"):
        if st.session_state.get('position_learning_mode', False):
            render_position_learning()
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**🤖 AI vás povedie otázkami pre vytvorenie pozície**")
                st.info("AI položí otázky a pomôže vyplniť štandardné informácie o pozícii.")
            
            with col2:
                if st.button("🚀 Začať s AI", type="primary", key="start_position_ai"):
                    st.session_state.position_learning_mode = True
                    st.session_state.position_learning_step = 0
                    st.session_state.position_learning_history = []
                    st.session_state.current_position_data = {}
                    st.rerun()
    
    # Zobrazenie existujúcich pozícií
    if not positions:
        st.info("👥 Žiadne pozície ešte nie sú definované")
        return
    
    # Moderné zobrazenie pozícií v jednotnom štýle
    st.markdown("### 👥 Prehľad pozícií")
    
    # Použijeme jednotný štýl pre všetky pozície (ako departments a processes)
    for pos in positions:
        with st.expander(f"👤 {pos['name']}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # Základné info v jednotnom štýle
                st.write(f"**📝 Popis:** {pos.get('description', 'Bez popisu')[:100]}{'...' if len(pos.get('description', '')) > 100 else ''}")
                st.write(f"**🏢 Oddelenie:** {pos.get('department', 'Neurčené')}")
                st.write(f"**📊 Úroveň:** {pos.get('level', 'Neurčené')}")
                st.write(f"**⏰ Pracovný čas:** {pos.get('work_time', 'Neurčené')}")
                
                if pos.get('requirements'):
                    st.write(f"**📋 Požiadavky:** {pos.get('requirements', '')[:100]}{'...' if len(pos.get('requirements', '')) > 100 else ''}")
            
            with col2:
                # TLAČIDLÁ DETAILY A ZODPOVEDNOSTI TERAZ ZOBRAZUJÚ MIMO EXPANDERA
                if st.button("📋 Detaily", key=f"pos_details_{pos['id']}", use_container_width=True):
                    st.session_state.show_position_details = pos['id']
                    st.rerun()
                
                if st.button("📊 Zodpovednosti", key=f"responsibilities_{pos['id']}", use_container_width=True):
                    st.session_state.show_position_responsibilities = pos['id']
                    st.rerun()
            
            with col3:
                if st.button("✏️ Upraviť", key=f"edit_pos_{pos['id']}", use_container_width=True):
                    st.session_state.edit_position_id = pos['id']
                    st.session_state.mode = "edit_position"
                    st.rerun()
                
                if st.button("🗑️ Zmazať", key=f"delete_pos_{pos['id']}", use_container_width=True):
                    st.warning(f"⚠️ Zmazanie pozície {pos['name']} - funkcia bude dostupná v ďalšej verzii")

def load_positions_from_db() -> List[Dict]:
    """Načíta pozície z databázy"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            
            # Vytvor tabuľku ak neexistuje
            conn.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    department TEXT,
                    level TEXT,
                    responsibilities TEXT,
                    requirements TEXT,
                    tools_systems TEXT,
                    work_time TEXT,
                    challenges TEXT,
                    success_metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor = conn.execute("""
                SELECT * FROM positions 
                ORDER BY name
            """)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"❌ Chyba načítavania pozícií: {e}")
        return []

def show_position_details(position_id: int):
    """Zobrazí detaily pozície"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
            position = dict(cursor.fetchone())
            
            st.markdown(f"### 👤 Detaily pozície: {position['name']}")
            
            # ÚPLNE BEZ STĹPCOV - všetko pod sebou na plnú šírku
            st.markdown("#### 📋 Základné informácie")
            
            # Všetko pod sebou namiesto stĺpcov
            st.markdown(f"**🏢 Oddelenie:** {position.get('department', 'Neurčené')}")
            st.markdown(f"**📊 Úroveň zodpovednosti:** {position.get('level', 'Neurčené')}")
            st.markdown(f"**⏰ Pracovný čas:** {position.get('work_time', 'Neurčené')}")
            
            # Oddeľovač
            st.markdown("---")
            
            # Detailné informácie na plnú šírku
            if position.get('description'):
                st.markdown("#### 📝 Úplný popis pozície")
                st.markdown(position['description'])
                st.markdown("")
            
            if position.get('responsibilities'):
                st.markdown("#### 📋 Zodpovednosti")
                st.markdown(position['responsibilities'])
                st.markdown("")
            
            if position.get('requirements'):
                st.markdown("#### ✅ Požiadavky") 
                st.markdown(position['requirements'])
                st.markdown("")
                
            if position.get('tools_systems'):
                st.markdown("#### 🛠️ Nástroje a systémy")
                st.markdown(position['tools_systems'])
                st.markdown("")
                
            if position.get('challenges'):
                st.markdown("#### ⚠️ Výzvy a problémy")
                st.markdown(position['challenges'])
                st.markdown("")
            
            if position.get('success_metrics'):
                st.markdown("#### 🎯 Metriky úspechu")
                st.markdown(position['success_metrics'])
                st.markdown("")
                
    except Exception as e:
        st.error(f"❌ Chyba načítavania detailov: {e}")

def show_position_responsibilities(position_id: int):
    """Zobrazí zodpovednosti pozície"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
            position = dict(cursor.fetchone())
            
            st.markdown(f"### 📊 Zodpovednosti: {position['name']}")
            
            # ŠIROKÝ LAYOUT - všetko na plnú šírku bez expanders
            st.markdown("#### 📋 Hlavné zodpovednosti a KPI")
            st.markdown("---")
                
            # Zodpovednosti na plnú šírku
            if position.get('responsibilities'):
                st.markdown("**📋 Zoznam zodpovedností:**")
                responsibilities = position['responsibilities'].split('\n')
                for i, resp in enumerate(responsibilities[:8], 1):  # Max 8
                    if resp.strip():
                        st.markdown(f"**{i}.** {resp.strip()}")
                st.markdown("")
            else:
                st.info("📝 Žiadne zadefinované zodpovednosti")
            
            # Metriky úspechu na plnú šírku  
            if position.get('success_metrics'):
                st.markdown("**🎯 KPI a metriky úspechu:**")
                metrics = position['success_metrics'].split('\n')
                for i, metric in enumerate(metrics[:8], 1):  # Max 8
                    if metric.strip():
                        st.markdown(f"**📊 {i}.** {metric.strip()}")
                st.markdown("")
            else:
                st.info("📊 Žiadne zadefinované metriky")
            
            # Výzvy a nástroje na plnú šírku
            st.markdown("---")
            
            if position.get('challenges'):
                st.markdown("#### ⚠️ Hlavné výzvy")
                st.markdown(position['challenges'])
                st.markdown("")
            
            if position.get('tools_systems'):
                st.markdown("#### 🛠️ Používané nástroje")
                st.markdown(position['tools_systems'])
                st.markdown("")
                
    except Exception as e:
        st.error(f"❌ Chyba načítavania zodpovedností: {e}")

def render_position_learning():
    """AI-driven učenie novej pozície s inteligentným dopĺňaním"""
    st.markdown("### 🤖 AI Asistent pre novú pozíciu")
    st.markdown("*AI vám pomôže vyplniť všetky polia o pozícii*")
    
    # KONTROLA PREPNUTIA NA STEP-BY-STEP
    if st.session_state.get('switch_to_position_step_by_step', False):
        # Vyčistíme flag a resetujeme na step-by-step
        del st.session_state.switch_to_position_step_by_step
        # Nastavíme default hodnotu pre radio (bude sa zobrazovať step-by-step)
        default_method = "🔄 Postupný sprievodca (krok za krokom)"
    else:
        # Ak nie je flag nastavený, použijeme existujúcu hodnotu alebo default
        default_method = st.session_state.get('position_creation_method', "🔄 Postupný sprievodca (krok za krokom)")
    
    # VÝBER SPÔSOBU VYTVORENIA POZÍCIE
    st.markdown("#### 🎯 Vyberte spôsob vytvorenia pozície:")
    
    creation_method = st.radio(
        "Ako chcete vytvoriť pozíciu?",
        [
            "🔄 Postupný sprievodca (krok za krokom)",
            "📋 Bulk import z ChatGPT konverzácie"
        ],
        index=0 if default_method == "🔄 Postupný sprievodca (krok za krokom)" else 1,
        key="position_creation_method"
    )
    
    if creation_method == "📋 Bulk import z ChatGPT konverzácie":
        render_position_bulk_import()
        return
    
    # PÔVODNÝ POSTUPNÝ SPRIEVODCA
    st.markdown("---")
    st.markdown("**🔄 Postupný sprievodca - krok za krokom**")
    
    # INICIALIZÁCIA DÁT AK NEEXISTUJÚ - MUSI BYŤ PRED PRVÝM PRÍSTUPOM!
    if 'current_position_data' not in st.session_state:
        st.session_state.current_position_data = {}
    
    # DEFINÍCIA POLÍ - MUSI BYŤ PRED PRVÝM POUŽITÍM!
    position_fields = [
        {
            'key': 'name',
            'label': 'Názov pozície',
            'question': 'Aký je názov novej pozície?',
            'placeholder': 'napr. Obchodný manažér, Programátor, HR manažér',
            'ai_prompt': 'Navrhni 3 alternatívne názvy pre pozíciu typu {value}'
        },
        {
            'key': 'description',
            'label': 'Popis pozície',
            'question': 'Aký je stručný popis tejto pozície?',
            'placeholder': 'Opíšte čo táto pozícia robí...',
            'ai_prompt': 'Napíš profesionálny popis pre pozíciu {name} - čo robí, aká je jej úloha vo firme'
        },
        {
            'key': 'department',
            'label': 'Oddelenie',
            'question': 'Do akého oddelenia patrí táto pozícia?',
            'placeholder': 'napr. Obchod, IT, HR, Výroba',
            'ai_prompt': 'Na základe pozície {name} a existujúcich oddelení navrhni vhodné oddelenie. Ak je možné, použi existujúce oddelenie.'
        },
        {
            'key': 'level',
            'label': 'Úroveň zodpovednosti',
            'question': 'Aká je úroveň zodpovednosti?',
            'placeholder': 'junior, senior, manažér, vedúci, riaditeľ',
            'ai_prompt': 'Navrhni úroveň zodpovednosti pre pozíciu {name}'
        },
        {
            'key': 'responsibilities',
            'label': 'Zodpovednosti',
            'question': 'Aké sú hlavné zodpovednosti tejto pozície?',
            'placeholder': 'Popíšte hlavné úlohy a zodpovednosti...',
            'ai_prompt': 'Napíš konkrétne zodpovednosti a úlohy pre pozíciu {name} v {department} oddelení'
        },
        {
            'key': 'requirements',
            'label': 'Požiadavky',
            'question': 'Aké sú požiadavky na túto pozíciu?',
            'placeholder': 'Vzdelanie, skúsenosti, schopnosti...',
            'ai_prompt': 'Napíš požiadavky na vzdelanie, skúsenosti a zručnosti pre pozíciu {name}'
        },
        {
            'key': 'tools_systems',
            'label': 'Nástroje/Systémy',
            'question': 'Aké nástroje a systémy bude používať?',
            'placeholder': 'Software, aplikácie, zariadenia...',
            'ai_prompt': 'Navrhni nástroje, software a systémy potrebné pre pozíciu {name}'
        },
        {
            'key': 'work_time',
            'label': 'Pracovný čas',
            'question': 'Aký je očakávaný pracovný čas?',
            'placeholder': 'Plný úväzok, čiastočný, flexibilný...',
            'ai_prompt': 'Navrhni typ pracovného času pre pozíciu {name}'
        },
        {
            'key': 'challenges',
            'label': 'Výzvy',
            'question': 'Aké sú hlavné výzvy tejto pozície?',
            'placeholder': 'Čo môže byť náročné alebo problematické...',
            'ai_prompt': 'Popíš hlavné výzvy a problémy pre pozíciu {name}'
        },
        {
            'key': 'success_metrics',
            'label': 'Meranie úspechu',
            'question': 'Ako sa bude merať úspech na tejto pozícii?',
            'placeholder': 'KPI, ciele, očakávané výsledky...',
            'ai_prompt': 'Navrhni KPI a metriky úspechu pre pozíciu {name}'
        }
    ]
    
    # KONTROLA PREDVYPLNENÝCH DÁT
    if st.session_state.current_position_data:
        filled_fields = sum(1 for field in position_fields if st.session_state.current_position_data.get(field['key']))
        total_fields = len(position_fields)
        
        # PROGRESS BAR
        progress = filled_fields / total_fields
        st.progress(progress, text=f"📊 Pokrok: {filled_fields}/{total_fields} polí vyplnených ({progress:.0%})")
        
        st.info(f"📋 **Predvyplnené dáta:** {filled_fields}/{total_fields} polí už vyplnených z bulk importu")
        
        # Možnosť preskočiť na nevyplnené polia
        if filled_fields < total_fields:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("💡 *Môžete začať od prvého nevyplneného poľa alebo prechádzať postupne*")
            with col2:
                if st.button("⏭️ Preskoč na nevyplnené"):
                    # Nájdi prvý nevyplnený krok
                    for i, field in enumerate(position_fields):
                        if not st.session_state.current_position_data.get(field['key']):
                            st.session_state.position_learning_step = i
                            st.rerun()
                            break
        else:
            st.success("🎉 **Všetky polia sú vyplnené!** Môžete pokračovať na finálny prehľad")
            if st.button("🏁 Prejsť na finálny prehľad"):
                st.session_state.position_learning_step = len(position_fields)
                st.rerun()
        
        # Zobrazenie prehľadu predvyplnených dát
        with st.expander("👀 Zobraziť všetky predvyplnené dáta"):
            for field in position_fields:
                value = st.session_state.current_position_data.get(field['key'], '')
                if value:
                    st.markdown(f"✅ **{field['label']}:** {value[:100]}{'...' if len(str(value)) > 100 else ''}")
                else:
                    st.markdown(f"⭕ **{field['label']}:** *Nevyplnené*")
    
    # Polia pre pozíciu
    current_step = st.session_state.get('position_learning_step', 0)
    
    if current_step < len(position_fields):
        field = position_fields[current_step]
        
        # VYLEPŠENÝ HEADER S INDIKÁTOROM STAVU
        is_field_filled = bool(st.session_state.current_position_data.get(field['key']))
        status_icon = "✅" if is_field_filled else "⭕"
        status_text = "už vyplnené" if is_field_filled else "nevyplnené"
        
        st.markdown(f"### 🎯 Krok {current_step + 1}/{len(position_fields)}: {status_icon} {field['label']}")
        
        if is_field_filled:
            st.success(f"💡 **Toto pole je {status_text}** z bulk importu - môžete hodnotu upraviť alebo ponechať")
        else:
            st.info(f"📝 **Toto pole je {status_text}** - zadajte novú hodnotu alebo použite AI pomoc")
        
        # Špeciálne spracovanie pre oddelenie - ukáž existujúce oddelenia
        if field['key'] == 'department':
            existing_departments = load_existing_departments()
            if existing_departments:
                st.info(f"🏢 **Existujúce oddelenia:** {', '.join(existing_departments)}")
                st.markdown(f"**Otázka:** Do akého oddelenia patrí táto pozícia? Môžete vybrať existujúce alebo zadať nové.")
            else:
                st.info(field['question'])
        else:
            st.info(field['question'])
        
        # Hlavné pole pre input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Špeciálne spracovanie pre department - selectbox + možnosť vlastného
            if field['key'] == 'department':
                existing_departments = load_existing_departments()
                current_value = st.session_state.current_position_data.get(field['key'], '')
                
                if existing_departments:
                    # Ak existujú oddelenia, ponúkni výber
                    options = ["-- Vybrať existujúce --"] + existing_departments + ["-- Zadať nové --"]
                    
                    if current_value and current_value in existing_departments:
                        index = existing_departments.index(current_value) + 1
                    elif current_value:
                        index = len(options) - 1  # "Zadať nové"
                    else:
                        index = 0
                    
                    selection = st.selectbox(
                        "🏢 Vyberte oddelenie:",
                        options,
                        index=index,
                        key=f"dept_select_{field['key']}"
                    )
                    
                    if selection == "-- Zadať nové --" or (selection == "-- Vybrať existujúce --" and current_value):
                        user_input = st.text_input(
                            "✍️ Názov nového oddelenia:",
                            value=current_value if selection == "-- Zadať nové --" else "",
                            placeholder=field['placeholder'],
                            key=f"field_{field['key']}"
                        )
                    elif selection != "-- Vybrať existujúce --":
                        user_input = selection
                        st.session_state.current_position_data[field['key']] = selection
                    else:
                        user_input = current_value
                else:
                    # Žiadne existujúce oddelenia - klasický input
                    user_input = st.text_input(
                        "✍️ Vaša odpoveď:",
                        value=current_value,
                        placeholder=field['placeholder'],
                        key=f"field_{field['key']}"
                    )
            elif field['key'] in ['description', 'responsibilities', 'requirements', 'challenges', 'success_metrics']:
                user_input = st.text_area(
                    "✍️ Vaša odpoveď:",
                    value=st.session_state.current_position_data.get(field['key'], ''),
                    placeholder=field['placeholder'],
                    height=100,
                    key=f"field_{field['key']}"
                )
            else:
                user_input = st.text_input(
                    "✍️ Vaša odpoveď:",
                    value=st.session_state.current_position_data.get(field['key'], ''),
                    placeholder=field['placeholder'],
                    key=f"field_{field['key']}"
                )
        
        with col2:
            st.markdown("**🤖 AI Pomoc**")
            if st.button("✨ AI Doplniť", key=f"ai_help_{field['key']}"):
                ai_suggestion = get_ai_suggestion(field, st.session_state.current_position_data)
                if ai_suggestion:
                    st.session_state.current_position_data[field['key']] = ai_suggestion
                    st.rerun()
        
        # AI návrh ak existuje
        if f"ai_suggestion_{field['key']}" in st.session_state:
            st.success(f"🤖 AI návrh: {st.session_state[f'ai_suggestion_{field['key']}']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Použiť AI návrh", key=f"use_ai_{field['key']}"):
                    st.session_state.current_position_data[field['key']] = st.session_state[f'ai_suggestion_{field['key']}']
                    del st.session_state[f'ai_suggestion_{field['key']}']
                    st.rerun()
            with col2:
                if st.button("❌ Zamietnuť", key=f"reject_ai_{field['key']}"):
                    del st.session_state[f'ai_suggestion_{field['key']}']
                    st.rerun()
        
        # Navigačné tlačidlá
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("⬅️ Späť") and current_step > 0:
                st.session_state.current_position_data[field['key']] = user_input
                st.session_state.position_learning_step = current_step - 1
                st.rerun()
        
        with col2:
            if st.button("➡️ Ďalej"):
                st.session_state.current_position_data[field['key']] = user_input
                st.session_state.position_learning_step = current_step + 1
                st.rerun()
        
        with col3:
            if st.button("💾 Uložiť pozíciu") and st.session_state.current_position_data.get('name'):
                st.session_state.current_position_data[field['key']] = user_input
                save_position_to_db(st.session_state.current_position_data)
                st.session_state.position_learning_mode = False
                st.success("✅ Pozícia uložená!")
                st.rerun()
        
        with col4:
            if st.button("❌ Zrušiť"):
                st.session_state.position_learning_mode = False
                st.rerun()
        
        # Aktualizuj dáta
        st.session_state.current_position_data[field['key']] = user_input
        
    else:
        # Všetky polia vyplnené - finálny prehľad
        st.success("🎉 Všetky polia vyplnené!")
        st.markdown("### 📋 Prehľad pozície:")
        
        for field in position_fields:
            value = st.session_state.current_position_data.get(field['key'], '')
            if value:
                st.markdown(f"**{field['label']}:** {value}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Uložiť pozíciu", type="primary"):
                save_position_to_db(st.session_state.current_position_data)
                st.session_state.position_learning_mode = False
                st.success("✅ Pozícia vytvorená!")
                st.rerun()
        
        with col2:
            if st.button("📝 Upraviť"):
                st.session_state.position_learning_step = 0
                st.rerun()

def render_position_bulk_import():
    """Bulk import pozície z ChatGPT konverzácie"""
    st.markdown("### 📋 Bulk Import pozície z ChatGPT konverzácie")
    st.markdown("**💡 Návod:** Skopírujte celú konverzáciu z ChatGPT kde ste diskutovali o pozícii a AI automaticky vyplní všetky polia.")
    
    # Príklad formátu
    with st.expander("📖 Príklad ChatGPT konverzácie pre pozíciu"):
        st.markdown("""
**Príklad správneho formátu:**

```
Používateľ: Potrebujem vytvoriť pozíciu senior programátora pre náš IT tím

ChatGPT: Pozícia senior programátora je kľúčová pre IT tím. Môžem vám pomôcť ju navrhnúť:

**Názov pozície:** Senior Software Developer
**Oddelenie:** IT
**Úroveň:** Senior
**Popis:** Vývoj a údržba softvérových aplikácií, vedenie menších projektov

**Zodpovednosti:**
- Navrhovanie a implementácia softvérových riešení
- Code review pre junior vývojárov
- Vedenie technických diskusií
- Optimalizácia výkonu aplikácií

**Požiadavky:** 
- Bakalárske vzdelanie v IT
- 5+ rokov skúseností s programovaním
- Znalosť Java, Python, SQL

**Nástroje:** IntelliJ IDEA, Git, Docker, Jenkins
**Pracovný čas:** Plný úväzok, možnosť home office
**Výzvy:** Rýchly technologický vývoj, deadlines
**KPI:** Počet dokončených projektov, kvalita kódu, mentoring
```
        """)
    
    # Vstupné pole pre konverzáciu
    conversation_text = st.text_area(
        "📝 Vložte ChatGPT konverzáciu o pozícii:",
        height=400,
        placeholder="Skopírujte sem celú konverzáciu z ChatGPT...",
        key="position_bulk_conversation_input"
    )
    
    # Tlačidlá
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🚀 Spracovať AI", type="primary", disabled=not conversation_text.strip()):
            with st.spinner("🤖 AI parsuje konverzáciu o pozícii..."):
                parsed_data = parse_position_chatgpt_conversation(conversation_text)
                if parsed_data:
                    st.session_state.position_bulk_parsed_data = parsed_data
                    st.rerun()
                else:
                    st.error("❌ AI nedokázalo parsovať konverzáciu. Skúste iný formát.")
    
    with col2:
        if st.button("🔄 Prepnúť na sprievodcu"):
            st.session_state.switch_to_position_step_by_step = True
            st.rerun()
    
    with col3:
        if st.button("❌ Zrušiť"):
            st.session_state.position_learning_mode = False
            st.rerun()
    
    # Zobrazenie parsovaných dát
    if 'position_bulk_parsed_data' in st.session_state:
        parsed_data = st.session_state.position_bulk_parsed_data
        
        st.markdown("---")
        st.success("✅ AI úspešne parsovalo konverzáciu o pozícii!")
        st.markdown("### 📋 Extraktované dáta pozície:")
        st.info("💡 **Môžete upraviť ľubovoľné pole pred uložením**")
        
        # EDITOVATEĽNÁ FORMA PRE VŠETKY POLIA
        with st.form("edit_position_bulk_data_form"):
            st.markdown("#### ✏️ Upravte parsované dáta pozície:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Základné informácie**")
                
                edited_name = st.text_input(
                    "👤 Názov pozície:",
                    value=parsed_data.get('name', ''),
                    key="edit_pos_name"
                )
                
                edited_department = st.text_input(
                    "🏢 Oddelenie:",
                    value=parsed_data.get('department', ''),
                    key="edit_pos_department"
                )
                
                edited_level = st.text_input(
                    "📊 Úroveň:",
                    value=parsed_data.get('level', ''),
                    key="edit_pos_level"
                )
                
                edited_work_time = st.text_input(
                    "⏰ Pracovný čas:",
                    value=parsed_data.get('work_time', ''),
                    key="edit_pos_work_time"
                )
            
            with col2:
                st.markdown("**📝 Popis pozície**")
                
                edited_description = st.text_area(
                    "📖 Popis pozície:",
                    value=parsed_data.get('description', ''),
                    height=120,
                    key="edit_pos_description"
                )
            
            # Dlhé texty na plnú šírku
            st.markdown("**📝 Detailné informácie**")
            
            edited_responsibilities = st.text_area(
                "📋 Zodpovednosti:",
                value=parsed_data.get('responsibilities', ''),
                height=120,
                key="edit_pos_responsibilities"
            )
            
            edited_requirements = st.text_area(
                "✅ Požiadavky:",
                value=parsed_data.get('requirements', ''),
                height=100,
                key="edit_pos_requirements"
            )
            
            edited_tools = st.text_area(
                "🛠️ Nástroje a systémy:",
                value=parsed_data.get('tools_systems', ''),
                height=80,
                key="edit_pos_tools"
            )
            
            edited_challenges = st.text_area(
                "⚠️ Výzvy:",
                value=parsed_data.get('challenges', ''),
                height=80,
                key="edit_pos_challenges"
            )
            
            edited_success_metrics = st.text_area(
                "🎯 Metriky úspechu:",
                value=parsed_data.get('success_metrics', ''),
                height=80,
                key="edit_pos_success_metrics"
            )
            
            # Tlačidlá formulára
            st.markdown("---")
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            
            with col1:
                save_edited = st.form_submit_button("💾 Uložiť upravené", type="primary")
            
            with col2:
                apply_changes = st.form_submit_button("✅ Aplikovať zmeny")
            
            with col3:
                go_to_guide = st.form_submit_button("📝 Pokračovať v sprievodcovi")
            
            with col4:
                discard_all = st.form_submit_button("🗑️ Zahodiť")
        
        # Spracovanie formulára
        if save_edited:
            # Ulož upravené dáta priamo
            final_data = {
                'name': edited_name,
                'description': edited_description,
                'department': edited_department,
                'level': edited_level,
                'responsibilities': edited_responsibilities,
                'requirements': edited_requirements,
                'tools_systems': edited_tools,
                'work_time': edited_work_time,
                'challenges': edited_challenges,
                'success_metrics': edited_success_metrics
            }
            save_position_to_db(final_data)
            del st.session_state.position_bulk_parsed_data
            st.session_state.position_learning_mode = False
            st.success("✅ Pozícia uložená s úpravami!")
            st.rerun()
        
        elif apply_changes:
            # Aplikuj zmeny do parsed_data a zobraziť aktualizované
            st.session_state.position_bulk_parsed_data = {
                'name': edited_name,
                'description': edited_description,
                'department': edited_department,
                'level': edited_level,
                'responsibilities': edited_responsibilities,
                'requirements': edited_requirements,
                'tools_systems': edited_tools,
                'work_time': edited_work_time,
                'challenges': edited_challenges,
                'success_metrics': edited_success_metrics
            }
            st.success("✅ Zmeny aplikované! Skontrolujte výsledok nižšie.")
            st.rerun()
        
        elif go_to_guide:
            # Presun do postupného sprievodcu s upravenými dátami
            final_data = {
                'name': edited_name,
                'description': edited_description,
                'department': edited_department,
                'level': edited_level,
                'responsibilities': edited_responsibilities,
                'requirements': edited_requirements,
                'tools_systems': edited_tools,
                'work_time': edited_work_time,
                'challenges': edited_challenges,
                'success_metrics': edited_success_metrics
            }
            st.session_state.current_position_data = final_data
            st.session_state.position_learning_step = 0
            del st.session_state.position_bulk_parsed_data
            st.session_state.switch_to_position_step_by_step = True
            st.rerun()
        
        elif discard_all:
            del st.session_state.position_bulk_parsed_data
            st.rerun()

def parse_position_chatgpt_conversation(conversation: str) -> dict:
    """Parsuje ChatGPT konverzáciu a extraktuje dáta o pozícii"""
    try:
        ai_engine = RealAIReasoningEngine()
        
        if not ai_engine.ai_available:
            st.warning("⚠️ AI nie je dostupné - zadajte OpenAI API kľúč")
            return {}
        
        system_prompt = """
Si expert na parsovanie konverzácií o pracovných pozíciách. 
Tvoja úloha je extrahovať štruktúrované dáta z ChatGPT konverzácie o pozícii.

VÝSTUP MUSÍ BYŤ VALID JSON s týmito poľami (všetky sú string):
{
    "name": "názov pozície",
    "description": "popis pozície",
    "department": "oddelenie", 
    "level": "úroveň zodpovednosti",
    "responsibilities": "zodpovednosti oddelené \\n",
    "requirements": "požiadavky na pozíciu",
    "tools_systems": "nástroje a systémy",
    "work_time": "pracovný čas",
    "challenges": "výzvy pozície",
    "success_metrics": "KPI a metriky úspechu"
}

Ak niektoré pole nenájdeš, nastav ho na prázdny string "".
Vráť VÝLUČNE JSON bez akýchkoľvek dodatočných textov.
"""
        
        user_prompt = f"""
Parsuj túto ChatGPT konverzáciu a extraktuj dáta o pozícii:

{conversation}

Vráť VALID JSON s extraktovanými dátami o pozícii.
"""
        
        if ai_engine.use_new_client:
            response = ai_engine.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            result = response.choices[0].message.content.strip()
        else:
            import openai
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            result = response.choices[0].message.content.strip()
        
        # Parsuj JSON
        import json
        import re
        
        # Očisti JSON (odstráň markdown bloky ak existujú)
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result, re.DOTALL)
        if json_match:
            result = json_match.group(1)
        
        # Parsuj JSON
        parsed_data = json.loads(result)
        
        # Validácia a čistenie dát
        cleaned_data = {}
        for key, value in parsed_data.items():
            if isinstance(value, str):
                cleaned_data[key] = value.strip()
            else:
                cleaned_data[key] = str(value).strip() if value else ""
        
        return cleaned_data
        
    except Exception as e:
        st.error(f"❌ Chyba parsovania pozície: {e}")
        return {}

def get_ai_suggestion(field: Dict, current_data: Dict) -> str:
    """Získa AI návrh pre pole"""
    try:
        ai_engine = RealAIReasoningEngine()
        
        if not ai_engine.ai_available:
            st.warning("⚠️ AI nie je dostupné - zadajte OpenAI API kľúč")
            return ""
        
        # Vytvor prompt na základe aktuálnych dát
        prompt = field['ai_prompt'].format(**current_data)
        
        # Špeciálne spracovanie pre department - pridaj existujúce oddelenia
        additional_context = ""
        if field['key'] == 'department':
            existing_departments = load_existing_departments()
            if existing_departments:
                additional_context = f"\nExistujúce oddelenia v databáze: {', '.join(existing_departments)}"
        
        system_prompt = f"""
Si HR expert na vytváranie pozícií. 
Pozícia: {current_data.get('name', 'pozícia')}
Oddelenie: {current_data.get('department', 'všeobecné')}{additional_context}

Napíš krátku, praktickú odpoveď v slovenčine.
"""
        
        if ai_engine.use_new_client:
            response = ai_engine.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        else:
            import openai
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
            
    except Exception as e:
        st.error(f"❌ Chyba AI návrhu: {e}")
        return ""

def save_position_to_db(position_data: Dict):
    """Uloží pozíciu do databázy"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Vytvor tabuľku ak neexistuje
            conn.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    department TEXT,
                    level TEXT,
                    responsibilities TEXT,
                    requirements TEXT,
                    tools_systems TEXT,
                    work_time TEXT,
                    challenges TEXT,
                    success_metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                INSERT INTO positions (
                    name, description, department, level, responsibilities,
                    requirements, tools_systems, work_time, challenges, success_metrics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                position_data.get('name', ''),
                position_data.get('description', ''),
                position_data.get('department', ''),
                position_data.get('level', ''),
                position_data.get('responsibilities', ''),
                position_data.get('requirements', ''),
                position_data.get('tools_systems', ''),
                position_data.get('work_time', ''),
                position_data.get('challenges', ''),
                position_data.get('success_metrics', '')
            ))
            conn.commit()
    except Exception as e:
        st.error(f"❌ Chyba ukladania: {e}")

def save_position_from_learning():
    """Uloží pozíciu z AI learning session - backward compatibility funkcia"""
    try:
        if not st.session_state.get('position_learning_history'):
            return
        
        # Extraktovanie dát z AI learning histórie
        history = st.session_state.position_learning_history
        
        position_name = history[0]['response'] if len(history) > 0 else "Nová pozícia"
        position_description = history[1]['response'] if len(history) > 1 else ""
        position_department = history[2]['response'] if len(history) > 2 else ""
        
        # V budúcnosti tu bude ukladanie do databázy
        position_data = {
            'name': position_name,
            'description': position_description,
            'department': position_department,
            'learning_history': history,
            'created_at': datetime.now().isoformat()
        }
        
        # Uloženie do JSON súboru ako demo
        try:
            with open("positions_ai_learned.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(position_data, ensure_ascii=False) + "\n")
        except:
            pass
            
    except Exception as e:
        st.error(f"❌ Chyba ukladania pozície: {e}")

def render_edit_position():
    """Editácia pozície"""
    st.markdown("## ✏️ Editácia pozície")
    
    position_id = st.session_state.get('edit_position_id')
    if not position_id:
        st.error("❌ Žiadna pozícia na editáciu")
        if st.button("🔙 Späť na zoznam"):
            st.session_state.mode = "positions"
            st.rerun()
        return
    
    # Načítaj pozíciu
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
            position = dict(cursor.fetchone())
    except Exception as e:
        st.error(f"❌ Chyba načítavania: {e}")
        return
    
    st.markdown(f"### Editácia: {position['name']}")
    
    # Editačný formulár
    with st.form("edit_position_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Názov pozície:", value=position.get('name', ''))
            new_department = st.text_input("Oddelenie:", value=position.get('department', ''))
            new_level = st.text_input("Úroveň:", value=position.get('level', ''))
            new_work_time = st.text_input("Pracovný čas:", value=position.get('work_time', ''))
        
        with col2:
            new_description = st.text_area("Popis:", value=position.get('description', ''), height=100)
            new_tools = st.text_area("Nástroje/Systémy:", value=position.get('tools_systems', ''), height=100)
        
        new_responsibilities = st.text_area("Zodpovednosti:", value=position.get('responsibilities', ''))
        new_requirements = st.text_area("Požiadavky:", value=position.get('requirements', ''))
        new_challenges = st.text_area("Výzvy:", value=position.get('challenges', ''))
        new_success = st.text_area("Meranie úspechu:", value=position.get('success_metrics', ''))
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            submit = st.form_submit_button("💾 Uložiť", type="primary")
        
        with col2:
            if st.form_submit_button("❌ Zrušiť"):
                st.session_state.mode = "positions"
                st.rerun()
        
        with col3:
            if st.form_submit_button("🗑️ Zmazať"):
                st.session_state.confirm_delete_position = True
    
    if submit:
        try:
            with sqlite3.connect("adsun_processes.db") as conn:
                conn.execute("""
                    UPDATE positions SET
                        name = ?, description = ?, department = ?, level = ?,
                        responsibilities = ?, requirements = ?, tools_systems = ?,
                        work_time = ?, challenges = ?, success_metrics = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    new_name, new_description, new_department, new_level,
                    new_responsibilities, new_requirements, new_tools,
                    new_work_time, new_challenges, new_success, position_id
                ))
                conn.commit()
            
            st.success("✅ Pozícia upravená!")
            st.session_state.mode = "positions"
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Chyba ukladania: {e}")
    
    # Potvrdenie mazania
    if st.session_state.get('confirm_delete_position'):
        st.warning("⚠️ Naozaj chcete zmazať túto pozíciu?")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Áno, zmazať", type="primary"):
                try:
                    with sqlite3.connect("adsun_processes.db") as conn:
                        conn.execute("DELETE FROM positions WHERE id = ?", (position_id,))
                        conn.commit()
                    
                    st.success("✅ Pozícia zmazaná!")
                    st.session_state.mode = "positions"
                    del st.session_state.confirm_delete_position
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Chyba mazania: {e}")
        
        with col2:
            if st.button("❌ Nie, zrušiť"):
                del st.session_state.confirm_delete_position
                st.rerun()
    
    # Späť button
    st.markdown("---")
    if st.button("🔙 Späť na pozície"):
        st.session_state.mode = "positions"
        del st.session_state.edit_position_id
        st.rerun() 