#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN Process Mapper s AI Reasoning
Inteligentný agent na dokumentovanie procesov s pokročilým premýšľaním
"""

import sqlite3
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class QuestionType(Enum):
    BASIC_INFO = "basic_info"
    PROCESS_FLOW = "process_flow"
    STAKEHOLDERS = "stakeholders"
    RESOURCES = "resources"
    PROBLEMS = "problems"
    AUTOMATION = "automation"
    OPTIMIZATION = "optimization"
    RELATIONSHIPS = "relationships"

@dataclass
class ProcessContext:
    """Kontext procesu pre AI reasoning"""
    name: Optional[str] = None
    category: Optional[str] = None
    complexity_score: int = 1  # 1-10
    automation_potential: int = 1  # 1-5
    identified_gaps: List[str] = None
    follow_up_areas: List[str] = None
    mentioned_systems: List[str] = None
    mentioned_people: List[str] = None
    decision_points: List[str] = None
    
    def __post_init__(self):
        if self.identified_gaps is None:
            self.identified_gaps = []
        if self.follow_up_areas is None:
            self.follow_up_areas = []
        if self.mentioned_systems is None:
            self.mentioned_systems = []
        if self.mentioned_people is None:
            self.mentioned_people = []
        if self.decision_points is None:
            self.decision_points = []

class AIReasoningEngine:
    """AI engine na analýzu a reasoning"""
    
    def __init__(self):
        self.context_keywords = {
            'systems': ['systém', 'aplikácia', 'nástroj', 'software', 'excel', 'email', 'crm', 'erp'],
            'people': ['manažér', 'vedúci', 'zodpovedný', 'tím', 'kolega', 'oddelenie'],
            'decisions': ['rozhodnutie', 'schválenie', 'posúdenie', 'kontrola', 'overenie'],
            'problems': ['problém', 'chyba', 'komplikácia', 'zdržanie', 'výnimka'],
            'frequency': ['denne', 'týždenne', 'mesačne', 'občas', 'pravidelne'],
            'automation': ['automaticky', 'manuálne', 'ručne', 'automatizácia']
        }
    
    def analyze_response(self, question: str, response: str, context: ProcessContext) -> Dict:
        """Analyzuje odpoveď a poskytne insights"""
        analysis = {
            'extracted_info': {},
            'identified_gaps': [],
            'follow_up_questions': [],
            'complexity_indicators': [],
            'automation_signals': []
        }
        
        response_lower = response.lower()
        
        # Extraktuj kľúčové informácie
        for category, keywords in self.context_keywords.items():
            found_items = []
            for keyword in keywords:
                if keyword in response_lower:
                    # Pokús sa extrahovať kontext okolo kľúčového slova
                    pattern = rf'.{{0,50}}{re.escape(keyword)}.{{0,50}}'
                    matches = re.findall(pattern, response_lower, re.IGNORECASE)
                    found_items.extend(matches)
            
            if found_items:
                analysis['extracted_info'][category] = found_items
        
        # Identifikuj medzery v informáciách
        analysis['identified_gaps'] = self._identify_gaps(response, context)
        
        # Generuj follow-up otázky
        analysis['follow_up_questions'] = self._generate_follow_up_questions(
            question, response, context, analysis['extracted_info']
        )
        
        # Analyzuj zložitosť
        analysis['complexity_indicators'] = self._analyze_complexity(response)
        
        # Analyzuj automatizačný potenciál
        analysis['automation_signals'] = self._analyze_automation_potential(response)
        
        return analysis
    
    def _identify_gaps(self, response: str, context: ProcessContext) -> List[str]:
        """Identifikuje medzery v informáciách"""
        gaps = []
        response_lower = response.lower()
        
        # Kontrola základných informácií
        if len(response) < 50:
            gaps.append("Odpoveď je príliš krátka - potrebujeme viac detailov")
        
        if 'neviem' in response_lower or 'nezáleží' in response_lower:
            gaps.append("Nejasné informácie - potrebuje upresnenie")
        
        if 'závisí' in response_lower:
            gaps.append("Podmienená logika - potrebujeme mapovať scenáre")
        
        if 'niekedy' in response_lower or 'občas' in response_lower:
            gaps.append("Neurčitá frekvencia - potrebuje kvantifikáciu")
        
        return gaps
    
    def _generate_follow_up_questions(self, original_question: str, response: str, 
                                    context: ProcessContext, extracted_info: Dict) -> List[str]:
        """Generuje inteligentné follow-up otázky"""
        follow_ups = []
        
        # Ak spomenul systémy, spýtaj sa na detaily
        if 'systems' in extracted_info:
            follow_ups.append("Aké konkrétne funkcie v týchto systémech používate?")
            follow_ups.append("Ako často sa tieto systémy pokazia alebo nefungujú?")
        
        # Ak spomenul ľudí, spýtaj sa na role
        if 'people' in extracted_info:
            follow_ups.append("Aké sú presné roly týchto ľudí v procese?")
            follow_ups.append("Čo sa stane, keď nie sú dostupní?")
        
        # Ak spomenul rozhodnutia, spýtaj sa na kritériá
        if 'decisions' in extracted_info:
            follow_ups.append("Podľa akých kritérií sa tieto rozhodnutia robia?")
            follow_ups.append("Kto má finálne slovo pri sporných prípadoch?")
        
        # Ak spomenul problémy, spýtaj sa na riešenia
        if 'problems' in extracted_info:
            follow_ups.append("Ako často sa tieto problémy vyskytujú?")
            follow_ups.append("Aké sú súčasné riešenia týchto problémov?")
        
        # Kontextové otázky na základe analýzy
        if 'manuálne' in response.lower():
            follow_ups.append("Čo konkrétne robíte manuálne a prečo nie je to automatizované?")
        
        if 'email' in response.lower():
            follow_ups.append("Aké informácie sa posielajú v emailoch a komu?")
        
        return follow_ups[:3]  # Maximálne 3 follow-up otázky
    
    def _analyze_complexity(self, response: str) -> List[str]:
        """Analyzuje zložitosť procesu"""
        indicators = []
        response_lower = response.lower()
        
        complexity_signals = [
            ('multiple systems', ['viac systémov', 'rôzne aplikácie', 'prepojenie']),
            ('decision branches', ['ak', 'podmienka', 'závisí od', 'rozhodnutie']),
            ('manual work', ['manuálne', 'ručne', 'osobne', 'telefonicky']),
            ('exceptions', ['výnimka', 'špeciálny prípad', 'niekedy inak']),
            ('approvals', ['schválenie', 'povolenie', 'súhlas', 'podpis'])
        ]
        
        for signal_type, keywords in complexity_signals:
            if any(keyword in response_lower for keyword in keywords):
                indicators.append(signal_type)
        
        return indicators
    
    def _analyze_automation_potential(self, response: str) -> List[str]:
        """Analyzuje potenciál pre automatizáciu"""
        signals = []
        response_lower = response.lower()
        
        # Pozitívne signály pre automatizáciu
        automation_positive = [
            'rovnaké kroky', 'štandardný postup', 'vždy rovnako',
            'jednoduché pravidlá', 'digitálne dáta'
        ]
        
        # Negatívne signály pre automatizáciu
        automation_negative = [
            'ľudské posúdenie', 'kreatívne riešenie', 'individuálny prístup',
            'komplexné rozhodnutie', 'výnimky'
        ]
        
        positive_count = sum(1 for signal in automation_positive if signal in response_lower)
        negative_count = sum(1 for signal in automation_negative if signal in response_lower)
        
        if positive_count > negative_count:
            signals.append("Vysoký automatizačný potenciál")
        elif negative_count > positive_count:
            signals.append("Vyžaduje ľudské posúdenie")
        else:
            signals.append("Čiastočná automatizácia možná")
        
        return signals

class ADSUNProcessMapperAI:
    """Hlavný agent s AI reasoning pre dokumentovanie procesov"""
    
    def __init__(self, db_path: str = "adsun_processes.db"):
        self.db_path = db_path
        self.ai_engine = AIReasoningEngine()
        self.current_context = ProcessContext()
        self.conversation_history = []
        self.init_database()
    
    def init_database(self):
        """Inicializuje databázu"""
        with sqlite3.connect(self.db_path) as conn:
            # Načítaj schému z SQL súboru
            try:
                with open('database_schema.sql', 'r', encoding='utf-8') as f:
                    conn.executescript(f.read())
            except FileNotFoundError:
                print("⚠️  Súbor database_schema.sql nebol nájdený. Vytváram základnú štruktúru...")
                self._create_basic_schema(conn)
    
    def _create_basic_schema(self, conn):
        """Vytvorí základnú databázovú štruktúru"""
        # Zjednodušená verzia schémy
        conn.execute('''
            CREATE TABLE IF NOT EXISTS processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def start_documentation_session(self, documenter_name: str) -> str:
        """Spustí novú dokumentačnú session"""
        self.current_context = ProcessContext()
        self.conversation_history = []
        
        welcome_message = f"""
