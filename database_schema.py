#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Database Schema Management
Štandardizácia štruktúry databázy pre kompatibilitu s Airtable
"""

import streamlit as st
import sqlite3
from typing import Dict, List, Any
from datetime import datetime

# Štandardizovaná schéma databázy
DATABASE_SCHEMA = {
    'processes': {
        'airtable_name': 'Processes',
        'description': 'Firemné procesy a postupy',
        'columns': {
            'id': {'type': 'INTEGER', 'primary_key': True, 'airtable_type': 'auto_number'},
            'name': {'type': 'TEXT', 'required': True, 'airtable_type': 'single_line_text'},
            'category': {'type': 'TEXT', 'required': True, 'airtable_type': 'single_select'},
            'description': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'owner': {'type': 'TEXT', 'required': True, 'airtable_type': 'single_line_text'},
            'steps': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'frequency': {'type': 'TEXT', 'airtable_type': 'single_select'},
            'duration_minutes': {'type': 'INTEGER', 'airtable_type': 'number'},
            'priority': {'type': 'INTEGER', 'airtable_type': 'rating'},
            'automation_readiness': {'type': 'INTEGER', 'airtable_type': 'rating'},
            'tools': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'risks': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'improvements': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'is_active': {'type': 'BOOLEAN', 'default': True, 'airtable_type': 'checkbox'},
            'created_at': {'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP', 'airtable_type': 'created_time'},
            'updated_at': {'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP', 'airtable_type': 'last_modified_time'}
        }
    },
    
    'departments': {
        'airtable_name': 'Departments',
        'description': 'Firemné oddelenia a ich charakteristiky',
        'columns': {
            'id': {'type': 'INTEGER', 'primary_key': True, 'airtable_type': 'auto_number'},
            'name': {'type': 'TEXT', 'required': True, 'airtable_type': 'single_line_text'},
            'function': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'manager': {'type': 'TEXT', 'airtable_type': 'single_line_text'},
            'processes': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'staff_count': {'type': 'TEXT', 'airtable_type': 'single_line_text'},
            'competencies': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'collaboration': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'tools': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'challenges': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'success_metrics': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'created_at': {'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP', 'airtable_type': 'created_time'},
            'updated_at': {'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP', 'airtable_type': 'last_modified_time'}
        }
    },
    
    'positions': {
        'airtable_name': 'Positions',
        'description': 'Firemné pozície a ich popis',
        'columns': {
            'id': {'type': 'INTEGER', 'primary_key': True, 'airtable_type': 'auto_number'},
            'name': {'type': 'TEXT', 'required': True, 'airtable_type': 'single_line_text'},
            'description': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'department': {'type': 'TEXT', 'airtable_type': 'single_select'},
            'level': {'type': 'TEXT', 'airtable_type': 'single_select'},
            'responsibilities': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'requirements': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'tools_systems': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'work_time': {'type': 'TEXT', 'airtable_type': 'single_select'},
            'challenges': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'success_metrics': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'created_at': {'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP', 'airtable_type': 'created_time'},
            'updated_at': {'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP', 'airtable_type': 'last_modified_time'}
        }
    },
    
    'documentation_sessions': {
        'airtable_name': 'Documentation_Sessions',
        'description': 'Dokumentačné sessions a AI interakcie',
        'columns': {
            'id': {'type': 'INTEGER', 'primary_key': True, 'airtable_type': 'auto_number'},
            'process_id': {'type': 'INTEGER', 'airtable_type': 'link_to_record'},
            'documented_by': {'type': 'TEXT', 'required': True, 'airtable_type': 'single_line_text'},
            'session_notes': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'ai_analysis': {'type': 'TEXT', 'airtable_type': 'long_text'},
            'created_at': {'type': 'TIMESTAMP', 'default': 'CURRENT_TIMESTAMP', 'airtable_type': 'created_time'}
        }
    }
}

# Mapovanie typov medzi SQLite a Airtable
AIRTABLE_TYPE_MAPPING = {
    'single_line_text': 'Text (single line)',
    'long_text': 'Long text',
    'number': 'Number',
    'rating': 'Rating (1-10)',
    'single_select': 'Single select',
    'checkbox': 'Checkbox',
    'auto_number': 'Autonumber',
    'created_time': 'Created time',
    'last_modified_time': 'Last modified time',
    'link_to_record': 'Link to another record'
}

def render_database_schema():
    """Render správy databázovej schémy"""
    st.markdown("## 🏗️ Schéma databázy")
    st.markdown("*Štandardizovaná štruktúra pre kompatibilitu s Airtable*")
    
    # Tabs pre rôzne sekcie
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Prehľad schémy", "🔄 Migrácia", "📋 Airtable mapping", "🛠️ Úpravy"])
    
    with tab1:
        render_schema_overview()
    
    with tab2:
        render_migration_tools()
    
    with tab3:
        render_airtable_mapping()
    
    with tab4:
        render_schema_modifications()

def render_schema_overview():
    """Zobrazí prehľad schémy"""
    st.markdown("### 📊 Prehľad štandardizovanej schémy")
    
    for table_name, table_info in DATABASE_SCHEMA.items():
        with st.expander(f"📋 {table_info['airtable_name']} ({table_name})"):
            st.markdown(f"**Popis:** {table_info['description']}")
            
            # Vytvor DataFrame pre stĺpce
            columns_data = []
            for col_name, col_info in table_info['columns'].items():
                # Konvertuj boolean hodnoty na stringy pre Arrow kompatibilitu
                default_value = col_info.get('default', '-')
                if isinstance(default_value, bool):
                    default_value = "✅ Áno" if default_value else "❌ Nie"
                elif default_value is None:
                    default_value = "-"
                else:
                    default_value = str(default_value)
                
                columns_data.append({
                    'Stĺpec': col_name,
                    'SQLite typ': col_info['type'],
                    'Airtable typ': AIRTABLE_TYPE_MAPPING.get(col_info['airtable_type'], col_info['airtable_type']),
                    'Povinný': '✅' if col_info.get('required') else '❌',
                    'Primárny': '🔑' if col_info.get('primary_key') else '-',
                    'Default': str(default_value)  # Zabezpečí, že všetko je string
                })
            
            import pandas as pd
            df = pd.DataFrame(columns_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

def render_migration_tools():
    """Nástroje pre migráciu databázy"""
    st.markdown("### 🔄 Migrácia databázy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📥 Import z aktuálnej DB")
        if st.button("🔍 Analyzovať aktuálnu štruktúru"):
            analyze_current_structure()
        
        if st.button("⚡ Migrovať na novú schému"):
            migrate_to_new_schema()
    
    with col2:
        st.markdown("#### 📤 Export do Airtable")
        if st.button("📋 Generovať Airtable schému"):
            generate_airtable_schema()
        
        if st.button("🔗 Vytvoriť prepojenie"):
            create_airtable_connection()
    
    # Nová sekcia pre synchronizáciu
    st.markdown("---")
    st.markdown("### 🔄 Synchronizácia SQLite ↔ Airtable")
    
    api_key = st.session_state.get('airtable_api_key', '')
    base_id = st.session_state.get('airtable_base_id', '')
    
    if api_key and base_id:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📤 SQLite → Airtable"):
                sync_sqlite_to_airtable(api_key, base_id)
        
        with col2:
            if st.button("📥 Airtable → SQLite"):
                sync_airtable_to_sqlite(api_key, base_id)
        
        with col3:
            if st.button("🔄 Aktivovať Airtable režim"):
                activate_airtable_mode(api_key, base_id)
    else:
        st.info("💡 Nastavte Airtable API údaje pre synchronizáciu")

def analyze_current_structure():
    """Analyzuje aktuálnu štruktúru databázy"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            current_tables = [row[0] for row in cursor.fetchall()]
        
        st.markdown("#### 🔍 Aktuálne tabuľky v databáze:")
        
        for table in current_tables:
            try:
                with sqlite3.connect("adsun_processes.db") as conn:
                    cursor = conn.execute(f"PRAGMA table_info(`{table}`)")
                    columns = cursor.fetchall()
                
                with st.expander(f"📋 {table}"):
                    st.write(f"**Počet stĺpcov:** {len(columns)}")
                    
                    # Porovnanie so štandardnou schémou
                    if table in DATABASE_SCHEMA:
                        standard_cols = set(DATABASE_SCHEMA[table]['columns'].keys())
                        current_cols = set([col[1] for col in columns])
                        
                        missing = standard_cols - current_cols
                        extra = current_cols - standard_cols
                        
                        if missing:
                            st.warning(f"**Chýbajúce stĺpce:** {', '.join(missing)}")
                        if extra:
                            st.info(f"**Navyše stĺpce:** {', '.join(extra)}")
                        if not missing and not extra:
                            st.success("✅ Štruktúra je v súlade so štandardom")
                    else:
                        st.warning("⚠️ Tabuľka nie je v štandardnej schéme")
                        
            except Exception as e:
                st.error(f"❌ Chyba analýzy tabuľky {table}: {e}")
                
    except Exception as e:
        st.error(f"❌ Chyba pripojenia k databáze: {e}")

