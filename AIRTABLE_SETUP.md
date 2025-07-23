# 🌩️ ADSUN Airtable Setup Guide

## 📋 Prehľad

Tento návod vás prevedie nastavením Airtable integrácie pre ADSUN AI Process Management systém. Airtable ponúka pokročilé cloud funkcie, real-time collaboration a lepšie reporting možnosti ako lokálna SQLite databáza.

## 🚀 Výhody Airtable

- **🌐 Cloud storage** - dáta dostupné kdekoľvek
- **👥 Real-time collaboration** - viacero používateľov súčasne
- **📊 Pokročilé views** - kanban, kalendár, galéria, gantt
- **🔍 Smart filtrovanie** - automatické organizovanie
- **📱 Mobile app** - dokumentovanie v teréne
- **🔗 API integrácie** - prepojenie s inými systémami
- **📈 Reportovanie** - grafy, dashboardy, analytika

## 🛠️ Krok za krokom setup

### 1. Vytvorenie Airtable účtu

1. Idite na [airtable.com](https://airtable.com)
2. Zaregistrujte sa (free účet stačí)
3. Prihláste sa do vášho workspace

### 2. Vytvorenie Base

1. Kliknite na **"Create a base"**
2. Vyberte **"Start from scratch"**
3. Pomenujte base: `ADSUN Process Management`
4. Vyberte ikonu a farbu

### 3. Získanie API prístupových údajov

#### API Key:
1. Idite na [airtable.com/account](https://airtable.com/account)
2. V sekcii **"API"** kliknite **"Generate API key"**
3. Skopírujte API key (začína `key...`)

#### Base ID:
1. V Airtable otvorte váš base
2. Kliknite na **"Help"** (? ikona)
3. Vyberte **"API documentation"**
4. Na vrchu stránky nájdete Base ID (začína `app...`)

### 4. Vytvorenie tabuliek

Vytvorte v Airtable base tieto 3 tabuľky:

#### 📋 Tabuľka: "Processes"

| Pole | Typ | Nastavenia |
|------|-----|------------|
| Process Name | Single line text | - |
| Category | Single select | Options: obchod, HR, administratíva, IT, výroba |
| Owner | Single line text | - |
| Frequency | Single select | Options: denne, týždenne, mesačne, občas |
| Duration (min) | Number | Integer |
| Priority | Single select | Options: vysoká, stredná, nízka |
| Automation Readiness | Rating | Max: 5 |
| Success Criteria | Long text | - |
| Common Problems | Long text | - |
| Mentioned Systems | Multiple select | - |
| Created At | Created time | - |
| Updated At | Last modified time | - |

#### 📝 Tabuľka: "Documentation Sessions"

| Pole | Typ | Nastavenia |
|------|-----|------------|
| Process | Link to another record | Table: Processes |
| Documenter | Single line text | - |
| Step Number | Number | Integer |
| Question | Long text | - |
| Response | Long text | - |
| AI Analysis | Long text | - |
| AI Powered | Checkbox | - |
| Session Date | Date | Include time |
| Completeness Score | Rating | Max: 10 |

#### 🔧 Tabuľka: "Process Steps"

| Pole | Typ | Nastavenia |
|------|-----|------------|
| Process | Link to another record | Table: Processes |
| Step Number | Number | Integer |
| Step Title | Single line text | - |
| Description | Long text | - |
| Responsible Person | Single line text | - |
| System/Tool | Single line text | - |
| Estimated Time (min) | Number | Integer |
| Automation Potential | Rating | Max: 5 |
| Is Automated | Checkbox | - |

### 5. Automatizácia v Airtable (voliteľné)

#### Notifikácie:
1. V base kliknite na **"Automations"**
2. **"Create automation"**
3. Trigger: **"When record created"** v Processes
4. Action: **"Send email"** alebo **"Send Slack message"**

#### Auto-tagging:
1. Trigger: **"When record updated"** v Documentation Sessions
2. Condition: **"AI Powered = true"**
3. Action: **"Update record"** - pridaj tag "AI-Enhanced"

### 6. Views a filtre

#### Pre Processes tabuľku:
- **Grid view**: Všetky procesy
- **Kanban view**: Podle Priority
- **Calendar view**: Podle Created At
- **Gallery view**: Vizuálny prehľad

#### Pre Documentation Sessions:
- **Filtered view**: Len AI-powered sessions
- **Grouped view**: Podle Documenter
- **Timeline view**: Chronológia dokumentovania

## 🔧 Konfigurácia v ADSUN

1. Spustite ADSUN GUI: `python run_adsun_gui.py`
2. V bočnom paneli:
   - Vyberte **"Airtable (cloud)"**
   - Zadajte váš **API Key**
   - Zadajte váš **Base ID**
3. Kliknite **"Test connection"**
4. Pri úspešnom pripojení sa zobrazí ✅

## 📊 Možnosti využitia

### Reportovanie
- **Dashboard view** - KPI metriky
- **Chart extension** - grafy automatizácie
- **Timeline view** - progress dokumentovania

### Collaboration
- **Comments** - diskusia k procesom
- **Mentions** - notifikácie pre tím
- **Revision history** - sledovanie zmien

### Integrácie
- **Slack** - notifikácie o nových procesoch
- **Google Calendar** - plánovanie review
- **Zapier** - prepojenie s inými nástrojmi

## 🔒 Bezpečnosť

### API Key:
- Nikdy nezdieľajte váš API key
- Používajte environment variables
- Regenerujte key ak je kompromitovaný

### Permissions:
- Nastavte správne permissions v base
- Používajte workspace-level security
- Audit access logs pravidelne

## 🆘 Troubleshooting

### Chyba pripojenia:
```
❌ Airtable pripojenie neúspešné
```
**Riešenie:**
1. Skontrolujte API key
2. Overíte Base ID
3. Skontrolujte internet pripojenie
4. Skontrolujte Airtable service status

### Chýbajúce tabuľky:
```
❌ Table 'Processes' not found
```
**Riešenie:**
1. Vytvorte tabuľky presne podľa návodu
2. Skontrolujte názvy tabuliek (case-sensitive)
3. Skontrolujte Base ID

### Rate limiting:
```
❌ Airtable rate limit exceeded
```
**Riešenie:**
- Počkajte 30 sekúnd
- Redukujte počet API calls
- Upgradejte Airtable plan

## 💰 Pricing

| Plan | Cena | Records | API calls |
|------|------|---------|-----------|
| Free | $0 | 1,200/base | 5/sec |
| Plus | $12/user | 5,000/base | 5/sec |
| Pro | $24/user | 50,000/base | 10/sec |

**Odporúčanie:** Free plan stačí pre väčšinu use cases.

## 🔄 Migrácia z SQLite

Ak už máte dáta v SQLite a chcete prejsť na Airtable:

1. Vytvorte Airtable base podľa návodu
2. V ADSUN GUI prepnite na Airtable
3. Dáta sa automaticky uložia do Airtable pri ďalšom použití

**Poznámka:** Stará SQLite databáza zostane ako backup.

## 📞 Podpora

- **ADSUN Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Airtable Help**: [support.airtable.com](https://support.airtable.com)
- **API Docs**: [airtable.com/api](https://airtable.com/api)

---

✅ **Po dokončení setup-u budete mať moderný cloud-based process management systém s AI reasoning!** 