#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Knowledge Assistant - Inteligentný asistent pre vyhľadávanie procesov
Vylepšený s lepšími odpoveďami keď nič nenájde
"""

import sqlite3
import json
import re
import streamlit as st
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class ADSUNKnowledgeAssistant:
    """Inteligentný asistent pre vyhľadávanie v procesoch"""
    
    def __init__(self, db_path: str = "adsun_processes.db"):
        self.db_path = db_path
        self.min_confidence_threshold = 0.6  # Zvýšený práh spoľahlivosti
    
    def answer_query(self, query: str) -> str:
        """Hlavná funkcia pre zodpovedanie otázok s SKUTOČNOU AI analýzou"""
        
        query_lower = query.lower().strip()
        
        # SKUTOČNÁ AI ANALÝZA INTENTU
        intent, confidence = self._analyze_query_intent(query_lower)
        
        # DEBUG: Vypíš rozoznané intent (len pre vývoj)
        # print(f"🔍 AI ASSISTANT DEBUG: Query='{query}' → Intent='{intent}' (confidence={confidence})")
        
        # Ak nie je AI k dispozícii, skús základnú analýzu a dáta
        if intent == 'no_ai':
            return self._handle_no_ai_available(query)
        
        # Spracuj podľa AI rozpoznaného intentu
        if intent == 'statistics':
            return self._handle_statistics_query(query_lower)
        elif intent == 'departments':
            return self._handle_departments_query(query_lower)
        elif intent == 'list_all':
            return self._handle_list_query(query_lower)
        elif intent == 'find_process':
            return self._handle_process_query(query)
        elif intent == 'pricing':
            return self._handle_pricing_query(query)
        elif intent == 'people_roles':
            return self._handle_people_query(query)
        elif intent == 'categories':
            return self._handle_categories_query(query)
        elif intent == 'off_topic':
            return self._handle_off_topic_query(query)
        elif intent == 'general_search':
            return self._handle_general_search(query)
        else:
            return self._generate_ai_powered_response(query)
    
    def _analyze_query_intent(self, query: str) -> tuple:
        """SKUTOČNÁ AI analýza intentu otázky pomocou OpenAI API"""
        
        # Najprv načítame základné info o databáze
        db_context = self._get_database_context()
        
        try:
            from openai import OpenAI
            
            # Skontroluj API key
            api_key = os.environ.get('OPENAI_API_KEY') or st.session_state.get('openai_api_key')
            if not api_key:
                return ('no_ai', 0.0)
            
            # Vytvor OpenAI klienta
            client = OpenAI(api_key=api_key)
            
            # AI prompt pre analýzu intentu
            system_prompt = f"""Si expert na analýzu používateľských otázok o firemných procesoch. 

KONTEXT DATABÁZY:
{db_context}

Analyzuj otázku používateľa a rozhoduj ktorý typ odpovede potrebuje:

TYPY INTENTOV:
- "statistics" - chce ČÍSELNÉ štatistiky/počty (koľko, počet, stats, prehľad čísiel)
- "departments" - pýta sa na oddelenia/organizáciu
- "list_all" - chce ZOZNAM/VÝPIS konkrétnych položiek (všetky, zoznam, zobraz, vypis, ukáž)
- "find_process" - hľadá konkrétny proces (ako robiť niečo)
- "people_roles" - pýta sa na ľudí/pozície/zodpovednosti
- "pricing" - pýta sa na ceny/cenník
- "categories" - pýta sa na kategórie/typy
- "general_search" - všeobecné vyhľadávanie
- "off_topic" - otázka nesúvisí s firemými procesmi (osobné veci, jedlo, počasie...)

KĽÚČOVÉ ROZLÍŠENIE:
- "statistics" = chce POČTY, ČÍSLA: "koľko procesov", "počet", "stats"
- "list_all" = chce ZOZNAM NÁZVOV: "všetky procesy", "zoznam procesov", "vypis procesy", "ukáž procesy"

PRÍKLADY:
- "koľko procesov mám" → statistics (chce ČÍSLO)
- "ake procesy vypis zoznam" → list_all (chce ZOZNAM NÁZVOV)
- "všetky procesy" → list_all (chce ZOZNAM NÁZVOV)
- "zobraz procesy" → list_all (chce ZOZNAM NÁZVOV)
- "počet procesov" → statistics (chce ČÍSLO)

