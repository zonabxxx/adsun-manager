#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Airtable Manager - Launcher
Clean chat interface pre prácu s Airtable procesmi
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Kontrola či sú nainštalované potrebné závislosti"""
    required = ['streamlit', 'cryptography', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Chýbajúce závislosti: {', '.join(missing)}")
        print("📦 Inštalujem závislosti...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
    else:
        print("✅ Všetky závislosti sú nainštalované")

def initialize_database():
    """Inicializácia databázy ak je potrebná"""
    try:
        from adsun_database_init import initialize_database_schema
        initialize_database_schema()
        print("✅ Databáza pripravená")
    except Exception as e:
        print(f"⚠️ Databáza: {e}")

def main():
    """Hlavná funkcia launcher"""
    print("=" * 60)
    print("🗄️ ADSUN Airtable Manager - Clean Interface")
    print("=" * 60)
    
    # Kontrola závislostí
    check_dependencies()
    
    # Inicializácia databázy
    print("🗄️ Inicializujem databázu...")
    initialize_database()
    
    # Spustenie Streamlit
    print("🚀 Spúšťam ADSUN Airtable Manager...")
    print("🌐 Otvorí sa v prehliadači na http://localhost:8502")
    print("💬 Clean chat interface pre prácu s Airtable")
    print("⏹️ Pre ukončenie stlačte Ctrl+C")
    
    try:
        # Spusti na inom porte ako hlavná aplikácia
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            'adsun_airtable_manager.py',
            '--server.port=8502',
            '--server.headless=true',
            '--browser.gatherUsageStats=false'
        ])
    except KeyboardInterrupt:
        print("\n👋 ADSUN Airtable Manager ukončený")
    except Exception as e:
        print(f"❌ Chyba pri spúšťaní: {e}")

if __name__ == "__main__":
    main() 