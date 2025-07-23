#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Database Components
Database manager a súvisiace funkcie
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
from adsun_process_mapper_ai import ProcessContext

class DatabaseManager:
    """Pôvodný SQLite manager pre backward compatibility"""
    
    def __init__(self, db_path: str = "adsun_processes.db"):
        self.db_path = db_path
    
    def save_process_session(self, process_name: str, conversation_history: List[Dict], 
                           context: ProcessContext, documenter: str) -> int:
        """Uloží session dokumentovania procesu do databázy"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Vytvor nový proces
                cursor = conn.execute("""
                    INSERT INTO processes (name, category, trigger_type, owner, frequency, 
                                         duration_minutes, priority, volume_per_period, 
                                         success_criteria, common_problems, automation_readiness, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    process_name,
                    getattr(context, 'category', None) or 'nezhodnotené',  # Fix: ensure non-null
                    'Definované v konverzácii',
                    documenter,
                    'nezhodnotené',
                    None,
                    'stredná',
                    None,
                    'Definované v konverzácii',
                    'Identifikované v konverzácii',
                    getattr(context, 'automation_potential', None) or 3,  # Fix: ensure non-null
                    json.dumps(getattr(context, 'mentioned_systems', None) or [], ensure_ascii=False)
                ))
                
                process_id = cursor.lastrowid
                
                # Ulož konverzačnú históriu
                for i, entry in enumerate(conversation_history):
                    conn.execute("""
                        INSERT INTO documentation_sessions (process_id, documented_by, session_notes, 
                                                          completeness_score, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        process_id,
                        documenter,
                        json.dumps({
                            'step': i + 1,
                            'question': entry['question'],
                            'response': entry['response'],
                            'analysis': entry.get('analysis', {}),
                            'timestamp': entry['timestamp'].isoformat()
                        }, ensure_ascii=False),
                        min(len(conversation_history), 10),
                        entry['timestamp']
                    ))
                
                return process_id
                
        except Exception as e:
            st.error(f"❌ Chyba pri ukladaní: {e}")
            return None
    
    def load_process_sessions(self, documenter: str = None) -> List[Dict]:
        """Načíta sessions dokumentovania z databázy"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                if documenter:
                    cursor = conn.execute("""
                        SELECT p.*, ds.session_notes, ds.created_at as session_date
                        FROM processes p
                        JOIN documentation_sessions ds ON p.id = ds.process_id
                        WHERE ds.documented_by = ?
                        ORDER BY ds.created_at DESC
                    """, (documenter,))
                else:
                    cursor = conn.execute("""
                        SELECT p.*, ds.session_notes, ds.created_at as session_date
                        FROM processes p
                        JOIN documentation_sessions ds ON p.id = ds.process_id
                        ORDER BY ds.created_at DESC
                    """)
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            st.error(f"❌ Chyba pri načítavaní: {e}")
            return []
    
    def get_process_statistics(self) -> Dict:
        """Získa štatistiky z databázy"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Základné počty
                cursor = conn.execute("SELECT COUNT(*) FROM processes WHERE is_active = 1")
                process_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM process_steps")
                steps_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM documentation_sessions")
                sessions_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT AVG(automation_readiness) FROM processes WHERE automation_readiness IS NOT NULL")
                avg_automation = cursor.fetchone()[0] or 0
                
                # Top dokumentátori
                cursor = conn.execute("""
                    SELECT documented_by, COUNT(*) as session_count
                    FROM documentation_sessions
                    GROUP BY documented_by
                    ORDER BY session_count DESC
                    LIMIT 5
                """)
                top_documenters = cursor.fetchall()
                
                return {
                    'process_count': process_count,
                    'steps_count': steps_count,
                    'sessions_count': sessions_count,
                    'avg_automation': avg_automation,
                    'top_documenters': top_documenters
                }
                
        except Exception as e:
            st.error(f"❌ Chyba pri načítavaní štatistík: {e}")
            return {
                'process_count': 0,
                'steps_count': 0,
                'sessions_count': 0,
                'avg_automation': 0,
                'top_documenters': []
            }
    
    def get_all_processes(self) -> List[Dict]:
        """Načíta všetky procesy pre zobrazenie"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT p.*, COUNT(ps.id) as step_count
                    FROM processes p
                    LEFT JOIN process_steps ps ON p.id = ps.process_id
                    WHERE p.is_active = 1
                    GROUP BY p.id
                    ORDER BY p.created_at DESC
                """)
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            st.error(f"❌ Chyba pri načítavaní procesov: {e}")
            return []

def get_sample_processes() -> List[Dict]:
    """Vráti vzorové procesy ak nie sú v databáze"""
    return [
        {
            'name': 'Príjem dopytu - polep auta',
            'category': 'obchod',
            'owner': 'Obchodník',
            'duration_minutes': 15,
            'priority': 'vysoká',
            'automation_readiness': 4
        },
        {
            'name': 'Nacenenie zákazky - polep auta', 
            'category': 'obchod',
            'owner': 'Obchodník',
            'duration_minutes': 37,
            'priority': 'vysoká',
            'automation_readiness': 3
        },
        {
            'name': 'Realizácia polepov vozidla',
            'category': 'výroba', 
            'owner': 'Technik polepu',
            'duration_minutes': 360,
            'priority': 'stredná',
            'automation_readiness': 2
        },
        {
            'name': 'Tvorba cenovej ponuky',
            'category': 'obchod',
            'owner': 'Obchodník', 
            'duration_minutes': 20,
            'priority': 'vysoká',
            'automation_readiness': 4
        }
    ] 