🎯 **ADSUN Process Mapper AI** 
Vitajte {documenter_name}! Som inteligentný agent na dokumentovanie procesov.

Použijem pokročilé AI reasoning na:
✅ Analýzu vašich odpovědí v kontexte
✅ Identifikáciu medzier v informáciách  
✅ Generovanie inteligentných follow-up otázok
✅ Hodnotenie automatizačného potenciálu
✅ Navrhovanie optimalizácií

Začnime prvou otázkou:

**Aký proces chcete zdokumentovať?** 
(Stručne opíšte, o čo ide - napr. "Spracovanie objednávok zákazníkov")
        """
        return welcome_message
    
    def process_response(self, response: str) -> str:
        """Spracuje odpoveď s AI reasoning"""
        if not response.strip():
            return "⚠️ Prosím, zadajte odpoveď aby som mohol pokračovať."
        
        # Uložiť do histórie
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'response': response,
            'context': self.current_context.__dict__.copy()
        })
        
        # Určiť typ otázky na základe histórie
        current_question_type = self._determine_current_question_type()
        
        # AI analýza odpovede
        ai_analysis = self.ai_engine.analyze_response(
            self._get_last_question(), response, self.current_context
        )
        
        # Aktualizovať kontext na základe analýzy
        self._update_context_from_analysis(ai_analysis)
        
        # Generovať ďalšiu otázku alebo ukončiť
        next_question = self._generate_next_question(ai_analysis, current_question_type)
        
        # Pridať AI insights
        ai_insights = self._format_ai_insights(ai_analysis)
        
        return f"{ai_insights}\n\n{next_question}"
    
    def _determine_current_question_type(self) -> QuestionType:
        """Určí typ aktuálnej otázky na základe histórie"""
        step = len(self.conversation_history)
        
        if step == 1:
            return QuestionType.BASIC_INFO
        elif step <= 3:
            return QuestionType.PROCESS_FLOW
        elif step <= 5:
            return QuestionType.STAKEHOLDERS
        elif step <= 7:
            return QuestionType.RESOURCES
        elif step <= 9:
            return QuestionType.PROBLEMS
        elif step <= 11:
            return QuestionType.AUTOMATION
        else:
            return QuestionType.OPTIMIZATION
    
    def _get_last_question(self) -> str:
        """Získa poslednú položenú otázku"""
        # V reálnej implementácii by sme sledovali otázky
        return "Predchádzajúca otázka"
    
    def _update_context_from_analysis(self, analysis: Dict):
        """Aktualizuje kontext na základe AI analýzy"""
        extracted = analysis.get('extracted_info', {})
        
        # Aktualizuj spomenuté systémy
        if 'systems' in extracted:
            self.current_context.mentioned_systems.extend(extracted['systems'])
        
        # Aktualizuj spomenutých ľudí
        if 'people' in extracted:
            self.current_context.mentioned_people.extend(extracted['people'])
        
        # Aktualizuj medzery
        self.current_context.identified_gaps.extend(analysis.get('identified_gaps', []))
        
        # Aktualizuj skóre zložitosti
        complexity_indicators = len(analysis.get('complexity_indicators', []))
        self.current_context.complexity_score = min(10, max(1, complexity_indicators * 2))
    
    def _generate_next_question(self, analysis: Dict, question_type: QuestionType) -> str:
        """Generuje ďalšiu inteligentnú otázku"""
        step = len(self.conversation_history)
        
        # Špecializované otázky na základe analýzy
        if analysis.get('follow_up_questions'):
            return f"**AI Follow-up otázka:**\n{analysis['follow_up_questions'][0]}"
        
        # Štandardné otázky podľa typu
        questions_map = {
            QuestionType.BASIC_INFO: [
                "Do akej kategórie tento proces patrí? (obchod/výroba/administratíva/IT/HR)",
                "Kto je hlavný vlastník tohto procesu?",
                "Ako často sa tento proces vykonáva?"
            ],
            QuestionType.PROCESS_FLOW: [
                "Popíšte mi prvý krok tohto procesu - čo presne sa deje?",
                "Aký je nasledujúci krok? Kto ho vykonáva a v akom systéme?",
                "Sú v procese nejaké rozhodnutia alebo vetvenia?"
            ],
            QuestionType.STAKEHOLDERS: [
                "Kto všetko je zapojený do tohto procesu?",
                "Aké sú ich konkrétne role a zodpovednosti?",
                "Komu sa výsledky procesu komunikujú?"
            ],
            QuestionType.RESOURCES: [
                "Aké systémy a nástroje sa používajú?",
                "Aké dokumenty alebo šablóny potrebujete?",
                "Sú nejaké externé závislosti?"
            ],
            QuestionType.PROBLEMS: [
                "Aké sú najčastejšie problémy v tomto procese?",
                "Ako často sa vyskytujú chyby alebo zdržania?",
                "Ako sa tieto problémy riešia?"
            ],
            QuestionType.AUTOMATION: [
                "Ktoré časti procesu sú už automatizované?",
                "Čo sa robí manuálne a prečo?",
                "Aké vidíte možnosti pre automatizáciu?"
            ],
            QuestionType.OPTIMIZATION: [
                "Čo by sa dalo v procese zlepšiť?",
                "Aké sú najväčšie úzke miesta?",
                "Ako by vyzeral ideálny stav tohto procesu?"
            ]
        }
        
        # Ukončenie po dostatočnom množstve informácií
        if step > 12:
            return self._generate_summary()
        
        questions = questions_map.get(question_type, ["Pokračujme ďalej..."])
        question_index = min(len(questions) - 1, (step - 1) % len(questions))
        
        return f"**{question_type.value.replace('_', ' ').title()}:**\n{questions[question_index]}"
    
    def _format_ai_insights(self, analysis: Dict) -> str:
        """Formatuje AI insights pre užívateľa"""
        insights = ["🤖 **AI Analýza:**"]
        
        # Extraktované informácie
        extracted = analysis.get('extracted_info', {})
        if extracted:
            insights.append("📊 **Identifikované:**")
            for category, items in extracted.items():
                if items:
                    insights.append(f"   • {category.title()}: {len(items)} položiek")
        
        # Medzery v informáciách
        gaps = analysis.get('identified_gaps', [])
        if gaps:
            insights.append("⚠️ **Potrebuje upresnenie:**")
            for gap in gaps[:2]:  # Maximálne 2 medzery
                insights.append(f"   • {gap}")
        
        # Automatizačný potenciál
        automation = analysis.get('automation_signals', [])
        if automation:
            insights.append(f"🚀 **Automatizácia:** {automation[0]}")
        
        return "\n".join(insights) if len(insights) > 1 else ""
    
    def _generate_summary(self) -> str:
        """Generuje záverečné zhrnutie s odporúčaniami"""
        return f"""
