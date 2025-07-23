#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Intelligent Agents Launcher
Hlavný spúšťač pre oba inteligentné agenty
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

# Import našich agentov
from adsun_process_mapper_ai import ADSUNProcessMapperAI
from adsun_knowledge_assistant import ADSUNKnowledgeAssistant

class ADSUNAgentLauncher:
    """Hlavný launcher pre ADSUN agentov"""
    
    def __init__(self):
        self.db_path = "adsun_processes.db"
        self.setup_database()
    
    def setup_database(self):
        """Nastaví databázu a vytvorí ukážkové dáta"""
        if not os.path.exists(self.db_path):
            print("🔧 Inicializujem databázu...")
            self._create_database()
            self._insert_sample_data()
            print("✅ Databáza vytvorená s ukážkovými dátami!")
    
    def _create_database(self):
        """Vytvorí databázu zo schémy"""
        with sqlite3.connect(self.db_path) as conn:
            if os.path.exists('database_schema.sql'):
                with open('database_schema.sql', 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
            else:
                # Základná schéma ak súbor neexistuje
                conn.executescript('''
                    CREATE TABLE processes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(255) NOT NULL,
                        category VARCHAR(100) NOT NULL,
                        trigger_type VARCHAR(255) NOT NULL,
                        owner VARCHAR(255) NOT NULL,
                        frequency VARCHAR(100) NOT NULL,
                        duration_minutes INTEGER,
                        priority VARCHAR(20) NOT NULL,
                        volume_per_period INTEGER,
                        success_criteria TEXT,
                        common_problems TEXT,
                        automation_readiness INTEGER,
                        tags TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    );
                    
                    CREATE TABLE process_steps (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        process_id INTEGER NOT NULL,
                        step_number INTEGER NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        responsible_person VARCHAR(255) NOT NULL,
                        system_tool VARCHAR(255),
                        input_data TEXT,
                        action_details TEXT NOT NULL,
                        output_data TEXT,
                        decision_logic TEXT,
                        estimated_time_minutes INTEGER,
                        is_automated BOOLEAN DEFAULT 0,
                        automation_potential INTEGER,
                        FOREIGN KEY (process_id) REFERENCES processes(id)
                    );
                ''')
    
    def _insert_sample_data(self):
        """Vloží ukážkové dáta pre testovanie"""
        sample_processes = [
            {
                'name': 'Spracovanie objednávok zákazníkov',
                'category': 'obchod',
                'trigger_type': 'Prijatie objednávky emailom alebo cez web',
                'owner': 'Mária Novák - Obchodný manažér',
                'frequency': 'denne',
                'duration_minutes': 45,
                'priority': 'vysoká',
                'volume_per_period': 25,
                'success_criteria': 'Objednávka spracovaná do 24 hodín, zákazník informovaný o stave',
                'common_problems': 'Neúplné údaje v objednávke, nedostupnosť tovaru, chyby v cenníku',
                'automation_readiness': 3,
                'tags': '["objednávky", "zákazník", "predaj", "email"]'
            },
            {
                'name': 'Schvaľovanie dovoleniek',
                'category': 'HR',
                'trigger_type': 'Žiadosť o dovolenku v HR systéme',
                'owner': 'Peter Kováč - HR manažér',
                'frequency': 'týždenne',
                'duration_minutes': 15,
                'priority': 'stredná',
                'volume_per_period': 8,
                'success_criteria': 'Dovolenka schválená/zamietnutá do 3 pracovných dní',
                'common_problems': 'Prekrývanie dovoleniek v tíme, nedostatočné informácie',
                'automation_readiness': 4,
                'tags': '["dovolenka", "schvaľovanie", "HR", "zamestnanci"]'
            },
            {
                'name': 'Fakturácia dodávateľom',
                'category': 'administratíva',
                'trigger_type': 'Prijatie faktúry od dodávateľa',
                'owner': 'Anna Krásna - Účtovníčka',
                'frequency': 'denne',
                'duration_minutes': 20,
                'priority': 'vysoká',
                'volume_per_period': 15,
                'success_criteria': 'Faktúra spracovaná a uhradená do splatnosti',
                'common_problems': 'Chýbajúce prílohy, nesprávne údaje, duplicitné faktúry',
                'automation_readiness': 2,
                'tags': '["faktúra", "účtovníctvo", "platby", "dodávateľ"]'
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            for process in sample_processes:
                cursor = conn.execute('''
                    INSERT INTO processes (name, category, trigger_type, owner, frequency, 
                                         duration_minutes, priority, volume_per_period, 
                                         success_criteria, common_problems, automation_readiness, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    process['name'], process['category'], process['trigger_type'],
                    process['owner'], process['frequency'], process['duration_minutes'],
                    process['priority'], process['volume_per_period'], 
                    process['success_criteria'], process['common_problems'],
                    process['automation_readiness'], process['tags']
                ))
                
                process_id = cursor.lastrowid
                
                # Pridaj ukážkové kroky pre prvý proces
                if process['name'] == 'Spracovanie objednávok zákazníkov':
                    steps = [
                        {
                            'step_number': 1,
                            'title': 'Prijatie objednávky',
                            'description': 'Kontrola a registrácia novej objednávky',
                            'responsible_person': 'Obchodný zástupca',
                            'system_tool': 'CRM systém',
                            'action_details': 'Skontrolovať úplnosť objednávky a zadať do systému',
                            'estimated_time_minutes': 10
                        },
                        {
                            'step_number': 2,
                            'title': 'Kontrola dostupnosti',
                            'description': 'Overenie dostupnosti tovaru na sklade',
                            'responsible_person': 'Skladník',
                            'system_tool': 'Skladový systém',
                            'action_details': 'Skontrolovať stav zásob a rezervovať tovar',
                            'estimated_time_minutes': 15
                        },
                        {
                            'step_number': 3,
                            'title': 'Potvrdenie objednávky',
                            'description': 'Odoslanie potvrdenia zákazníkovi',
                            'responsible_person': 'Obchodný zástupca',
                            'system_tool': 'Email + CRM',
                            'action_details': 'Vygenerovať a odoslať potvrdenie s termínom dodania',
                            'estimated_time_minutes': 5
                        }
                    ]
                    
                    for step in steps:
                        conn.execute('''
                            INSERT INTO process_steps (process_id, step_number, title, description,
                                                     responsible_person, system_tool, action_details,
                                                     estimated_time_minutes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            process_id, step['step_number'], step['title'], step['description'],
                            step['responsible_person'], step['system_tool'], 
                            step['action_details'], step['estimated_time_minutes']
                        ))
    
    def show_main_menu(self):
        """Zobrazí hlavné menu"""
        print("\n" + "="*60)
        print("🎯 ADSUN Intelligent Process Management System")
        print("="*60)
        print("\n🤖 Dostupné AI agenti:")
        print("\n1️⃣  Process Mapper AI - Dokumentovanie nových procesov")
        print("    • Inteligentné rozhovory s AI reasoning")
        print("    • Automatická analýza odpovědí")
        print("    • Identifikácia medzier a optimalizácií")
        print("\n2️⃣  Knowledge Assistant AI - Poskytovanie informácií")
        print("    • Inteligentné odpovede na otázky")
        print("    • Detekcia intentu a kontextová analýza")
        print("    • Návrhy optimalizácií a riešení")
        print("\n3️⃣  Zobrazenie dostupných procesov")
        print("4️⃣  Správa databázy")
        print("0️⃣  Ukončiť")
        print("\n" + "-"*60)
    
    def launch_process_mapper(self):
        """Spustí Process Mapper AI"""
        print("\n🚀 Spúšťam ADSUN Process Mapper AI...")
        print("-" * 50)
        
        mapper = ADSUNProcessMapperAI(self.db_path)
        
        print("👋 Vitajte v inteligentnom mapovači procesov!")
        documenter = input("📝 Zadajte vaše meno: ")
        
        print(mapper.start_documentation_session(documenter))
        
        while True:
            user_input = input("\n👤 Vaša odpoveď: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'koniec', 'ukončiť', 'späť']:
                print("🔚 Process Mapper ukončený.")
                break
            
            if not user_input:
                continue
                
            response = mapper.process_response(user_input)
            print(f"\n🤖 {response}")
            
            # Kontrola ukončenia
            if "Chcete pokračovať s dokumentovaním ďalšieho procesu?" in response:
                continue_choice = input("\n▶️ Pokračovať? (áno/nie): ").strip().lower()
                if continue_choice in ['nie', 'n', 'no']:
                    print("🔚 Ďakujem za dokumentovanie procesov!")
                    break
    
    def launch_knowledge_assistant(self):
        """Spustí Knowledge Assistant AI"""
        print("\n🚀 Spúšťam ADSUN Knowledge Assistant AI...")
        print("-" * 50)
        
        assistant = ADSUNKnowledgeAssistant(self.db_path)
        
        print("🎓 Vitajte v inteligentnom asistentovi znalostí!")
        print("💡 Spýtajte sa na čokoľvek o procesoch v ADSUN")
        print("📋 Napíšte 'procesy' pre zoznam dostupných procesov")
        print("🔙 Napíšte 'späť' pre návrat do hlavného menu\n")
        
        while True:
            user_query = input("❓ Vaša otázka: ").strip()
            
            if user_query.lower() in ['späť', 'back', 'exit', 'quit']:
                print("🔚 Knowledge Assistant ukončený.")
                break
            
            if not user_query:
                continue
            
            if user_query.lower() in ['procesy', 'zoznam', 'list']:
                response = assistant.get_available_processes()
            else:
                response = assistant.answer_query(user_query)
            
            print(f"\n🤖 {response}\n")
            print("-" * 50)
    
    def show_processes(self):
        """Zobrazí všetky dostupné procesy"""
        assistant = ADSUNKnowledgeAssistant(self.db_path)
        print("\n📊 Prehľad dostupných procesov:")
        print("=" * 50)
        print(assistant.get_available_processes())
        
        input("\n⏎ Stlačte Enter pre pokračovanie...")
    
    def database_management(self):
        """Správa databázy"""
        print("\n🔧 Správa databázy:")
        print("-" * 30)
        print("1. Vymazať všetky dáta")
        print("2. Obnoviť ukážkové dáta")
        print("3. Zobraziť štatistiky")
        print("0. Späť")
        
        choice = input("\nVyberte možnosť: ").strip()
        
        if choice == "1":
            confirm = input("⚠️ Naozaj chcete vymazať všetky dáta? (áno/nie): ")
            if confirm.lower() in ['áno', 'ano', 'yes', 'y']:
                self._clear_database()
                print("✅ Všetky dáta boli vymazané.")
        
        elif choice == "2":
            self._insert_sample_data()
            print("✅ Ukážkové dáta boli obnovené.")
        
        elif choice == "3":
            self._show_statistics()
        
        input("\n⏎ Stlačte Enter pre pokračovanie...")
    
    def _clear_database(self):
        """Vymaže všetky dáta z databázy"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM process_steps")
            conn.execute("DELETE FROM processes")
            conn.execute("DELETE FROM documentation_sessions")
    
    def _show_statistics(self):
        """Zobrazí štatistiky databázy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM processes WHERE is_active = 1")
            process_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM process_steps")
            steps_count = cursor.fetchone()[0]
            
            cursor = conn.execute("""
                SELECT category, COUNT(*) 
                FROM processes 
                WHERE is_active = 1 
                GROUP BY category
            """)
            categories = cursor.fetchall()
        
        print(f"\n📊 Štatistiky databázy:")
        print(f"• Aktívne procesy: {process_count}")
        print(f"• Celkový počet krokov: {steps_count}")
        print(f"• Kategórie procesov:")
        for category, count in categories:
            print(f"  - {category}: {count}")
    
    def run(self):
        """Hlavná slučka aplikácie"""
        while True:
            self.show_main_menu()
            choice = input("🎯 Vyberte možnosť (0-4): ").strip()
            
            if choice == "1":
                self.launch_process_mapper()
            elif choice == "2":
                self.launch_knowledge_assistant()
            elif choice == "3":
                self.show_processes()
            elif choice == "4":
                self.database_management()
            elif choice == "0":
                print("\n👋 Ďakujem za používanie ADSUN AI systému!")
                break
            else:
                print("❌ Neplatná voľba. Skúste znovu.")
                input("⏎ Stlačte Enter pre pokračovanie...")

if __name__ == "__main__":
    print("🚀 Inicializujem ADSUN Intelligent Process Management System...")
    
    try:
        launcher = ADSUNAgentLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n\n👋 Systém ukončený užívateľom. Dovidenia!")
    except Exception as e:
        print(f"\n❌ Chyba: {e}")
        print("🔧 Skontrolujte konfiguráciu a súbory systému.") 