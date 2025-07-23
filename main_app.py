#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN AI Assistant - Hlavná aplikácia
Refaktorovaný modulárny systém pod 600 riadkov
"""

import streamlit as st
import sqlite3
import os
import json

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

def initialize_database():
    """Inicializuje databázu s ukážkovými dátami pre Streamlit Cloud"""
    db_path = "adsun_processes.db"
    
    try:
        # Skontroluj či databáza existuje a má dáta
        if os.path.exists(db_path):
            with sqlite3.connect(db_path) as conn:
                try:
                    cursor = conn.execute("SELECT COUNT(*) FROM processes")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        return  # Databáza už má dáta
                except sqlite3.OperationalError:
                    pass  # Tabuľka neexistuje, pokračuj s vytvorením
        
        # Vytvor databázu a tabuľky
        with sqlite3.connect(db_path) as conn:
            # Vytvor základné tabuľky
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS processes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT '',
                    description TEXT DEFAULT '',
                    owner TEXT NOT NULL DEFAULT '',
                    steps TEXT DEFAULT '',
                    step_details TEXT DEFAULT '',
                    frequency TEXT DEFAULT '',
                    duration_minutes INTEGER DEFAULT 0,
                    priority INTEGER DEFAULT 3,
                    tools TEXT DEFAULT '',
                    risks TEXT DEFAULT '',
                    automation_readiness INTEGER DEFAULT 3,
                    improvements TEXT DEFAULT '',
                    trigger_type TEXT NOT NULL DEFAULT 'manuálny proces',
                    success_criteria TEXT DEFAULT 'dokončenie úloh',
                    common_problems TEXT DEFAULT 'žiadne známe problémy',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS departments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    manager TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    department_id INTEGER,
                    description TEXT DEFAULT '',
                    responsibilities TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (department_id) REFERENCES departments(id)
                );
            ''')
            
            # Vlož ukážkové dáta
            sample_processes = [
                {
                    'name': 'Spracovanie objednávok zákazníkov',
                    'category': 'obchod',
                    'description': 'Kompletný proces spracovania objednávky od príjmu až po expedíciu.',
                    'owner': 'Mária Novák - Obchodný manažér',
                    'steps': '1. Príjem objednávky\n2. Overenie dostupnosti\n3. Konfirmácia zákazníkovi\n4. Spracovanie platby\n5. Expedícia',
                    'step_details': '1. Príjem objednávky: E-mail alebo telefón od zákazníka\n2. Overenie dostupnosti: Kontrola skladu\n3. Konfirmácia zákazníkovi: Potvrdenie objednávky\n4. Spracovanie platby: Faktúra a platba\n5. Expedícia: Balenie a odoslanie',
                    'frequency': 'denne',
                    'duration_minutes': 45,
                    'priority': 5,
                    'tools': 'CRM systém, Email, Telefón',
                    'risks': 'Chyby v objednávke, nedostupnosť tovaru',
                    'automation_readiness': 4,
                    'improvements': 'Automatické potvrdenia, Online katalóg, Platobný gateway',
                    'trigger_type': 'Prijatie objednávky emailom alebo cez web',
                    'success_criteria': 'Objednávka spracovaná do 24 hodín, zákazník informovaný',
                    'common_problems': 'Neúplné údaje, nedostupnosť tovaru, chyby v cenníku'
                },
                {
                    'name': 'Schvaľovanie dovoleniek',
                    'category': 'HR',
                    'description': 'Proces schvaľovania žiadostí o dovolenku zamestnancov.',
                    'owner': 'Peter Kováč - HR manažér',
                    'steps': '1. Podanie žiadosti\n2. Kontrola nárokov\n3. Schválenie manažérom\n4. Zápis do systému\n5. Potvrdenie zamestnancovi',
                    'step_details': '1. Podanie žiadosti: Zamestnanec podá žiadosť\n2. Kontrola nárokov: Overenie dostupných dní\n3. Schválenie manažérom: Súhlas priameho nadriadeného\n4. Zápis do systému: Aktualizácia HR systému\n5. Potvrdenie zamestnancovi: Email s potvrdením',
                    'frequency': 'týždenne',
                    'duration_minutes': 15,
                    'priority': 3,
                    'tools': 'HR systém, Email',
                    'risks': 'Prekrývanie dovoleniek, nedostatočné informácie',
                    'automation_readiness': 5,
                    'improvements': 'Online formulár, Automatické schvaľovanie, Kalendárna integrácia',
                    'trigger_type': 'Žiadosť o dovolenku v HR systéme',
                    'success_criteria': 'Dovolenka schválená/zamietnutá do 3 pracovných dní',
                    'common_problems': 'Prekrývanie dovoleniek v tíme, nedostatočné informácie'
                },
                {
                    'name': 'Fakturácia dodávateľom',
                    'category': 'administratíva',
                    'description': 'Spracovanie a úhrada faktúr od dodávateľov.',
                    'owner': 'Anna Krásna - Účtovníčka',
                    'steps': '1. Príjem faktúry\n2. Kontrola údajov\n3. Schválenie platby\n4. Zadanie do systému\n5. Úhrada',
                    'step_details': '1. Príjem faktúry: Email alebo pošta\n2. Kontrola údajov: Overenie správnosti\n3. Schválenie platby: Podpis zodpovednej osoby\n4. Zadanie do systému: Účtovný zápis\n5. Úhrada: Bankový prevod',
                    'frequency': 'denne',
                    'duration_minutes': 20,
                    'priority': 4,
                    'tools': 'Účtovný systém, Email, Internetbanking',
                    'risks': 'Duplicitné faktúry, chyby v údajoch, omeškanie platby',
                    'automation_readiness': 3,
                    'improvements': 'OCR rozpoznávanie, Automatické párovanie, Workflow schvaľovania',
                    'trigger_type': 'Prijatie faktúry od dodávateľa',
                    'success_criteria': 'Faktúra spracovaná a uhradená do splatnosti',
                    'common_problems': 'Chýbajúce prílohy, nesprávne údaje, duplicitné faktúry'
                }
            ]
            
            for process in sample_processes:
                conn.execute('''
                    INSERT INTO processes (name, category, description, owner, steps, step_details,
                                         frequency, duration_minutes, priority, tools, risks, 
                                         automation_readiness, improvements, trigger_type, 
                                         success_criteria, common_problems)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    process['name'], process['category'], process['description'], 
                    process['owner'], process['steps'], process['step_details'],
                    process['frequency'], process['duration_minutes'], process['priority'],
                    process['tools'], process['risks'], process['automation_readiness'],
                    process['improvements'], process['trigger_type'], 
                    process['success_criteria'], process['common_problems']
                ))
            
            # Ukážkové oddelenia
            sample_departments = [
                {'name': 'Obchod', 'description': 'Obchodný tím a predaj', 'manager': 'Mária Novák'},
                {'name': 'HR', 'description': 'Ľudské zdroje', 'manager': 'Peter Kováč'},
                {'name': 'Administratíva', 'description': 'Účtovníctvo a správa', 'manager': 'Anna Krásna'},
                {'name': 'Výroba', 'description': 'Výrobné procesy', 'manager': 'Ján Kováč'}
            ]
            
            for dept in sample_departments:
                conn.execute('''
                    INSERT INTO departments (name, description, manager)
                    VALUES (?, ?, ?)
                ''', (dept['name'], dept['description'], dept['manager']))
                
    except Exception as e:
        st.error(f"⚠️ Chyba inicializácie databázy: {e}")

def main():
    """Hlavná funkcia aplikácie"""
    init_streamlit_config()
    
    # Inicializácia databázy (predovšetkým pre Streamlit Cloud)
    initialize_database()
    
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
    
    # Business management módy
    elif st.session_state.mode == "process_management":
        render_process_management()
    elif st.session_state.mode == "departments":
        render_departments()
    elif st.session_state.mode == "positions":
        render_positions()
    elif st.session_state.mode == "company_settings":
        render_company_settings()
    elif st.session_state.mode == "edit_process":
        render_edit_process()
    elif st.session_state.mode == "edit_department":
        render_edit_department()
    elif st.session_state.mode == "edit_position":
        render_edit_position()
    elif st.session_state.mode == "database_management":
        render_database_management()
    elif st.session_state.mode == "database_schema":
        render_database_schema()

if __name__ == "__main__":
    main() 