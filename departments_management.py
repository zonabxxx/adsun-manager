#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Departments Management
Správa oddelení s AI-driven vytváraním
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from ui_components import render_section_header, render_action_buttons, render_modern_dataframe

def render_departments():
    """Render správy oddelení"""
    
    # Načítanie oddelení z procesov
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row  # Fix: pridané pre dict() konverziu
            cursor = conn.execute("""
                SELECT category, COUNT(*) as process_count,
                       AVG(automation_readiness) as avg_automation,
                       GROUP_CONCAT(DISTINCT owner) as employees
                FROM processes 
                WHERE is_active = 1 AND category IS NOT NULL
                GROUP BY category
                ORDER BY process_count DESC
            """)
            departments = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"❌ Chyba načítavania oddelení: {e}")
        departments = []
    
    # Moderný header so štatistikami
    total_processes = sum(dept.get('process_count', 0) for dept in departments)
    avg_automation = sum(dept.get('avg_automation', 0) or 0 for dept in departments) / len(departments) if departments else 0
    
    stats = {
        "departments": {"icon": "🏢", "text": f"{len(departments)} oddelení"},
        "processes": {"icon": "📋", "text": f"{total_processes} procesov"},
        "automation": {"icon": "🤖", "text": f"{avg_automation:.1f}/5 automatizácia"}
    }
    
    render_section_header(
        title="Oddelenia",
        subtitle="Správa firemných oddelení a ich procesov",
        icon="🏢",
        stats=stats
    )
    
    # DETAILY MIMO EXPANDERA - AK SÚ ZOBRAZENÉ
    if 'show_department_details' in st.session_state:
        category = st.session_state.show_department_details
        st.markdown("---")
        show_department_details(category)
        
        if st.button("❌ Zavrieť detaily", type="secondary"):
            del st.session_state.show_department_details
            st.rerun()
        
        st.markdown("---")
    
    # Pridanie nového oddelenia
    with st.expander("➕ Pridať nové oddelenie"):
        if st.session_state.get('department_learning_mode', False):
            render_department_learning()
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**🤖 AI vás povedie otázkami pre vytvorenie oddelenia**")
                st.info("AI položí inteligentné otázky o novom oddelení - jeho funkcii, procesoch, ľuďoch a zodpovednostiach.")
            
            with col2:
                if st.button("🚀 Začať s AI", type="primary"):
                    st.session_state.department_learning_mode = True
                    st.session_state.department_learning_step = 0
                    st.session_state.department_learning_history = []
                    st.rerun()
    
    # Zobrazenie existujúcich oddelení
    if not departments:
        st.info("🏢 Žiadne oddelenia ešte nie sú definované")
        return
    
    # POTVRDENIE MAZANIA ODDELENIA
    if 'confirm_delete_department' in st.session_state:
        department_name = st.session_state.confirm_delete_department
        process_count = st.session_state.department_process_count
        
        st.warning(f"⚠️ **Pozor!** Chystáte sa zmazať oddelenie **{department_name}** ktoré obsahuje **{process_count} procesov**")
        
        # Načítanie iných oddelení pre transfer
        other_departments = [d['category'] for d in departments if d['category'] != department_name]
        
        if other_departments:
            st.markdown("**🎯 Vyberte možnosť:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Zmazať oddelenie + všetky procesy", type="secondary"):
                    delete_department_and_processes(department_name)
                    del st.session_state.confirm_delete_department
                    del st.session_state.department_process_count
                    st.success(f"✅ Oddelenie {department_name} a všetky jeho procesy boli zmazané!")
                    st.rerun()
            
            with col2:
                st.markdown("**📋 Alebo presunúť procesy do:**")
                target_department = st.selectbox(
                    "Cieľové oddelenie:",
                    other_departments,
                    key="target_dept_transfer"
                )
                
                if st.button(f"📤 Presunúť do {target_department}", type="primary"):
                    transfer_department_processes(department_name, target_department)
                    del st.session_state.confirm_delete_department
                    del st.session_state.department_process_count
                    st.success(f"✅ Procesy z {department_name} boli presunuté do {target_department}!")
                    st.rerun()
        else:
            st.markdown("**⚠️ Toto je jediné oddelenie - môžete len zmazať všetky procesy:**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Zmazať oddelenie + všetky procesy", type="secondary"):
                    delete_department_and_processes(department_name)
                    del st.session_state.confirm_delete_department
                    del st.session_state.department_process_count
                    st.success(f"✅ Oddelenie {department_name} a všetky jeho procesy boli zmazané!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Zrušiť", type="primary"):
                    del st.session_state.confirm_delete_department
                    del st.session_state.department_process_count
                    st.rerun()
        
        # Možnosť zrušenia vždy k dispozícii
        if st.button("❌ Zrušiť mazanie"):
            del st.session_state.confirm_delete_department
            del st.session_state.department_process_count
            st.rerun()
        
        st.markdown("---")
    
    # Moderné zobrazenie oddelení
    st.markdown("### 🏢 Prehľad oddelení")
    
    # Použijeme jednotný štýl pre všetky oddelenia
    for dept in departments:
        with st.expander(f"🏢 {dept['category']}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # Základné info v jednotnom štýle
                st.write(f"**📋 Procesy:** {dept['process_count']}")
                st.write(f"**🤖 Automatizácia:** {dept['avg_automation']:.1f}/5")
                
                if dept['employees']:
                    employees = dept['employees'].split(',')
                    st.write(f"**👥 Zamestnanci:** {', '.join(employees[:3])}{'...' if len(employees) > 3 else ''}")
                    st.write(f"**👥 Počet:** {len(employees)} ľudí")
            
            with col2:
                if st.button("📋 Procesy", key=f"processes_{dept['category']}", use_container_width=True):
                    show_department_processes(dept['category'])
                
                # TLAČIDLO DETAILY TERAZ ZOBRAZUJE MIMO EXPANDERA
                if st.button("📊 Detaily", key=f"details_{dept['category']}", use_container_width=True):
                    st.session_state.show_department_details = dept['category']
                    st.rerun()
            
            with col3:
                if st.button("✏️ Upraviť", key=f"edit_dept_{dept['category']}", use_container_width=True):
                    st.session_state.edit_department = dept['category']
                    st.session_state.mode = "edit_department"
                    st.rerun()
                
                if st.button("🗑️ Zmazať", key=f"delete_dept_{dept['category']}", use_container_width=True):
                    st.session_state.confirm_delete_department = dept['category']
                    st.session_state.department_process_count = dept['process_count']
                    st.rerun()

def show_department_processes(category: str):
    """Zobrazí procesy oddelenia"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT name, owner, priority, automation_readiness
                FROM processes 
                WHERE category = ? AND is_active = 1
                ORDER BY priority DESC, name
            """, (category,))
            processes = [dict(row) for row in cursor.fetchall()]
        
        st.markdown(f"### 📋 Procesy oddelenia: {category}")
        
        if processes:
            for proc in processes:
                st.write(f"• **{proc['name']}** - {proc['owner']} ({proc['priority']}) - Automatizácia: {proc['automation_readiness']}/5")
        else:
            st.info("Žiadne procesy")
            
    except Exception as e:
        st.error(f"❌ Chyba: {e}")

