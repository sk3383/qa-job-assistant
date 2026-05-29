import json, html, re
from datetime import datetime
from collections import Counter

oferty = json.load(open("oferty.json", encoding="utf-8"))
MOJE = json.load(open("moje_skillz.json", encoding="utf-8"))
MOJE = MOJE if isinstance(MOJE, list) else MOJE.get("skills", [])
MOJE = [s.lower() for s in MOJE]

for o in oferty:
    musts = o.get("musts", [])
    haves = [m for m in musts if any(s in m.lower() for s in MOJE)]
    pct = int(len(haves)/len(musts)*100) if musts else 0
    o.update({
        "musts": musts,
        "haves": haves,
        "match_pct": pct,
        "ocena_bielika": "IDEALNY" if pct>=70 else "DOBRY" if pct>=50 else "ŚREDNI" if pct>=30 else "SŁABY",
        "miasto": o.get("miasto",""),
        "firma_opis": o.get("firma_opis","Brak opisu")[:300]
    })

oferty.sort(key=lambda x: x["match_pct"], reverse=True)

# TOP SKILLS
all_skills = [m.lower() for o in oferty for m in o["musts"]]
top = Counter(all_skills).most_common(20)
ranking = "<div style='background:#1e293b;padding:15px;border-radius:8px;margin-bottom:20px'><h3 style='color:#7dd3fc;margin:0 0 10px'>🔥 TOP umiejętności w ofertach</h3><div style='display:flex;flex-wrap:wrap;gap:6px'>"
for s,c in top:
    color = "#22c55e" if s in MOJE else "#64748b"
    ranking += f"<span style='background:#0f172a;padding:5px 10px;border-radius:4px;font-size:12px;border-left:3px solid {color}'>{s.title()} <b style='color:#fbbf24'>{c}x</b></span>"
ranking += "</div></div>"

rows = ""
for i,o in enumerate(oferty,1):
    safe = re.sub(r'[^\w]','_',o['company'])
    pct = o['match_pct']
    col = "#22c55e" if pct>=70 else "#fbbf24" if pct>=40 else "#ef4444"
    rows += f"""
<tr>
<td style="text-align:center">{i}<div style="color:{col};font-weight:700;font-size:16px">{pct}%</div></td>
<td><a href="{o['url']}" target="_blank" style="color:#7dd3fc;text-decoration:none;font-weight:500">{html.escape(o['title'])}</a><br><small style="color:#94a3b8">{html.escape(o['company'])}</small></td>
<td style="color:#fbbf24;font-size:12px;max-width:200px">{html.escape(', '.join(o['musts'][:5]))}</td>
<td style="color:#22c55e;font-size:12px;max-width:180px">{html.escape(', '.join(o['haves']))}</td>
<td style="font-size:12px">{html.escape(o['miasto'])}</td>
<td style="font-size:11px;color:#cbd5e1;max-width:250px">{html.escape(o['firma_opis'])}</td>
<td><b style="color:{col}">{o['ocena_bielika']}</b><br><small style="color:#64748b">{o['match_pct']}% match</small></td>
<td style="white-space:nowrap">
 <a href="http://localhost:5000/pdf?type=lm&company={safe}&title={html.escape(o['title'])}" target="_blank" style="background:#2563eb;color:white;padding:6px 10px;border-radius:4px;font-size:12px;text-decoration:none;display:inline-block;margin:2px">LM</a>
 <a href="http://localhost:5000/pdf?type=cv&company={safe}&title={html.escape(o['title'])}" target="_blank" style="background:#16a34a;color:white;padding:6px 10px;border-radius:4px;font-size:12px;text-decoration:none;display:inline-block;margin:2px">CV</a>
</td>
</tr>"""

html_out = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Raport QA {datetime.now().strftime('%d.%m.%Y')}</title>
<style>
body{{background:#0f172a;color:#e2e8f0;font-family:system-ui;padding:20px;margin:0}}
table{{width:100%;border-collapse:collapse;background:#1e293b;font-size:13px;box-shadow:0 4px 6px rgba(0,0,0,0.3)}}
th,td{{padding:12px 10px;border-bottom:1px solid #334155;vertical-align:top}}
th{{background:#0f172a;color:#94a3b8;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;position:sticky;top:0}}
tr:hover{{background:#273449}}
h2{{margin:0 0 10px;color:#f1f5f9}}
</style>
</head><body>
<h2>🎯 Raport QA - {len(oferty)} ofert | {datetime.now().strftime('%d.%m.%Y %H:%M')}</h2>
{ranking}
<table>
<thead><tr><th>#</th><th>Oferta</th><th>Wymagane</th><th>Masz</th><th>Miasto</th><th>Opis firmy</th><th>Opinia</th><th>PDF</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<p style="color:#64748b;font-size:12px;margin-top:20px">PDF generowane on-demand przez Bielika • Kliknij LM/CV aby wygenerować</p>
</body></html>"""

open("raport.html","w",encoding="utf-8").write(html_out)
print(f"✓ raport.html z pełnymi informacjami - {len(oferty)} ofert")