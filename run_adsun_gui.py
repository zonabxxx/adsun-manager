#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN AI GUI Launcher
Spúšťač pre Streamlit GUI aplikáciu
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Kontrola a inštalácia závislostí"""
    try:
        import streamlit
        import openai
        print("✅ Všetky závislosti sú nainštalované")
        return True
    except ImportError as e:
        print(f"❌ Chýbajúca závislosť: {e}")
        return False

def install_dependencies():
    """Inštalácia závislostí z requirements.txt"""
    print("🔧 Inštalujem závislosti...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Závislosti úspešne nainštalované")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Chyba pri inštalácii: {e}")
        return False

def setup_database():
    """Inicializácia databázy s ukážkovými dátami"""
    print("🗄️ Inicializujem databázu...")
    try:
        from adsun_launcher import ADSUNAgentLauncher
        launcher = ADSUNAgentLauncher()
        print("✅ Databáza pripravená")
        return True
    except Exception as e:
        print(f"❌ Chyba databázy: {e}")
        return False

def run_streamlit_app():
    """Spustenie Streamlit aplikácie"""
    print("🚀 Spúšťam ADSUN AI GUI...")
    print("🌐 Otvorí sa v prehliadači na http://localhost:8501")
    print("🔑 Pre AI reasoning zadajte OpenAI API kľúč v bočnom paneli")
    print("⏹️ Pre ukončenie stlačte Ctrl+C")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main_app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 ADSUN AI GUI ukončený")
    except Exception as e:
        print(f"❌ Chyba pri spúšťaní: {e}")

def main():
    """Hlavná funkcia launcher"""
    print("="*60)
    print("🎯 ADSUN AI Process Management - GUI Launcher")
    print("="*60)
    
    # Kontrola závislostí
    if not check_dependencies():
        print("\n📦 Inštalujem potrebné závislosti...")
        if not install_dependencies():
            print("❌ Nepodarilo sa nainštalovať závislosti")
            return
    
    # Setup databázy
    if not setup_database():
        print("⚠️ Databáza nebola správne inicializovaná")
    
    # Spustenie GUI
    run_streamlit_app()

if __name__ == "__main__":
    main() 