Odpoveď musí byť len jeden zo týchto typov. Rozlišuj presne medzi číslami a zoznamami!
"""

            user_prompt = f"Otázka používateľa: '{query}'"
            
            # Zavolaj OpenAI API
            response = client.chat.completions.create(
                model=st.session_state.get('ai_model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Nízka teplota pre konzistentné rozhodovanie
                max_tokens=50
            )
            
            ai_intent = response.choices[0].message.content.strip().lower()
            
            # Mapuj AI odpoveď na naše intenty
            intent_mapping = {
                'statistics': 'statistics',
                'departments': 'departments', 
                'list_all': 'list_all',
                'find_process': 'find_process',
                'people_roles': 'people_roles',
                'pricing': 'pricing',
                'categories': 'categories',
                'general_search': 'general_search',
                'off_topic': 'off_topic'
            }
            
            # Nájdi najlepší match
            for key, value in intent_mapping.items():
                if key in ai_intent:
                    return (value, 0.9)
            
            # Fallback
            return ('general_search', 0.6)
            
        except Exception as e:
            print(f"AI analýza zlyhala: {e}")
            # Fallback na jednoduchú analýzu len ako backup
            return self._simple_fallback_analysis(query)
    
    def _get_database_context(self) -> str:
        """Získa kontext databázy pre AI"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Počet procesov
                cursor = conn.execute("SELECT COUNT(*) FROM processes WHERE is_active = 1")
                process_count = cursor.fetchone()[0]
                
                # Kategórie
                cursor = conn.execute("SELECT category, COUNT(*) FROM processes WHERE is_active = 1 GROUP BY category LIMIT 5")
                categories = cursor.fetchall()
                
                # Vlastníci
                cursor = conn.execute("SELECT owner, COUNT(*) FROM processes WHERE is_active = 1 GROUP BY owner LIMIT 5")  
                owners = cursor.fetchall()
                
                context = f"""V databáze je:
- {process_count} procesov celkom
- Kategórie: {', '.join([f"{cat[0]} ({cat[1]}×)" for cat in categories]) if categories else 'žiadne'}
- Vlastníci: {', '.join([f"{owner[0]} ({owner[1]}×)" for owner in owners]) if owners else 'žiadni'}"""
                
                return context
        except:
            return "Databáza sa inicializuje..."
    
    def _simple_fallback_analysis(self, query: str) -> tuple:
        """Jednoduchá fallback analýza ak AI nefunguje"""
        query_lower = query.lower()
        
        # Veľmi základné rozoznávanie s lepšími slovak patterns
        if any(word in query_lower for word in ['koľko', 'kolko', 'počet', 'pocet', 'stats', 'štatistiky', 'statistiky']):
            return ('statistics', 0.8)
        elif any(word in query_lower for word in ['všetky', 'vsetky', 'zoznam', 'zobraz', 'ukaz', 'ukáž', 'vypis', 'vypiš', 'show', 'list']):
            return ('list_all', 0.8)
        elif any(word in query_lower for word in ['oddelen', 'divíz', 'organizác', 'struktur']):
            return ('departments', 0.7)
        elif any(word in query_lower for word in ['ako', 'proces', 'postup']):
            return ('find_process', 0.7)
        else:
            return ('general_search', 0.5)
    
    def _normalize_and_expand_query(self, query: str) -> str:
        """Normalizuje text a rozšíri synonymá pre lepšie porozumenie"""
        
        # Mapa synonym pre lepšie rozoznávanie
        synonyms = {
            # Počet/koľko
            'kolko': 'koľko', 'pocet': 'počet', 'count': 'počet',
            'stats': 'štatistiky', 'statistics': 'štatistiky',
            
            # Mám/máme  
            'mam': 'mám', 'mame': 'máme', 'mame': 'máme',
            
            # Procesy
            'process': 'proces', 'processes': 'procesy',
            
            # Ukáž/zobraz
            'ukaz': 'ukáž', 'show': 'zobraz', 'display': 'zobraz',
            
            # Všetky
            'vsetky': 'všetky', 'vsetko': 'všetko', 'all': 'všetky',
            
            # Kategórie
            'kategor': 'kategórie', 'category': 'kategórie', 'type': 'typ',
            
            # Databáza
            'databaz': 'databáza', 'database': 'databáza', 'db': 'databáza',
            
            # Oddelenia - nové synonymá
            'oddelen': 'oddelenie', 'oddeleni': 'oddelenia', 'department': 'oddelenie',
            'departments': 'oddelenia', 'diviz': 'divízia', 'divizia': 'divízia',
            'sekc': 'sekcia', 'section': 'sekcia', 'organizacia': 'organizácia',
            'struktur': 'štruktúra', 'org': 'organizácia',
            
            # Ako
            'how': 'ako', 'what': 'čo', 'who': 'kto', 'where': 'kde',
        }
        
        # Aplikuj synonymá
        for old, new in synonyms.items():
            query = query.replace(old, new)
        
        return query
    
    def _handle_departments_query(self, query: str) -> str:
        """Spracúva otázky o oddeleniach"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Skús najprv načítať z departments tabuľky
                try:
                    cursor = conn.execute("""
                        SELECT id, name, function, manager, staff_count, 
                               competencies, collaboration, tools, challenges
                        FROM departments 
                        ORDER BY name
                    """)
                    departments = [dict(row) for row in cursor.fetchall()]
                    
                    if departments:
                        response = f"""🏢 **ODDELENIA FIRMY** ({len(departments)} oddelení)

🎯 **PREHĽAD ODDELENÍ:**
"""
                        for dept in departments:
                            manager = dept.get('manager', 'Neurčený')
                            staff = dept.get('staff_count', 'Neurčené')
                            function = dept.get('function', 'Bez opisu')
                            
                            response += f"""
📂 **{dept['name']}**
• 👤 **Vedúci:** {manager}
• 👥 **Počet zamestnancov:** {staff}  
• 🎯 **Funkcia:** {function[:100]}{'...' if len(function) > 100 else ''}
"""
                        
                        response += f"""

💼 **ŠTATISTIKY:**
• **Celkom oddelení:** {len(departments)}
• **S definovaným vedúcim:** {len([d for d in departments if d.get('manager') and d['manager'] != 'Neurčený'])}
• **S popisom funkcií:** {len([d for d in departments if d.get('function') and d['function'] != 'Bez opisu'])}

💡 **Tip:** Spýtajte sa na konkrétne oddelenie pre detaily!"""
                        
                        return response
                        
                except sqlite3.OperationalError:
                    pass  # Tabuľka departments neexistuje
                
                # Fallback - analyzuj oddelenia z kategórií procesov
                cursor = conn.execute("""
                    SELECT category, COUNT(*) as process_count,
                           AVG(automation_readiness) as avg_automation,
                           GROUP_CONCAT(DISTINCT owner) as employees
                    FROM processes 
                    WHERE is_active = 1 AND category IS NOT NULL
                    GROUP BY category
                    ORDER BY process_count DESC
                """)
                dept_categories = [dict(row) for row in cursor.fetchall()]
                
                if not dept_categories:
                    return """🏢 **ODDELENIA FIRMY**

❌ **Žiadne oddelenia zatiaľ definované**

🎯 **Ako pridať oddelenia:**
1. **📚 Učenie procesov** - AI sa opýta na kategóriu
2. **🏢 Business Management → Oddelenia** - vytvorenie oddelenia
3. **Zadajte procesy** s kategóriami (obchod, HR, IT...)

💡 **Odporúčané oddelenia:** Obchod, Administratíva, Výroba, HR, IT, Marketing"""
                
                response = f"""🏢 **ODDELENIA FIRMY** (analýza z procesov)

