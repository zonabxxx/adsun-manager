# 🎯 ADSUN AI Process Management System

Kompletný systém pre učenie, dokumentovanie a správu business procesov s umelou inteligenciou.

## 🚀 Spustenie aplikácie

### 🔘 Hlavný launcher (odporúčané)
```bash
python launcher.py
```

**Ponúka voľbu medzi:**
1. **🤖 ADSUN AI Assistant** - Kompletný systém s AI reasoning
2. **🗄️ ADSUN Airtable Manager** - Clean chat interface  
3. **⚙️ Konfigurácia API kľúčov** - Pomoc s nastavením

### 🔘 Priamo spustenie jednotlivých interface

**Kompletný ADSUN AI Assistant:**
```bash
python run_adsun_gui.py
# URL: http://localhost:8501
```

**Clean Airtable Manager:**
```bash
python run_airtable_manager.py  
# URL: http://localhost:8502
```

## 🌟 Interface možnosti

### 🤖 ADSUN AI Assistant (Port 8501)
- **AI-driven learning režim** - Inteligentné otázky pre dokumentovanie procesov
- **Assistant režim** - AI odpovede s predikciami a návrhmi
- **Pokročilé AI reasoning** - GPT-3.5-turbo analýza
- **Multi-database podpora** - SQLite + Airtable
- **Komplexný dizajn** - Karty, metriky, pokročilé funkcie

### 🗄️ ADSUN Airtable Manager (Port 8502)  
- **Clean chat interface** - Jednoduché a čisté rozhranie
- **Fokus na Airtable** - Optimalizované pre cloud databázu
- **Rýchle otázky** - Predefined buttony pre časté úlohy
- **Real-time chat** - Chat s dátami ako s assistantom
- **Minimalistický dizajn** - Inšpirované moderným UI

## 💾 Ukladanie API kľúčov

### 🔒 Tri spôsoby bezpečného ukladania:

**1. Zašifrované ukladanie (najbezpečnejšie)**
- AES-256 šifrovanie
- Vyžaduje heslo pri každom načítaní
- Ukladá sa do `~/.adsun/keys.enc`

**2. .env súbor (odporúčané)**
- Štandardný development spôsob
- Automaticky načítané pri spustení
- Súbor `.env` v projekte

**3. Lokálny config (testing)**
- Rýchle a jednoduché
- Uložené v `~/.adsun/config.json`
- Menej bezpečné

### 🔑 Potrebné API kľúče:

**OpenAI API Key (povinné pre AI):**
- Získať: https://platform.openai.com/api-keys
- Používa sa: GPT-3.5-turbo pre reasoning

**Airtable API (voliteľné):**
- Získať: https://airtable.com/create/tokens
- Base ID: ID vašej Airtable databázy
- Používa sa: Cloud synchronizácia procesov

## 🗄️ Databázová podpora

### Hybrid Database Manager
- **SQLite** - Lokálne ukladanie (default)
- **Airtable** - Cloud synchronizácia
- **Automatické fallback** - Ak Airtable zlyhá, použije SQLite
- **Real-time sync** - Okamžitá synchronizácia s cloud

### Airtable Setup
1. Vytvorte nový Airtable base
2. Vytvorte tabuľky: `Processes`, `Documentation Sessions`, `Process Steps`
3. Získajte Personal Access Token
4. Skopírujte Base ID z URL
5. Zadajte do aplikácie

## 🤖 AI Reasoning Engine

### Skutočné AI (s OpenAI API):
- **Analýza odpovedí** - Extrakcia systémov, ľudí, problémov
- **Inteligentné otázky** - Kontextové follow-up otázky
- **Automatizačný potenciál** - Hodnotenie 1-5 s odôvodnením
- **Predikcie** - Ďalšie otázky a akcie
- **JSON štruktúrované odpovede**

### Fallback režim (bez API):
- **Keyword analýza** - Základné rozpoznávanie
- **Preddefinované otázky** - Štandardné flow
- **Základné insights** - Algoritmická analýza

## 🎯 Funkcie systému

### 📚 Učenie procesov
- AI sa pýta inteligentné otázky
- Postupné budovanie kontextu
- Automatická analýza odpovedí
- Identifikácia automatizačného potenciálu

### 🤖 AI Assistant
- Chat s existujúcimi procesmi
- Predikcia ďalších otázok
- Odporúčané akcie
- Automatizačné možnosti

### 📊 Process Management
- Kategorizácia procesov
- Vlastníci a zodpovednosti
- Časové odhady
- KPI a metriky

### 💾 Persistent Storage
- Lokálne SQLite databáza
- Cloud Airtable synchronizácia
- Kompletná historia konverzácií
- Exportovateľné dáta

## 🔧 Inštalácia

### Požiadavky
```
Python 3.8+
streamlit>=1.28.0
openai>=1.3.0
cryptography>=41.0.0
requests>=2.31.0
pandas>=2.1.0
plotly>=5.17.0
```

### Setup
```bash
# 1. Klonujte/stiahnite projekt
git clone <repo> && cd adsun

# 2. Nainštalujte závislosti
pip install -r requirements.txt

# 3. Spustite launcher
python launcher.py

# Alebo priamo interface:
python run_adsun_gui.py        # Kompletný systém
python run_airtable_manager.py # Clean chat
```

## 🏗️ Architektúra

```
ADSUN System
├── 🎯 launcher.py                 # Hlavný menu launcher
├── 🤖 adsun_ai_gui.py            # Kompletný AI Assistant
├── 🗄️ adsun_airtable_manager.py  # Clean chat interface
├── 🔐 api_manager.py             # Bezpečné API kľúče
├── 🗄️ airtable_connector.py      # Cloud databáza
├── 🧠 AI reasoning modules       # OpenAI integrácia
└── 📊 Database managers          # SQLite + Hybrid
```

## 🎨 UI Design

### ADSUN AI Assistant
- **Moderný card-based layout**
- **Responsive dizajn**
- **Interaktívne elementy**
- **Profesionálne farby**

### Airtable Manager  
- **Clean minimalistický dizajn**
- **Chat-focused interface**
- **Rýchle action buttony**
- **Status indikátory**

## 🔒 Bezpečnosť

- **API kľúče nikdy v kóde**
- **Lokálne šifrovanie**
- **Session-based autentifikácia**
- **Oprávnenia pre súbory**

## 🚀 Použitie

1. **Spustite launcher:** `python launcher.py`
2. **Vyberte interface** podľa vašich potrieb
3. **Nastavte API kľúče** (jednorazovo)
4. **Začnite dokumentovať procesy!**

---

## 📞 Podpora

Pre otázky a problémy vytvorte issue alebo kontaktujte vývojový tím.

**🎯 ADSUN - Automatizujeme váš business!** 