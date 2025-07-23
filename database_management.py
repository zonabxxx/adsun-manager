#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Database Management
Správa databázy s prehľadom tabuliek a priamou editáciou
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any

def render_database_management():
    """Render správy databázy s prehľadom tabuliek"""
    st.markdown("## 🗄️ Správa databázy")
    st.markdown("*Prehľad všetkých tabuliek a dát s možnosťou priamej editácie*")
    
    # Získanie zoznamu tabuliek
    tables = get_database_tables()
    
    if not tables:
        st.error("❌ Žiadne tabuľky v databáze nenájdené")
        return
    
    # Výber tabuľky
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_table = st.selectbox(
            "📊 Vyberte tabuľku:",
            options=tables,
            format_func=lambda x: f"{x['name']} ({x['count']} záznamov)"
        )
    
    with col2:
        if st.button("🔄 Obnoviť"):
            st.rerun()
    
    with col3:
        if st.button("📈 Štatistiky"):
            show_database_statistics()
    
    if selected_table:
        render_table_management(selected_table['name'])

def get_database_tables() -> List[Dict]:
    """Získa zoznam všetkých tabuliek v databáze"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Získaj zoznam tabuliek
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            table_names = [row[0] for row in cursor.fetchall()]
            
            tables = []
            for table_name in table_names:
                # Spočítaj záznamy v každej tabuľke
                try:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    count = cursor.fetchone()[0]
                    tables.append({
                        'name': table_name,
                        'count': count
                    })
                except Exception:
                    tables.append({
                        'name': table_name,
                        'count': 0
                    })
            
            return tables
            
    except Exception as e:
        st.error(f"❌ Chyba načítavania tabuliek: {e}")
        return []

def get_table_structure(table_name: str) -> List[Dict]:
    """Získa štruktúru tabuľky"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            cursor = conn.execute(f"PRAGMA table_info(`{table_name}`)")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'not_null': bool(row[3]),
                    'default': row[4],
                    'primary_key': bool(row[5])
                })
            return columns
    except Exception as e:
        st.error(f"❌ Chyba načítavania štruktúry: {e}")
        return []

def render_table_management(table_name: str):
    """Render správy konkrétnej tabuľky"""
    st.markdown(f"### 📋 Tabuľka: **{table_name}**")
    
    # Tabs pre rôzne pohľady
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dáta", "🏗️ Štruktúra", "✏️ Editácia", "➕ Pridať záznam"])
    
    with tab1:
        render_table_data(table_name)
    
    with tab2:
        render_table_structure(table_name)
    
    with tab3:
        render_table_edit(table_name)
    
    with tab4:
        render_add_record(table_name)

