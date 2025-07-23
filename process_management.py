#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Process Management
Správa procesov - zoznam, editácia, mazanie
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from ui_components import render_section_header, render_action_buttons, render_modern_dataframe

def get_fallback_processes():
    """Vráti fallback procesy ak databáza nefunguje"""
    return [
        {
            'id': 1,
            'name': 'Spracovanie objednávok zákazníkov',
            'category': 'obchod',
            'owner': 'Mária Novák - Obchodný manažér',
            'frequency': 'denne',
            'duration_minutes': 45,
            'priority': 5,
            'automation_readiness': 4,
            'created_at': '2024-01-01'
        },
        {
            'id': 2,
            'name': 'Schvaľovanie dovoleniek',
            'category': 'HR',
            'owner': 'Peter Kováč - HR manažér',
            'frequency': 'týždenne',
            'duration_minutes': 15,
            'priority': 3,
            'automation_readiness': 5,
            'created_at': '2024-01-02'
        },
        {
            'id': 3,
            'name': 'Fakturácia dodávateľom',
            'category': 'administratíva',
            'owner': 'Anna Krásna - Účtovníčka',
            'frequency': 'denne',
            'duration_minutes': 20,
            'priority': 4,
            'automation_readiness': 3,
            'created_at': '2024-01-03'
        }
    ]

