import requests, json, re, time, os
from datetime import datetime
import urllib3
urllib3.disable_warnings()

print("1/3 Pobieram NoFluffJobs (scraping)...")

oferty = []
try:
    url = "https://nofluffjobs.com/pl/testing?remote=true"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "pl-PL,pl;q=0.9"
    }
    r = requests.get(url, headers=headers, timeout=30)
    print(f" - status: {r.status_code}")

    # wyciągnij JSON z Next.js
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text, re.DOTALL)
    if not m:
        raise Exception("Nie znaleziono danych JSON")
    
    data = json.loads(m.group(1))
    # ścieżka do ofert w Next.js (zmienia się, więc szukamy rekurencyjnie)
    postings = []
    def find_postings(obj):
        if isinstance(obj, dict):
            if "postings" in obj and isinstance(obj["postings"], list):
                postings.extend(obj["postings"])
            for v in obj.values():
                find_postings(v)
        elif isinstance(obj, list):
            for item in obj:
                find_postings(item)
    find_postings(data)

    print(f" - znaleziono {len(postings)} ofert w JSON")

    for p in postings[:50]:
        title = p.get("title","")
        company = p.get("company",{}).get("name","")
        pid = p.get("id","")
        link = f"https://nofluffjobs.com/pl/job/{pid}"
        posted = p.get("posted","")[:10] or datetime.now().strftime("%Y-%m-%d")
        
        salary = ""
        if p.get("salary"):
            s = p["salary"]
            if s.get("from") and s.get("to"):
                salary = f"{s['from']//1000}-{s['to']//1000}k PLN"

        musts = []
        for tech in p.get("technology",{}).get("musts",[]):
            musts.append(tech.get("value",""))
        
        # filtr QA
        if not any(k in title.lower() for k in ["test","qa","quality"]):
            continue

        oferty.append({
            "title": title,
            "company": company,
            "url": link,
            "posted": posted,
            "salary": salary,
            "musts": musts[:8],
            "nices": [],
            "firma_opis": "",
            "miasto": "Remote"
        })

except Exception as e:
    print(f" BŁĄD: {e}")

print(f" - wybrano {len(oferty)} testing remote")

# zapisz
with open("oferty.json","w",encoding="utf-8") as f:
    json.dump(oferty, f, ensure_ascii=False, indent=2)

print(f"\nGOTOWE - {len(oferty)} ofert")
print("Uruchom: python raport.py")