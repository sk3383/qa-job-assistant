# QA Job Assistant - Automatyzacja Aplikacji z Bielik LLM

Narzędzie dla testerów do automatycznej analizy ofert pracy i generowania spersonalizowanych CV/LM przy użyciu lokalnego modelu językowego Bielik.

## 🎯 Co robi?

- Pobiera aktualne oferty QA z JustJoin.it
- Analizuje dopasowanie Twoich umiejętności do wymagań
- Generuje raport HTML z rankingiem ofert
- Tworzy spersonalizowane CV i listy motywacyjne przez Bielik LLM (on-demand)
- Buduje ranking najpopularniejszych umiejętności na rynku

## 🛠️ Technologie

- **Python 3.10+** - requests, json, podstawy automatyzacji
- **Flask** - lokalne API do generowania PDF
- **ReportLab** - generowanie PDF z polskimi znakami
- **Bielik 11B** - lokalny LLM przez LM Studio
- **HTML/CSS** - interaktywny raport

## 📦 Instalacja

1. **Sklonuj repozytorium:**
```bash
git clone https://github.com/sk3383/qa-job-assistant.git
cd qa-job-assistant
```

2. **Zainstaluj zależności:**
```bash
pip install flask requests reportlab
```

3. **Skonfiguruj Bielika (LM Studio):**
   - Pobierz [LM Studio](https://lmstudio.ai/)
   - Discover > wyszukaj `bielik-11b-v2.3-instruct` (wersja Q4_K_M ~7GB)
   - Local Server > Port 1234 > Start Server
   - Ustawienia: Context Length 4096, Temperature 0.6

4. **Skonfiguruj swoje umiejętności** w `moje_skillz.json`:
```json
[
  "manual testing",
  "api testing",
  "postman",
  "rest api",
  "sql",
  "playwright",
  "jira",
  "git",
  "agile"
]
```

## 🚀 Uruchomienie

**WAŻNE: Potrzebujesz DWÓCH terminali**

**Terminal 1 - Serwer PDF (zostaw uruchomiony):**
```bash
python server.py
# [Running on http://127.0.0.1:5000]
```

**Terminal 2 - Generowanie raportu:**
```bash
python pobierz.py    # pobiera oferty z JustJoin.it
python raport.py     # tworzy raport.html
```
Otwórz `raport.html` w przeglądarce i klikaj przyciski LM/CV.

Nie zamykaj Terminala 1 podczas generowania PDF.

## 🔌 API

Serwer działa na `http://localhost:5000`

### `GET /pdf`
Generuje CV lub list motywacyjny

**Parametry:**
- `type` - `lm` lub `cv`
- `company` - nazwa firmy
- `title` - stanowisko

**Przykład:**
```
http://localhost:5000/pdf?type=lm&company=Google&title=QA+Engineer
```

### `GET /status`
Status serwera i cache

## 📁 Struktura projektu

```
├── pobierz.py           # Scraper JustJoin.it API
├── raport.py            # Generator raportu HTML
├── server.py            # API Flask do PDF
├── moje_skillz.json     # Twoje umiejętności
├── oferty.json          # Cache ofert (gitignored)
├── firmy_cache.json     # Cache opisów firm
├── cv/                  # Wygenerowane CV
├── lm/                  # Wygenerowane LM
└── fonts/               # Fonty DejaVu (auto-download)
```

## 🌐 Źródło danych

- **JustJoin.it API:** `https://api.justjoin.it/v2/user-panel/offers`
- Filtry w `pobierz.py`: kategoria `testing`, lokalizacje remote/hybrid/Polska

## 💡 Dlaczego powstał?

Jako tester manualny przeglądałem codziennie dziesiątki ofert. Zamiast robić to ręcznie:
1. Skrypt pobiera oferty i liczy dopasowanie skilli
2. Widzę od razu gdzie mam największe szanse
3. Bielik generuje spersonalizowane dokumenty w 5 sekund

Projekt do nauki automatyzacji, pracy z API i integracji LLM.

## 🔧 Troubleshooting

**"Błąd połączenia z localhost:5000"**
→ Uruchom `python server.py` w Terminalu 1

**"Błąd połączenia z localhost:1234"**
→ LM Studio > Local Server nie działa

**PDF z kwadratami zamiast ąęć**
→ usuń folder `fonts/`, uruchom ponownie server.py

**Wolne generowanie**
→ LM Studio > zmniejsz Context Length do 2048

**Wyczyść cache:**
```bash
del firmy_cache.json
rmdir /s /q cv lm
mkdir cv lm
```

## 📝 Licencja

MIT - używaj, modyfikuj, ucz się

## 🤝 Autor

Projekt edukacyjny - stworzony do nauki automatyzacji w QA