🎯 **PREHĽAD ({len(dept_categories)} oddelení identifikovaných):**
"""
                
                total_processes = sum(cat['process_count'] for cat in dept_categories)
                
                for i, dept in enumerate(dept_categories, 1):
                    employees = dept['employees'].split(',') if dept['employees'] else []
                    avg_auto = dept['avg_automation'] or 0
                    
                    response += f"""
{i}. 📂 **{dept['category'].title()}**
   • 📋 **Procesy:** {dept['process_count']} ({dept['process_count']/total_processes*100:.1f}%)
   • 🤖 **Automatizácia:** {avg_auto:.1f}/5
   • 👥 **Ľudia:** {len(employees)} zamestnancov
   • 👤 **Tím:** {', '.join(employees[:3])}{'...' if len(employees) > 3 else ''}
"""
                
                response += f"""

💼 **CELKOVÉ ŠTATISTIKY:**
• **Identifikované oddelenia:** {len(dept_categories)}
• **Celkom procesov:** {total_processes}
• **Najväčšie oddelenie:** {dept_categories[0]['category']} ({dept_categories[0]['process_count']} procesov)
• **Najautomatizovanejšie:** {max(dept_categories, key=lambda x: x['avg_automation'] or 0)['category']} ({max(d['avg_automation'] or 0 for d in dept_categories):.1f}/5)

💡 **Tip:** Pre detailný prehľad oddelenia spýtajte sa: "Procesy oddelenia {dept_categories[0]['category']}" """
                
                return response
                
        except Exception as e:
            return f"""❌ **Chyba načítavania oddelení:** {e}

💡 **Skúste:**
• "Koľko procesov mám?" - celkové štatistiky
• "Všetky procesy" - kompletný zoznam
• Alebo prejdite do **🏢 Business Management → Oddelenia**"""
    
    def _handle_categories_query(self, query: str) -> str:
        """Spracúva otázky o kategóriách"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT category, COUNT(*) as count, 
                           AVG(duration_minutes) as avg_duration
                    FROM processes 
                    WHERE category IS NOT NULL AND is_active = 1
                    GROUP BY category 
                    ORDER BY count DESC
                """)
                categories = cursor.fetchall()
                
                if not categories:
                    return """📂 **KATEGÓRIE PROCESOV**

❌ **Žiadne kategórie zatiaľ**

🎯 **Pridajte prvé procesy:**
1. **📚 Učenie procesov** (sidebar)
2. **Zadajte kategóriu** pri vytváraní procesu
3. **AI si zapamätá** organizačnú štruktúru

💡 **Odporúčané kategórie:** Obchod, Administratíva, Výroba, HR, IT"""
                
                total_processes = sum(cat[1] for cat in categories)
                
                response = f"""📂 **KATEGÓRIE PROCESOV** ({len(categories)} typov)

🎯 **PREHĽAD ({total_processes} procesov celkom):**

"""
                
                for category, count, avg_duration in categories:
                    percentage = (count / total_processes * 100) if total_processes > 0 else 0
                    duration_text = f"{avg_duration:.0f}min priemer" if avg_duration else "bez časov"
                    
                    response += f"""**{category}:**
• {count} procesov ({percentage:.1f}%)
• {duration_text}

"""
                
                return response
                
        except Exception as e:
            return f"❌ **Chyba získavania kategórií:** {e}"
    
    def _handle_general_search(self, query: str) -> str:
        """Inteligentné všeobecné vyhľadávanie"""
        results = self._search_processes(query)
        
        if results and results[0][1] > 0.2:  # Veľmi nízky práh
            return self._format_results(results, query)
        
        # Ak nič nenašiel, skús rozložiť otázku
        return self._smart_search_suggestion(query)
    
    def _detect_query_type(self, query: str) -> str:
        """Detekuje typ otázky pre lepšie odpovede"""
        query_lower = query.lower()
        
        # Typy otázok
        if any(word in query_lower for word in ['proces', 'postup', 'kroky', 'ako sa rob', 'ako nacen']):
            return 'process_inquiry'
        elif any(word in query_lower for word in ['pozícia', 'pozície', 'práca', 'zamestnanci', 'tím', 'ľudia']):
            return 'position_inquiry'
        elif any(word in query_lower for word in ['cena', 'ceny', 'cenník', 'koľko stoj']):
            return 'pricing_inquiry'
        elif any(word in query_lower for word in ['systém', 'nástroj', 'software', 'aplikácia']):
            return 'system_inquiry'
        elif any(word in query_lower for word in ['štatistiky', 'počet', 'koľko', 'stats']):
            return 'statistics_inquiry'
        elif any(word in query_lower for word in ['všetky', 'zoznam', 'zobraz', 'ukáž']):
            return 'list_inquiry'
        else:
            return 'general_inquiry'
    
    def _generate_helpful_fallback(self, query: str, query_type: str, weak_results: List) -> str:
        """Generuje užitočné odpovede keď nič nenájde"""
        
        if query_type == 'process_inquiry':
            process_name = self._extract_process_name(query)
            return f"""❌ **Nenašiel som proces: "{query}"**

🎯 **Riešenie:**
1. **Kliknite "Učenie procesov"** v sidebar
2. **AI položí otázky** a naučí sa proces "{process_name}"
3. **Proces sa automaticky uloží** do databázy
4. **Potom môžete vyhľadávať** a dostanete presné odpovede

📋 **Aktuálne procesy:**
{self._get_available_processes_summary()}

💡 **Tip:** Najprv naučte AI vaše procesy pre najlepšie výsledky"""

        elif query_type == 'position_inquiry':
            return f"""👥 **Nenašiel som pozície: "{query}"**

🎯 **Riešenie:**
1. **Kliknite "Učenie procesov"**
2. **Popíšte prácu na pozícii** (úlohy, zodpovednosti)
3. **AI sa naučí kompetencie** a organizačnú štruktúru

💼 **Aktuálne pozície:**
{self._get_current_positions()}

💡 **Príklad:** Vytvorte proces "Práca obchodníka" a popíšte čo robí"""

        elif query_type == 'pricing_inquiry':
            return f"""💰 **Nenašiel som cenové info: "{query}"**

