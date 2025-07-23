# 🎯 ADSUN AI Process Management System

**Inteligentný systém na správu firemných procesov s AI podporou**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green?style=flat&logo=openai&logoColor=white)](https://openai.com/)

## 📋 Prehľad

ADSUN je moderný web-based systém na správu firemných procesov s pokročilými AI funkciami. Umožňuje firmám efektívne organizovať, analyzovať a optimalizovať svoje business procesy pomocou umelej inteligencie.

## 🚀 Hlavné funkcie

### 🤖 AI-Powered Features
- **Postupný AI sprievodca** - krok za krokom tvorba procesov s AI odporúčaniami
- **Bulk import z ChatGPT** - nahratie celej konverzácie a automatické parsovanie
- **Inteligentný AI asistent** - odpovedá na otázky o procesoch v slovenčine
- **Smart kategorizácia** - AI automaticky navrhuje kategórie a vylepšenia

### 📊 Process Management
- **Kompletná správa procesov** - vytváranie, editácia, mazanie, zobrazovanie
- **Detailné kroky procesov** - oddelené hlavné kroky a detailné popisy
- **Rizikové analýzy** - identifikácia problémov a návrhov riešení
- **Automatizačné hodnotenie** - posúdenie vhodnosti procesov na automatizáciu

### 🏢 Organizačná štruktúra
- **Správa oddelení** - organizácia procesov podľa oddelení
- **Riadenie pozícií** - definovanie rolí a zodpovedností
- **Vlastníci procesov** - priradenie zodpovedných osôb

### 📈 Analytics & Insights
- **Procesné štatistiky** - prehľady a metriky
- **Výkonnostné analýzy** - hodnotenie efektívnosti
- **Automatizačné odporúčania** - AI návrhy na zlepšenie

## 🛠️ Technické špecifikácie

### Tech Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.8+
- **Database**: SQLite (lokálne úložisko)
- **AI Engine**: OpenAI GPT-3.5-turbo/GPT-4
- **UI Framework**: Custom Streamlit components

### Architektúra
```
📁 ADSUN/
├── 🎯 main_app.py              # Hlavná aplikácia
├── 🧠 ai_components.py         # AI funkcionalita  
├── 💾 database_components.py   # Databázové operácie
├── 🎨 ui_components.py         # UI komponenty
├── 📊 process_management.py    # Správa procesov
├── 🏢 departments_management.py # Správa oddelení
├── 👥 positions_management.py  # Správa pozícií
├── 🤖 adsun_knowledge_assistant.py # AI asistent
└── 📋 requirements.txt         # Dependencies
```

## 🚀 Rýchly štart

### 1. Lokálne spustenie

```bash
# Clone repository
git clone https://github.com/zonabxxx/adsun-manager.git
cd adsun-manager

# Inštalácia závislostí
pip install -r requirements.txt

# Spustenie aplikácie
python run_adsun_gui.py
```

**Aplikácia sa otvorí na: http://localhost:8501**

### 2. Deploy na Streamlit Cloud

1. **Fork tento repozitár**
2. **Prejdite na [share.streamlit.io](https://share.streamlit.io/)**
3. **Pripojte GitHub repozitár**
4. **Main file**: `main_app.py`
5. **Pridajte OpenAI API kľúč v Secrets**:
   ```
   OPENAI_API_KEY = "your-api-key-here"
   ```
6. **Deploy!**

## 🔧 Konfigurácia

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Databáza
Systém automaticky vytvorí SQLite databázu `adsun_processes.db` pri prvom spustení.

## 📖 Používateľská príručka

### Vytvorenie procesu

#### Spôsob 1: Postupný sprievodca
1. Choďte do **"🎓 Tvorba procesov"**
2. Vyberte **"🔄 Postupný sprievodca"**
3. Vyplňte postupne všetky polia s AI pomocou
4. Uložte proces

#### Spôsob 2: Bulk import
1. Skopírujte ChatGPT konverzáciu o procese
2. Vyberte **"📥 Bulk import z ChatGPT"**
3. Vložte text konverzácie
4. AI automaticky extrahuje štruktúrované dáta
5. Upravte podľa potreby a uložte

### AI Asistent
- Choďte do **"🤖 AI Asistent"**
- Pýtajte sa otázky ako:
  - "Aké procesy máme?"
  - "Koľko procesov má oddelenie obchod?"
  - "Ktoré procesy majú najvyššiu prioritu?"

## 🎨 Screenshots

### Dashboard
![Dashboard](docs/dashboard.png)

### Process Creation
![Process Creation](docs/process-creation.png)

### AI Assistant
![AI Assistant](docs/ai-assistant.png)

## 🤝 Príspevky

Vítame príspevky od komunity! 

1. **Fork** repozitár
2. **Vytvorte** feature branch (`git checkout -b nova-funkcionalita`)
3. **Commit** zmeny (`git commit -am 'Pridaná nová funkcionalita'`)
4. **Push** do branch (`git push origin nova-funkcionalita`)
5. **Vytvorte** Pull Request

## 📝 Licencia

Tento projekt je licencovaný pod MIT licenciou - detaily v [LICENSE](LICENSE) súbore.

## 🆘 Podpora

### Dokumentácia
- [Deployment Guide](DEPLOYMENT.md)
- [API Documentation](docs/api.md)
- [User Manual](docs/manual.md)

### Kontakt
- **GitHub Issues**: [Nahlásiť problém](https://github.com/zonabxxx/adsun-manager/issues)
- **Email**: support@adsun.sk
- **Discord**: [ADSUN Community](https://discord.gg/adsun)

## 🏆 Autori

**ADSUN Development Team**
- Lead Developer: [@zonabxxx](https://github.com/zonabxxx)
- AI Specialist: ADSUN AI
- UX Designer: ADSUN Design

---

**⭐ Ak sa vám projekt páči, pridajte hviezdu na GitHub!**

[![GitHub stars](https://img.shields.io/github/stars/zonabxxx/adsun-manager.svg?style=social&label=Star)](https://github.com/zonabxxx/adsun-manager) 