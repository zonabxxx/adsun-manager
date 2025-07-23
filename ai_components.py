#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADSUN AI Components
AI reasoning engine a súvisiace funkcie
"""

import streamlit as st
import json
import os
from typing import Dict, Optional
from adsun_process_mapper_ai import ProcessContext

class RealAIReasoningEngine:
    """Skutočný AI reasoning engine s OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            try:
                # Try new OpenAI client first
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.ai_available = True
                self.use_new_client = True
            except:
                try:
                    # Fallback to old client
                    import openai
                    openai.api_key = self.api_key
                    self.ai_available = True
                    self.use_new_client = False
                except:
                    self.ai_available = False
        else:
            self.ai_available = False
    
    def analyze_response_with_ai(self, question: str, response: str, context: ProcessContext) -> Dict:
        """Analyzuje odpoveď pomocou skutočného AI"""
        if not self.ai_available:
            return self._fallback_analysis(response)
        
        try:
            # Priprav kontext pre AI
            context_info = {
                "previous_responses": len(getattr(context, 'conversation_history', [])),
                "mentioned_systems": getattr(context, 'mentioned_systems', []),
                "mentioned_people": getattr(context, 'mentioned_people', []),
                "complexity_score": getattr(context, 'complexity_score', 1)
            }
            
            # AI prompt pre analýzu
            prompt = f"""
Analyzuj túto odpoveď v kontexte dokumentovania business procesu:

OTÁZKA: {question}
ODPOVEĎ: {response}
KONTEXT: {json.dumps(context_info, ensure_ascii=False)}

Vráť JSON odpoveď s:
1. extracted_info: {{
   "systems": [zoznam spomenutých systémov],
   "people": [zoznam spomenutých ľudí/rolí], 
   "decisions": [rozhodnutia v procese],
   "problems": [spomenuté problémy],
   "frequency": [informácie o frekvencii]
}}
2. identified_gaps: [zoznam medzier v informáciách]
3. follow_up_questions: [3 inteligentné follow-up otázky]
4. complexity_indicators: [indikátory zložitosti procesu]
5. automation_potential: [hodnotenie 1-5 + odôvodnenie]
6. ai_insights: [kľúčové AI postrehy]

Odpovedaj POUZE v JSON formáte v slovenčine.
            """
            
            # Use appropriate client
            if self.use_new_client:
                response_ai = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Si expert na business proces analýzu. Odpovedáš presne a štruktúrovane v JSON formáte."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                ai_content = response_ai.choices[0].message.content
            else:
                import openai
                response_ai = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Si expert na business proces analýzu. Odpovedáš presne a štruktúrovane v JSON formáte."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.3
                )
                ai_content = response_ai.choices[0].message.content
            
            ai_analysis = json.loads(ai_content)
            ai_analysis['ai_powered'] = True
            return ai_analysis
            
        except Exception as e:
            st.error(f"❌ Chyba AI analýzy: {e}")
            return self._fallback_analysis(response)
    
    def _fallback_analysis(self, response: str) -> Dict:
        """Záložná algoritmická analýza"""
        # Základná keyword analýza
        keywords = {
            'systems': ['systém', 'aplikácia', 'nástroj', 'excel', 'email'],
            'people': ['manažér', 'vedúci', 'tím', 'zodpovedný'],
            'problems': ['problém', 'chyba', 'komplikácia']
        }
        
        extracted = {}
        for category, words in keywords.items():
            found = [word for word in words if word in response.lower()]
            if found:
                extracted[category] = found
        
        return {
            'extracted_info': extracted,
            'identified_gaps': ['Algoritmická analýza - potrebné AI pre hlbší insight'],
            'follow_up_questions': ['Môžete poskytnúť viac detailov?'],
            'complexity_indicators': ['basic_analysis'],
            'automation_potential': 'Vyžaduje AI analýzu',
            'ai_insights': ['Použitá záložná analýza bez AI'],
            'ai_powered': False
        }
    
    def generate_smart_question(self, context: ProcessContext, step: int) -> str:
        """Generuje inteligentné otázky pomocou AI"""
        if not self.ai_available:
            return self._fallback_question(step)
        
        # Pre logické otázky použijeme štruktúrovaný prístup
        process_name = getattr(context, 'name', 'tento proces')
        
        # Databázové polia ktoré potrebujeme vyplniť
        structured_questions = [
            f"**Do akej kategórie patrí proces '{process_name}'?** (Obchod, Výroba, HR, IT, Administratíva)",
            f"**Kto je zodpovedný** za proces '{process_name}'? (meno, pozícia)",
            f"**Čo spustí** proces '{process_name}'? (email klienta, telefón, osobný kontakt...)",
            f"**Ako často sa stáva** proces '{process_name}'? (denne, týždenne, mesačne, občas)",
            f"**Ako dlho trvá** proces '{process_name}' od začiatku do konca? (minúty, hodiny)",
            f"**Aká je priorita** procesu '{process_name}'? (vysoká, stredná, nízka) a prečo?",
            f"**Koľko prípadov** procesu '{process_name}' spracúvate za týždeň/mesiac?",
            f"**Aké sú kroky** procesu '{process_name}'? Popíšte stručne čo sa deje krok za krokom.",
            f"**Čo znamená úspech** pre proces '{process_name}'? Kedy je proces úspešne dokončený?",
            f"**Aké sú časté problémy** pri procese '{process_name}'? Čo sa môže pokaziť?",
            f"**Aké nástroje/systémy** používate pre proces '{process_name}'? (Excel, email, telefón...)",
            f"**Automatizačný potenciál:** Čo z procesu '{process_name}' by sa dalo zautomatizovať? (1-5, kde 5=všetko)"
        ]
        
        # Ak máme menej ako 12 krokov, použij štruktúrované otázky
        if step <= len(structured_questions):
            return structured_questions[step - 1]
        
        # Pre ďalšie kroky použij AI generovanie
        try:
            prompt = f"""
Proces: "{process_name}"
Krok: {step}
Kontext: {getattr(context, 'mentioned_systems', [])}

Vygeneruj 1 konkrétnu praktickú otázku o procese "{process_name}" ktorá:
- Vyplní chýbajúce detaily o procese
- Je špecifická pre oblasť polep/reklama/obchod
- Pomôže pochopiť proces lepšie
- Zistí praktické informácie

Odpoveď len otázka, nie JSON.
            """
            
            # Use appropriate client
            if self.use_new_client:
                response_ai = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Si expert na business procesy. Generuješ presné, praktické otázky."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.4
                )
                return response_ai.choices[0].message.content.strip()
            else:
                import openai
                response_ai = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Si expert na business procesy. Generuješ presné, praktické otázky."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.4
                )
                return response_ai.choices[0].message.content.strip()
            
        except Exception as e:
            st.error(f"❌ Chyba generovania otázky: {e}")
            return self._fallback_question(step)
    
    def _fallback_question(self, step: int) -> str:
        """Záložné otázky bez AI"""
        fallback_questions = [
            "Aký je nasledujúci krok v procese?",
            "Kto je za tento krok zodpovedný?",
            "Aké nástroje sa používajú?",
            "Aké sú časté problémy?",
            "Ako by sa dal proces zlepšiť?"
        ]
        return fallback_questions[min(step-1, len(fallback_questions)-1)]

    def generate_predictions(self, user_query: str) -> Dict:
        """Generuje AI predikcie a návrhy"""
        if not self.ai_available:
            return self._fallback_predictions()
        
        try:
            prediction_prompt = f"""
Na základe otázky: "{user_query}"

Vygeneruj 3 inteligentné predikcie a návrhy riešení pre ADSUN business procesy:

1. **Najbližšie otázky** - čo sa používateľ bude pýtať ďalej
2. **Odporúčané akcie** - konkrétne kroky na zlepšenie 
3. **Automatizačné možnosti** - ako by sa dal proces zautomatizovať

Odpoveď formatuj ako JSON:
{{
  "next_questions": ["otázka1", "otázka2", "otázka3"],
  "recommended_actions": ["akcia1", "akcia2", "akcia3"], 
  "automation_opportunities": ["možnosť1", "možnosť2", "možnosť3"]
}}
            """
            
            if self.use_new_client:
                pred_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Si expert na business procesy pre ADSUN. Generuješ predikcie a návrhy v JSON formáte."},
                        {"role": "user", "content": prediction_prompt}
                    ],
                    max_tokens=800,
                    temperature=0.4
                )
                return json.loads(pred_response.choices[0].message.content)
            else:
                import openai
                pred_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Si expert na business procesy pre ADSUN. Generuješ predikcie a návrhy v JSON formáte."},
                        {"role": "user", "content": prediction_prompt}
                    ],
                    max_tokens=800,
                    temperature=0.4
                )
                return json.loads(pred_response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"❌ Chyba AI predikcie: {e}")
            return self._fallback_predictions()
    
    def _fallback_predictions(self) -> Dict:
        """Záložné predikcie bez AI"""
        return {
            "next_questions": ["Aké sú kroky procesu?", "Kto je zodpovedný?", "Aký je čas realizácie?"],
            "recommended_actions": ["Zdokumentovať proces", "Definovať KPI", "Trénovať tím"],
            "automation_opportunities": ["Automatizovať notifikácie", "Digitalizovať formuláre", "Integrovať systémy"]
        } 