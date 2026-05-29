import json
from datetime import datetime

# WCZYTAJ TWOJE SKILLE
try:
    with open("moje_skillz.json", encoding="utf-8") as f:
        your_skills = json.load(f)["skills"]
except:
    your_skills = ["Manual Testing", "Selenium", "API Testing"] # fallback

print("1/3 Wczytuje oferty...")
with open("oferty.json", encoding="utf-8") as f:
    oferty = json.load(f)

print(f" - wczytano {len(oferty)} ofert")
print(f" - Twoje skilli: {len(your_skills)}")

# analiza
for o in oferty:
    musts = o.get("musts", [])
    masz = [s for s in your_skills if any(s.lower() in m.lower() or m.lower() in s.lower() for m in musts)]
    o["masz"] = masz
    o["match"] = round(len(masz)/len(musts)*100,0) if musts else 0

oferty.sort(key=lambda x: x["match"], reverse=True)

print("2/3 Generuje HTML...")
html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Raport QA {datetime.now().strftime('%d.%m.%Y')}</title>
<style>
body{{background:#0f172a;color:#e2e8f0;font-family:system-ui;padding:20px;margin:0}}
table{{width:100%;border-collapse:collapse;background:#1e293b;font-size:13px}}
th,td{{padding:12px 10px;border-bottom:1px solid #334155;vertical-align:top}}
th{{background:#0f172a;color:#94a3b8;font-size:11px;text-transform:uppercase;position:sticky;top:0}}
tr:hover{{background:#273449}}
</style>
</head><body>
<h2>🎯 Raport QA - {len(oferty)} ofert | {datetime.now().strftime('%d.%m.%Y %H:%M')}</h2>
<table>
<thead><tr><th>#</th><th>Oferta</th><th>Pensja</th><th>Wymagane</th><th>Masz ({len(your_skills)})</th><th>Opis firmy</th><th>Match</th></tr></thead>
<tbody>
"""

for i,o in enumerate(oferty,1):
    color = "#22c55e" if o["match"]>=70 else "#fbbf24" if o["match"]>=40 else "#ef4444"
    html += f"""<tr>
<td style="text-align:center">{i}<div style="color:{color};font-weight:700">{int(o['match'])}%</div></td>
<td><a href="{o['url']}" target="_blank" style="color:#7dd3fc;text-decoration:none">{o['title']}</a><br><small style="color:#94a3b8">{o['company']}</small></td>
<td style="font-size:12px;color:#fbbf24">{o.get('salary','')}</td>
<td style="color:#fbbf24;font-size:12px">{', '.join(o.get('musts',[])[:6])}</td>
<td style="color:#22c55e;font-size:12px">{', '.join(o.get('masz',[])[:6])}</td>
<td style="font-size:11px;color:#cbd5e1;max-width:300px">{o.get('firma_opis','')[:180]}...</td>
<td><b style="color:{color}">{'IDEALNY' if o['match']>=70 else 'DOBRY' if o['match']>=40 else 'SŁABY'}</b></td>
</tr>"""

html += "</tbody></table></body></html>"

with open("raport.html","w",encoding="utf-8") as f:
    f.write(html)

print("GOTOWE - raport.html")