def show_department_details(category: str):
    """Zobrazí detailné informácie o oddelení"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            
            # Základné štatistiky oddelenia
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_processes,
                    AVG(automation_readiness) as avg_automation,
                    AVG(duration_minutes) as avg_duration,
                    COUNT(DISTINCT owner) as unique_owners,
                    GROUP_CONCAT(DISTINCT owner) as all_owners,
                    MAX(priority) as highest_priority,
                    COUNT(CASE WHEN automation_readiness >= 4 THEN 1 END) as highly_automated
                FROM processes 
                WHERE category = ? AND is_active = 1
            """, (category,))
            stats = dict(cursor.fetchone())
            
            st.markdown(f"### 📊 Detaily oddelenia: {category}")
            
            # ÚPLNE BEZ STĹPCOV - všetko pod sebou na plnú šírku
            st.markdown("#### 📈 Kľúčové metriky")
            
            # Všetko pod sebou namiesto stĺpcov
            st.markdown(f"**📋 Celkom procesov v oddelení:** {stats['total_processes']}")
            
            avg_auto = stats['avg_automation'] or 0
            st.markdown(f"**🤖 Priemerná úroveň automatizácie:** {avg_auto:.1f}/5")
            
            avg_dur = stats['avg_duration'] or 0
            st.markdown(f"**⏱️ Priemerné trvanie procesov:** {avg_dur:.0f} minút")
            
            st.markdown(f"**👥 Počet zamestnancov:** {stats['unique_owners']} ľudí")
            
            # Analýza na plnú šírku
            st.markdown("---")
            st.markdown("#### 🎯 Analýza oddelenia")
            
            # Tím - všetko pod sebou
            st.markdown("**👥 Tím oddelenia:**")
            if stats['all_owners']:
                owners = stats['all_owners'].split(',')
                for owner in owners:
                    st.markdown(f"• {owner.strip()}")
            else:
                st.markdown("• Žiadni priradení vlastníci")
            
            st.markdown("")  # Medzera
            
            # Automatizácia - všetko pod sebou
            st.markdown("**🚀 Úroveň automatizácie:**")
            highly_auto = stats['highly_automated'] or 0
            total = stats['total_processes'] or 1
            auto_percentage = (highly_auto / total) * 100
            st.markdown(f"• Vysoko automatizovaných procesov: {highly_auto}/{total}")
            st.markdown(f"• Percentuálne zastúpenie: {auto_percentage:.1f}%")
            st.markdown(f"• Najvyššia priorita: {stats['highest_priority'] or 'Neurčená'}")
            
            # Procesy oddelenia v širšej tabuľke
            cursor = conn.execute("""
                SELECT name, owner, priority, automation_readiness, duration_minutes
                FROM processes 
                WHERE category = ? AND is_active = 1
                ORDER BY priority DESC, automation_readiness DESC
            """, (category,))
            processes = [dict(row) for row in cursor.fetchall()]
            
            if processes:
                st.markdown("---")
                st.markdown("#### 📋 Kompletný zoznam procesov")
                
                # Širšia tabuľka procesov
                import pandas as pd
                df = pd.DataFrame(processes)
                df.columns = ['Názov procesu', 'Vlastník', 'Priorita', 'Automatizácia', 'Trvanie (min)']
                
                # Konvertuj na stringy pre PyArrow kompatibilitu
                for col in df.columns:
                    df[col] = df[col].astype(str)
                
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("📝 Žiadne procesy v tomto oddelení")
            
    except Exception as e:
        st.error(f"❌ Chyba načítavania detailov: {e}")

