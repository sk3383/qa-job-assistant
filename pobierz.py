import requests
import json
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime

print("1/3 Pobieram NoFluffJobs...")

oferty = []
headers = {"User-Agent": "Mozilla/5.0"}

r = requests.get("https://nofluffjobs.com/pl/testing?criteria=remote", headers=headers, timeout=20)
soup = BeautifulSoup(r.text, "html.parser")

for a in soup.find_all("a", href=re.compile(r"/pl/job/"))[:30]:
    href = a.get("href")
    if not href:
        continue

    url = "https://nofluffjobs.com" + href
    title_raw = a.get_text(" ", strip=True)
    title = re.split(r'NOWA|\d{2}\s?\d{3}', title_raw)[0].strip()

    if not re.search(r'\b(qa|test|tester|quality|testing)\b', title, re.I):
        continue

    print(f" + {title}")

    try:
        pr = requests.get(url, headers=headers, timeout=12)
        ps = BeautifulSoup(pr.text, "html.parser")
        txt = ps.get_text("\n", strip=True)

        # FIRMA
        company_tag = ps.find("a", href=re.compile("/company/"))
        company = company_tag.get_text(strip=True) if company_tag else ""

        # PENSJA
        salary = ""
        sal = re.search(r'(\d{1,2}[\s\u202f]?\d{3}\s*[–-]\s*\d{1,2}[\s\u202f]?\d{3}\s*PLN)', txt)
        if sal:
            salary = sal.group(1).replace("\u202f", " ")

        # MIASTO
        miasto = "Zdalnie"
        loc = re.search(r'Praca zdalna\s*[-–\n ]+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+(?:,\s*[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)*)', txt)
        if loc:
            miasto = loc.group(1)

        # === WYMAGANE - NAPRAWIONE ===
        musts = []
        # metoda 1: wyciągnij blok po "Obowiązkowe"
        obow_match = re.search(r'Obowiązkowe\s*(.*?)\s*(?:Mile widziane|Nice to have|Benefity|Opis wymagań|Opis oferty)', txt, re.S | re.I)
        if obow_match:
            block = obow_match.group(1)
            lines = block.split("\n")
            for line in lines:
                clean = line.strip(" •-–\t")
                if 2 < len(clean) < 50 and not clean.lower().startswith("http"):
                    # odfiltruj śmieci
                    if clean.lower() not in ["apple", "windows", "notebook", "komputer"]:
                        musts.append(clean)
            musts = musts[:12]

        # metoda 2: fallback - szukaj technologii
        if not musts:
            techs = re.findall(r'\b(Selenium|Playwright|Cypress|Postman|JIRA|SQL|Python|Java|JavaScript|TypeScript|REST API|API testing|Test management|Testing|TestRail|ISTQB|Git|Jenkins|Docker|C#|Robot Framework|Azure|AWS)\b', txt, re.I)
            musts = list(dict.fromkeys([t.title() for t in techs]))

        # wyczyść
        musts = [m for m in musts if m.lower() not in ["apple", "windows", "notebook", "komputer", "praca zdalna"]]

        # === OPIS FIRMY z NoFluff ===
        firma_opis = ""
        o_firmie = ps.find(lambda t: t.name in ["h2", "h3"] and "O firmie" in t.get_text())
        if o_firmie:
            for sib in o_firmie.find_next_siblings()[:4]:
                if sib.name == "p":
                    firma_opis += sib.get_text(" ", strip=True) + " "

        if not firma_opis:
            opis = ps.find(lambda t: t.name in ["h2", "h3"] and "Opis oferty" in t.get_text())
            if opis:
                p = opis.find_next("p")
                if p:
                    firma_opis = p.get_text(" ", strip=True)

        if not firma_opis:
            firma_opis = f"{company} - firma IT"

        firma_opis = firma_opis[:280].strip()

        oferty.append({
            "title": title,
            "company": company,
            "url": url,
            "posted": datetime.now().strftime("%Y-%m-%d"),
            "salary": salary,
            "musts": musts,
            "nices": [],
            "firma_opis": firma_opis,
            "miasto": miasto
        })

        time.sleep(0.6)

    except Exception as e:
        print(f"! błąd: {e}")
        continue

print(f"\n - wybrano {len(oferty)} ofert")

with open("oferty.json", "w", encoding="utf-8") as f:
    json.dump(oferty, f, ensure_ascii=False, indent=2)

print("GOTOWE - uruchom: python raport.py")