🎯 **Riešenie:**
1. **Vytvorte proces "Tvorba cenovej ponuky"**
2. **Popíšte faktory:** materiál, práca, marža
3. **AI si zapamätá** vašu metodiku nacenenia

📈 **Odporúčanie:** Začnite s najčastejším produktom/službou"""

        elif query_type == 'system_inquiry':
            return f"""🖥️ **Nenašiel som systémové info: "{query}"**

🎯 **Riešenie:**
1. **Pri učení procesov spomente nástroje** ktoré používate
2. **AI si zapamätá systémy** a ich použitie
3. **Môže navrhnúť automatizácie** a integrácie"""

        elif query_type == 'list_inquiry':
            return f"""📋 **Kompletný prehľad:**

{self._get_comprehensive_overview()}

💡 **Ďalšie kroky:**
• Spýtajte sa na konkrétny proces
• Použite "Učenie procesov" pre nové
• Skúste AI Assistant"""

        else:
            return f"""🤖 **Nerozumel som otázke: "{query}"**

🎯 **Skúste tiete otázky:**
• "Ako naceniť polep auta?"
• "Ukáž všetky procesy"  
• "Aké pozície máme?"
• "Kroky príjmu objednávky"

📊 **Stav systému:**
{self._get_available_processes_summary()}

💡 **Pomoc:** Kliknite "Učenie procesov" pre pridanie nových"""

    def _extract_process_name(self, query: str) -> str:
        """Extrahuje meno procesu z otázky"""
        # Odstráň otázovacie slová
        clean_query = re.sub(r'(ako|čo|kde|kedy|prečo|proces|postup|kroky)', '', query.lower())
        clean_query = clean_query.strip()
        return clean_query if clean_query else "tento proces"
    
    def _get_comprehensive_overview(self) -> str:
        """Získa kompletný prehľad systému"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Počet procesov
                cursor = conn.execute("SELECT COUNT(*) FROM processes WHERE is_active = 1")
                process_count = cursor.fetchone()[0]
                
                # Kategórie
                cursor = conn.execute("SELECT category, COUNT(*) FROM processes WHERE is_active = 1 GROUP BY category")
                categories = cursor.fetchall()
                
                # Vlastníci
                cursor = conn.execute("SELECT owner, COUNT(*) FROM processes WHERE is_active = 1 GROUP BY owner LIMIT 3")
                owners = cursor.fetchall()
                
                overview = f"""📊 **Celkom: {process_count} procesov**

📂 **Kategórie:**
{chr(10).join([f"• {cat[0]}: {cat[1]}×" for cat in categories]) if categories else "• Žiadne"}

👥 **Vlastníci:**
{chr(10).join([f"• {owner[0]}: {owner[1]}×" for owner in owners]) if owners else "• Žiadni"}"""
                
                return overview
        except:
            return "📊 **Systém sa inicializuje...**"
    
    def _get_available_processes_summary(self) -> str:
        """Získa zhrnutie dostupných procesov"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT name, category FROM processes WHERE is_active = 1 LIMIT 3")
                processes = cursor.fetchall()
                
                if processes:
                    return "\n".join([f"• {proc[0]} ({proc[1]})" for proc in processes])
                else:
                    return "• Zatiaľ žiadne - začnite prvým!"
        except:
            return "• Systém sa spúšťa..."
    
    def _get_current_positions(self) -> str:
        """Získa aktuálne pozície zo systému"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT DISTINCT owner FROM processes WHERE owner IS NOT NULL AND is_active = 1 LIMIT 3")
                positions = [row[0] for row in cursor.fetchall()]
                
                if positions:
                    return "\n".join([f"• {pos}" for pos in positions])
                else:
                    return "• Zatiaľ žiadne v systéme"
        except:
            return "• Databáza nedostupná"
    
    def _generate_error_response(self, query: str, query_type: str, error: str) -> str:
        """Generuje odpoveď pri chybe"""
        return f"""⚠️ **Technická chyba pri spracovaní otázky: "{query}"**

🔧 **Riešenie:**
• 🔄 Skúste otázku znovu  
• 📚 Skúste "Učenie procesov" v sidebar
• 🗄️ Skontrolujte databázové pripojenie

**🤖 AI je pripravený pomôcť hneď ako sa problém vyrieši!**

*Technické detaily: {error}*"""

    def _search_processes(self, query: str) -> List[Tuple[Dict, float]]:
        """Hľadá procesy v databáze s confidence scoring"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Základné vyhľadávanie
                cursor = conn.execute("""
                    SELECT * FROM processes 
                    WHERE (name LIKE ? OR category LIKE ? OR owner LIKE ? OR tags LIKE ?) 
                    AND is_active = 1
                    ORDER BY created_at DESC
                """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
                
                results = []
                for row in cursor.fetchall():
                    process = dict(row)
                    confidence = self._calculate_confidence(query, process)
                    results.append((process, confidence))
                
                # Zoraď podľa confidence
                results.sort(key=lambda x: x[1], reverse=True)
                return results
                
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _calculate_confidence(self, query: str, process: Dict) -> float:
        """Vypočíta confidence score pre relevantnosť procesu"""
        query_lower = query.lower()
        confidence = 0.0
        
        # Zhoda v názve (najvyššia váha)
        if process.get('name'):
            name_lower = process['name'].lower()
            if query_lower in name_lower:
                confidence += 0.8
            elif any(word in name_lower for word in query_lower.split()):
                confidence += 0.4
        
        # Zhoda v kategórii
        if process.get('category'):
            category_lower = process['category'].lower()
            if query_lower in category_lower:
                confidence += 0.3
        
        # Zhoda vo vlastníkovi
        if process.get('owner'):
            owner_lower = process['owner'].lower()
            if query_lower in owner_lower:
                confidence += 0.2
        
        # Zhoda v tags
        if process.get('tags'):
            tags_lower = process['tags'].lower()
            if query_lower in tags_lower:
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _format_results(self, results: List[Tuple[Dict, float]], query: str) -> str:
        """Formatuje výsledky vyhľadávania"""
        if not results:
            return f"Nenašiel som žiadne procesy pre: '{query}'"
        
        best_result = results[0]
        process, confidence = best_result
        
        # Základné info
        duration = process.get('duration_minutes', 0)
        duration_text = f"{duration} minút" if duration else "neurčené"
        
        response = f"""✅ **Proces nájdený: {process.get('name', 'Bez názvu')}**