def render_department_learning():
    """AI-driven učenie nového oddelenia s inteligentným dopĺňaním"""
    st.markdown("### 🤖 AI Asistent pre nové oddelenie")
    st.markdown("*AI vám pomôže vyplniť všetky polia o oddelení*")
    
    # KONTROLA PREPNUTIA NA STEP-BY-STEP
    if st.session_state.get('switch_to_department_step_by_step', False):
        # Vyčistíme flag a resetujeme na step-by-step
        del st.session_state.switch_to_department_step_by_step
        # Nastavíme default hodnotu pre radio (bude sa zobrazovať step-by-step)
        default_method = "🔄 Postupný sprievodca (krok za krokom)"
    else:
        # Ak nie je flag nastavený, použijeme existujúcu hodnotu alebo default
        default_method = st.session_state.get('department_creation_method', "🔄 Postupný sprievodca (krok za krokom)")
    
    # VÝBER SPÔSOBU VYTVORENIA ODDELENIA
    st.markdown("#### 🎯 Vyberte spôsob vytvorenia oddelenia:")
    
    creation_method = st.radio(
        "Ako chcete vytvoriť oddelenie?",
        [
            "🔄 Postupný sprievodca (krok za krokom)",
            "📋 Bulk import z ChatGPT konverzácie"
        ],
        index=0 if default_method == "🔄 Postupný sprievodca (krok za krokom)" else 1,
        key="department_creation_method"
    )
    
    if creation_method == "📋 Bulk import z ChatGPT konverzácie":
        render_department_bulk_import()
        return
    
    # PÔVODNÝ POSTUPNÝ SPRIEVODCA
    st.markdown("---")
    st.markdown("**🔄 Postupný sprievodca - krok za krokom**")
    
    # INICIALIZÁCIA DÁT AK NEEXISTUJÚ - MUSI BYŤ PRED PRVÝM PRÍSTUPOM!
    if 'current_department_data' not in st.session_state:
        st.session_state.current_department_data = {}
    
    # DEFINÍCIA POLÍ - MUSI BYŤ PRED PRVÝM POUŽITÍM!
    department_fields = [
        {
            'key': 'name',
            'label': 'Názov oddelenia',
            'question': 'Aký je názov nového oddelenia?',
            'placeholder': 'napr. Marketing, Zákaznícky servis, IT Support',
            'ai_prompt': 'Navrhni 3 alternatívne názvy pre oddelenie typu {value}'
        },
        {
            'key': 'function',
            'label': 'Hlavná funkcia',
            'question': 'Aká je hlavná funkcia tohto oddelenia?',
            'placeholder': 'Popíšte čo toto oddelenie robí pre firmu...',
            'ai_prompt': 'Napíš hlavnú funkciu a úlohu oddelenia {name} vo firme'
        },
        {
            'key': 'manager',
            'label': 'Vedúci oddelenia',
            'question': 'Kto bude vedúci tohto oddelenia?',
            'placeholder': 'Meno a pozícia vedúceho...',
            'ai_prompt': 'Navrhni typ vedúcej pozície pre oddelenie {name}'
        },
        {
            'key': 'processes',
            'label': 'Hlavné procesy',
            'question': 'Aké procesy bude toto oddelenie vykonávať?',
            'placeholder': 'Vymenovajte hlavné činnosti a procesy...',
            'ai_prompt': 'Napíš hlavné procesy a činnosti pre oddelenie {name}'
        },
        {
            'key': 'staff_count',
            'label': 'Počet zamestnancov',
            'question': 'Koľko ľudí bude v tomto oddelení pracovať?',
            'placeholder': 'Aktuálny alebo plánovaný počet...',
            'ai_prompt': 'Navrhni optimálny počet zamestnancov pre oddelenie {name}'
        },
        {
            'key': 'competencies',
            'label': 'Kľúčové kompetencie',
            'question': 'Aké sú kľúčové kompetencie tohto oddelenia?',
            'placeholder': 'Čo musia ľudia vedieť/umieť...',
            'ai_prompt': 'Napíš kľúčové schopnosti a kompetencie pre oddelenie {name}'
        },
        {
            'key': 'collaboration',
            'label': 'Spolupráca s oddeleniami',
            'question': 'S akými oddeleniami bude najčastejšie spolupracovať?',
            'placeholder': 'Iné oddelenia, s ktorými bude spolupracovať...',
            'ai_prompt': 'Navrhni oddelenia ktoré najviac spolupracujú s oddelením {name}'
        },
        {
            'key': 'tools',
            'label': 'Nástroje a systémy',
            'question': 'Aké nástroje/systémy bude toto oddelenie používať?',
            'placeholder': 'Software, aplikácie, zariadenia...',
            'ai_prompt': 'Napíš nástroje a systémy potrebné pre oddelenie {name}'
        },
        {
            'key': 'challenges',
            'label': 'Hlavné výzvy',
            'question': 'Aké sú hlavné výzvy tohto oddelenia?',
            'placeholder': 'Čo môže byť problematické...',
            'ai_prompt': 'Popíš hlavné výzvy a problémy pre oddelenie {name}'
        },
        {
            'key': 'success_metrics',
            'label': 'Meranie úspechu',
            'question': 'Ako sa bude merať úspech tohto oddelenia?',
            'placeholder': 'KPI, metriky, ciele...',
            'ai_prompt': 'Navrhni KPI a metriky úspechu pre oddelenie {name}'
        }
    ]
    
    # KONTROLA PREDVYPLNENÝCH DÁT
    if st.session_state.current_department_data:
        filled_fields = sum(1 for field in department_fields if st.session_state.current_department_data.get(field['key']))
        total_fields = len(department_fields)
        
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
                    for i, field in enumerate(department_fields):
                        if not st.session_state.current_department_data.get(field['key']):
                            st.session_state.department_learning_step = i
                            st.rerun()
                            break
        else:
            st.success("🎉 **Všetky polia sú vyplnené!** Môžete pokračovať na finálny prehľad")
            if st.button("🏁 Prejsť na finálny prehľad"):
                st.session_state.department_learning_step = len(department_fields)
                st.rerun()
        
        # Zobrazenie prehľadu predvyplnených dát
        with st.expander("👀 Zobraziť všetky predvyplnené dáta"):
            for field in department_fields:
                value = st.session_state.current_department_data.get(field['key'], '')
                if value:
                    st.markdown(f"✅ **{field['label']}:** {value[:100]}{'...' if len(str(value)) > 100 else ''}")
                else:
                    st.markdown(f"⭕ **{field['label']}:** *Nevyplnené*")
    
    # Polia pre oddelenie s AI promptmi
    current_step = st.session_state.get('department_learning_step', 0)
    
    if current_step < len(department_fields):
        field = department_fields[current_step]
        
        # VYLEPŠENÝ HEADER S INDIKÁTOROM STAVU
        is_field_filled = bool(st.session_state.current_department_data.get(field['key']))
        status_icon = "✅" if is_field_filled else "⭕"
        status_text = "už vyplnené" if is_field_filled else "nevyplnené"
        
        st.markdown(f"### 🎯 Krok {current_step + 1}/{len(department_fields)}: {status_icon} {field['label']}")
        
        if is_field_filled:
            st.success(f"💡 **Toto pole je {status_text}** z bulk importu - môžete hodnotu upraviť alebo ponechať")
        else:
            st.info(f"📝 **Toto pole je {status_text}** - zadajte novú hodnotu alebo použite AI pomoc")
        
        st.info(field['question'])
        
        # Hlavné pole pre input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if field['key'] in ['function', 'processes', 'competencies', 'challenges', 'success_metrics']:
                user_input = st.text_area(
                    "✍️ Vaša odpoveď:",
                    value=st.session_state.current_department_data.get(field['key'], ''),
                    placeholder=field['placeholder'],
                    height=100,
                    key=f"field_{field['key']}"
                )
            else:
                user_input = st.text_input(
                    "✍️ Vaša odpoveď:",
                    value=st.session_state.current_department_data.get(field['key'], ''),
                    placeholder=field['placeholder'],
                    key=f"field_{field['key']}"
                )
        
        with col2:
            st.markdown("**🤖 AI Pomoc**")
            if st.button("✨ AI Doplniť", key=f"ai_help_{field['key']}"):
                ai_suggestion = get_department_ai_suggestion(field, st.session_state.current_department_data)
                if ai_suggestion:
                    st.session_state[f"ai_suggestion_{field['key']}"] = ai_suggestion
                    st.rerun()
        
        # AI návrh ak existuje
        if f"ai_suggestion_{field['key']}" in st.session_state:
            st.success(f"🤖 AI návrh: {st.session_state[f'ai_suggestion_{field['key']}']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Použiť AI návrh", key=f"use_ai_{field['key']}"):
                    st.session_state.current_department_data[field['key']] = st.session_state[f'ai_suggestion_{field['key']}']
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
                st.session_state.current_department_data[field['key']] = user_input
                st.session_state.department_learning_step = current_step - 1
                st.rerun()
        
        with col2:
            if st.button("➡️ Ďalej"):
                st.session_state.current_department_data[field['key']] = user_input
                st.session_state.department_learning_step = current_step + 1
                st.rerun()
        
        with col3:
            if st.button("💾 Uložiť oddelenie") and st.session_state.current_department_data.get('name'):
                st.session_state.current_department_data[field['key']] = user_input
                save_department_to_db(st.session_state.current_department_data)
                st.session_state.department_learning_mode = False
                st.success("✅ Oddelenie uložené!")
                st.rerun()
        
        with col4:
            if st.button("❌ Zrušiť"):
                st.session_state.department_learning_mode = False
                st.rerun()
        
        # Aktualizuj dáta
        st.session_state.current_department_data[field['key']] = user_input
        
    else:
        # Všetky polia vyplnené - finálny prehľad
        st.success("🎉 Všetky polia vyplnené!")
        st.markdown("### 📋 Prehľad oddelenia:")
        
        for field in department_fields:
            value = st.session_state.current_department_data.get(field['key'], '')
            if value:
                st.markdown(f"**{field['label']}:** {value}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Uložiť oddelenie", type="primary"):
                save_department_to_db(st.session_state.current_department_data)
                st.session_state.department_learning_mode = False
                st.success("✅ Oddelenie vytvorené!")
                st.rerun()
        
        with col2:
            if st.button("📝 Upraviť"):
                st.session_state.department_learning_step = 0
                st.rerun()

