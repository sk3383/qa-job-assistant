# QA Job Assistant – Bielik + NoFluffJobs

Automat dla testerów. Pobiera oferty QA z NoFluffJobs, liczy dopasowanie do Twoich skilli i generuje **PDF** (CV/LM) przez lokalnego Bielika.

## 🎯 Co robi?

- Scrapuje NoFluffJobs (remote testing)
- Wyciąga "Obowiązkowe" i opis firmy bezpośrednio z oferty
- Liczy % dopasowania do `moje_skillz.json`
- Pokazuje statystyki TOP technologii na rynku
- Generuje raport HTML z rankingiem
- **Na klik** tworzy PDF listu motywacyjnego lub CV przez Bielik 11B

## 🛠️ Stack

- Python 3.10+ – requests, BeautifulSoup
- http.server – lokalne API (port 8000)
- ReportLab – PDF z polskimi znakami (DejaVu)
- Bielik 11B v2.3 – LM Studio na porcie 1234
- HTML/CSS/JS – raport

## 📦 Instalacja

```bash
git clone https://github.com/TWOJ_NICK/bielik-qa-scraper.git
cd bielik-qa-scraper
pip install requests beautifulsoup4 reportlab
```

**LM Studio:**
1. Pobierz LM Studio
2. Model: `bielik-11b-v2.3-instruct` (Q4_K_M)
3. Local Server → Port **1234** → Start

**Twoje skille** – edytuj `moje_skillz.json`:
```json
{"skills": ["Manual Testing","Selenium","Playwright","API Testing","Postman","JIRA","SQL","Python"]}
```

## 🚀 Uruchomienie (2 terminale)

**Terminal 1 – serwer PDF:**
```bash
python server.py
# http://localhost:8000
```

**Terminal 2:**
```bash
python pobierz.py   # pobiera ~20 ofert
python raport.py    # tworzy raport.html
```

Otwórz: **http://localhost:8000/raport.html**
Kliknij **LM** lub **CV** → pobierze PDF.

## 📊 v1.3 – co nowego (29.05.2026)

- ✅ PDF generowany lokalnie (400-500 słów, akapity, justowanie)
- ✅ Statystyki TOP 12 technologii na górze raportu
- ✅ Parsowanie "Obowiązkowe" z NoFluffJobs – 100% trafność
- ✅ Opis firmy z oferty (bez AI)
- ✅ CORS fix – działa z przeglądarki
- ✅ Ranking dopasowania do Twoich skilli

## 📁 Struktura

```
pobierz.py       # scraper NoFluffJobs
raport.py        # generator HTML + statystyki
server.py        # API /lm i /cv → PDF
moje_skillz.json # Twoje umiejętności
oferty.json      # cache (gitignored)
fonts/           # DejaVu (auto-pobierane)
```

## 🔧 Troubleshooting

**Przyciski nie działają** → uruchom `server.py` i LM Studio
**Błąd OPTIONS 501** → masz starą wersję server.py – zaktualizuj
**Kwadraty zamiast ąę** → usuń folder `fonts/`, uruchom ponownie
**Za krótki tekst** → w LM Studio ustaw Context 4096, max_tokens 900

## 📝 Licencja

MIT