📊 **Základné údaje:**
• **Kategória:** {process.get('category', 'Neurčené')}
• **Vlastník:** {process.get('owner', 'Neurčený')}
• **Trvanie:** {duration_text}
• **Automatizácia:** {process.get('automation_readiness', 'neurčené')}/5

🎯 **Proces:**
• **Spúšťač:** {process.get('trigger_type', 'Nie je definovaný')}
• **Úspech:** {process.get('success_criteria', 'Nie je definované')}

🤖 **AI hodnotenie:** Confidence {confidence:.1f} | Nájdených: {len(results)}"""
        
        return response
    
    def get_available_processes(self) -> str:
        """Vráti zoznam všetkých dostupných procesov"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT name, category, owner, duration_minutes 
                    FROM processes 
                    WHERE is_active = 1
                    ORDER BY category, name
                """)
                
                processes = cursor.fetchall()
                
                if not processes:
                    return """📋 **Žiadne procesy v databáze**

🎯 **Začnite:**
1. **Kliknite "Učenie procesov"** v sidebar
2. **AI vás povedie** vytvorením prvého procesu  
3. **Proces sa uloží** automaticky
4. **Potom môžete vyhľadávať**

💡 **Tip:** Začnite s procesom ktorý najčastejšie používate"""
                
                # Zoskup podľa kategórií
                by_category = {}
                for proc in processes:
                    cat = proc['category'] or 'Ostatné'
                    if cat not in by_category:
                        by_category[cat] = []
                    by_category[cat].append(proc)
                
                response = f"📋 **Dostupné procesy ({len(processes)}):**\n\n"
                
                for category, procs in by_category.items():
                    response += f"**{category}:**\n"
                    for proc in procs[:5]:  # Max 5 procesov na kategóriu
                        duration = f" ({proc['duration_minutes']}min)" if proc['duration_minutes'] else ""
                        owner = f" - {proc['owner']}" if proc['owner'] else ""
                        response += f"• {proc['name']}{owner}{duration}\n"
                    
                    if len(procs) > 5:
                        response += f"... a ďalších {len(procs) - 5}\n"
                    response += "\n"
                
                return response
                
        except Exception as e:
            return f"❌ **Chyba:** {e}" 

    def _handle_statistics_query(self, query: str) -> str:
        """Spracúva otázky o štatistikách a počtoch"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Základné štatistiky
                cursor = conn.execute("SELECT COUNT(*) FROM processes WHERE is_active = 1")
                total_processes = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(DISTINCT category) FROM processes WHERE category IS NOT NULL AND is_active = 1")
                total_categories = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(DISTINCT owner) FROM processes WHERE owner IS NOT NULL AND is_active = 1")
                total_owners = cursor.fetchone()[0]
                
                # KRÁTKA ODPOVEĎ BEZ EXTRA INFORMÁCIÍ
                if total_processes == 0:
                    return "0 procesov v databáze."
                
                response = f"Celkom: {total_processes} procesov"
                
                if total_categories > 0:
                    response += f", {total_categories} kategórií"
                    
                if total_owners > 0:
                    response += f", {total_owners} vlastníkov"
                
                # Pridaj top kategórie ak sú
                cursor = conn.execute("""
                    SELECT category, COUNT(*) as count 
                    FROM processes 
                    WHERE category IS NOT NULL AND is_active = 1 
                    GROUP BY category 
                    ORDER BY count DESC
                    LIMIT 3
                """)
                categories = cursor.fetchall()
                
                if categories:
                    response += "\n\nNajviac procesov:"
                    for cat, count in categories:
                        response += f"\n• {cat}: {count}"
                
                return response
                
        except Exception as e:
            return f"Chyba získavania štatistík: {e}"
    
    def _handle_list_query(self, query: str) -> str:
        """Spracúva otázky o zoznamoch"""
        
        # DEBUG: Info about list handling
        # print(f"🔍 LIST QUERY DEBUG: Handling list query '{query}'")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Zistí čo užívateľ chce - pre "ake procesy vypis zoznam" sa prioritne zobrazí zoznam procesov
                if any(word in query.lower() for word in ['proces', 'procesy', 'všetky', 'vsetky', 'zoznam', 'vypis', 'zobraz', 'ukaz']):
                    cursor = conn.execute("SELECT name, category, owner, duration_minutes FROM processes WHERE is_active = 1 ORDER BY created_at DESC")
                    items = cursor.fetchall()
                    
                    # print(f"🔍 LIST QUERY DEBUG: Found {len(items)} processes")
                    
                    if not items:
                        return "Žiadne procesy v databáze."
                    
                    # KRÁTKA ODPOVEĎ BEZ EXTRA INFORMÁCIÍ
                    response = f"Procesy ({len(items)}):\n"
                    
                    by_category = {}
                    for item in items:
                        cat = item['category'] or 'Ostatné'
                        if cat not in by_category:
                            by_category[cat] = []
                        by_category[cat].append(item)
                    
                    for category, procs in sorted(by_category.items()):
                        if category != 'Ostatné' or len(by_category) == 1:
                            response += f"\n{category}:\n"
                        for proc in procs:
                            duration = f" ({proc['duration_minutes']}min)" if proc['duration_minutes'] else ""
                            owner = f" - {proc['owner']}" if proc['owner'] else ""
                            response += f"• {proc['name']}{owner}{duration}\n"
                    
                    return response.rstrip()
                
                elif any(word in query for word in ['kategór', 'typ']):
                    cursor = conn.execute("SELECT category, COUNT(*) as count FROM processes WHERE category IS NOT NULL AND is_active = 1 GROUP BY category ORDER BY count DESC")
                    categories = cursor.fetchall()
                    
                    if not categories:
                        return "Žiadne kategórie."
                    
                    response = "Kategórie:\n"
                    for cat, count in categories:
                        response += f"• {cat}: {count}\n"
                    
                    return response.rstrip()
                
                elif any(word in query for word in ['vlastník', 'ľud', 'kto', 'pozíc']):
                    cursor = conn.execute("SELECT owner, COUNT(*) as count FROM processes WHERE owner IS NOT NULL AND is_active = 1 GROUP BY owner ORDER BY count DESC")
                    owners = cursor.fetchall()
                    
                    if not owners:
                        return "Žiadni vlastníci."
                    
                    response = "Vlastníci:\n"
                    for owner, count in owners:
                        response += f"• {owner}: {count}\n"
                    
                    return response.rstrip()
                
                else:
                    # Pre akúkoľvek inú otázku o liste - defaultne ukáž procesy
                    cursor = conn.execute("SELECT name, category, owner, duration_minutes FROM processes WHERE is_active = 1 ORDER BY created_at DESC")
                    items = cursor.fetchall()
                    
                    if not items:
                        return "Žiadne procesy."
                    
                    response = f"Procesy ({len(items)}):\n"
                    
                    by_category = {}
                    for item in items:
                        cat = item['category'] or 'Ostatné'
                        if cat not in by_category:
                            by_category[cat] = []
                        by_category[cat].append(item)
                    
                    for category, procs in sorted(by_category.items()):
                        if category != 'Ostatné' or len(by_category) == 1:
                            response += f"\n{category}:\n"
                        for proc in procs:
                            duration = f" ({proc['duration_minutes']}min)" if proc['duration_minutes'] else ""
                            owner = f" - {proc['owner']}" if proc['owner'] else ""
                            response += f"• {proc['name']}{owner}{duration}\n"
                    
                    return response.rstrip()
                    
        except Exception as e:
            # print(f"🔍 LIST QUERY ERROR: {e}")
            return f"Chyba: {e}"
    
    def _handle_process_query(self, query: str) -> str:
        """Spracúva otázky o konkrétnych procesoch - s AI inteligentným vyhľadávaním"""
        
        try:
            from openai import OpenAI
            
            # Skontroluj API key
            api_key = os.environ.get('OPENAI_API_KEY') or st.session_state.get('openai_api_key')
            if not api_key:
                return self._handle_no_ai_available(query)
            
            # Načítaj všetky procesy z databázy
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT id, name, category, owner, description, steps, 
                           duration_minutes, automation_readiness, tools, risks
                    FROM processes 
                    WHERE is_active = 1
                    ORDER BY created_at DESC
                """)
                processes = [dict(row) for row in cursor.fetchall()]
            
            if not processes:
                return """❌ **Žiadne procesy v databáze**

