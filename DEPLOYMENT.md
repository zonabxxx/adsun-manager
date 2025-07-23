# 🚀 ADSUN - Návod na zdieľanie aplikácie

## 📋 Možnosti zdieľania

### 1️⃣ **STREAMLIT CLOUD (Najjednoduchšie - ODPORÚČANÉ)**

#### **Krok 1: Príprava kódu**
```bash
# Skontrolujte, že aplikácia funguje lokálne
python run_adsun_gui.py
```

#### **Krok 2: GitHub**
1. Vytvorte nový repozitár na GitHub
2. Nahrajte všetky súbory **OKREM** `.env` súboru
3. V `.env` máte citlivé API kľúče - nikdy ich nezdieľajte!

#### **Krok 3: Streamlit Cloud deployment**
1. Otvorte: https://share.streamlit.io/
2. Prihlásť sa cez GitHub
3. Kliknite "New app"
4. Vyberte váš GitHub repozitár
5. Main file: `main_app.py`
6. Kliknite "Deploy!"

#### **Krok 4: Nastavenie API kľúčov v cloude**
1. Po deployment kliknite "Settings" → "Secrets"
2. Pridajte: `OPENAI_API_KEY = your_api_key_here`
3. Reštartujte aplikáciu

### 2️⃣ **LOKÁLNE ZDIEĽANIE V SIETI**

```bash
# Spustite pre celú lokálnu sieť
streamlit run main_app.py --server.address 0.0.0.0 --server.port 8501
```

**Prístup pre ostatných:**
- Nájdite vašu IP adresu: `ifconfig` (Mac/Linux) alebo `ipconfig` (Windows)
- Ostatní prejdú na: `http://VASA_IP_ADRESA:8501`

### 3️⃣ **INÉ CLOUD PLATFORMY**

#### **Heroku:**
```bash
# Pridajte súbory
echo "web: streamlit run main_app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
echo "python-3.11.0" > runtime.txt

# Deploy
heroku create your-app-name
git push heroku main
```

#### **Railway.app:**
1. Prihlásť sa na railway.app
2. Importovať GitHub repo
3. Nastaviť environment variables
4. Deploy automaticky

## 🔐 Bezpečnosť

### **NIKDY nezdieľajte:**
- `.env` súbor
- `adsun_processes.db` (obsahuje vaše dáta)
- API kľúče v kóde

### **Pri zdieľaní:**
- Vytvorte novú databázu pre každé nasadenie
- Používajte environment variables pre API kľúče
- Nastavte prístupové práva ak potrebné

## 📝 Environment Variables na cloude

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🎯 Kroky pre úspešný deployment

1. ✅ Otestujte aplikáciu lokálne
2. ✅ Nahrajte kód na GitHub (bez .env)
3. ✅ Deployujte na Streamlit Cloud
4. ✅ Nastavte API kľúče v Secrets
5. ✅ Otestujte online verziu
6. ✅ Zdieľajte link s ostatnými

## 🔗 Výsledok

Po úspešnom deployment budete mať:
- **Verejnú URL:** `https://your-app-name.streamlit.app`
- **24/7 dostupnosť**
- **Automatické aktualizácie** pri zmene kódu
- **Bezplatné hosting**

## 🆘 Riešenie problémov

### **Aplikácia sa nenačítava:**
- Skontrolujte logs v Streamlit Cloud
- Overte, či sú správne nastavené API kľúče

### **Chýbajúce moduly:**
- Pridajte ich do `requirements.txt`
- Redeployujte aplikáciu

### **Databáza je prázdna:**
- Normálne - každé nasadenie začína s čistou databázou
- Dáta sa ukladajú v cloude oddelene od vašich lokálnych dát 