#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Airtable Connector
Integrácia s Airtable pre ukladanie a synchronizáciu procesov
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st

class AirtableConnector:
    """Connector pre Airtable API integráciu"""
    
    def __init__(self, api_key: str, base_id: str):
        self.api_key = api_key
        self.base_id = base_id
        self.base_url = f"https://api.airtable.com/v0/{base_id}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self) -> bool:
        """Testuje pripojenie k Airtable"""
        try:
            # Test spojenia pomocou meta API
            response = requests.get(
                f"https://api.airtable.com/v0/meta/bases/{self.base_id}/tables",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            st.error(f"❌ Chyba pripojenia k Airtable: {e}")
            return False
    
    def create_process_tables(self) -> bool:
        """Vytvorí potrebné tabuľky v Airtable base (len informačne - manuálne setup)"""
        tables_schema = {
            "Processes": {
                "fields": [
                    {"name": "Process Name", "type": "singleLineText"},
                    {"name": "Category", "type": "singleSelect", "options": ["obchod", "HR", "administratíva", "IT", "výroba"]},
                    {"name": "Owner", "type": "singleLineText"},
                    {"name": "Frequency", "type": "singleSelect", "options": ["denne", "týždenne", "mesačne", "občas"]},
                    {"name": "Duration (min)", "type": "number"},
                    {"name": "Priority", "type": "singleSelect", "options": ["vysoká", "stredná", "nízka"]},
                    {"name": "Automation Readiness", "type": "rating", "max": 5},
                    {"name": "Success Criteria", "type": "multilineText"},
                    {"name": "Common Problems", "type": "multilineText"},
                    {"name": "Mentioned Systems", "type": "multipleSelects"},
                    {"name": "Created At", "type": "createdTime"},
                    {"name": "Updated At", "type": "lastModifiedTime"}
                ]
            },
            "Documentation Sessions": {
                "fields": [
                    {"name": "Process", "type": "linkToAnotherRecord", "linkedTable": "Processes"},
                    {"name": "Documenter", "type": "singleLineText"},
                    {"name": "Step Number", "type": "number"},
                    {"name": "Question", "type": "multilineText"},
                    {"name": "Response", "type": "multilineText"},
                    {"name": "AI Analysis", "type": "multilineText"},
                    {"name": "AI Powered", "type": "checkbox"},
                    {"name": "Session Date", "type": "dateTime"},
                    {"name": "Completeness Score", "type": "rating", "max": 10}
                ]
            },
            "Process Steps": {
                "fields": [
                    {"name": "Process", "type": "linkToAnotherRecord", "linkedTable": "Processes"},
                    {"name": "Step Number", "type": "number"},
                    {"name": "Step Title", "type": "singleLineText"},
                    {"name": "Description", "type": "multilineText"},
                    {"name": "Responsible Person", "type": "singleLineText"},
                    {"name": "System/Tool", "type": "singleLineText"},
                    {"name": "Estimated Time (min)", "type": "number"},
                    {"name": "Automation Potential", "type": "rating", "max": 5},
                    {"name": "Is Automated", "type": "checkbox"}
                ]
            }
        }
        
        st.info("""
        📋 **Airtable Setup Inštrukcie:**
        
        Vytvorte v Airtable tieto tabuľky s poľami:
        
        **1. Processes tabuľka:**
        - Process Name (Single line text)
        - Category (Single select: obchod, HR, administratíva, IT, výroba)
        - Owner (Single line text)
        - Frequency (Single select: denne, týždenne, mesačne, občas)
        - Duration (min) (Number)
        - Priority (Single select: vysoká, stredná, nízka)
        - Automation Readiness (Rating 1-5)
        - Success Criteria (Long text)
        - Common Problems (Long text)
        - Mentioned Systems (Multiple select)
        - Created At (Created time)
        - Updated At (Last modified time)
        
        **2. Documentation Sessions tabuľka:**
        - Process (Link to Processes)
        - Documenter (Single line text)
        - Step Number (Number)
        - Question (Long text)
        - Response (Long text)
        - AI Analysis (Long text)
        - AI Powered (Checkbox)
        - Session Date (Date with time)
        - Completeness Score (Rating 1-10)
        
        **3. Process Steps tabuľka:**
        - Process (Link to Processes)
        - Step Number (Number)
        - Step Title (Single line text)
        - Description (Long text)
        - Responsible Person (Single line text)
        - System/Tool (Single line text)
        - Estimated Time (min) (Number)
        - Automation Potential (Rating 1-5)
        - Is Automated (Checkbox)
        """)
        
        return True
    
    def save_process(self, process_data: Dict) -> Optional[str]:
        """Uloží proces do Airtable"""
        try:
            # Príprava dát pre Airtable
            airtable_data = {
                "fields": {
                    "Process Name": process_data.get("name", ""),
                    "Category": process_data.get("category", "nezhodnotené"),
                    "Owner": process_data.get("owner", ""),
                    "Frequency": process_data.get("frequency", "nezhodnotené"),
                    "Priority": process_data.get("priority", "stredná"),
                    "Automation Readiness": process_data.get("automation_readiness", 3),
                    "Success Criteria": process_data.get("success_criteria", ""),
                    "Common Problems": process_data.get("common_problems", ""),
                    "Mentioned Systems": process_data.get("mentioned_systems", [])
                }
            }
            
            # Pridaj číselné hodnoty len ak sú definované
            if process_data.get("duration_minutes"):
                airtable_data["fields"]["Duration (min)"] = process_data["duration_minutes"]
            
            response = requests.post(
                f"{self.base_url}/Processes",
                headers=self.headers,
                json=airtable_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()["id"]
            else:
                st.error(f"❌ Airtable chyba: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            st.error(f"❌ Chyba pri ukladaní do Airtable: {e}")
            return None
    
    def save_documentation_session(self, process_id: str, session_data: Dict) -> Optional[str]:
        """Uloží dokumentačnú session do Airtable"""
        try:
            airtable_data = {
                "fields": {
                    "Process": [process_id],  # Link to Process record
                    "Documenter": session_data.get("documenter", ""),
                    "Step Number": session_data.get("step", 1),
                    "Question": session_data.get("question", ""),
                    "Response": session_data.get("response", ""),
                    "AI Analysis": json.dumps(session_data.get("analysis", {}), ensure_ascii=False),
                    "AI Powered": session_data.get("ai_powered", False),
                    "Session Date": session_data.get("timestamp", datetime.now().isoformat()),
                    "Completeness Score": session_data.get("completeness_score", 5)
                }
            }
            
            response = requests.post(
                f"{self.base_url}/Documentation Sessions",
                headers=self.headers,
                json=airtable_data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()["id"]
            else:
                st.error(f"❌ Airtable session chyba: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"❌ Chyba pri ukladaní session do Airtable: {e}")
            return None
    
    def get_processes(self, limit: int = 100) -> List[Dict]:
        """Načíta procesy z Airtable"""
        try:
            params = {
                "maxRecords": limit,
                "sort[0][field]": "Created At",
                "sort[0][direction]": "desc"
            }
            
            response = requests.get(
                f"{self.base_url}/Processes",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                records = response.json().get("records", [])
                
                # Transformuj Airtable formát na náš formát
                processes = []
                for record in records:
                    fields = record["fields"]
                    process = {
                        "id": record["id"],
                        "name": fields.get("Process Name", ""),
                        "category": fields.get("Category", ""),
                        "owner": fields.get("Owner", ""),
                        "frequency": fields.get("Frequency", ""),
                        "duration_minutes": fields.get("Duration (min)", 0),
                        "priority": fields.get("Priority", ""),
                        "automation_readiness": fields.get("Automation Readiness", 0),
                        "success_criteria": fields.get("Success Criteria", ""),
                        "common_problems": fields.get("Common Problems", ""),
                        "mentioned_systems": fields.get("Mentioned Systems", []),
                        "created_at": fields.get("Created At", ""),
                        "step_count": 0  # Môže sa doplniť dodatočne
                    }
                    processes.append(process)
                
                return processes
            else:
                st.error(f"❌ Chyba načítavania z Airtable: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"❌ Chyba pri načítavaní z Airtable: {e}")
            return []
    
    def get_documentation_sessions(self, process_id: str = None) -> List[Dict]:
        """Načíta dokumentačné sessions z Airtable"""
        try:
            params = {
                "maxRecords": 100,
                "sort[0][field]": "Session Date",
                "sort[0][direction]": "desc"
            }
            
            # Filter by process if specified
            if process_id:
                params["filterByFormula"] = f"{{Process}} = '{process_id}'"
            
            response = requests.get(
                f"{self.base_url}/Documentation Sessions",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                records = response.json().get("records", [])
                
                sessions = []
                for record in records:
                    fields = record["fields"]
                    session = {
                        "id": record["id"],
                        "process_id": fields.get("Process", [""])[0],
                        "documenter": fields.get("Documenter", ""),
                        "step": fields.get("Step Number", 1),
                        "question": fields.get("Question", ""),
                        "response": fields.get("Response", ""),
                        "analysis": fields.get("AI Analysis", "{}"),
                        "ai_powered": fields.get("AI Powered", False),
                        "session_date": fields.get("Session Date", ""),
                        "completeness_score": fields.get("Completeness Score", 5)
                    }
                    sessions.append(session)
                
                return sessions
            else:
                st.error(f"❌ Chyba načítavania sessions z Airtable: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"❌ Chyba pri načítavaní sessions z Airtable: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Získa štatistiky z Airtable"""
        try:
            # Základné počty z každej tabuľky
            stats = {
                'process_count': 0,
                'sessions_count': 0,
                'avg_automation': 0,
                'top_documenters': []
            }
            
            # Počet procesov
            response = requests.get(
                f"{self.base_url}/Processes",
                headers=self.headers,
                params={"maxRecords": 1, "fields": ["Process Name"]},
                timeout=10
            )
            
            if response.status_code == 200:
                # Airtable nevracia total count priamo, ale môžeme odhadnúť
                data = response.json()
                if "records" in data and len(data["records"]) > 0:
                    # Pre presný počet by sme potrebovali stránkovanie
                    processes = self.get_processes(1000)  # Načítaj viac pre počet
                    stats['process_count'] = len(processes)
                    
                    # Vypočítaj priemernú automatizáciu
                    automation_scores = [p.get('automation_readiness', 0) for p in processes if p.get('automation_readiness')]
                    if automation_scores:
                        stats['avg_automation'] = sum(automation_scores) / len(automation_scores)
            
            # Počet sessions
            sessions = self.get_documentation_sessions()
            stats['sessions_count'] = len(sessions)
            
            # Top dokumentátori
            documenter_counts = {}
            for session in sessions:
                doc = session.get('documenter', 'Unknown')
                documenter_counts[doc] = documenter_counts.get(doc, 0) + 1
            
            stats['top_documenters'] = sorted(
                documenter_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return stats
            
        except Exception as e:
            st.error(f"❌ Chyba pri načítavaní štatistík z Airtable: {e}")
            return {
                'process_count': 0,
                'sessions_count': 0,
                'avg_automation': 0,
                'top_documenters': []
            }

class HybridDatabaseManager:
    """Hybridný manager pre SQLite a Airtable"""
    
    def __init__(self, use_airtable: bool = False, airtable_api_key: str = None, airtable_base_id: str = None):
        self.use_airtable = use_airtable
        
        if use_airtable and airtable_api_key and airtable_base_id:
            self.airtable = AirtableConnector(airtable_api_key, airtable_base_id)
            self.connection_ok = self.airtable.test_connection()
            if not self.connection_ok:
                st.warning("⚠️ Airtable pripojenie neúspešné, používa sa SQLite backup")
                use_airtable = False
        else:
            self.connection_ok = False
        
        # Vždy maj SQLite ako backup
        from database_components import DatabaseManager
        self.sqlite_manager = DatabaseManager()
    
    def save_process_session(self, process_name: str, conversation_history: List[Dict], 
                           context, documenter: str) -> Optional[str]:
        """Uloží process session do vybranej databázy"""
        
        # Ak používame Airtable a pripojenie je OK
        if self.use_airtable and self.connection_ok:
            try:
                # Uložiť proces
                process_data = {
                    "name": process_name,
                    "category": getattr(context, 'category', None) or 'nezhodnotené',  # Fix: ensure non-null
                    "owner": documenter,
                    "frequency": "nezhodnotené",
                    "priority": "stredná",
                    "automation_readiness": getattr(context, 'automation_potential', None) or 3,  # Fix: ensure non-null
                    "success_criteria": "Definované v konverzácii",
                    "common_problems": "Identifikované v konverzácii",
                    "mentioned_systems": getattr(context, 'mentioned_systems', None) or []  # Fix: ensure non-null
                }
                
                process_id = self.airtable.save_process(process_data)
                
                if process_id:
                    # Uložiť všetky session kroky
                    for i, entry in enumerate(conversation_history):
                        session_data = {
                            "documenter": documenter,
                            "step": i + 1,
                            "question": entry['question'],
                            "response": entry['response'],
                            "analysis": entry.get('analysis', {}),
                            "ai_powered": entry.get('analysis', {}).get('ai_powered', False),
                            "timestamp": entry['timestamp'].isoformat(),
                            "completeness_score": min(len(conversation_history), 10)
                        }
                        
                        self.airtable.save_documentation_session(process_id, session_data)
                    
                    st.success("✅ Dáta uložené do Airtable!")
                    return process_id
                
            except Exception as e:
                st.error(f"❌ Airtable chyba, používa sa SQLite backup: {e}")
        
        # Fallback na SQLite
        return self.sqlite_manager.save_process_session(process_name, conversation_history, context, documenter)
    
    def get_process_statistics(self) -> Dict:
        """Získa štatistiky z vybranej databázy"""
        if self.use_airtable and self.connection_ok:
            return self.airtable.get_statistics()
        else:
            return self.sqlite_manager.get_process_statistics()
    
    def load_process_sessions(self, documenter: str = None) -> List[Dict]:
        """Načíta sessions z vybranej databázy"""
        if self.use_airtable and self.connection_ok:
            sessions = self.airtable.get_documentation_sessions()
            
            # Filter by documenter if specified
            if documenter:
                sessions = [s for s in sessions if s.get('documenter') == documenter]
            
            return sessions
        else:
            return self.sqlite_manager.load_process_sessions(documenter)
    
    def get_available_processes(self) -> List[Dict]:
        """Načíta dostupné procesy"""
        if self.use_airtable and self.connection_ok:
            return self.airtable.get_processes()
        else:
            # Implementuj pre SQLite ak potrebné
            return [] 