🎯 **Pridajte prvý proces:**
1. **📚 Učenie procesov** (sidebar)
2. Opíšte váš proces AI asistentovi
3. AI vytvorí proces automaticky"""
            
            # Vytvor OpenAI klienta
            client = OpenAI(api_key=api_key)
            
            # AI prompt pre inteligentné vyhľadávanie
            processes_list = "\n".join([f"- {p['name']} (kategória: {p['category']}, vlastník: {p['owner']})" for p in processes])
            
            system_prompt = f"""Si expert na vyhľadávanie firemných procesov. 

DOSTUPNÉ PROCESY:
{processes_list}

Používateľ hľadá proces. Nájdi NAJLEPŠÍ zhodný proces zo zoznamu na základe sémantického významu, nie presnej zhody textu.

Príklady inteligentného spojenia:
- "dopyt polep auta" = "objednávky zákazníkov" (oba sú o požiadavkách zákazníkov)
- "faktúra dodávateľa" = "fakturácia" (oba o fakturácii)
- "dovolenka zamestnanca" = "schvaľovanie dovoleniek" (oba o dovolenkách)

Odpoveď musí byť presný názov procesu zo zoznamu, alebo "NENÁJDENÝ" ak naozaj niečo podobné neexistuje."""
            
            user_prompt = f"Používateľ hľadá: '{query}'"
            
            # Zavolaj OpenAI API
            response = client.chat.completions.create(
                model=st.session_state.get('ai_model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            ai_match = response.choices[0].message.content.strip()
            
            # Nájdi zhodný proces
            found_process = None
            for process in processes:
                if ai_match.lower() in process['name'].lower() or process['name'].lower() in ai_match.lower():
                    found_process = process
                    break
            
            if found_process:
                return self._format_process_details(found_process, query)
            else:
                return f"""❌ **AI nenašlo proces pre: "{query}"**

🤖 **AI analýza:** "{ai_match}"

📋 **Dostupné procesy:**
{chr(10).join([f"• **{p['name']}** ({p['category']})" for p in processes[:5]])}

🎯 **Riešenie:**
• Skúste jednoduchšie: "objednávky", "faktúry", "dovolenky"  
• Alebo použite **📚 Učenie procesov** pre vytvorenie nového"""
                
        except Exception as e:
            return f"""❌ **Chyba AI vyhľadávania:** {e}

💡 **Fallback vyhľadávanie:**
{self._simple_process_search(query)}"""
    
    def _format_process_details(self, process: Dict, original_query: str) -> str:
        """Formatuje detaily nájdeného procesu"""
        
        duration = process.get('duration_minutes', 0) or 0
        duration_text = f"{duration} minút" if duration else "neurčené"
        
        automation = process.get('automation_readiness', 0) or 0
        
        response = f"""✅ **Proces nájdený pre: "{original_query}"**

# 📋 {process['name']}

## 🎯 Základné údaje
• **Kategória:** {process.get('category', 'Neurčené')}
• **Vlastník:** {process.get('owner', 'Neurčený')}  
• **Trvanie:** {duration_text}
• **Automatizácia:** {automation}/5

"""
        
        # Popis ak existuje
        if process.get('description'):
            response += f"""## 📝 Popis
{process['description']}

"""
        
        # Kroky ak existujú
        if process.get('steps'):
            response += f"""## 🔄 Kroky procesu
{process['steps']}