def render_department_bulk_import():
    """Bulk import oddelenia z ChatGPT konverzácie"""
    st.markdown("### 📋 Bulk Import oddelenia z ChatGPT konverzácie")
    st.markdown("**💡 Návod:** Skopírujte celú konverzáciu z ChatGPT kde ste diskutovali o oddelení a AI automaticky vyplní všetky polia.")
    
    # Príklad formátu
    with st.expander("📖 Príklad ChatGPT konverzácie pre oddelenie"):
        st.markdown("""
**Príklad správneho formátu:**

```
Používateľ: Chcem vytvoriť nové marketing oddelenie pre našu firmu

ChatGPT: Marketing oddelenie je kľúčové pre rast firmy. Môžem vám pomôcť ho navrhnúť:

**Názov oddelenia:** Marketing a komunikácia
**Hlavná funkcia:** Budovanie značky, získavanie zákazníkov a komunikácia s verejnosťou
**Vedúci:** Marketing Manager alebo Head of Marketing

**Hlavné procesy:**
- Tvorba marketingových kampaní
- Správa sociálnych sietí
- PR a komunikácia s médiami
- Analýza trhu a konkurencie
- Event management

**Počet zamestnancov:** 4-6 ľudí
**Kľúčové kompetencie:** Kreativita, analytické myslenie, komunikačné schopnosti
**Spolupráca:** Obchod, IT, Vedenie
**Nástroje:** Google Analytics, Facebook Ads, Canva, CRM systém
**Výzvy:** Rýchle zmeny v digitálnom marketingu
**KPI:** ROI kampaní, brand awareness, lead generation
```
        """)
    
    # Vstupné pole pre konverzáciu
    conversation_text = st.text_area(
        "📝 Vložte ChatGPT konverzáciu o oddelení:",
        height=400,
        placeholder="Skopírujte sem celú konverzáciu z ChatGPT...",
        key="department_bulk_conversation_input"
    )
    
    # Tlačidlá
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🚀 Spracovať AI", type="primary", disabled=not conversation_text.strip()):
            with st.spinner("🤖 AI parsuje konverzáciu o oddelení..."):
                parsed_data = parse_department_chatgpt_conversation(conversation_text)
                if parsed_data:
                    st.session_state.department_bulk_parsed_data = parsed_data
                    st.rerun()
                else:
                    st.error("❌ AI nedokázalo parsovať konverzáciu. Skúste iný formát.")
    
    with col2:
        if st.button("🔄 Prepnúť na sprievodcu"):
            # Nastavíme flag na prepnutie na step-by-step  
            st.session_state.switch_to_department_step_by_step = True
            st.rerun()
    
    with col3:
        if st.button("❌ Zrušiť"):
            st.session_state.department_learning_mode = False
            st.rerun()
    
    # Zobrazenie parsovaných dát
    if 'department_bulk_parsed_data' in st.session_state:
        parsed_data = st.session_state.department_bulk_parsed_data
        
        st.markdown("---")
        st.success("✅ AI úspešne parsovalo konverzáciu o oddelení!")
        st.markdown("### 📋 Extraktované dáta oddelenia:")
        st.info("💡 **Môžete upraviť ľubovoľné pole pred uložením**")
        
        # EDITOVATEĽNÁ FORMA PRE VŠETKY POLIA
        with st.form("edit_department_bulk_data_form"):
            st.markdown("#### ✏️ Upravte parsované dáta oddelenia:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Základné informácie**")
                
                edited_name = st.text_input(
                    "🏢 Názov oddelenia:",
                    value=parsed_data.get('name', ''),
                    key="edit_dept_name"
                )
                
                edited_function = st.text_input(
                    "⚙️ Hlavná funkcia:",
                    value=parsed_data.get('function', ''),
                    key="edit_dept_function"
                )
                
                edited_manager = st.text_input(
                    "👤 Vedúci:",
                    value=parsed_data.get('manager', ''),
                    key="edit_dept_manager"
                )
                
                edited_size = st.text_input(
                    "👥 Veľkosť tímu:",
                    value=parsed_data.get('size', ''),
                    key="edit_dept_size"
                )
            
            with col2:
                st.markdown("**📝 Popis oddelenia**")
                
                edited_description = st.text_area(
                    "📖 Popis oddelenia:",
                    value=parsed_data.get('description', ''),
                    height=120,
                    key="edit_dept_description"
                )
            
            # Dlhé texty na plnú šírku
            st.markdown("**📝 Detailné informácie**")
            
            edited_responsibilities = st.text_area(
                "📋 Zodpovednosti:",
                value=parsed_data.get('responsibilities', ''),
                height=120,
                key="edit_dept_responsibilities"
            )
            
            edited_processes = st.text_area(
                "⚙️ Hlavné procesy:",
                value=parsed_data.get('processes', ''),
                height=100,
                key="edit_dept_processes"
            )
            
            edited_tools = st.text_area(
                "🛠️ Nástroje a systémy:",
                value=parsed_data.get('tools_systems', ''),
                height=80,
                key="edit_dept_tools"
            )
            
            edited_challenges = st.text_area(
                "⚠️ Výzvy:",
                value=parsed_data.get('challenges', ''),
                height=80,
                key="edit_dept_challenges"
            )
            
            edited_goals = st.text_area(
                "🎯 Ciele a KPI:",
                value=parsed_data.get('goals', ''),
                height=80,
                key="edit_dept_goals"
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
                'function': edited_function,
                'manager': edited_manager,
                'size': edited_size,
                'responsibilities': edited_responsibilities,
                'processes': edited_processes,
                'tools_systems': edited_tools,
                'challenges': edited_challenges,
                'goals': edited_goals
            }
            save_department_to_db(final_data)
            del st.session_state.department_bulk_parsed_data
            st.session_state.department_learning_mode = False
            st.success("✅ Oddelenie uložené s úpravami!")
            st.rerun()
        
        elif apply_changes:
            # Aplikuj zmeny do parsed_data a zobraziť aktualizované
            st.session_state.department_bulk_parsed_data = {
                'name': edited_name,
                'description': edited_description,
                'function': edited_function,
                'manager': edited_manager,
                'size': edited_size,
                'responsibilities': edited_responsibilities,
                'processes': edited_processes,
                'tools_systems': edited_tools,
                'challenges': edited_challenges,
                'goals': edited_goals
            }
            st.success("✅ Zmeny aplikované! Skontrolujte výsledok nižšie.")
            st.rerun()
        
        elif go_to_guide:
            # Presun do postupného sprievodcu s upravenými dátami
            final_data = {
                'name': edited_name,
                'description': edited_description,
                'function': edited_function,
                'manager': edited_manager,
                'size': edited_size,
                'responsibilities': edited_responsibilities,
                'processes': edited_processes,
                'tools_systems': edited_tools,
                'challenges': edited_challenges,
                'goals': edited_goals
            }
            st.session_state.current_department_data = final_data
            st.session_state.department_learning_step = 0
            del st.session_state.department_bulk_parsed_data
            st.session_state.switch_to_department_step_by_step = True
            st.rerun()
        
        elif discard_all:
            del st.session_state.department_bulk_parsed_data
            st.rerun()

