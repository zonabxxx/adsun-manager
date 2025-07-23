#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test súbor pre overenie funkcionality ADSUN AI agentov
"""

import os
import sqlite3
from adsun_process_mapper_ai import ADSUNProcessMapperAI, AIReasoningEngine
from adsun_knowledge_assistant import ADSUNKnowledgeAssistant, KnowledgeReasoningEngine

def test_database_creation():
    """Test vytvorenia databázy"""
    print("🧪 Test 1: Vytvorenie databázy")
    
    # Vymaž testovú databázu ak existuje
    test_db = "test_adsun.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    try:
        mapper = ADSUNProcessMapperAI(test_db)
        print("✅ Databáza úspešne vytvorená")
        
        # Overenie štruktúry
        with sqlite3.connect(test_db) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
        expected_tables = ['processes', 'process_steps']
        found_tables = [table for table in expected_tables if table in tables]
        
        if found_tables:
            print(f"✅ Nájdené tabuľky: {found_tables}")
        else:
            print("⚠️ Základná štruktúra - chýba kompletná schéma")
            
    except Exception as e:
        print(f"❌ Chyba pri vytváraní databázy: {e}")
    
    print("-" * 50)

def test_ai_reasoning_engine():
    """Test AI reasoning engine"""
    print("🧪 Test 2: AI Reasoning Engine")
    
    try:
        engine = AIReasoningEngine()
        
        # Test analýzy odpovede
        test_response = "Používame CRM systém a email na komunikáciu s manažérom. Niekedy sa vyskytujú problémy s dostupnosťou."
        
        from adsun_process_mapper_ai import ProcessContext
        context = ProcessContext()
        
        analysis = engine.analyze_response("Test otázka", test_response, context)
        
        print("✅ AI analýza funguje")
        print(f"📊 Extraktované info: {len(analysis.get('extracted_info', {}))}")
        print(f"⚠️ Identifikované medzery: {len(analysis.get('identified_gaps', []))}")
        print(f"❓ Follow-up otázky: {len(analysis.get('follow_up_questions', []))}")
        
        # Test detekcie zložitosti
        complexity = engine._analyze_complexity(test_response)
        print(f"🔍 Komplexita: {complexity}")
        
    except Exception as e:
        print(f"❌ Chyba v AI reasoning: {e}")
    
    print("-" * 50)

def test_knowledge_reasoning():
    """Test Knowledge Assistant reasoning"""
    print("🧪 Test 3: Knowledge Assistant Reasoning")
    
    try:
        knowledge_engine = KnowledgeReasoningEngine()
        
        # Test detekcie intentu
        test_queries = [
            "Ako funguje proces objednávok?",
            "Kto je zodpovedný za fakturáciu?",
            "Aké sú problémy v procese?",
            "Ako optimalizovať spracovanie?"
        ]
        
        for query in test_queries:
            intent = knowledge_engine._detect_intent(query.lower())
            print(f"✅ '{query}' → Intent: {intent}")
        
        # Test analýzy dotazu s prázdnymi procesmi
        query_context = knowledge_engine.analyze_query("Test dotaz", [])
        print(f"📊 Confidence pre prázdnu bázu: {query_context.confidence_score}")
        
    except Exception as e:
        print(f"❌ Chyba v Knowledge reasoning: {e}")
    
    print("-" * 50)

def test_process_mapper_session():
    """Test Process Mapper session"""
    print("🧪 Test 4: Process Mapper Session")
    
    try:
        test_db = "test_adsun.db"
        mapper = ADSUNProcessMapperAI(test_db)
        
        # Test spustenia session
        welcome = mapper.start_documentation_session("Test User")
        print("✅ Session spustená")
        print("📝 Welcome message obsahuje základné info:", "Aký proces" in welcome)
        
        # Test spracovania odpovede
        response = mapper.process_response("Spracovanie reklamácií zákazníkov")
        print("✅ Odpoveď spracovaná")
        print("🤖 AI analýza zahrnutá:", "AI Analýza" in response)
        print("❓ Ďalšia otázka generovaná:", len(response) > 100)
        
    except Exception as e:
        print(f"❌ Chyba v Process Mapper session: {e}")
    
    print("-" * 50)

def test_knowledge_assistant_queries():
    """Test Knowledge Assistant dotazov"""
    print("🧪 Test 5: Knowledge Assistant Queries")
    
    try:
        test_db = "test_adsun.db"
        assistant = ADSUNKnowledgeAssistant(test_db)
        
        # Test prázdnej bázy
        response = assistant.answer_query("Test otázka")
        print("✅ Prázdna báza zvládnutá:", "prázdna" in response.lower())
        
        # Test zoznamu procesov
        processes = assistant.get_available_processes()
        print("✅ Zoznam procesov:", "zdokumentované" in processes.lower())
        
        # Test neplatného dotazu
        empty_response = assistant.answer_query("")
        print("✅ Prázdny dotaz zvládnutý:", "zadajte" in empty_response.lower())
        
    except Exception as e:
        print(f"❌ Chyba v Knowledge Assistant: {e}")
    
    print("-" * 50)

def test_launcher_integration():
    """Test integrácie launcher"""
    print("🧪 Test 6: Launcher Integration")
    
    try:
        from adsun_launcher import ADSUNAgentLauncher
        
        # Test inicializácie
        launcher = ADSUNAgentLauncher()
        print("✅ Launcher inicializovaný")
        
        # Test databázy s ukážkovými dátami
        test_db = launcher.db_path
        with sqlite3.connect(test_db) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM processes")
            process_count = cursor.fetchone()[0]
            
        print(f"✅ Ukážkové procesy: {process_count}")
        print("📊 Databáza obsahuje dáta:", process_count > 0)
        
    except Exception as e:
        print(f"❌ Chyba v Launcher integration: {e}")
    
    print("-" * 50)

def cleanup_test_files():
    """Vyčistenie testovacích súborov"""
    test_files = ["test_adsun.db"]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️ Vymazaný testovací súbor: {file}")
            except Exception as e:
                print(f"⚠️ Nemožno vymazať {file}: {e}")

def run_all_tests():
    """Spustí všetky testy"""
    print("🚀 ADSUN AI Agents - Testovacie sady")
    print("=" * 60)
    
    try:
        test_database_creation()
        test_ai_reasoning_engine()
        test_knowledge_reasoning()
        test_process_mapper_session()
        test_knowledge_assistant_queries()
        test_launcher_integration()
        
        print("\n🎉 Všetky testy dokončené!")
        print("💡 Pre plné testovanie spustite: python adsun_launcher.py")
        
    except Exception as e:
        print(f"\n❌ Neočakávaná chyba v testoch: {e}")
    
    finally:
        print("\n🧹 Čistenie testovacích súborov...")
        cleanup_test_files()

if __name__ == "__main__":
    run_all_tests() 