"""
        
        # Nástroje ak existujú
        if process.get('tools'):
            response += f"""## 🛠️ Používané nástroje
{process['tools']}

"""
        
        # Riziká ak existujú  
        if process.get('risks'):
            response += f"""## ⚠️ Riziká
{process['risks']}

"""
        
        response += """💡 **Potrebujete viac detailov?** Spýtajte sa konkrétne!"""
        
        return response
    
    def _simple_process_search(self, query: str) -> str:
        """Jednoduchý fallback search bez AI"""
        try:
            results = self._search_processes(query)
            if results and results[0][1] > 0.2:
                return self._format_process_details(results[0][0], query)
            else:
                return f"Nenašiel som podobný proces pre '{query}'"
        except:
            return "Chyba vyhľadávania"
    
    def _handle_pricing_query(self, query: str) -> str:
        """Spracúva cenové otázky"""
        return f"""💰 **CENOVÉ INFORMÁCIE**

❌ **Nenašiel som cenník pre: "{query}"**

🎯 **RIEŠENIE:**
1. **📚 Učenie procesov** → Vytvorte "Tvorba cenovej ponuky"
2. **Opíšte faktory:** materiál, práca, marža, čas
3. **AI si zapamätá** vašu metodiku

💡 **Príklad procesu:**
• Meranie plochy
• Výber materiálu  
• Výpočet práce
• Pridanie marže
• Finálna cena

🚀 **Potom budete môcť pýtať:** "Ako naceniť polep 50m²?"
"""
    
    def _handle_people_query(self, query: str) -> str:
        """Spracúva otázky o ľuďoch a pozíciách"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT owner, COUNT(*) as process_count, 
                           GROUP_CONCAT(DISTINCT category) as categories
                    FROM processes 
                    WHERE owner IS NOT NULL AND is_active = 1 
                    GROUP BY owner 
                    ORDER BY process_count DESC
                """)
                people = cursor.fetchall()
                
                if not people:
                    return """👥 **POZÍCIE A ZODPOVEDNOSTI**

❌ **Žiadne pozície zadefinované**

🎯 **RIEŠENIE:**
1. **📚 Učenie procesov** → Pri každom procese zadajte vlastníka
2. **AI si zapamätá** kto za čo zodpovedá
3. **Môžete sa pýtať** "Kto má na starosti marketing?"

💡 **Príklad:** Proces "Príjem objednávky" → Vlastník: "Obchodník"
"""
                
                response = "👥 **POZÍCIE A ZODPOVEDNOSTI:**\n\n"
                
                for person, count, categories in people:
                    cats = categories.split(',') if categories else []
                    unique_cats = list(set(cats))
                    response += f"**{person}:**\n"
                    response += f"• {count} procesov\n"
                    if unique_cats:
                        response += f"• Oblasti: {', '.join(unique_cats)}\n"
                    response += "\n"
                
                return response
                
        except Exception as e:
            return f"❌ **Chyba:** {e}"
    
    def _smart_search_suggestion(self, query: str) -> str:
        """Inteligentné návrhy keď vyhľadávanie zlyhá"""
        
        # Analyzuj slová v otázke
        words = query.lower().split()
        key_words = [w for w in words if len(w) > 3 and w not in ['ako', 'čo', 'kde', 'kedy', 'prečo', 'the', 'and', 'or']]
        
        if not key_words:
            return self._generate_intelligent_fallback(query)
        
        # Skús hľadať podobné procesy
        similar_suggestions = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                for word in key_words[:3]:  # Max 3 kľúčové slová
                    cursor = conn.execute("""
                        SELECT name, category FROM processes 
                        WHERE (name LIKE ? OR category LIKE ? OR owner LIKE ?) 
                        AND is_active = 1
                        LIMIT 3
                    """, (f"%{word}%", f"%{word}%", f"%{word}%"))
                    
                    similar = cursor.fetchall()
                    for proc in similar:
                        if proc['name'] not in [s['name'] for s in similar_suggestions]:
                            similar_suggestions.append(dict(proc))
        except:
            pass
        
        response = f"""🔍 **Hľadám: "{query}"**

❌ **Presný proces nenájdený**
"""
        
        if similar_suggestions:
            response += f"""
💡 **Možno ste mysleli:**
"""
            for proc in similar_suggestions[:3]:
                response += f"• **{proc['name']}** ({proc['category']})\n"
        
        response += f"""
🎯 **NÁVRHY PRE LEPŠIE VYHĽADÁVANIE:**
• **Skúste jednoduchšie:** napr. "polep auta" namiesto "ako naceniť polep auta"
• **Použite kľúčové slová:** "{' '.join(key_words[:2])}"
• **Spýtajte sa všeobecne:** "všetky procesy", "kategórie"

📚 **RIEŠENIE:**
1. **Kliknite "Učenie procesov"** ak proces neexistuje
2. **AI sa naučí nový proces** podľa vašich potrieb
3. **Potom budete môcť vyhľadávať** presne