def get_department_ai_suggestion(field: Dict, current_data: Dict) -> str:
    """Získa AI návrh pre pole oddelenia"""
    try:
        from ai_components import RealAIReasoningEngine
        ai_engine = RealAIReasoningEngine()
        
        if not ai_engine.ai_available:
            st.warning("⚠️ AI nie je dostupné - zadajte OpenAI API kľúč")
            return ""
        
        # Vytvor prompt na základe aktuálnych dát
        prompt = field['ai_prompt'].format(**current_data)
        
        system_prompt = f"""
Si expert na organizačnú štruktúru firiem a tvorbu oddelení.
Oddelenie: {current_data.get('name', 'oddelenie')}
Funkcia: {current_data.get('function', 'všeobecná')}

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

def save_department_to_db(department_data: Dict):
    """Uloží oddelenie do databázy s novým formátom"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Vytvor tabuľku ak neexistuje
            conn.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    function TEXT,
                    manager TEXT,
                    processes TEXT,
                    staff_count TEXT,
                    competencies TEXT,
                    collaboration TEXT,
                    tools TEXT,
                    challenges TEXT,
                    success_metrics TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                INSERT INTO departments (
                    name, function, manager, processes, staff_count,
                    competencies, collaboration, tools, challenges, success_metrics
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                department_data.get('name', ''),
                department_data.get('function', ''),
                department_data.get('manager', ''),
                department_data.get('processes', ''),
                department_data.get('staff_count', ''),
                department_data.get('competencies', ''),
                department_data.get('collaboration', ''),
                department_data.get('tools', ''),
                department_data.get('challenges', ''),
                department_data.get('success_metrics', '')
            ))
            conn.commit()
    except Exception as e:
        st.error(f"❌ Chyba ukladania: {e}")

