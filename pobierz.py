import requests, json, re, time, os
from datetime import datetime
import urllib3
urllib3.disable_warnings()

print("1/3 Wczytuje RSS...")
xml = open("test3.xml", encoding="utf-8", errors="ignore").read()
items = re.findall(r'<item>(.*?)</item>', xml, re.DOTALL)
print(f" - znaleziono {len(items)} ofert")

oferty = []
for block in items:
    title = re.search(r'<title>(.*?)</title>', block, re.DOTALL)
    link = re.search(r'<link>(.*?)</link>', block)
    date = re.search(r'<pubDate>(.*?)</pubDate>', block)
    desc = re.search(r'<description>(.*?)</description>', block, re.DOTALL)
    if not title or not link: continue
    t = title.group(1).replace("&amp;","&").strip()
    l = link.group(1).strip()
    d = desc.group(1).lower() if desc else ""
    if not any(k in t.lower() for k in ["test","qa","tester","quality"]): continue
    if "remote" not in l.lower() and "remote" not in d and "zdaln" not in d: continue
    title_clean, company = (t.split(" @ ",1)+[""])[:2]
    try: posted = datetime.strptime(date.group(1), "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d")
    except: posted = datetime.now().strftime("%Y-%m-%d")
    oferty.append({"title": title_clean,"company": company,"url": l,"posted": posted,"salary": "","musts": [],"nices": [],"firma_opis": "","miasto": ""})
    if len(oferty) >= 50: break
print(f" - wybrano {len(oferty)} testing remote")

print("\n2/3 Pobieram szczegoly...")
s = requests.Session(); s.headers.update({"User-Agent":"Mozilla/5.0"}); s.verify=False
for i,o in enumerate(oferty,1):
    time.sleep(1)
    try:
        h = s.get(o["url"], timeout=20).text
        m = re.search(r'"salary":\{"from":(\d+),"to":(\d+),"currency":"PLN"', h)
        if m: o["salary"] = f"{int(m.group(1))//1000}-{int(m.group(2))//1000}k PLN"
        musts = re.findall(r'"musts":\[([^\]]+)\]', h)
        if musts: o["musts"] = re.findall(r'"value":"([^"]+)"', musts[0])[:8]
        nices = re.findall(r'"nices":\[([^\]]+)\]', h)
        if nices: o["nices"] = re.findall(r'"value":"([^"]+)"', nices[0])[:6]
    except: pass
    print(f" {i}/{len(oferty)} - {o['company']}")

print("\n3/3 Pytam Bielika...")
API = "http://localhost:1234/v1/chat/completions"
cache = {}
if os.path.exists("firmy_cache.json"):
    old = json.load(open("firmy_cache.json", encoding="utf-8"))
    for k,v in old.items():
        cache[k] = v if isinstance(v, dict) else {"miasto":"—","opis":v}

for o in oferty:
    firma = o["company"]
    if firma and firma not in cache:
        try:
            r = requests.post(API, json={
                "model":"bielik-11b-v2.3-instruct",
                "messages":[
                    {"role":"system","content":"Odpowiadaj TYLKO: Miasto: X | Opis: Y"},
                    {"role":"user","content":f"Firma '{firma}' - podaj miasto siedziby w Polsce i 2 zdania o jej działalności (jakie produkty/usługi)."}
                ],
                "temperature":0.1,
                "max_tokens":180
            }, timeout=15)
            txt = r.json()["choices"][0]["message"]["content"].strip()

            # lepszy parser
            miasto = "—"
            opis = txt
            if "Miasto:" in txt:
                parts = txt.split("Opis:",1)
                m_part = parts[0]
                miasto = m_part.replace("Miasto:","").strip().split("\n")[0].strip()
                if len(parts) > 1:
                    opis = parts[1].strip()

            # wyczyść
            opis = re.sub(r'^[:\-\s]+', '', opis)
            opis = opis[:400] # max 400 znaków

            cache[firma] = {"miasto": miasto, "opis": opis}
            print(f" OK {firma} ({miasto})")
            time.sleep(0.2)
        except Exception as e:
            print(f" BLAD {firma}: {e}")
            cache[firma] = {"miasto":"—","opis":""}
    item = cache.get(firma, {})
    o["firma_opis"] = item.get("opis","") if isinstance(item,dict) else str(item)
    o["miasto"] = item.get("miasto","—") if isinstance(item,dict) else "—"

with open("oferty.json","w",encoding="utf-8") as f: json.dump(oferty, f, ensure_ascii=False, indent=2)
with open("firmy_cache.json","w",encoding="utf-8") as f: json.dump(cache, f, ensure_ascii=False, indent=2)
print(f"\nGOTOWE - {len(oferty)} ofert")