def render_table_data(table_name: str):
    """Zobrazí dáta z tabuľky"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Načítaj dáta
            df = pd.read_sql_query(f"SELECT * FROM `{table_name}` LIMIT 100", conn)
            
            if df.empty:
                st.info("📭 Tabuľka je prázdna")
                return
            
            st.markdown(f"**Zobrazených: {len(df)} záznamov (max 100)**")
            
            # Filter a vyhľadávanie
            if len(df.columns) > 0:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    search_term = st.text_input("🔍 Vyhľadávanie:", placeholder="Zadajte text na vyhľadanie...")
                
                with col2:
                    search_column = st.selectbox("🎯 V stĺpci:", ["Všetky"] + list(df.columns))
                
                # Filtrovanie
                if search_term:
                    if search_column == "Všetky":
                        # Hľadaj vo všetkých textových stĺpcoch
                        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                        df = df[mask]
                    else:
                        # Hľadaj v konkrétnom stĺpci
                        mask = df[search_column].astype(str).str.contains(search_term, case=False, na=False)
                        df = df[mask]
                    
                    st.markdown(f"**Nájdených: {len(df)} záznamov**")
            
            # Zobrazenie dát
            # Konvertuj všetky hodnoty na stringy pre PyArrow kompatibilitu
            df_display = df.copy()
            for col in df_display.columns:
                df_display[col] = df_display[col].astype(str)
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    col: st.column_config.TextColumn(
                        width="medium" if len(str(df[col].iloc[0] if not df.empty else "")) < 50 else "large"
                    ) for col in df.columns
                }
            )
            
            # Export možnosti
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("📥 Export CSV"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="💾 Stiahnuť CSV",
                        data=csv,
                        file_name=f"{table_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime='text/csv'
                    )
            
            with col2:
                if st.button("🗑️ Zmazať všetko"):
                    st.session_state.confirm_delete_all = table_name
            
            # Potvrdenie mazania
            if st.session_state.get('confirm_delete_all') == table_name:
                st.warning("⚠️ Naozaj chcete zmazať všetky záznamy z tejto tabuľky?")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Áno, zmazať všetko", type="primary"):
                        delete_all_records(table_name)
                        del st.session_state.confirm_delete_all
                        st.rerun()
                
                with col2:
                    if st.button("❌ Zrušiť"):
                        del st.session_state.confirm_delete_all
                        st.rerun()
            
    except Exception as e:
        st.error(f"❌ Chyba načítavania dát: {e}")

def render_table_structure(table_name: str):
    """Zobrazí štruktúru tabuľky"""
    columns = get_table_structure(table_name)
    
    if not columns:
        st.error("❌ Nepodarilo sa načítať štruktúru tabuľky")
        return
    
    st.markdown("### 🏗️ Štruktúra tabuľky")
    
    # Vytvor DataFrame pre lepšie zobrazenie
    structure_data = []
    for col in columns:
        structure_data.append({
            "Stĺpec": col['name'],
            "Typ": col['type'],
            "Povinný": "✅" if col['not_null'] else "❌",
            "Predvolená hodnota": col['default'] or "-",
            "Primárny kľúč": "🔑" if col['primary_key'] else "-"
        })
    
    df_structure = pd.DataFrame(structure_data)
    
    # Konvertuj na stringy pre PyArrow kompatibilitu
    for col in df_structure.columns:
        df_structure[col] = df_structure[col].astype(str)
    
    st.dataframe(df_structure, use_container_width=True, hide_index=True)
    
    # Dodatočné informácie
    with st.expander("📊 Ďalšie informácie"):
        try:
            with sqlite3.connect("adsun_processes.db") as conn:
                # Počet záznamov
                cursor = conn.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                count = cursor.fetchone()[0]
                
                # Veľkosť tabuľky (približne)
                cursor = conn.execute(f"SELECT SUM(LENGTH(CAST(* AS TEXT))) FROM `{table_name}`")
                size_result = cursor.fetchone()[0]
                size = size_result if size_result else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📊 Počet záznamov", count)
                
                with col2:
                    st.metric("🗂️ Počet stĺpcov", len(columns))
                
                with col3:
                    st.metric("💾 Približná veľkosť", f"{size:,} znakov")
                
        except Exception as e:
            st.warning(f"⚠️ Nepodarilo sa načítať dodatočné informácie: {e}")

def render_table_edit(table_name: str):
    """Render editácie záznamov"""
    st.markdown("### ✏️ Editácia záznamov")
    
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Načítaj prvých 20 záznamov na editáciu
            df = pd.read_sql_query(f"SELECT * FROM `{table_name}` LIMIT 20", conn)
            
            if df.empty:
                st.info("📭 Žiadne záznamy na editáciu")
                return
            
            st.info("💡 Zobrazených je max 20 záznamov. Použite vyhľadávanie na nájdenie konkrétneho záznamu.")
            
            # Výber záznamu na editáciu
            if 'id' in df.columns:
                record_options = [f"ID {row['id']}: {str(row[df.columns[1]])[:50]}..." 
                                for _, row in df.iterrows()]
                selected_idx = st.selectbox("🎯 Vyberte záznam na editáciu:", range(len(record_options)), 
                                          format_func=lambda x: record_options[x])
                
                if selected_idx is not None:
                    render_record_editor(table_name, df.iloc[selected_idx])
            else:
                st.warning("⚠️ Tabuľka nemá stĺpec 'id' - editácia nie je podporovaná")
                
    except Exception as e:
        st.error(f"❌ Chyba načítavania editácie: {e}")

def render_record_editor(table_name: str, record: pd.Series):
    """Render editora pre konkrétny záznam"""
    st.markdown(f"#### 📝 Editácia záznamu ID: {record.get('id', 'N/A')}")
    
    columns = get_table_structure(table_name)
    
    with st.form(f"edit_record_{record.get('id')}"):
        edited_values = {}
        
        col1, col2 = st.columns(2)
        
        for i, column in enumerate(columns):
            col_name = column['name']
            current_value = record.get(col_name, '')
            
            # Preskočiť ID a auto-generated polia
            if column['primary_key'] or col_name in ['created_at', 'updated_at']:
                continue
            
            target_col = col1 if i % 2 == 0 else col2
            
            with target_col:
                if column['type'].upper() in ['TEXT', 'VARCHAR']:
                    if isinstance(current_value, str) and len(current_value) > 100:
                        edited_values[col_name] = st.text_area(
                            f"{col_name}:",
                            value=str(current_value) if current_value is not None else "",
                            height=100
                        )
                    else:
                        edited_values[col_name] = st.text_input(
                            f"{col_name}:",
                            value=str(current_value) if current_value is not None else ""
                        )
                elif column['type'].upper() in ['INTEGER', 'INT']:
                    edited_values[col_name] = st.number_input(
                        f"{col_name}:",
                        value=int(current_value) if current_value is not None and str(current_value).isdigit() else 0
                    )
                elif column['type'].upper() in ['REAL', 'FLOAT']:
                    edited_values[col_name] = st.number_input(
                        f"{col_name}:",
                        value=float(current_value) if current_value is not None else 0.0,
                        format="%.2f"
                    )
                elif column['type'].upper() == 'BOOLEAN':
                    edited_values[col_name] = st.checkbox(
                        f"{col_name}:",
                        value=bool(current_value) if current_value is not None else False
                    )
                else:
                    edited_values[col_name] = st.text_input(
                        f"{col_name}:",
                        value=str(current_value) if current_value is not None else ""
                    )
        
        # Tlačidlá
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.form_submit_button("💾 Uložiť zmeny", type="primary"):
                update_record(table_name, record['id'], edited_values)
                st.success("✅ Záznam uložený!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("🗑️ Zmazať záznam"):
                delete_record(table_name, record['id'])
                st.success("✅ Záznam zmazaný!")
                st.rerun()
        
        with col3:
            if st.form_submit_button("↩️ Zrušiť"):
                st.rerun()

def render_add_record(table_name: str):
    """Render pridávania nového záznamu"""
    st.markdown("### ➕ Pridať nový záznam")
    
    columns = get_table_structure(table_name)
    
    with st.form(f"add_record_{table_name}"):
        new_values = {}
        
        col1, col2 = st.columns(2)
        
        for i, column in enumerate(columns):
            col_name = column['name']
            
            # Preskočiť auto-generated polia
            if column['primary_key'] or col_name in ['id', 'created_at', 'updated_at']:
                continue
            
            target_col = col1 if i % 2 == 0 else col2
            
            with target_col:
                if column['type'].upper() in ['TEXT', 'VARCHAR']:
                    new_values[col_name] = st.text_area(
                        f"{col_name}*" if column['not_null'] else f"{col_name}:",
                        height=80 if 'description' in col_name.lower() else None
                    )
                elif column['type'].upper() in ['INTEGER', 'INT']:
                    new_values[col_name] = st.number_input(
                        f"{col_name}*" if column['not_null'] else f"{col_name}:",
                        value=0
                    )
                elif column['type'].upper() in ['REAL', 'FLOAT']:
                    new_values[col_name] = st.number_input(
                        f"{col_name}*" if column['not_null'] else f"{col_name}:",
                        value=0.0,
                        format="%.2f"
                    )
                elif column['type'].upper() == 'BOOLEAN':
                    new_values[col_name] = st.checkbox(
                        f"{col_name}*" if column['not_null'] else f"{col_name}:"
                    )
                else:
                    new_values[col_name] = st.text_input(
                        f"{col_name}*" if column['not_null'] else f"{col_name}:"
                    )
        
        if st.form_submit_button("✅ Pridať záznam", type="primary"):
            # Validácia povinných polí
            missing_fields = []
            for column in columns:
                if column['not_null'] and column['name'] not in ['id', 'created_at', 'updated_at']:
                    if not new_values.get(column['name']):
                        missing_fields.append(column['name'])
            
            if missing_fields:
                st.error(f"❌ Povinné polia: {', '.join(missing_fields)}")
            else:
                add_record(table_name, new_values)
                st.success("✅ Záznam pridaný!")
                st.rerun()

def update_record(table_name: str, record_id: int, values: Dict[str, Any]):
    """Aktualizuje záznam v databáze"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Vytvor SET clause
            set_clauses = []
            params = []
            
            for col_name, value in values.items():
                set_clauses.append(f"`{col_name}` = ?")
                params.append(value)
            
            # Pridaj updated_at ak existuje
            try:
                columns = get_table_structure(table_name)
                if any(col['name'] == 'updated_at' for col in columns):
                    set_clauses.append("`updated_at` = CURRENT_TIMESTAMP")
            except:
                pass
            
            params.append(record_id)
            
            query = f"UPDATE `{table_name}` SET {', '.join(set_clauses)} WHERE id = ?"
            conn.execute(query, params)
            conn.commit()
            
    except Exception as e:
        st.error(f"❌ Chyba aktualizácie: {e}")