🎉 **Dokumentácia procesu je kompletná!**

📋 **Zhrnutie AI analýzy:**
• **Zložitosť procesu:** {self.current_context.complexity_score}/10
• **Spomenuté systémy:** {len(self.current_context.mentioned_systems)}
• **Zapojené osoby:** {len(self.current_context.mentioned_people)}
• **Identifikované medzery:** {len(self.current_context.identified_gaps)}

🚀 **AI Odporúčania:**
• Začnite automatizáciou najjednoduchších krokov
• Zamerajte sa na odstránenie manuálnych úloh
• Zvážte integráciu spomenutých systémov

**Chcete pokračovať s dokumentovaním ďalšieho procesu? (áno/nie)**
        """

# Spustenie aplikácie
if __name__ == "__main__":
    mapper = ADSUNProcessMapperAI()
    
    print("=== ADSUN Process Mapper AI ===")
    documenter = input("Zadajte vaše meno: ")
    
    print(mapper.start_documentation_session(documenter))
    
    while True:
        user_input = input("\n👤 Vaša odpoveď: ")
        
        if user_input.lower() in ['quit', 'exit', 'koniec', 'ukončiť']:
            print("🔚 Dokumentácia ukončená. Ďakujem!")
            break
        
        response = mapper.process_response(user_input)
        print(f"\n🤖 {response}") 