def migrate_to_new_schema():
    """Migruje databázu na novú schému"""
    st.markdown("#### ⚡ Migrácia na novú schému")
    
    with st.form("migration_form"):
        st.warning("⚠️ Táto operácia upraví štruktúru databázy. Odporúčame zálohu!")
        
        tables_to_migrate = st.multiselect(
            "Vyberte tabuľky na migráciu:",
            list(DATABASE_SCHEMA.keys()),
            default=list(DATABASE_SCHEMA.keys())
        )
        
        backup_before = st.checkbox("Vytvoriť zálohu pred migráciou", value=True)
        
        if st.form_submit_button("🚀 Spustiť migráciu", type="primary"):
            if backup_before:
                create_database_backup()
            
            for table_name in tables_to_migrate:
                migrate_table(table_name)
            
            st.success("✅ Migrácia dokončená!")

def migrate_table(table_name: str):
    """Migruje konkrétnu tabuľku"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            schema = DATABASE_SCHEMA[table_name]
            
            # Vytvor SQL pre novú tabuľku
            create_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}_new` ("
            column_definitions = []
            
            for col_name, col_info in schema['columns'].items():
                col_def = f"`{col_name}` {col_info['type']}"
                
                if col_info.get('primary_key'):
                    col_def += " PRIMARY KEY AUTOINCREMENT"
                elif col_info.get('required'):
                    col_def += " NOT NULL"
                
                if col_info.get('default'):
                    if col_info['default'] == 'CURRENT_TIMESTAMP':
                        col_def += " DEFAULT CURRENT_TIMESTAMP"
                    elif isinstance(col_info['default'], bool):
                        col_def += f" DEFAULT {1 if col_info['default'] else 0}"
                    else:
                        col_def += f" DEFAULT '{col_info['default']}'"
                
                column_definitions.append(col_def)
            
            create_sql += ", ".join(column_definitions) + ")"
            
            # Vytvor novú tabuľku
            conn.execute(create_sql)
            
            # Skús kopírovať dáta z pôvodnej tabuľky ak existuje
            try:
                cursor = conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if cursor.fetchone():
                    # Získaj spoločné stĺpce
                    cursor = conn.execute(f"PRAGMA table_info(`{table_name}`)")
                    old_columns = [row[1] for row in cursor.fetchall()]
                    new_columns = list(schema['columns'].keys())
                    common_columns = [col for col in old_columns if col in new_columns]
                    
                    if common_columns:
                        columns_str = ", ".join([f"`{col}`" for col in common_columns])
                        conn.execute(f"""
                            INSERT INTO `{table_name}_new` ({columns_str})
                            SELECT {columns_str} FROM `{table_name}`
                        """)
                    
                    # Premenuj tabuľky
                    conn.execute(f"DROP TABLE `{table_name}`")
                    conn.execute(f"ALTER TABLE `{table_name}_new` RENAME TO `{table_name}`")
                else:
                    conn.execute(f"ALTER TABLE `{table_name}_new` RENAME TO `{table_name}`")
                    
            except Exception as e:
                st.warning(f"⚠️ Nemožno kopírovať dáta pre {table_name}: {e}")
                conn.execute(f"ALTER TABLE `{table_name}_new` RENAME TO `{table_name}`")
            
            conn.commit()
            st.success(f"✅ Tabuľka {table_name} migrovaná")
            
    except Exception as e:
        st.error(f"❌ Chyba migrácie {table_name}: {e}")

def create_database_backup():
    """Vytvorí zálohu databázy"""
    try:
        import shutil
        backup_name = f"adsun_processes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2("adsun_processes.db", backup_name)
        st.success(f"✅ Záloha vytvorená: {backup_name}")
    except Exception as e:
        st.error(f"❌ Chyba zálohy: {e}")

def render_airtable_mapping():
    """Zobrazí mapování pre Airtable"""
    st.markdown("### 📋 Mapovanie pre Airtable")
    
    st.markdown("#### 🔗 Odporúčaná štruktúra Airtable Base:")
    
    for table_name, table_info in DATABASE_SCHEMA.items():
        with st.expander(f"📊 {table_info['airtable_name']}"):
            st.markdown(f"**Popis:** {table_info['description']}")
            
            # Airtable polia
            st.markdown("**Polia v Airtable:**")
            for col_name, col_info in table_info['columns'].items():
                airtable_type = AIRTABLE_TYPE_MAPPING.get(col_info['airtable_type'], col_info['airtable_type'])
                st.write(f"• **{col_name}**: {airtable_type}")

def generate_airtable_schema():
    """Generuje schému pre Airtable"""
    st.markdown("#### 📋 Airtable schéma (JSON)")
    
    airtable_schema = {}
    for table_name, table_info in DATABASE_SCHEMA.items():
        airtable_schema[table_info['airtable_name']] = {
            'description': table_info['description'],
            'fields': {}
        }
        
        for col_name, col_info in table_info['columns'].items():
            airtable_schema[table_info['airtable_name']]['fields'][col_name] = {
                'type': col_info['airtable_type'],
                'description': AIRTABLE_TYPE_MAPPING.get(col_info['airtable_type'], ''),
                'required': col_info.get('required', False)
            }
    
    import json
    schema_json = json.dumps(airtable_schema, indent=2, ensure_ascii=False)
    
    st.code(schema_json, language='json')
    
    st.download_button(
        label="📥 Stiahnuť schému",
        data=schema_json,
        file_name=f"airtable_schema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime='application/json'
    )

def create_airtable_connection():
    """Vytvorí prepojenie s Airtable"""
    st.markdown("#### 🔗 Prepojenie s Airtable")
    
    # Načítaj API údaje zo session state
    api_key = st.session_state.get('airtable_api_key', '')
    base_id = st.session_state.get('airtable_base_id', '')
    
    if not api_key or not base_id:
        st.warning("⚠️ Prosím nastavte Airtable API kľúč a Base ID v bočnom paneli")
        
        # Rýchla pomoc pre nastavenie
        with st.expander("❓ Ako získať API údaje"):
            st.markdown("""
            **1. API kľúč:**
            - Idite na: https://airtable.com/create/tokens
            - Vytvorte nový token s oprávneniami: `data.records:read`, `data.records:write`, `schema.bases:read`
            - Skopírujte token
            
            **2. Base ID:**
            - Otvorte vašu Airtable base v prehliadači
            - Z URL skopírujte časť začínajúcu 'app' (napr. appXXXXXXXXXXXXXX)
            
            **3. Nastavte v aplikácii:**
            - Bočný panel → Databáza → Airtable (cloud)
            - Vložte API kľúč a Base ID
            """)
        return
    
    st.info(f"🔑 **API Key:** ...{api_key[-6:] if len(api_key) > 6 else '***'}")
    st.info(f"🏢 **Base ID:** {base_id}")
    
    # Rýchky status check
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("⚡ Rýchly test", help="Základný test pripojenia", key="quick_test_btn"):
                st.session_state.run_quick_test = True
                st.session_state.show_detailed_diagnostic = False
        
        with col2:
            if st.button("🔧 Detailná diagnostika", help="Kompletná diagnostika s riešeniami", key="detailed_diag_btn"):
                st.session_state.show_detailed_diagnostic = True
                st.session_state.run_quick_test = False
    
    # Jednoduchý test tlačidla
    if st.button("🧪 Test tlačidla", key="simple_test_btn"):
        st.success("✅ Tlačidlo funguje!")
        st.write(f"API Key: {api_key[:10]}...")
        st.write(f"Base ID: {base_id}")
    
    # Spusti rýchly test ak je požadovaný
    if st.session_state.get('run_quick_test', False):
        st.markdown("### ⚡ Rýchly test výsledky")
        try:
            quick_airtable_test(api_key, base_id)
        except Exception as e:
            st.error(f"❌ Chyba rýchleho testu: {e}")
            st.code(str(e))
        
        if st.button("🔄 Spustiť znovu", key="rerun_quick_btn"):
            st.session_state.run_quick_test = True
            st.rerun()
        
        if st.button("🔙 Skryť výsledky", key="hide_quick_btn"):
            st.session_state.run_quick_test = False
            st.rerun()
    
    # Zobraz detailnú diagnostiku ak je požadovaná
    if st.session_state.get('show_detailed_diagnostic', False):
        st.markdown("### 🔧 Detailná diagnostika")
        try:
            test_airtable_connection(api_key, base_id)
        except Exception as e:
            st.error(f"❌ Chyba detailnej diagnostiky: {e}")
            st.code(str(e))
        
        if st.button("🔙 Skryť diagnostiku", key="hide_diag_btn"):
            st.session_state.show_detailed_diagnostic = False
            st.rerun()
    
    # Test tlačidlá
    st.markdown("---")
    st.markdown("#### 🧪 Testovací panel")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Test pripojenia"):
            test_airtable_connection(api_key, base_id)
    
    with col2:
        if st.button("📊 Test čítania"):
            test_airtable_read(api_key, base_id)
    
    with col3:
        if st.button("💾 Test zápisu"):
            test_airtable_write(api_key, base_id)
    
    # Návod na setup
    with st.expander("📋 Návod na nastavenie Airtable"):
        st.markdown("""
        **Kroky pre prepojenie:**
        1. **Vytvorte Airtable Base** s nasledujúcimi tabuľkami:
           - `Processes` - hlavné procesy
           - `Departments` - oddelenia  
           - `Positions` - pozície
           - `Documentation_Sessions` - AI sessions
        
        2. **Vytvorte polia podľa schémy** (viď tab "Airtable mapping")
        
        3. **Získajte API údaje:**
           - API kľúč: https://airtable.com/create/tokens
           - Base ID: z URL vašej Base (appXXXXXX)
        
        4. **Nastavte v aplikácii** (bočný panel)
        
        5. **Otestujte pripojenie** tlačidlami vyššie
        """)
    
    # Troubleshooting sekcia
    with st.expander("🔧 Riešenie problémov"):
        st.markdown("""
        ### 🚨 Najčastejšie problémy a riešenia:
        
        **❌ "Neautorizovaný prístup"**
        - Skontrolujte API kľúč na https://airtable.com/create/tokens
        - Overte že token nie je expirovaný
        - Vytvorte nový token ak potrebné
        
        **❌ "Nedostatočné oprávnenia"** 
        - API token musí mať tieto oprávnenia:
          - `data.records:read` - čítanie záznamov
          - `data.records:write` - zápis záznamov  
          - `schema.bases:read` - čítanie štruktúry
        
        **❌ "Base nenájdená"**
        - Base ID musí začínať 'app' a mať 17 znakov
        - Skopírujte z URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
        - Overte že máte prístup k tejto base
        
        **❌ "Chýbajúce tabuľky"**
        - V Airtable base vytvorte tieto tabuľky:
          - `Processes` (povinná)
          - `Departments` 
          - `Positions`
          - `Documentation_Sessions`
        
        **❌ "Timeout/Pripojenie"**
        - Skontrolujte internetové pripojenie
        - Skúste znovu o chvíľu (možný dočasný problém)
        - Overte firewall nastavenia
        
        **💡 Tip:** Použite "⚡ Rýchly test" pre rýchlu diagnostiku
        """)
    
    # Status indikátor
    if st.session_state.get('airtable_connection_status'):
        status = st.session_state.airtable_connection_status
        if status == 'success':
            st.success("🟢 Airtable pripojenie aktívne")
        elif status == 'warning':
            st.warning("🟡 Airtable pripojenie s obmedzeniami")
        elif status == 'error':
            st.error("🔴 Airtable pripojenie neaktívne")

def test_airtable_connection(api_key: str, base_id: str):
    """Testuje základné pripojenie k Airtable"""
    try:
        from airtable_connector import AirtableConnector
        
        with st.spinner("🔍 Testujem pripojenie..."):
            
            # Detailná diagnostika
            st.markdown("### 🔍 Detailná diagnostika")
            
            # 1. Validácia API údajov
            st.write("**1. Validácia API údajov:**")
            if len(api_key) < 10:
                st.error("❌ API kľúč je príliš krátky")
                return
            else:
                st.success(f"✅ API kľúč: {len(api_key)} znakov")
            
            if not base_id.startswith('app') or len(base_id) != 17:
                st.error("❌ Base ID má nesprávny formát (očakáva sa appXXXXXXXXXXXXXX)")
                return
            else:
                st.success(f"✅ Base ID: {base_id}")
            
            # 2. Test základného API pripojenia
            st.write("**2. Test základného pripojenia:**")
            try:
                import requests
                
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                # Test s jednoduchým API volaním
                response = requests.get(
                    f"https://api.airtable.com/v0/meta/bases/{base_id}",
                    headers=headers,
                    timeout=15
                )
                
                st.write(f"Status kód: {response.status_code}")
                
                if response.status_code == 200:
                    st.success("✅ Základné pripojenie úspešné!")
                    
                    # Zobraz informácie o base
                    base_data = response.json()
                    st.info(f"📊 Base: {base_data.get('name', 'Bez názvu')}")
                    
                elif response.status_code == 401:
                    st.error("❌ Neautorizovaný prístup - nesprávny API kľúč")
                    st.write("**Riešenie:** Overte API kľúč na https://airtable.com/create/tokens")
                    return
                elif response.status_code == 403:
                    st.error("❌ Zakázaný prístup - nedostatočné oprávnenia")
                    st.write("**Riešenie:** API kľúč musí mať oprávnenia 'data.records:read' a 'schema.bases:read'")
                    return
                elif response.status_code == 404:
                    st.error("❌ Base nenájdená - nesprávny Base ID")
                    st.write("**Riešenie:** Skontrolujte Base ID v URL vašej Airtable base")
                    return
                else:
                    st.error(f"❌ Neočakávaný status kód: {response.status_code}")
                    if response.text:
                        st.code(response.text)
                    return
                    
            except requests.exceptions.Timeout:
                st.error("❌ Timeout - pripojenie trvá príliš dlho")
                st.write("**Riešenie:** Skontrolujte internetové pripojenie")
                return
            except requests.exceptions.ConnectionError:
                st.error("❌ Chyba pripojenia - nemožno sa spojiť s Airtable")
                st.write("**Riešenie:** Skontrolujte internetové pripojenie a firewall")
                return
            except Exception as e:
                st.error(f"❌ Neočakávaná chyba: {e}")
                return
            
            # 3. Test AirtableConnector triedy
            st.write("**3. Test AirtableConnector:**")
            connector = AirtableConnector(api_key, base_id)
            
            if connector.test_connection():
                st.success("✅ AirtableConnector pripojenie úspešné!")
                
                # 4. Test získania tabuliek
                st.write("**4. Test získania tabuliek:**")
                try:
                    response = requests.get(
                        f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        tables_data = response.json()
                        tables = tables_data.get('tables', [])
                        
                        st.success(f"✅ Nájdených {len(tables)} tabuliek v base:")
                        for table in tables[:5]:  # Zobraz prvých 5
                            st.write(f"• **{table['name']}** ({len(table.get('fields', []))} polí)")
                        
                        # Kontrola očakávaných tabuliek
                        table_names = [t['name'] for t in tables]
                        expected_tables = ['Processes', 'Departments', 'Positions', 'Documentation_Sessions']
                        missing_tables = [t for t in expected_tables if t not in table_names]
                        
                        if missing_tables:
                            st.warning(f"⚠️ Chýbajúce tabuľky: {', '.join(missing_tables)}")
                            st.info("💡 Vytvorte chýbajúce tabuľky v Airtable podľa schémy")
                            
                            # Ukáž ako vytvoriť tabuľky
                            with st.expander("📋 Ako vytvoriť chýbajúce tabuľky"):
                                st.markdown("""
                                **V Airtable base vytvorte tieto tabuľky:**
                                
                                **Processes:**
                                - Process Name (Single line text)
                                - Category (Single select: obchod, HR, administratíva, IT, výroba)
                                - Owner (Single line text)
                                - Frequency (Single select: denne, týždenne, mesačne, občas)
                                - Duration (min) (Number)
                                
                                **Departments, Positions, Documentation_Sessions:**
                                - Vytvorte prázdne tabuľky s týmito názvami
                                - Polia sa pridajú automaticky pri prvom zápise
                                """)
                        else:
                            st.success("✅ Všetky očakávané tabuľky nájdené!")
                            
                        # 5. Test čítania dát
                        st.write("**5. Test čítania dát z tabuľky Processes:**")
                        if 'Processes' in table_names:
                            try:
                                processes = connector.get_processes(limit=1)
                                if processes:
                                    st.success(f"✅ Načítaný {len(processes)} proces")
                                else:
                                    st.info("📭 Tabuľka Processes je prázdna (OK)")
                            except Exception as e:
                                st.warning(f"⚠️ Chyba čítania procesov: {e}")
                        else:
                            st.warning("⚠️ Tabuľka Processes neexistuje")
                            
                    else:
                        st.error(f"❌ Nemožno načítať tabuľky (status: {response.status_code})")
                        
                except Exception as e:
                    st.error(f"❌ Chyba načítavania tabuliek: {e}")
                    
            else:
                st.error("❌ AirtableConnector test neúspešný")
                
    except ImportError:
        st.error("❌ Modul airtable_connector nenájdený")
    except Exception as e:
        st.error(f"❌ Neočakávaná chyba diagnostiky: {e}")
        st.code(str(e))

def test_airtable_read(api_key: str, base_id: str):
    """Testuje čítanie dát z Airtable"""
    try:
        from airtable_connector import AirtableConnector
        
        with st.spinner("📊 Testujem čítanie dát..."):
            connector = AirtableConnector(api_key, base_id)
            
            # Test čítania procesov
            processes = connector.get_processes(limit=5)
            
            if processes:
                st.success(f"✅ Načítaných {len(processes)} procesov z Airtable!")
                
                # Zobraz prvé procesy
                for i, process in enumerate(processes[:3]):
                    with st.expander(f"📋 {process.get('name', 'Bez názvu')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**ID:** {process.get('id', 'N/A')}")
                            st.write(f"**Kategória:** {process.get('category', 'N/A')}")
                            st.write(f"**Vlastník:** {process.get('owner', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Frekvencia:** {process.get('frequency', 'N/A')}")
                            st.write(f"**Trvanie:** {process.get('duration_minutes', 0)} min")
                            st.write(f"**Automatizácia:** {process.get('automation_readiness', 0)}/5")
                
            else:
                st.warning("⚠️ Žiadne procesy nenájdené alebo tabuľka 'Processes' neexistuje")
                st.info("💡 Vytvorte tabuľku 'Processes' v Airtable s polami podľa schémy")
                
    except Exception as e:
        st.error(f"❌ Chyba čítania z Airtable: {e}")

def test_airtable_write(api_key: str, base_id: str):
    """Testuje zápis dát do Airtable"""
    try:
        from airtable_connector import AirtableConnector
        
        st.markdown("**⚠️ Test zápisu vytvorí testovací záznam v Airtable**")
        
        if st.button("✅ Pokračovať s testom zápisu", type="primary"):
            with st.spinner("💾 Testujem zápis dát..."):
                connector = AirtableConnector(api_key, base_id)
                
                # Vytvor testovací proces
                test_process = {
                    "name": f"🧪 Test proces {datetime.now().strftime('%H:%M:%S')}",
                    "category": "test",
                    "owner": "ADSUN Test",
                    "frequency": "test",
                    "duration_minutes": 5,
                    "priority": "nízka",
                    "automation_readiness": 1,
                    "success_criteria": "Test úspešný",
                    "common_problems": "Žiadne",
                    "mentioned_systems": ["ADSUN"]
                }
                
                # Pokús sa uložiť
                process_id = connector.save_process(test_process)
                
                if process_id:
                    st.success(f"✅ Test proces uložený! ID: {process_id}")
                    
                    # Test session uloženia
                    test_session = {
                        "documenter": "ADSUN Test",
                        "step": 1,
                        "question": "Test otázka?",
                        "response": "Test odpoveď",
                        "analysis": {"test": True},
                        "ai_powered": True,
                        "timestamp": datetime.now().isoformat(),
                        "completeness_score": 10
                    }
                    
                    session_id = connector.save_documentation_session(process_id, test_session)
                    
                    if session_id:
                        st.success(f"✅ Test session uložená! ID: {session_id}")
                        st.info("🧹 Môžete vymazať test záznamy z Airtable")
                    else:
                        st.warning("⚠️ Process uložený, ale session sa nepodarilo uložiť")
                        
                else:
                    st.error("❌ Nepodarilo sa uložiť test proces")
                    st.write("**Možné príčiny:**")
                    st.write("• Tabuľka 'Processes' neexistuje")
                    st.write("• Chýbajúce alebo nesprávne polia")
                    st.write("• Nedostatočné oprávnenia")
                    
    except Exception as e:
        st.error(f"❌ Chyba zápisu do Airtable: {e}")
        st.write("**Debug info:**")
        st.code(str(e))

def render_schema_modifications():
    """Nástroje na úpravu schémy"""
    st.markdown("### 🛠️ Úpravy schémy")
    
    st.markdown("#### ➕ Pridať nové pole")
    
    with st.form("add_field_form"):
        table_name = st.selectbox("Tabuľka:", list(DATABASE_SCHEMA.keys()))
        field_name = st.text_input("Názov poľa:")
        field_type = st.selectbox("SQLite typ:", ['TEXT', 'INTEGER', 'REAL', 'BOOLEAN', 'TIMESTAMP'])
        airtable_type = st.selectbox("Airtable typ:", list(AIRTABLE_TYPE_MAPPING.keys()))
        is_required = st.checkbox("Povinné pole")
        
        if st.form_submit_button("➕ Pridať pole"):
            add_custom_field(table_name, field_name, field_type, airtable_type, is_required)

def add_custom_field(table_name: str, field_name: str, field_type: str, airtable_type: str, is_required: bool):
    """Pridá vlastné pole do schémy"""
    try:
        # Pridaj do runtime schémy
        DATABASE_SCHEMA[table_name]['columns'][field_name] = {
            'type': field_type,
            'required': is_required,
            'airtable_type': airtable_type
        }
        
        # Pridaj do databázy
        with sqlite3.connect("adsun_processes.db") as conn:
            required_clause = "NOT NULL" if is_required else ""
            conn.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{field_name}` {field_type} {required_clause}")
            conn.commit()
        
        st.success(f"✅ Pole {field_name} pridané do {table_name}")
        
    except Exception as e:
        st.error(f"❌ Chyba pridávania poľa: {e}")

# Export schémy pre ďalšie použitie
def get_standardized_schema():
    """Vracia štandardizovanú schému"""
    return DATABASE_SCHEMA

def quick_airtable_test(api_key: str, base_id: str):
    """Rýchly test Airtable pripojenia"""
    
    st.write("🔍 **Test spustený!**")
    
    # Debug info
    st.write("🔍 **Debug info:**")
    st.write(f"API Key dĺžka: {len(api_key) if api_key else 0}")
    st.write(f"Base ID: {base_id}")
    
    if not api_key or not base_id:
        st.error("❌ Chýbajú API údaje!")
        return
    
    if len(api_key) < 10:
        st.error("❌ API kľúč je príliš krátky!")
        return
        
    if not base_id.startswith('app'):
        st.error("❌ Base ID musí začínať 'app'!")
        return
        
    try:
        st.write("📡 **Importujem requests modul...**")
        import requests
        st.success("✅ Requests modul načítaný")
        
        st.write("📡 **Pripravujem API volanie...**")
        headers = {"Authorization": f"Bearer {api_key}"}
        url = f"https://api.airtable.com/v0/meta/bases/{base_id}"
        
        st.write(f"🔗 URL: {url}")
        st.write("📡 **Volám Airtable API...**")
        
        # Test základného pripojenia
        response = requests.get(url, headers=headers, timeout=10)
        
        st.write(f"🔍 **Odpoveď prijatá. Status kód: {response.status_code}**")
        
        if response.status_code == 200:
            st.success("✅ Pripojenie úspešné!")
            try:
                base_data = response.json()
                st.info(f"📊 Base: {base_data.get('name', 'Bez názvu')}")
            except Exception as e:
                st.warning(f"⚠️ Nemožno parsovať JSON: {e}")
            
            # Test tabuliek
            st.write("📋 **Testujem tabuľky...**")
            try:
                tables_url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
                tables_response = requests.get(tables_url, headers=headers, timeout=10)
                
                if tables_response.status_code == 200:
                    tables_data = tables_response.json()
                    tables = tables_data.get('tables', [])
                    st.success(f"✅ Nájdených {len(tables)} tabuliek")
                    
                    # Zobraz názvy tabuliek
                    if tables:
                        st.write("**Existujúce tabuľky:**")
                        for table in tables[:5]:  # Max 5
                            st.write(f"• {table['name']}")
                    
                    # Kontrola očakávaných tabuliek
                    expected = ['Processes', 'Departments', 'Positions', 'Documentation_Sessions']
                    existing = [t['name'] for t in tables]
                    missing = [t for t in expected if t not in existing]
                    
                    if missing:
                        st.warning(f"⚠️ Chýbajúce tabuľky: {', '.join(missing)}")
                        st.info("💡 V Airtable vytvorte tieto tabuľky:")
                        for table in missing:
                            st.write(f"   • `{table}`")
                    else:
                        st.success("✅ Všetky potrebné tabuľky existujú!")
                        
                else:
                    st.error(f"❌ Chyba načítavania tabuliek: {tables_response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ Chyba testovania tabuliek: {e}")
                
        elif response.status_code == 401:
            st.error("❌ Neautorizovaný prístup - nesprávny API kľúč")
            st.info("💡 Skontrolujte API kľúč na: https://airtable.com/create/tokens")
        elif response.status_code == 403:
            st.error("❌ Nedostatočné oprávnenia")
            st.info("💡 API token musí mať oprávnenia: data.records:read, data.records:write, schema.bases:read")
        elif response.status_code == 404:
            st.error("❌ Base nenájdená")
            st.info("💡 Skontrolujte Base ID - musí začínať 'app' a mať 17 znakov")
        else:
            st.error(f"❌ Neočakávaný status kód: {response.status_code}")
            try:
                error_text = response.text[:300] if response.text else "Žiadna odpoveď"
                st.code(error_text)
            except:
                st.write("Nemožno zobraziť chybovú správu")
                
    except requests.exceptions.Timeout:
        st.error("❌ Timeout - pripojenie trvá príliš dlho")
        st.info("💡 Skontrolujte internetové pripojenie")
    except requests.exceptions.ConnectionError:
        st.error("❌ Problém s internetovým pripojením")
        st.info("💡 Skontrolujte internetové pripojenie alebo firewall")
    except ImportError:
        st.error("❌ Chýba modul requests")
        st.info("💡 Nainštalujte: pip install requests")
    except Exception as e:
        st.error(f"❌ Neočakávaná chyba: {e}")
        st.write("**Debug informácie:**")
        st.code(str(e))
        
        import traceback
        st.write("**Kompletný error:**")
        st.code(traceback.format_exc())

def sync_sqlite_to_airtable(api_key: str, base_id: str):
    """Synchronizuje dáta z SQLite do Airtable"""
    try:
        from airtable_connector import AirtableConnector
        import sqlite3
        
        with st.spinner("📤 Synchronizujem SQLite → Airtable..."):
            connector = AirtableConnector(api_key, base_id)
            
            if not connector.test_connection():
                st.error("❌ Airtable pripojenie neúspešné!")
                return
            
            # Synchronizuj procesy
            with sqlite3.connect("adsun_processes.db") as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM processes WHERE is_active = 1 LIMIT 10")
                processes = [dict(row) for row in cursor.fetchall()]
            
            if processes:
                uploaded_count = 0
                for process in processes:
                    # Transformuj na Airtable formát
                    airtable_process = {
                        "name": process.get('name', ''),
                        "category": process.get('category', 'nezhodnotené'),
                        "owner": process.get('owner', ''),
                        "frequency": process.get('frequency', 'nezhodnotené'),
                        "duration_minutes": process.get('duration_minutes', 0),
                        "priority": process.get('priority', 'stredná'),
                        "automation_readiness": process.get('automation_readiness', 0),
                        "success_criteria": process.get('success_criteria', ''),
                        "common_problems": process.get('common_problems', ''),
                        "mentioned_systems": []
                    }
                    
                    if connector.save_process(airtable_process):
                        uploaded_count += 1
                
                st.success(f"✅ Synchronizovaných {uploaded_count}/{len(processes)} procesov!")
            else:
                st.info("📭 Žiadne procesy na synchronizáciu")
                
    except Exception as e:
        st.error(f"❌ Chyba synchronizácie: {e}")

def sync_airtable_to_sqlite(api_key: str, base_id: str):
    """Synchronizuje dáta z Airtable do SQLite"""
    try:
        from airtable_connector import AirtableConnector
        import sqlite3
        
        with st.spinner("📥 Synchronizujem Airtable → SQLite..."):
            connector = AirtableConnector(api_key, base_id)
            
            if not connector.test_connection():
                st.error("❌ Airtable pripojenie neúspešné!")
                return
            
            # Načítaj procesy z Airtable
            airtable_processes = connector.get_processes(limit=50)
            
            if airtable_processes:
                imported_count = 0
                
                with sqlite3.connect("adsun_processes.db") as conn:
                    for process in airtable_processes:
                        try:
                            # Skontroluj či proces už existuje
                            cursor = conn.execute(
                                "SELECT id FROM processes WHERE name = ? AND owner = ?",
                                (process.get('name', ''), process.get('owner', ''))
                            )
                            
                            if not cursor.fetchone():
                                # Vlož nový proces
                                conn.execute("""
                                    INSERT INTO processes (
                                        name, category, owner, frequency, duration_minutes,
                                        priority, automation_readiness, success_criteria,
                                        common_problems, is_active, created_at
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, datetime('now'))
                                """, (
                                    process.get('name', ''),
                                    process.get('category', ''),
                                    process.get('owner', ''),
                                    process.get('frequency', ''),
                                    process.get('duration_minutes', 0),
                                    process.get('priority', ''),
                                    process.get('automation_readiness', 0),
                                    process.get('success_criteria', ''),
                                    process.get('common_problems', '')
                                ))
                                imported_count += 1
                        except Exception as e:
                            st.warning(f"⚠️ Chyba importu procesu {process.get('name', '')}: {e}")
                    
                    conn.commit()
                
                st.success(f"✅ Importovaných {imported_count}/{len(airtable_processes)} nových procesov!")
            else:
                st.info("📭 Žiadne procesy v Airtable")
                
    except Exception as e:
        st.error(f"❌ Chyba synchronizácie: {e}")

def activate_airtable_mode(api_key: str, base_id: str):
    """Aktivuje Airtable režim v aplikácii"""
    try:
        from airtable_connector import HybridDatabaseManager
        
        with st.spinner("🔄 Aktivujem Airtable režim..."):
            # Test pripojenia
            test_manager = HybridDatabaseManager(
                use_airtable=True,
                airtable_api_key=api_key,
                airtable_base_id=base_id
            )
            
            if test_manager.connection_ok:
                # Ulož nastavenia do session state
                st.session_state.use_airtable = True
                st.session_state.hybrid_db_manager = test_manager
                
                st.success("✅ Airtable režim aktivovaný!")
                st.info("🔄 Aplikácia teraz používa Airtable pre ukladanie nových dát")
                st.balloons()
                
                # Zobraz status
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📊 Databáza", "Airtable (aktívna)")
                with col2:
                    st.metric("🔗 Pripojenie", "Úspešné")
                    
            else:
                st.error("❌ Nemožno aktivovať Airtable režim - pripojenie neúspešné")
                
    except Exception as e:
        st.error(f"❌ Chyba aktivácie: {e}") 