def delete_record(table_name: str, record_id: int):
    """Zmaže záznam z databázy"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.execute(f"DELETE FROM `{table_name}` WHERE id = ?", (record_id,))
            conn.commit()
    except Exception as e:
        st.error(f"❌ Chyba mazania: {e}")

def add_record(table_name: str, values: Dict[str, Any]):
    """Pridá nový záznam do databázy"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            columns = list(values.keys())
            placeholders = ["?" for _ in columns]
            
            # Pridaj created_at ak existuje
            try:
                table_columns = get_table_structure(table_name)
                if any(col['name'] == 'created_at' for col in table_columns):
                    columns.append('created_at')
                    placeholders.append('CURRENT_TIMESTAMP')
            except:
                pass
            
            query = f"INSERT INTO `{table_name}` ({', '.join([f'`{col}`' for col in columns])}) VALUES ({', '.join(placeholders)})"
            conn.execute(query, list(values.values()))
            conn.commit()
            
    except Exception as e:
        st.error(f"❌ Chyba pridávania: {e}")

def delete_all_records(table_name: str):
    """Zmaže všetky záznamy z tabuľky"""
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            conn.execute(f"DELETE FROM `{table_name}`")
            conn.commit()
    except Exception as e:
        st.error(f"❌ Chyba mazania: {e}")

def show_database_statistics():
    """Zobrazí štatistiky databázy"""
    st.markdown("### 📈 Štatistiky databázy")
    
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            # Celková veľkosť databázy
            cursor = conn.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]
            
            # Štatistiky tabuliek
            tables = get_database_tables()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("🗄️ Počet tabuliek", len(tables))
            
            with col2:
                total_records = sum(table['count'] for table in tables)
                st.metric("📊 Celkom záznamov", total_records)
            
            with col3:
                st.metric("💾 Veľkosť DB", f"{db_size / 1024:.1f} KB")
            
            # Tabuľka s detailmi
            if tables:
                df_stats = pd.DataFrame(tables)
                df_stats = df_stats.sort_values('count', ascending=False)
                df_stats = df_stats.rename(columns={'name': 'Tabuľka', 'count': 'Počet záznamov'})
                
                # Konvertuj na stringy pre PyArrow kompatibilitu
                for col in df_stats.columns:
                    df_stats[col] = df_stats[col].astype(str)
                
                st.markdown("#### 📋 Detaily tabuliek")
                st.dataframe(
                    df_stats,
                    use_container_width=True,
                    hide_index=True
                )
            
    except Exception as e:
        st.error(f"❌ Chyba štatistík: {e}") 