def render_process_management():
    """Render správy procesov - zoznam, editácia, mazanie"""
    
    st.markdown("### 🔍 DEBUG INFORMÁCIE")
    st.info("Testovanie načítavania procesov...")
    
    # Načítanie procesov s detailným debugom
    processes = []
    debug_info = []
    
    try:
        import os
        db_path = "adsun_processes.db"
        
        # Debug: skontroluj súbor
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            debug_info.append(f"✅ Databáza existuje: {db_path} ({file_size} bytov)")
        else:
            debug_info.append(f"❌ Databáza neexistuje: {db_path}")
            st.error("Databáza neexistuje! Používam fallback dáta.")
            processes = get_fallback_processes()
        
        if not processes:  # Ak ešte stále nemáme procesy, skús načítať z DB
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Debug: skontroluj tabuľky
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                debug_info.append(f"📊 Tabuľky v DB: {tables}")
                
                if 'processes' in tables:
                    # Debug: skontroluj stĺpce
                    cursor = conn.execute("PRAGMA table_info(processes)")
                    columns = [row[1] for row in cursor.fetchall()]
                    debug_info.append(f"📋 Stĺpce v processes: {columns}")
                    
                    # Skús načítať procesy
                    if 'is_active' in columns:
                        cursor = conn.execute("""
                            SELECT id, name, category, owner, frequency, duration_minutes, 
                                   priority, automation_readiness, created_at
                            FROM processes 
                            WHERE is_active = 1
                            ORDER BY category, name
                        """)
                    else:
                        # Ak chýba is_active stĺpec
                        cursor = conn.execute("""
                            SELECT id, name, category, owner, frequency, duration_minutes, 
                                   priority, automation_readiness, created_at
                            FROM processes 
                            ORDER BY category, name
                        """)
                    
                    processes = [dict(row) for row in cursor.fetchall()]
                    debug_info.append(f"📈 Načítaných procesov: {len(processes)}")
                    
                else:
                    debug_info.append("❌ Tabuľka 'processes' neexistuje")
                    processes = get_fallback_processes()
                    
    except Exception as e:
        debug_info.append(f"❌ Chyba: {str(e)}")
        st.error(f"❌ Chyba načítavania: {e}")
        processes = get_fallback_processes()
    
    # Zobraz debug info
    with st.expander("🔍 Debug informácie", expanded=True):
        for info in debug_info:
            st.text(info)
    
    # Ak stále nemáme procesy, použij fallback
    if not processes:
        st.warning("⚠️ Žiadne procesy v databáze. Používam ukážkové dáta.")
        processes = get_fallback_processes()
    
    # Moderný header so štatistikami
    stats = {
        "total": {"icon": "📋", "text": f"{len(processes)} procesov"},
        "categories": {"icon": "📂", "text": f"{len(set(p.get('category', 'Nezhodnotené') for p in processes))} kategórií"},
        "owners": {"icon": "👥", "text": f"{len(set(p.get('owner', 'Neurčený') for p in processes))} vlastníkov"}
    }
    
    render_section_header(
        title="Správa procesov",
        subtitle="Kompletný zoznam procesov s možnosťou editácie a mazania",
        icon="📋",
        stats=stats
    )
    
    # DETAILY MIMO EXPANDERA - AK SÚ ZOBRAZENÉ
    if 'show_process_details' in st.session_state:
        process_id = st.session_state.show_process_details
        st.markdown("---")
        show_process_details(process_id)
        
        if st.button("❌ Zavrieť detaily", type="secondary"):
            del st.session_state.show_process_details
            st.rerun()
        
        st.markdown("---")
    
    # Filter a vyhľadávanie
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("🔍 Vyhľadávanie procesov", placeholder="názov, kategória, vlastník...")
    
    with col2:
        categories = ["Všetky"] + list(set([p.get('category', 'Nezhodnotené') for p in processes]))
        selected_category = st.selectbox("📂 Kategória", categories)
    
    with col3:
        if st.button("➕ Nový proces"):
            st.session_state.mode = "learning"
            st.rerun()
    
    # Filtrovanie procesov
    filtered_processes = processes
    if search:
        filtered_processes = [
            p for p in filtered_processes 
            if search.lower() in str(p.get('name', '')).lower() 
            or search.lower() in str(p.get('category', '')).lower()
            or search.lower() in str(p.get('owner', '')).lower()
        ]
    
    if selected_category != "Všetky":
        filtered_processes = [p for p in filtered_processes if p.get('category') == selected_category]
    
    # Zobrazenie procesov v tabuľke
    if not filtered_processes:
        st.info("📭 Žiadne procesy nenájdené")
        return
    
    st.markdown(f"**Nájdených: {len(filtered_processes)} procesov**")
    
    # Tabuľka procesov
    for i, process in enumerate(filtered_processes):
        with st.expander(f"📋 {process.get('name', 'Bez názvu')} ({process.get('category', 'Nezhodnotené')})", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # Základné info
                st.write(f"**Vlastník:** {process.get('owner', 'Neurčený')}")
                st.write(f"**Frekvencia:** {process.get('frequency', 'Neurčené')}")
                st.write(f"**Trvanie:** {process.get('duration_minutes', 0) or 0} minút")
                st.write(f"**Priorita:** {process.get('priority', 'Neurčené')}")
                st.write(f"**Automatizácia:** {process.get('automation_readiness', 0)}/5")
                st.write(f"**Vytvorené:** {process.get('created_at', '')[:10] if process.get('created_at') else 'Neznáme'}")
            
            with col2:
                if st.button("✏️ Upraviť", key=f"edit_{process['id']}"):
                    st.session_state.edit_process_id = process['id']
                    st.session_state.mode = "edit_process"
                    st.rerun()
                
                # TLAČIDLO DETAILY TERAZ ZOBRAZUJE MIMO EXPANDERA
                if st.button("📊 Detaily", key=f"detail_{process['id']}"):
                    st.session_state.show_process_details = process['id']
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Zmazať", key=f"delete_{process['id']}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_{process['id']}", False):
                        delete_process(process['id'])
                        st.success("✅ Proces zmazaný!")
                        st.rerun()
                    else:
                        st.session_state[f"confirm_delete_{process['id']}"] = True
                        st.warning("⚠️ Kliknite znovu pre potvrdenie")

def show_process_details(process_id: int):
    """Zobrazí detaily procesu"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            
            # Proces
            cursor = conn.execute("SELECT * FROM processes WHERE id = ?", (process_id,))
            process = dict(cursor.fetchone())
            
            # Sessions
            cursor = conn.execute("""
                SELECT * FROM documentation_sessions 
                WHERE process_id = ? 
                ORDER BY created_at DESC
            """, (process_id,))
            sessions = [dict(row) for row in cursor.fetchall()]
            
            st.markdown(f"### 📊 Detaily: {process['name']}")
            
            # ÚPLNE BEZ STĹPCOV - všetko pod sebou na plnú šírku
            st.markdown("#### 📋 Základné informácie")
            
            # Všetko pod sebou namiesto stĺpcov
            st.markdown(f"**🏢 Kategória/Oddelenie:** {process.get('category', 'Nezhodnotené')}")
            st.markdown(f"**👤 Vlastník procesu:** {process.get('owner', 'Neurčený')}")
            st.markdown(f"**⚡ Priorita procesu:** {process.get('priority', 'Neurčené')}")
            st.markdown(f"**🔄 Frekvencia vykonávania:** {process.get('frequency', 'Neurčené')}")
            st.markdown(f"**⏱️ Čas potrebný na vykonanie:** {process.get('duration_minutes', 0) or 0} minút")
            st.markdown(f"**🤖 Úroveň automatizácie:** {process.get('automation_readiness', 0)}/5")
            
            # Oddeľovač
            st.markdown("---")
            
            # Detailné informácie na plnú šírku
            if process.get('description'):
                st.markdown("#### 📝 Popis procesu")
                st.markdown(f"**{process['description']}**")
                st.markdown("")
            
            if process.get('steps'):
                st.markdown("#### 📋 Hlavné kroky procesu") 
                st.markdown(process['steps'])
                st.markdown("")
            
            if process.get('step_details'):
                st.markdown("#### 📝 Detailný popis krokov") 
                st.markdown(process['step_details'])
                st.markdown("")
            
            if process.get('tools'):
                st.markdown("#### 🛠️ Nástroje a systémy")
                st.markdown(process['tools'])
                st.markdown("")
            
            if process.get('risks'):
                st.markdown("#### ⚠️ Riziká a problémy")
                st.markdown(process['risks'])
                st.markdown("")
            
            if process.get('improvements'):
                st.markdown("#### 🚀 Možnosti zlepšenia")
                st.markdown(process['improvements'])
                st.markdown("")
            
            # História dokumentácie - BEZ EXPANDERS, široký formát
            if sessions:
                st.markdown("#### 📝 História dokumentácie")
                st.markdown("---")
                
                # Zobraz sessions v širokom formáte
                for i, session in enumerate(sessions[:3]):  # Top 3
                    st.markdown(f"**📅 Dokumentačná session {i+1}**")
                    st.markdown(f"*Dokumentoval:* {session.get('documented_by', 'Neznámy')} | *Dátum:* {session.get('created_at', '')[:16]}*")
                    
                    if session.get('session_notes'):
                        try:
                            notes = json.loads(session['session_notes'])
                            
                            # Široký layout pre otázky a odpovede - na plnú šírku
                            st.markdown(f"**❓ Otázka:** {notes.get('question', 'N/A')}")
                            st.markdown(f"**💬 Odpoveď:** {notes.get('response', 'N/A')}")
                                
                        except:
                            st.markdown(f"**📄 Poznámky:** {session['session_notes']}")
                    
                    if i < len(sessions[:3]) - 1:  # Nie posledný
                        st.markdown("---")
            else:
                st.info("📝 Žiadna história dokumentácie")
            
    except Exception as e:
        st.error(f"❌ Chyba načítavania detailov: {e}")

def delete_process(process_id: int):
    """Zmaže proces z databázy"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Soft delete - označí ako neaktívny
            conn.execute("UPDATE processes SET is_active = 0 WHERE id = ?", (process_id,))
            conn.commit()
    except Exception as e:
        st.error(f"❌ Chyba mazania: {e}")

def render_edit_process():
    """Editácia procesu"""
    st.markdown("## ✏️ Editácia procesu")
    st.markdown("*Upravte detaily procesu*")
    
    # Získaj ID procesu na editáciu
    process_id = st.session_state.get('edit_process_id')
    if not process_id:
        st.error("❌ Žiadny proces na editáciu")
        if st.button("🔙 Späť na zoznam"):
            st.session_state.mode = "process_management"
            st.rerun()
        return
    
    # Načítaj proces z databázy
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM processes WHERE id = ?", (process_id,))
            process = dict(cursor.fetchone())
    except Exception as e:
        st.error(f"❌ Chyba načítavania: {e}")
        return
    
    # Editačný formulár
    with st.form("edit_process_form"):
        st.markdown(f"### Editácia: {process['name']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Názov procesu:", value=process.get('name', ''))
            new_category = st.selectbox("Kategória:", 
                                      ["obchod", "výroba", "administratíva", "IT", "HR"],
                                      index=["obchod", "výroba", "administratíva", "IT", "HR"].index(process.get('category', 'obchod')) if process.get('category') in ["obchod", "výroba", "administratíva", "IT", "HR"] else 0)
            new_owner = st.text_input("Vlastník:", value=process.get('owner', ''))
            new_frequency = st.selectbox("Frekvencia:", 
                                       ["denne", "týždenne", "mesačne", "príležitostne"],
                                       index=["denne", "týždenne", "mesačne", "príležitostne"].index(process.get('frequency', 'príležitostne')) if process.get('frequency') in ["denne", "týždenne", "mesačne", "príležitostne"] else 3)
        
        with col2:
            new_duration = st.number_input("Trvanie (minúty):", value=process.get('duration_minutes', 0) or 0, min_value=0)
            new_priority = st.selectbox("Priorita:",
                                      ["vysoká", "stredná", "nízka"],
                                      index=["vysoká", "stredná", "nízka"].index(process.get('priority', 'stredná')) if process.get('priority') in ["vysoká", "stredná", "nízka"] else 1)
            new_automation = st.slider("Automatizácia (1-5):", 1, 5, value=process.get('automation_readiness', 3) or 3)
        
        # Pokročilé nastavenia
        with st.expander("🔧 Pokročilé nastavenia"):
            new_trigger = st.text_area("Spúšťač procesu:", value=process.get('trigger_type', ''))
            new_success = st.text_area("Kritériá úspechu:", value=process.get('success_criteria', ''))
            new_problems = st.text_area("Časté problémy:", value=process.get('common_problems', ''))
        
        # Tlačidlá
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            submit_button = st.form_submit_button("💾 Uložiť zmeny", type="primary")
        
        with col2:
            if st.form_submit_button("❌ Zrušiť"):
                st.session_state.mode = "process_management"
                st.rerun()
        
        with col3:
            if st.form_submit_button("🗑️ Zmazať proces"):
                st.session_state.confirm_delete_edit = True
    
    # Spracovanie uloženia
    if submit_button:
        try:
            with sqlite3.connect("adsun_processes.db") as conn:
                conn.execute("""
                    UPDATE processes 
                    SET name = ?, category = ?, owner = ?, frequency = ?, 
                        duration_minutes = ?, priority = ?, automation_readiness = ?,
                        trigger_type = ?, success_criteria = ?, common_problems = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    new_name, new_category, new_owner, new_frequency,
                    new_duration, new_priority, new_automation,
                    new_trigger, new_success, new_problems,
                    process_id
                ))
                conn.commit()
            
            st.success("✅ Proces úspešne upravený!")
            st.session_state.mode = "process_management"
            if 'edit_process_id' in st.session_state:
                del st.session_state.edit_process_id
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Chyba ukladania: {e}")
    
    # Potvrdenie mazania
    if st.session_state.get('confirm_delete_edit'):
        st.warning("⚠️ Naozaj chcete zmazať tento proces?")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Áno, zmazať", type="primary"):
                try:
                    with sqlite3.connect("adsun_processes.db") as conn:
                        conn.execute("UPDATE processes SET is_active = 0 WHERE id = ?", (process_id,))
                        conn.commit()
                    
                    st.success("✅ Proces zmazaný!")
                    st.session_state.mode = "process_management"
                    if 'edit_process_id' in st.session_state:
                        del st.session_state.edit_process_id
                    if 'confirm_delete_edit' in st.session_state:
                        del st.session_state.confirm_delete_edit
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Chyba mazania: {e}")
        
        with col2:
            if st.button("❌ Nie, zrušiť"):
                if 'confirm_delete_edit' in st.session_state:
                    del st.session_state.confirm_delete_edit
                st.rerun()
    
    # Späť button
    st.markdown("---")
    if st.button("🔙 Späť na správu procesov"):
        st.session_state.mode = "process_management"
        if 'edit_process_id' in st.session_state:
            del st.session_state.edit_process_id
        st.rerun() 

def render_process_learning():
    """AI-driven učenie nového procesu s inteligentným dopĺňaním"""
    st.markdown("### 🤖 AI Asistent pre nový proces")
    st.markdown("*AI vám pomôže vyplniť všetky polia o procese*")
    
    # INICIALIZÁCIA DÁT AK NEEXISTUJÚ - MUSI BYŤ PRED PRVÝM PRÍSTUPOM!
    if 'current_process_data' not in st.session_state:
        st.session_state.current_process_data = {}
    
    # DEFINÍCIA POLÍ - MUSI BYŤ PRED PRVÝM POUŽITÍM!
    process_fields = [
        {
            'key': 'name',
            'label': 'Názov procesu',
            'question': 'Aký je názov nového procesu?',
            'placeholder': 'napr. Vystavenie faktúry, Prijatie objednávky, Nábor zamestnanca',
            'ai_prompt': 'Navrhni 3 alternatívne názvy pre proces typu {value}'
        },
        {
            'key': 'category',
            'label': 'Kategória/Oddelenie',
            'question': 'Do akej kategórie alebo oddelenia proces patri?',
            'placeholder': 'napr. Obchod, HR, Účtovníctvo, IT',
            'ai_prompt': 'Navrhni vhodnú kategóriu pre proces {name}'
        },
        {
            'key': 'description',
            'label': 'Popis procesu',
            'question': 'Ako by ste opísali tento proces?',
            'placeholder': 'Stručný popis čo proces robí...',
            'ai_prompt': 'Napíš jasný popis procesu {name} v oddelení {category}'
        },
        {
            'key': 'owner',
            'label': 'Vlastník procesu',
            'question': 'Kto je zodpovedný za tento proces?',
            'placeholder': 'Meno alebo pozícia zodpovednej osoby...',
            'ai_prompt': 'Navrhni typ pozície zodpovednej za proces {name}'
        },
        {
            'key': 'steps',
            'label': 'Hlavné kroky (stručne)',
            'question': 'Aké sú hlavné kroky tohto procesu? (len názvy krokov)',
            'placeholder': '1. Prvý krok\n2. Druhý krok\n3. Tretí krok',
            'ai_prompt': 'Napíš HLAVNÉ KROKY procesu {name} ako stručný zoznam bez detailov'
        },
        {
            'key': 'step_details',
            'label': 'Detailný popis krokov',
            'question': 'Popíšte detailne čo sa deje v každom kroku procesu',
            'placeholder': '1. Prvý krok: Detailný popis čo sa presne deje...\n2. Druhý krok: Detailný popis...',
            'ai_prompt': 'Napíš DETAILNÉ kroky procesu {name} vrátane opisu čo sa v každom kroku presne deje, kto je zodpovedný a aké nástroje sa používajú'
        },
        {
            'key': 'frequency',
            'label': 'Frekvencia',
            'question': 'Ako často sa tento proces vykonáva?',
            'placeholder': 'napr. Denne, Týždenne, Mesačne, Podľa potreby',
            'ai_prompt': 'Navrhni typickú frekvenciu pre proces {name}'
        },
        {
            'key': 'duration_minutes',
            'label': 'Trvanie (minúty)',
            'question': 'Koľko času proces trvá?',
            'placeholder': 'Počet minút...',
            'ai_prompt': 'Odhadni typické trvanie procesu {name} v minútach'
        },
        {
            'key': 'priority',
            'label': 'Priorita',
            'question': 'Aká je priorita tohto procesu?',
            'placeholder': '1-10 (1=nízka, 10=vysoká)',
            'ai_prompt': 'Ohodnoť prioritu procesu {name} na škále 1-10'
        },
        {
            'key': 'tools',
            'label': 'Nástroje a systémy',
            'question': 'Aké nástroje sa pri procese používajú?',
            'placeholder': 'Software, aplikácie, dokumenty...',
            'ai_prompt': 'Navrhni nástroje a systémy potrebné pre proces {name}'
        },
        {
            'key': 'risks',
            'label': 'Riziká a problémy',
            'question': 'Aké riziká môžu pri procese nastať?',
            'placeholder': 'Možné problémy a komplikácie...',
            'ai_prompt': 'Identifikuj hlavné riziká a problémy procesu {name}'
        },
        {
            'key': 'automation_readiness',
            'label': 'Možnosť automatizácie',
            'question': 'Dá sa tento proces automatizovať?',
            'placeholder': '1-5 (1=nemožné, 5=úplne automatizovateľné)',
            'ai_prompt': 'Ohodnoť možnosť automatizácie procesu {name} na škále 1-5'
        },
        {
            'key': 'improvements',
            'label': 'Možnosti zlepšenia',
            'question': 'Ako by sa dal proces zlepšiť?',
            'placeholder': 'Návrhy na optimalizáciu...',
            'ai_prompt': 'Navrhni možnosti zlepšenia a optimalizácie procesu {name}'
        }
    ]
    
    # KONTROLA PREPNUTIA NA STEP-BY-STEP - po definícii process_fields
    if st.session_state.get('switch_to_step_by_step', False):
        # Vyčistíme flag a resetujeme na step-by-step
        del st.session_state.switch_to_step_by_step
        # Nastavíme default hodnotu pre radio (bude sa zobrazovať step-by-step)
        default_method = "🔄 Postupný sprievodca (krok za krokom)"
    else:
        # Ak nie je flag nastavený, použijeme existujúcu hodnotu alebo default
        default_method = st.session_state.get('process_creation_method', "🔄 Postupný sprievodca (krok za krokom)")
    
    # VÝBER SPÔSOBU VYTVORENIA PROCESU
    st.markdown("#### 🎯 Vyberte spôsob vytvorenia procesu:")
    
    creation_method = st.radio(
        "Ako chcete vytvoriť proces?",
        [
            "🔄 Postupný sprievodca (krok za krokom)",
            "📋 Bulk import z ChatGPT konverzácie"
        ],
        index=0 if default_method == "🔄 Postupný sprievodca (krok za krokom)" else 1
        # ODSTRÁNENÝ key parameter pre predchádzanie session state konfliktom
    )
    
    if creation_method == "📋 Bulk import z ChatGPT konverzácie":
        render_bulk_import_mode()
        return
    
    # PÔVODNÝ POSTUPNÝ SPRIEVODCA
    st.markdown("---")
    st.markdown("**🔄 Postupný sprievodca - krok za krokom**")
    
    # KONTROLA PREDVYPLNENÝCH DÁT - po definícii process_fields
    if st.session_state.current_process_data:
        filled_fields = sum(1 for field in process_fields if st.session_state.current_process_data.get(field['key']))
        total_fields = len(process_fields)
        
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
                    for i, field in enumerate(process_fields):
                        if not st.session_state.current_process_data.get(field['key']):
                            st.session_state.process_learning_step = i
                            st.rerun()
                            break
        else:
            st.success("🎉 **Všetky polia sú vyplnené!** Môžete pokračovať na finálny prehľad")
            if st.button("🏁 Prejsť na finálny prehľad"):
                st.session_state.process_learning_step = len(process_fields)
                st.rerun()
        
        # Zobrazenie prehľadu predvyplnených dát
        with st.expander("👀 Zobraziť všetky predvyplnené dáta"):
            for field in process_fields:
                value = st.session_state.current_process_data.get(field['key'], '')
                if value:
                    st.markdown(f"✅ **{field['label']}:** {value[:100]}{'...' if len(str(value)) > 100 else ''}")
                else:
                    st.markdown(f"⭕ **{field['label']}:** *Nevyplnené*")
    
    # Polia pre proces s AI promptmi
    current_step = st.session_state.get('process_learning_step', 0)
    
    if current_step < len(process_fields):
        field = process_fields[current_step]
        
        # VYLEPŠENÝ HEADER S INDIKÁTOROM STAVU
        is_field_filled = bool(st.session_state.current_process_data.get(field['key']))
        status_icon = "✅" if is_field_filled else "⭕"
        status_text = "už vyplnené" if is_field_filled else "nevyplnené"
        
        st.markdown(f"### 🎯 Krok {current_step + 1}/{len(process_fields)}: {status_icon} {field['label']}")
        
        if is_field_filled:
            st.success(f"💡 **Toto pole je {status_text}** z bulk importu - môžete hodnotu upraviť alebo ponechať")
        else:
            st.info(f"📝 **Toto pole je {status_text}** - zadajte novú hodnotu alebo použite AI pomoc")
        
        # Špeciálne spracovanie pre kategóriu - ukáž existujúce kategórie
        if field['key'] == 'category':
            existing_categories = load_existing_categories()
            if existing_categories:
                st.info(f"📂 **Existujúce kategórie:** {', '.join(existing_categories)}")
                st.markdown(f"**Otázka:** {field['question']} Môžete vybrať existujúcu alebo zadať novú.")
            else:
                st.info(field['question'])
        else:
            st.info(field['question'])
        
        # Hlavné pole pre input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Špeciálne spracovanie pre category - selectbox + možnosť vlastného
            if field['key'] == 'category':
                existing_categories = load_existing_categories()
                current_value = st.session_state.current_process_data.get(field['key'], '')
                
                if existing_categories:
                    # Ak existujú kategórie, ponúkni výber
                    options = ["-- Vybrať existujúcu --"] + existing_categories + ["-- Zadať novú --"]
                    
                    if current_value and current_value in existing_categories:
                        index = existing_categories.index(current_value) + 1
                    elif current_value:
                        index = len(options) - 1  # "Zadať novú"
                    else:
                        index = 0
                    
                    selection = st.selectbox(
                        "📂 Vyberte kategóriu:",
                        options,
                        index=index,
                        key=f"cat_select_{field['key']}"
                    )
                    
                    if selection == "-- Zadať novú --" or (selection == "-- Vybrať existujúcu --" and current_value):
                        user_input = st.text_input(
                            "✍️ Názov novej kategórie:",
                            value=current_value if selection == "-- Zadať novú --" else "",
                            placeholder=field['placeholder'],
                            key=f"field_{field['key']}"
                        )
                    elif selection != "-- Vybrať existujúcu --":
                        user_input = selection
                        # DÔLEŽITÉ: Okamžite aktualizuj session state
                        st.session_state.current_process_data[field['key']] = selection
                    else:
                        user_input = current_value
                else:
                    # Žiadne existujúce kategórie - ponúkni základné možnosti
                    basic_categories = ["obchod", "výroba", "administratíva", "IT", "HR", "iné"]
                    
                    if current_value and current_value in basic_categories:
                        index = basic_categories.index(current_value)
                    else:
                        index = 0
                    
                    user_input = st.selectbox(
                        "📂 Vyberte kategóriu:",
                        basic_categories,
                        index=index,
                        key=f"field_{field['key']}"
                    )
                    
                    # DÔLEŽITÉ: Okamžite aktualizuj session state
                    st.session_state.current_process_data[field['key']] = user_input
            elif field['key'] in ['description', 'steps', 'step_details', 'tools', 'risks', 'improvements']:
                user_input = st.text_area(
                    "✍️ Vaša odpoveď:",
                    value=st.session_state.current_process_data.get(field['key'], ''),
                    placeholder=field['placeholder'],
                    height=100,
                    key=f"field_{field['key']}"
                )
            elif field['key'] in ['duration_minutes', 'priority', 'automation_readiness']:
                user_input = st.number_input(
                    "✍️ Vaša odpoveď:",
                    value=int(st.session_state.current_process_data.get(field['key'], 0)) if st.session_state.current_process_data.get(field['key']) else 0,
                    min_value=0,
                    max_value=10 if field['key'] in ['priority', 'automation_readiness'] else 9999,
                    key=f"field_{field['key']}"
                )
            else:
                user_input = st.text_input(
                    "✍️ Vaša odpoveď:",
                    value=st.session_state.current_process_data.get(field['key'], ''),
                    placeholder=field['placeholder'],
                    key=f"field_{field['key']}"
                )
        
        with col2:
            st.markdown("**🤖 AI Pomoc**")
            if st.button("✨ AI Doplniť", key=f"ai_help_{field['key']}"):
                ai_suggestion = get_process_ai_suggestion(field, st.session_state.current_process_data)
                if ai_suggestion:
                    st.session_state[f"ai_suggestion_{field['key']}"] = ai_suggestion
                    st.rerun()
        
        # AI návrh ak existuje
        if f"ai_suggestion_{field['key']}" in st.session_state:
            st.success(f"🤖 AI návrh: {st.session_state[f'ai_suggestion_{field['key']}']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Použiť AI návrh", key=f"use_ai_{field['key']}"):
                    st.session_state.current_process_data[field['key']] = st.session_state[f'ai_suggestion_{field['key']}']
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
                st.session_state.current_process_data[field['key']] = user_input
                st.session_state.process_learning_step = current_step - 1
                st.rerun()
        
        with col2:
            if st.button("➡️ Ďalej"):
                st.session_state.current_process_data[field['key']] = user_input
                st.session_state.process_learning_step = current_step + 1
                st.rerun()
        
        with col3:
            if st.button("💾 Uložiť proces") and st.session_state.current_process_data.get('name'):
                st.session_state.current_process_data[field['key']] = user_input
                
                # DEBUG INFO
                st.write("🔍 **DEBUG:** Pokúšam sa uložiť proces...")
                st.write(f"📝 **Dáta na uloženie:** {len(st.session_state.current_process_data)} polí")
                
                try:
                    save_process_to_db(st.session_state.current_process_data)
                    st.success("✅ Proces úspešne uložený!")
                    
                    # ZOBRAZ NAVIGAČNÉ MOŽNOSTI
                    st.markdown("### 🎉 Proces bol vytvorený!")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("➕ Vytvoriť ďalší", key="create_another"):
                            # Vyčisti dáta
                            st.session_state.current_process_data = {}
                            st.session_state.process_learning_step = 0
                            st.rerun()
                    
                    with col2:
                        if st.button("📋 Správa procesov", key="goto_processes"):
                            st.session_state.mode = "processes"
                            st.rerun()
                    
                    with col3:
                        if st.button("🏠 Domov", key="goto_home"):
                            st.session_state.mode = "home"
                            st.rerun()
                    
                    # NEPOUŽÍVAJ st.rerun() automaticky
                    return
                    
                except Exception as e:
                    st.error(f"❌ CHYBA ukladania: {e}")
                    st.write(f"🔍 **DEBUG ERROR:** {str(e)}")
                    return
        
        with col4:
            if st.button("❌ Zrušiť"):
                st.session_state.mode = "processes"
                st.rerun()
        
        # Aktualizuj dáta
        st.session_state.current_process_data[field['key']] = user_input
        
    else:
        # Všetky polia vyplnené - finálny prehľad
        st.success("🎉 Všetky polia vyplnené!")
        st.markdown("### 📋 Prehľad procesu:")
        
        for field in process_fields:
            value = st.session_state.current_process_data.get(field['key'], '')
            if value:
                st.markdown(f"**{field['label']}:** {value}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Uložiť proces", type="primary"):
                # DEBUG INFO
                st.write("🔍 **DEBUG:** FINÁLNY PREHĽAD - Pokúšam sa uložiť proces...")
                st.write(f"📝 **Dáta na uloženie:** {len(st.session_state.current_process_data)} polí")
                for key, value in st.session_state.current_process_data.items():
                    st.write(f"  - {key}: {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
                
                try:
                    save_process_to_db(st.session_state.current_process_data)
                    st.success("✅ Proces vytvorený!")
                    
                    # NAVIGAČNÉ MOŽNOSTI
                    st.markdown("### 🎉 Úspešne vytvorený!")
                    nav_col1, nav_col2, nav_col3 = st.columns(3)
                    
                    with nav_col1:
                        if st.button("➕ Vytvoriť ďalší", key="final_create_another"):
                            st.session_state.current_process_data = {}
                            st.session_state.process_learning_step = 0
                            st.rerun()
                    
                    with nav_col2:
                        if st.button("📋 Správa procesov", key="final_goto_processes"):
                            st.session_state.mode = "processes"
                            st.rerun()
                    
                    with nav_col3:
                        if st.button("🏠 Domov", key="final_goto_home"):
                            st.session_state.mode = "home"
                            st.rerun()
                    
                    return
                    
                except Exception as e:
                    st.error(f"❌ CHYBA ukladania: {e}")
                    st.write(f"🔍 **DEBUG ERROR:** {str(e)}")
                    return
        
        with col2:
            if st.button("📝 Upraviť"):
                st.session_state.process_learning_step = 0
                st.rerun()

def render_bulk_import_mode():
    """Bulk import z ChatGPT konverzácie"""
    st.markdown("### 📋 Bulk Import z ChatGPT konverzácie")
    st.markdown("**💡 Návod:** Skopírujte celú konverzáciu z ChatGPT kde ste diskutovali o procese a AI automaticky vyplní všetky polia.")
    
    # Príklad formátu
    with st.expander("📖 Príklad ChatGPT konverzácie"):
        st.markdown("""
**Príklad správneho formátu:**

```
Používateľ: Chcem vytvoriť proces fakturácie pre našu firmu

ChatGPT: Proces fakturácie je kľúčový administratívny proces. Môžem vám pomôcť ho navrhnúť:

**Názov procesu:** Fakturácia klientom
**Kategória:** Administratíva  
**Popis:** Kompletný proces od objednávky po zaplatenie faktúry

**Kroky procesu:**
1. Príjem objednávky od klienta
2. Overenie údajov a dostupnosti
3. Vytvorenie faktúry v systéme
4. Odoslanie faktúry klientovi
5. Sledovanie platby

**Nástroje:** Excel, Gmail, účtovný systém, CRM
**Frekvencia:** Denne
**Trvanie:** 15 minút
**Priorita:** Vysoká (8/10)
**Automatizácia:** 4/5 - možné automatizovať až na kontrolu
**Riziká:** Chyby v údajoch, oneskorenie platby
```
        """)
    
    # Vstupné pole pre konverzáciu
    conversation_text = st.text_area(
        "📝 Vložte ChatGPT konverzáciu:",
        height=400,
        placeholder="Skopírujte sem celú konverzáciu z ChatGPT...",
        key="bulk_conversation_input"
    )
    
    # Tlačidlá
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🚀 Spracovať AI", type="primary", disabled=not conversation_text.strip()):
            with st.spinner("🤖 AI parsuje konverzáciu..."):
                parsed_data = parse_chatgpt_conversation(conversation_text)
                if parsed_data:
                    st.session_state.bulk_parsed_data = parsed_data
                    st.rerun()
                else:
                    st.error("❌ AI nedokázalo parsovať konverzáciu. Skúste iný formát.")
    
    with col2:
        if st.button("🔄 Prepnúť na sprievodcu"):
            # ODSTRÁNENÉ - nenastavujem radio widget session state
            # Namiesto toho použijem flag pre prepnutie
            st.session_state.switch_to_step_by_step = True
            st.rerun()
    
    with col3:
        if st.button("❌ Zrušiť"):
            st.session_state.mode = "processes"
            st.rerun()
    
    # Zobrazenie parsovaných dát
    if 'bulk_parsed_data' in st.session_state:
        parsed_data = st.session_state.bulk_parsed_data
        
        st.markdown("---")
        st.success("✅ AI úspešne parsovalo konverzáciu!")
        st.markdown("### 📋 Extraktované dáta:")
        st.info("💡 **Môžete upraviť ľubovoľné pole pred uložením**")
        
        # EDITOVATEĽNÁ FORMA PRE VŠETKY POLIA
        with st.form("edit_bulk_data_form"):
            st.markdown("#### ✏️ Upravte parsované dáta:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Základné informácie**")
                
                edited_name = st.text_input(
                    "📝 Názov procesu:",
                    value=parsed_data.get('name', ''),
                    key="edit_name"
                )
                
                edited_category = st.text_input(
                    "📂 Kategória:",
                    value=parsed_data.get('category', ''),
                    key="edit_category"
                )
                
                edited_owner = st.text_input(
                    "👤 Vlastník:",
                    value=parsed_data.get('owner', ''),
                    key="edit_owner"
                )
                
                edited_frequency = st.text_input(
                    "🔄 Frekvencia:",
                    value=parsed_data.get('frequency', ''),
                    key="edit_frequency"
                )
            
            with col2:
                st.markdown("**⚙️ Detaily procesu**")
                
                edited_duration = st.number_input(
                    "⏱️ Trvanie (minúty):",
                    value=int(parsed_data.get('duration_minutes', 0)) if parsed_data.get('duration_minutes') else 0,
                    min_value=0,
                    key="edit_duration"
                )
                
                edited_priority = st.number_input(
                    "⚡ Priorita (1-10):",
                    value=int(parsed_data.get('priority', 5)) if parsed_data.get('priority') else 5,
                    min_value=1,
                    max_value=10,
                    key="edit_priority"
                )
                
                edited_automation = st.number_input(
                    "🤖 Automatizácia (1-5):",
                    value=int(parsed_data.get('automation_readiness', 3)) if parsed_data.get('automation_readiness') else 3,
                    min_value=1,
                    max_value=5,
                    key="edit_automation"
                )
            
            # Dlhé texty na plnú šírku
            st.markdown("**📝 Detailné informácie**")
            
            edited_description = st.text_area(
                "📖 Popis procesu:",
                value=parsed_data.get('description', ''),
                height=80,
                key="edit_description"
            )
            
            edited_steps = st.text_area(
                "📋 Hlavné kroky (stručne):",
                value=parsed_data.get('steps', ''),
                height=80,
                key="edit_steps"
            )
            
            edited_step_details = st.text_area(
                "📝 Detailný popis krokov:",
                value=parsed_data.get('step_details', ''),
                height=120,
                key="edit_step_details"
            )
            
            edited_tools = st.text_area(
                "🛠️ Nástroje a systémy:",
                value=parsed_data.get('tools', ''),
                height=80,
                key="edit_tools"
            )
            
            edited_risks = st.text_area(
                "⚠️ Riziká a problémy:",
                value=parsed_data.get('risks', ''),
                height=80,
                key="edit_risks"
            )
            
            edited_improvements = st.text_area(
                "🚀 Možnosti zlepšenia:",
                value=parsed_data.get('improvements', ''),
                height=80,
                key="edit_improvements"
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
                'category': edited_category,
                'description': edited_description,
                'owner': edited_owner,
                'steps': edited_steps,
                'step_details': edited_step_details,
                'frequency': edited_frequency,
                'duration_minutes': edited_duration,
                'priority': edited_priority,
                'tools': edited_tools,
                'risks': edited_risks,
                'automation_readiness': edited_automation,
                'improvements': edited_improvements
            }
            
            # Uloženie do databázy
            try:
                save_process_to_db(final_data)
                # NEPREHOĎ NA INÚ STRÁNKU - ZOSTAŤ TU A UKÁZAŤ SUCCESS
                del st.session_state.bulk_parsed_data
                st.success("✅ Proces úspešne uložený s úpravami!")
                st.info("📋 Proces bol pridaný do databázy. Môžete vytvoriť ďalší proces alebo prejsť na správu procesov.")
                
                # Pridaj tlačidlá na navigáciu
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("➕ Vytvoriť ďalší proces", type="primary"):
                        # Vyčisti dáta a zostań v learning mode
                        if 'current_process_data' in st.session_state:
                            del st.session_state.current_process_data
                        if 'process_learning_step' in st.session_state:
                            del st.session_state.process_learning_step
                        st.rerun()
                
                with col2:
                    if st.button("📋 Správa procesov"):
                        st.session_state.mode = "processes"
                        st.rerun()
                
                with col3:
                    if st.button("🏠 Domov"):
                        st.session_state.mode = "home"
                        st.rerun()
                
                # NEPOUŽÍVAJ st.rerun() tu - nech sa zobrazí success hlaska
                return
                
            except Exception as e:
                st.error(f"❌ Chyba ukladania: {e}")
                return
        
        elif apply_changes:
            # Aplikuj zmeny do parsed_data a zobraziť aktualizované
            st.session_state.bulk_parsed_data = {
                'name': edited_name,
                'category': edited_category,
                'description': edited_description,
                'owner': edited_owner,
                'steps': edited_steps,
                'step_details': edited_step_details,
                'frequency': edited_frequency,
                'duration_minutes': str(edited_duration),
                'priority': str(edited_priority),
                'tools': edited_tools,
                'risks': edited_risks,
                'automation_readiness': str(edited_automation),
                'improvements': edited_improvements
            }
            st.success("✅ Zmeny aplikované! Skontrolujte výsledok nižšie.")
            st.rerun()
        
        elif go_to_guide:
            # Presun do postupného sprievodcu s upravenými dátami
            final_data = {
                'name': edited_name,
                'category': edited_category,
                'description': edited_description,
                'owner': edited_owner,
                'steps': edited_steps,
                'step_details': edited_step_details,
                'frequency': edited_frequency,
                'duration_minutes': str(edited_duration),
                'priority': str(edited_priority),
                'tools': edited_tools,
                'risks': edited_risks,
                'automation_readiness': str(edited_automation),
                'improvements': edited_improvements
            }
            st.session_state.current_process_data = final_data
            st.session_state.process_learning_step = 0
            del st.session_state.bulk_parsed_data
            st.session_state.switch_to_step_by_step = True
            st.rerun()
        
        elif discard_all:
            del st.session_state.bulk_parsed_data
            st.rerun()

def parse_chatgpt_conversation(conversation: str) -> dict:
    """Parsuje ChatGPT konverzáciu a extraktuje dáta o procese"""
    try:
        from ai_components import RealAIReasoningEngine
        ai_engine = RealAIReasoningEngine()
        
        if not ai_engine.ai_available:
            st.warning("⚠️ AI nie je dostupné - zadajte OpenAI API kľúč")
            return {}
        
        system_prompt = """
Si expert na parsovanie konverzácií o business procesoch. 
Tvoja úloha je extrahovať štruktúrované dáta z ChatGPT konverzácie.

VÝSTUP MUSÍ BYŤ VALID JSON s týmito poľami (všetky sú string okrem číselných):
{
    "name": "názov procesu",
    "category": "kategória/oddelenie", 
    "description": "popis procesu",
    "owner": "vlastník procesu",
    "steps": "hlavné kroky ako zoznam - len názvy (1. Krok1\\n2. Krok2)",
    "step_details": "detailný popis každého kroku (1. Krok1: detailný popis...\\n2. Krok2: detailný popis...)",
    "frequency": "frekvencia vykonávania",
    "duration_minutes": "číslo - počet minút",
    "priority": "číslo 1-10",
    "tools": "nástroje a systémy",
    "risks": "riziká a problémy", 
    "automation_readiness": "číslo 1-5",
    "improvements": "možnosti zlepšenia"
}

Ak niektoré pole nenájdeš, nastav ho na prázdny string "".
Čísla vráť ako stringy obsahujúce len číslice.
Vráť VÝLUČNE JSON bez akýchkoľvek dodatočných textov.
"""
        
        user_prompt = f"""
Parsuj túto ChatGPT konverzáciu a extraktuj dáta o procese:

{conversation}

Vráť VALID JSON s extraktovanými dátami.
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
        st.error(f"❌ Chyba parsovania: {e}")
        return {}

def load_existing_categories() -> List[str]:
    """Načíta existujúce kategórie z databázy"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            cursor = conn.execute("SELECT DISTINCT category FROM processes WHERE category IS NOT NULL AND category != '' ORDER BY category")
            categories = [row[0] for row in cursor.fetchall() if row[0]]
            return categories
    except Exception as e:
        st.error(f"❌ Chyba načítavania kategórií: {e}")
        return []

def get_process_ai_suggestion(field: Dict, current_data: Dict) -> str:
    """Získa AI návrh pre pole procesu"""
    try:
        from ai_components import RealAIReasoningEngine
        ai_engine = RealAIReasoningEngine()
        
        if not ai_engine.ai_available:
            st.warning("⚠️ AI nie je dostupné - zadajte OpenAI API kľúč")
            return ""
        
        # Vytvor prompt na základe aktuálnych dát
        prompt = field['ai_prompt'].format(**current_data)
        
        # Špeciálne spracovanie pre category - pridaj existujúce kategórie
        additional_context = ""
        if field['key'] == 'category':
            existing_categories = load_existing_categories()
            if existing_categories:
                additional_context = f"\nExistujúce kategórie v databáze: {', '.join(existing_categories)}"
        
        system_prompt = f"""
Si expert na business procesy a procesné riadenie.
Proces: {current_data.get('name', 'proces')}
Kategória: {current_data.get('category', 'všeobecná')}{additional_context}

Napíš detailnú, užitočnú odpoveď v slovenčine. Buď konkrétny a zachovaj všetky dôležité informácie.
"""
        
        if ai_engine.use_new_client:
            response = ai_engine.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
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
                max_tokens=800,
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
            
    except Exception as e:
        st.error(f"❌ Chyba AI návrhu: {e}")
        return ""

def save_process_to_db(process_data: Dict):
    """Uloží proces do databázy"""
    try:
        # DEBUG INFO
        print(f"🔍 save_process_to_db called with data: {process_data}")
        
        with sqlite3.connect("adsun_processes.db") as conn:
            # Pridaj nové stĺpce ak neexistujú
            try:
                conn.execute("ALTER TABLE processes ADD COLUMN description TEXT")
            except sqlite3.OperationalError:
                pass  # Stĺpec už existuje
            
            try:
                conn.execute("ALTER TABLE processes ADD COLUMN steps TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                conn.execute("ALTER TABLE processes ADD COLUMN tools TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                conn.execute("ALTER TABLE processes ADD COLUMN risks TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                conn.execute("ALTER TABLE processes ADD COLUMN improvements TEXT")
            except sqlite3.OperationalError:
                pass
            
            try:
                conn.execute("ALTER TABLE processes ADD COLUMN step_details TEXT")
            except sqlite3.OperationalError:
                pass  # Stĺpec už existuje
            
            # HLAVNÝ INSERT
            insert_query = """
                INSERT INTO processes (
                    name, category, description, owner, steps, step_details, frequency, 
                    duration_minutes, priority, tools, risks, automation_readiness, 
                    improvements, trigger_type, success_criteria, common_problems, 
                    is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, datetime('now'))
            """
            
            insert_values = (
                process_data.get('name', ''),
                process_data.get('category', 'nezhodnotené'),
                process_data.get('description', ''),
                process_data.get('owner', ''),
                process_data.get('steps', ''),
                process_data.get('step_details', ''),  # Nový stĺpec
                process_data.get('frequency', 'nezhodnotené'),
                int(process_data.get('duration_minutes', 0)),
                int(process_data.get('priority', 0)),
                process_data.get('tools', ''),
                process_data.get('risks', ''),
                int(process_data.get('automation_readiness', 0)),
                process_data.get('improvements', ''),
                'manuálny proces',  # trigger_type - DEFAULT hodnota
                'dokončenie úloh',  # success_criteria - DEFAULT hodnota  
                'žiadne známe problémy'  # common_problems - DEFAULT hodnota
            )
            
            # DEBUG INFO
            print(f"🔍 INSERT VALUES: {insert_values}")
            
            cursor = conn.execute(insert_query, insert_values)
            process_id = cursor.lastrowid
            conn.commit()
            
            print(f"✅ Proces uložený s ID: {process_id}")
            
            # OVERENIE - načítaj späť z DB
            verify_cursor = conn.execute("SELECT name FROM processes WHERE id = ?", (process_id,))
            saved_name = verify_cursor.fetchone()
            print(f"🔍 OVERENIE: Uložený proces má názov: {saved_name[0] if saved_name else 'NENAŠIEL SA!'}")
            
    except Exception as e:
        error_msg = f"❌ Chyba ukladania procesu: {e}"
        print(error_msg)
        st.error(error_msg)
        raise e  # Re-raise pre debug 