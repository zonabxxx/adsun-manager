#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN System Launcher - Voľba medzi rôznymi interface
"""

import subprocess
import sys
import os

def show_menu():
    """Zobrazí menu na výber interface"""
    print("=" * 70)
    print("🎯 ADSUN AI Process Management System")
    print("=" * 70)
    print()
    print("Vyberte interface ktorý chcete spustiť:")
    print()
    print("1. 🤖 ADSUN AI Assistant (Kompletný systém)")
    print("   - AI učenie procesov")
    print("   - Dokumentovanie s rozhovorom")
    print("   - Pokročilé AI reasoning")
    print("   - Multi-režimové rozhranie")
    print("   - Port: 8501")
    print()
    print("2. 🗄️ ADSUN Airtable Manager (Clean chat)")
    print("   - Čistý chat interface")
    print("   - Fokus na Airtable")
    print("   - Rýchle otázky")
    print("   - Jednoduchý dizajn")
    print("   - Port: 8502")
    print()
    print("3. ⚙️ Konfigurácia API kľúčov")
    print("4. 🚪 Ukončiť")
    print()

def run_main_gui():
    """Spustí hlavný ADSUN AI GUI"""
    print("🚀 Spúšťam ADSUN AI Assistant...")
    try:
        subprocess.run([sys.executable, 'run_adsun_gui.py'])
    except Exception as e:
        print(f"❌ Chyba: {e}")

def run_airtable_manager():
    """Spustí Airtable Manager"""
    print("🗄️ Spúšťam ADSUN Airtable Manager...")
    try:
        subprocess.run([sys.executable, 'run_airtable_manager.py'])
    except Exception as e:
        print(f"❌ Chyba: {e}")

def setup_api_keys():
    """Pomôže s nastavením API kľúčov"""
    print("\n🔑 Konfigurácia API kľúčov")
    print("=" * 40)
    print()
    print("Pre plnú funkcionalitu potrebujete:")
    print()
    print("1. 🤖 OpenAI API Key:")
    print("   - Idite na: https://platform.openai.com/api-keys")
    print("   - Vytvorte nový API kľúč")
    print("   - Zadajte ho v aplikácii")
    print()
    print("2. 🗄️ Airtable API Key (voliteľné):")
    print("   - Idite na: https://airtable.com/create/tokens")
    print("   - Vytvorte Personal Access Token")
    print("   - Zadajte aj Base ID vašej databázy")
    print()
    print("💡 Tip: Aplikácia má pokročilé ukladanie API kľúčov")
    print("   - Zašifrované ukladanie")
    print("   - .env súbory")
    print("   - Automatické načítavanie")
    print()
    input("Stlačte Enter pre pokračovanie...")

def main():
    """Hlavná funkcia launcher"""
    while True:
        try:
            show_menu()
            choice = input("👉 Vaša voľba (1-4): ").strip()
            
            if choice == "1":
                run_main_gui()
            elif choice == "2":
                run_airtable_manager()
            elif choice == "3":
                setup_api_keys()
            elif choice == "4":
                print("👋 Ďakujeme za používanie ADSUN!")
                break
            else:
                print("❌ Neplatná voľba. Zadajte 1-4.")
                input("Stlačte Enter pre pokračovanie...")
            
        except KeyboardInterrupt:
            print("\n👋 Ukončené používateľom")
            break
        except Exception as e:
            print(f"❌ Chyba: {e}")
            input("Stlačte Enter pre pokračovanie...")

if __name__ == "__main__":
    main() 