🔍 **AI rozumie týmto otázkam:**
• "Koľko procesov mám?" (aj "pocet procesov zatial")
• "Všetky procesy" (aj "zobraz procesy")  
• "Aké kategórie?" (aj "typy procesov")
• "Kto za čo zodpovedá?" (aj "pozície ľudí")
"""
        
        return response
    
    def _generate_intelligent_fallback(self, query: str) -> str:
        """Vylepšený inteligentný fallback s analýzou otázky"""
        
        # Rozpoznaj čo používateľ možno chcel na základe slov v otázke
        query_words = query.lower().split()
        suggestions = []
        
        # Analýza možných intentov
        if any(word in query_words for word in ['koľko', 'kolko', 'počet', 'pocet', 'count', 'mám', 'mam']):
            suggestions.append("• **'Koľko procesov mám?'** - zobrazí presné čísla a štatistiky")
            suggestions.append("• **'Aké kategórie mám?'** - rozdelenie procesov podľa typov")
        
        if any(word in query_words for word in ['všetky', 'vsetky', 'zoznam', 'zobraz', 'ukaz', 'show']):
            suggestions.append("• **'Všetky procesy'** - kompletný zoznam všetkého")
            suggestions.append("• **'Aké kategórie'** - typy procesov")
        
        if any(word in query_words for word in ['kto', 'who', 'pozícia', 'pozicia', 'zodpoved']):
            suggestions.append("• **'Kto za čo zodpovedá?'** - organizačná štruktúra")
            suggestions.append("• **'Aké pozície máme?'** - zoznam rolí")
        
        if any(word in query_words for word in ['ako', 'how', 'proces', 'process', 'postup']):
            suggestions.append("• **'Ako naceniť polep auta?'** - hľadá konkrétny proces")
            suggestions.append("• **'Proces realizácie'** - konkrétne kroky")
        
        # Ak neboli rozpoznané žiadne patterny, daj všeobecné návrhy
        if not suggestions:
            suggestions = [
                "• **'Koľko procesov mám?'** - štatistiky a prehľad",
                "• **'Všetky procesy'** - kompletný zoznam", 
                "• **'Aké kategórie mám?'** - typy procesov",
                "• **'Kto za čo zodpovedá?'** - organizácia"
            ]
        
        return f"""🤖 **AI nerozoznal otázku: "{query}"**

💡 **INTELIGENTNÉ NÁVRHY:**
{chr(10).join(suggestions[:4])}

📊 **AKTUÁLNY STAV SYSTÉMU:**
{self._get_available_processes_summary()}

🎯 **AI ROZUMIE FLEXIBILNE:**
• **Rôzne formulácie:** "koľko procesov", "počet procesov", "mám nejaké procesy"
• **Synonymá:** "všetky"="vsetky", "ukáž"="zobraz", "kategórie"="typy"  
• **Bez diakritiky:** "kolko", "vsetky", "zobraz"
• **Angličtina:** "how many processes", "show all", "categories"

🚀 **POMOC:**
• **📚 Učenie procesov** - pridanie nových procesov pre AI
• **🤖 Inteligentné vyhľadávanie** - skúste rôzne formulácie

🔍 **AI sa stále učí rozumieť vašim otázkam lepšie!**
""" 

    def _handle_off_topic_query(self, query: str) -> str:
        """Spracuje otázky ktoré nesúvisia s firmou"""
        return f"""🤖 **"{query}"**

😊 Toto nie je o firemných procesoch. Som AI asistent pre vaše procesy a dokumentáciu.

💼 Spýtajte sa radšej na niečo o vašej firme!"""
    
    def _handle_no_ai_available(self, query: str) -> str:
        """Spracuje otázku keď AI nie je k dispozícii"""
        return f"""🤖 **AI Assistant potrebuje OpenAI API kľúč**

❌ **Nemôžem inteligentne analyzovať: "{query}"**

🔑 **Riešenie:**
1. **Zadajte OpenAI API kľúč** v bočnom paneli (🤖 AI Nastavenia)
2. **AI potom bude rozumieť** akejkoľvek otázke prirodzene
3. **Žiadne natvrdo naprogramované vzory** - skutočná AI komunikácia

💡 **Zatiaľ môžete skúsiť:**
• "Koľko procesov mám?" - základné štatistiky
• "Všetky procesy" - zoznam všetkého  
• Prejsť do **📚 Učenie procesov** pre pridanie dát

🚀 **S AI kľúčom bude rozumieť aj otázkam ako:**
• "Mám nejaké procesy v systéme?"
• "Ukáž mi čo môžem robiť"  
• "Organizácia firmy"
• Akejkoľvek inej formulácii!

{self._get_available_processes_summary()}"""
    
    def _generate_ai_powered_response(self, query: str) -> str:
        """Generuje AI-powered odpoveď pre komplikované otázky"""
        try:
            from openai import OpenAI
            
            # Skontroluj API key
            api_key = os.environ.get('OPENAI_API_KEY') or st.session_state.get('openai_api_key')
            if not api_key:
                return self._handle_no_ai_available(query)
            
            # Vytvor OpenAI klienta
            client = OpenAI(api_key=api_key)
            
            # Získaj dáta z databázy
            db_data = self._get_comprehensive_db_data()
            
            # AI prompt pre odpoveď
            system_prompt = f"""Si expert AI asistent pre firemné procesy. Odpovedaj prirodzene a užitočne.

DATABÁZA:
{db_data}

Odpovz na otázku používateľa na základe týchto dát. Ak niečo nevieš, navrhni ako to doplniť cez "Učenie procesov".
Odpoveď v slovenčine, používaj emotikoniky a markdown formátovanie."""
            
            user_prompt = f"Otázka: {query}"
            
            # Zavolaj OpenAI API
            response = client.chat.completions.create(
                model=st.session_state.get('ai_model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=st.session_state.get('ai_temperature', 0.7),
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return f"""🤖 **AI Analýza:**

{ai_response}

💡 **AI rozumie prirodzenej komunikácii!** Pýtajte sa ako chcete."""
            
        except Exception as e:
            return f"""❌ **AI chyba:** {e}

💡 **Skúste:**
• Jednoduchšie otázky: "Koľko procesov mám?"
• Použite **📚 Učenie procesov** pre pridanie dát
• Skontrolujte AI nastavenia v sidebari"""
    
    def _get_comprehensive_db_data(self) -> str:
        """Získa komplexné dáta z databázy pre AI"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Všetky procesy
                cursor = conn.execute("SELECT name, category, owner FROM processes WHERE is_active = 1 LIMIT 10")
                processes = [dict(row) for row in cursor.fetchall()]
                
                # Štatistiky
                cursor = conn.execute("SELECT COUNT(*) FROM processes WHERE is_active = 1")
                total = cursor.fetchone()[0]
                
                data = f"""PROCESY ({total} celkom):
"""
                for proc in processes:
                    data += f"- {proc['name']} (kategória: {proc['category']}, vlastník: {proc['owner']})\n"
                
                if total > 10:
                    data += f"... a ďalších {total - 10} procesov\n"
                
                return data
        except:
            return "Databáza sa načítava..." 