def save_department_from_learning():
    """Uloží oddelenie z AI learning session"""
    try:
        if not st.session_state.get('department_learning_history'):
            return
        
        # Extraktovanie dát z odpovedí
        history = st.session_state.department_learning_history
        
        dept_name = history[0]['response'] if len(history) > 0 else "Nové oddelenie"
        dept_function = history[1]['response'] if len(history) > 1 else ""
        dept_head = history[2]['response'] if len(history) > 2 else ""
        
        # V budúcnosti tu bude ukladanie do databázy
        # Zatiaľ len log
        department_data = {
            'name': dept_name,
            'function': dept_function,
            'head': dept_head,
            'learning_history': history,
            'created_at': datetime.now().isoformat()
        }
        
        # Uloženie do JSON súboru ako demo
        try:
            with open("departments_ai_learned.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(department_data, ensure_ascii=False) + "\n")
        except:
            pass
            
    except Exception as e:
        st.error(f"❌ Chyba ukladania: {e}")

def render_edit_department():
    """Editácia oddelenia"""
    st.markdown("## ✏️ Editácia oddelenia") 
    st.markdown("*Upravte detaily oddelenia*")
    
    department_name = st.session_state.get('edit_department')
    if not department_name:
        st.error("❌ Žiadne oddelenie na editáciu")
        if st.button("🔙 Späť na zoznam"):
            st.session_state.mode = "departments"
            st.rerun()
        return
    
    st.info("🔧 Editácia oddelení bude dostupná po rozšírení databázy o departments tabuľku")
    
    # Zatiaľ len basic info
    st.markdown(f"### Editácia oddelenia: {department_name}")
    
    # Načítanie procesov oddelenia
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, name, owner, priority, automation_readiness
                FROM processes 
                WHERE category = ? AND is_active = 1
                ORDER BY name
            """, (department_name,))
            processes = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"❌ Chyba načítavania: {e}")
        processes = []
    
    st.markdown("### 📋 Procesy oddelenia:")
    if processes:
        for proc in processes:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{proc['name']}** - {proc['owner']}")
            
            with col2:
                st.write(f"Priorita: {proc['priority']}")
            
            with col3:
                if st.button("✏️", key=f"edit_proc_{proc['id']}"):
                    st.session_state.edit_process_id = proc['id']
                    st.session_state.mode = "edit_process"
                    st.rerun()
    else:
        st.info("Žiadne procesy v tomto oddelení")
    
    # Späť button
    st.markdown("---")
    if st.button("🔙 Späť na oddelenia"):
        st.session_state.mode = "departments"
        if 'edit_department' in st.session_state:
            del st.session_state.edit_department
        st.rerun()

def delete_department_and_processes(department_name: str):
    """Zmaže oddelenie a všetky jeho procesy (soft delete)"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Soft delete všetkých procesov v oddelení
            cursor = conn.execute(
                "UPDATE processes SET is_active = 0 WHERE category = ? AND is_active = 1", 
                (department_name,)
            )
            deleted_count = cursor.rowcount
            conn.commit()
            
            # Debug info
            print(f"🗑️ Deleted {deleted_count} processes from department: {department_name}")
            
    except Exception as e:
        st.error(f"❌ Chyba mazania oddelenia: {e}")
        raise e

def transfer_department_processes(source_department: str, target_department: str):
    """Presunie všetky procesy z jedného oddelenia do druhého"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Presun všetkých aktívnych procesov
            cursor = conn.execute(
                "UPDATE processes SET category = ? WHERE category = ? AND is_active = 1",
                (target_department, source_department)
            )
            transferred_count = cursor.rowcount
            conn.commit()
            
            # Debug info  
            print(f"📤 Transferred {transferred_count} processes from {source_department} to {target_department}")
            
    except Exception as e:
        st.error(f"❌ Chyba presunutia procesov: {e}")
        raise e

def parse_department_chatgpt_conversation(conversation: str) -> dict:
    """Parsuje ChatGPT konverzáciu a extraktuje dáta o oddelení"""
    try:
        from ai_components import RealAIReasoningEngine
        ai_engine = RealAIReasoningEngine()
        
        if not ai_engine.ai_available:
            st.warning("⚠️ AI nie je dostupné - zadajte OpenAI API kľúč")
            return {}
        
        system_prompt = """
Si expert na parsovanie konverzácií o firemných oddeleniach. 
Tvoja úloha je extrahovať štruktúrované dáta z ChatGPT konverzácie o oddelení.

VÝSTUP MUSÍ BYŤ VALID JSON s týmito poľami (všetky sú string):
{
    "name": "názov oddelenia",
    "function": "hlavná funkcia oddelenia",
    "manager": "vedúci oddelenia", 
    "processes": "hlavné procesy oddelené \\n",
    "staff_count": "počet zamestnancov",
    "competencies": "kľúčové kompetencie",
    "collaboration": "spolupráca s oddeleniami",
    "tools": "nástroje a systémy",
    "challenges": "hlavné výzvy",
    "success_metrics": "KPI a metriky úspechu"
}

Ak niektoré pole nenájdeš, nastav ho na prázdny string "".
Vráť VÝLUČNE JSON bez akýchkoľvek dodatočných textov.
"""
        
        user_prompt = f"""
Parsuj túto ChatGPT konverzáciu a extraktuj dáta o oddelení:

{conversation}

Vráť VALID JSON s extraktovanými dátami o oddelení.
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
        st.error(f"❌ Chyba parsovania oddelenia: {e}")
        return {} 