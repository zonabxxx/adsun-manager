#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Company Settings
Konfigurácia firemných údajov a parametrov
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

def render_company_settings():
    """Render nastavení firmy"""
    st.markdown("## ⚙️ Nastavenia firmy")
    st.markdown("*Konfigurácia firemných údajov a parametrov*")
    
    # NAČÍTANIE ULOŽENÝCH NASTAVENÍ
    saved_settings = load_company_settings()
    
    # Firemné údaje
    st.markdown("### 🏢 Základné údaje")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("Názov firmy", value=saved_settings["company"]["name"], help="Oficiálny názov spoločnosti")
        company_address = st.text_area("Adresa", value=saved_settings["company"]["address"], help="Sídlo spoločnosti")
        company_phone = st.text_input("Telefón", value=saved_settings["company"]["phone"])
    
    with col2:
        company_email = st.text_input("Email", value=saved_settings["company"]["email"])
        company_website = st.text_input("Webstránka", value=saved_settings["company"]["website"])
        company_ico = st.text_input("IČO", value=saved_settings["company"]["ico"])
    
    # Systémové nastavenia
    st.markdown("### ⚙️ Systémové nastavenia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🤖 AI Nastavenia")
        ai_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        ai_model_index = ai_models.index(saved_settings["ai"]["model"]) if saved_settings["ai"]["model"] in ai_models else 0
        ai_model = st.selectbox("AI Model", ai_models, index=ai_model_index)
        ai_temperature = st.slider("Kreativita AI", 0.0, 1.0, saved_settings["ai"]["temperature"], help="Vyššia hodnota = kreatívnejšie odpovede")
        auto_analysis = st.checkbox("Automatická analýza procesov", value=saved_settings["ai"]["auto_analysis"])
    
    with col2:
        st.subheader("📊 Reporting")
        report_frequencies = ["Denne", "Týždenne", "Mesačne"]
        report_freq_index = report_frequencies.index(saved_settings["reporting"]["frequency"]) if saved_settings["reporting"]["frequency"] in report_frequencies else 1
        report_frequency = st.selectbox("Frekvencia reportov", report_frequencies, index=report_freq_index)
        email_notifications = st.checkbox("Email notifikácie", value=saved_settings["reporting"]["email_notifications"])
        backup_frequencies = ["Denne", "Týždenne", "Mesačne"]
        backup_freq_index = backup_frequencies.index(saved_settings["reporting"]["backup_frequency"]) if saved_settings["reporting"]["backup_frequency"] in backup_frequencies else 1
        backup_frequency = st.selectbox("Zálohovanie", backup_frequencies, index=backup_freq_index)
    
    # Procesy nastavenia
    st.markdown("### 📋 Proces nastavenia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        categories = ["Obchod", "Výroba", "HR", "IT", "Administratíva"]
        cat_index = categories.index(saved_settings["processes"]["default_category"]) if saved_settings["processes"]["default_category"] in categories else 0
        default_category = st.selectbox("Predvolená kategória", categories, index=cat_index)
        priorities = ["Vysoká", "Stredná", "Nízka"]
        priority_index = priorities.index(saved_settings["processes"]["default_priority"]) if saved_settings["processes"]["default_priority"] in priorities else 1
        default_priority = st.selectbox("Predvolená priorita", priorities, index=priority_index)
    
    with col2:
        auto_assign = st.checkbox("Automatické pridelenie vlastníka", value=saved_settings["processes"]["auto_assign"])
        require_approval = st.checkbox("Vyžadovať schválenie nových procesov", value=saved_settings["processes"]["require_approval"])
    
    # Uloženie nastavení
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("💾 Uložiť nastavenia", type="primary"):
            # Uloženie do súboru/databázy
            settings = {
                "company": {
                    "name": company_name,
                    "address": company_address,
                    "phone": company_phone,
                    "email": company_email,
                    "website": company_website,
                    "ico": company_ico
                },
                "ai": {
                    "model": ai_model,
                    "temperature": ai_temperature,
                    "auto_analysis": auto_analysis
                },
                "reporting": {
                    "frequency": report_frequency,
                    "email_notifications": email_notifications,
                    "backup_frequency": backup_frequency
                },
                "processes": {
                    "default_category": default_category,
                    "default_priority": default_priority,
                    "auto_assign": auto_assign,
                    "require_approval": require_approval
                }
            }
            
            # Uloženie do súboru
            try:
                with open("company_settings.json", "w", encoding="utf-8") as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                
                # DÔLEŽITÉ: Zachovaj session state mode aby sa nestratila navigácia
                st.session_state.mode = "company_settings"
                st.success("✅ Nastavenia uložené!")
                
                # Refresh stránku ale zostať na nastaveniach
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Chyba ukladania: {e}")
    
    # Štatistiky
    st.markdown("### 📊 Systémové štatistiky")
    
    try:
        with sqlite3.connect("adsun_processes.db") as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM processes WHERE is_active = 1")
            process_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(DISTINCT category) FROM processes WHERE is_active = 1")
            dept_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(DISTINCT owner) FROM processes WHERE is_active = 1")
            employee_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM documentation_sessions")
            session_count = cursor.fetchone()[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Procesy", process_count)
        
        with col2:
            st.metric("🏢 Oddelenia", dept_count)
        
        with col3:
            st.metric("👥 Zamestnanci", employee_count)
        
        with col4:
            st.metric("📝 Sessions", session_count)
            
    except Exception as e:
        st.error(f"❌ Chyba načítavania štatistík: {e}")

def load_company_settings():
    """Načíta nastavenia firmy zo súboru"""
    try:
        with open("company_settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return get_default_settings()
    except Exception as e:
        st.error(f"❌ Chyba načítavania nastavení: {e}")
        return get_default_settings()

def get_default_settings():
    """Vráti predvolené nastavenia"""
    return {
        "company": {
            "name": "ADSUN Company",
            "address": "Bratislava, Slovensko",
            "phone": "+421 XXX XXX XXX",
            "email": "info@adsun.sk",
            "website": "https://adsun.sk",
            "ico": "12345678"
        },
        "ai": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.3,
            "auto_analysis": True
        },
        "reporting": {
            "frequency": "Týždenne",
            "email_notifications": True,
            "backup_frequency": "Týždenne"
        },
        "processes": {
            "default_category": "Obchod",
            "default_priority": "Stredná",
            "auto_assign": False,
            "require_approval": False
        }
    } 