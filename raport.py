import json
from datetime import datetime
from collections import Counter

# skilli
try:
    with open("moje_skillz.json", encoding="utf-8") as f:
        your_skills = json.load(f)["skills"]
except:
    your_skills = ["Manual Testing", "Selenium", "API Testing", "Postman", "JIRA", "SQL"]

with open("oferty.json", encoding="utf-8") as f:
    oferty = json.load(f)

for o in oferty:
    musts = o.get("musts", [])
    masz = [s for s in your_skills if any(s.lower() in m.lower() or m.lower() in s.lower() for m in musts)]
    o["masz"] = masz
    o["match"] = round(len(masz)/len(musts)*100, 0) if musts else 0

oferty.sort(key=lambda x: x["match"], reverse=True)

# STATYSTYKI
all_tech = []
for o in oferty:
    for m in o.get("musts", []):
        clean = m.strip().title()
        if clean and len(clean) > 2 and clean.lower() not in ["praca zdalna", "testing"]:
            all_tech.append(clean)

top_tech = Counter(all_tech).most_common(12)
stats_html = "".join([f"<span class='stat'>{t} <b>{c}</b></span>" for t, c in top_tech])

html = f"""<!DOCTYPE html><html lang="pl"><head><meta charset="UTF-8">
<title>QA Jobs {datetime.now():%d.%m}</title>
<style>
:root{{--bg:#0f172a;--card:#1e293b;--text:#e2e8f0;--muted:#94a3b8;--accent:#7dd3fc;--ok:#22c55e;--warn:#fbbf24;--bad:#ef4444}}
body{{background:var(--bg);color:var(--text);font-family:system-ui;margin:0;padding:20px}}
h2{{margin:0 0 8px}}
.stats{{background:var(--card);padding:14px;border-radius:12px;margin:12px 0 20px;display:flex;flex-wrap:wrap;gap:8px}}
.stat{{background:#0f172a;padding:6px 10px;border-radius:8px;font-size:12px;color:var(--muted);border:1px solid #334155}}
.stat b{{color:var(--accent);margin-left:4px}}
table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:12px;overflow:hidden}}
th,td{{padding:12px 10px;border-bottom:1px solid #334155;vertical-align:top;font-size:13px}}
th{{background:#0f172a;color:var(--muted);text-transform:uppercase;font-size:11px;position:sticky;top:0}}
tr:hover{{background:#273449}} a{{color:var(--accent);text-decoration:none}}
.badge{{padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600}}
.badge.ok{{background:rgba(34,197,94,.15);color:var(--ok)}}.badge.warn{{background:rgba(251,191,36,.15);color:var(--warn)}}.badge.bad{{background:rgba(239,68,68,.15);color:var(--bad)}}
.btn{{padding:6px 10px;border:0;border-radius:8px;cursor:pointer;font-size:12px;font-weight:600;margin:2px}}
.btn.lm{{background:var(--accent);color:#0f172a}}.btn.cv{{background:var(--ok);color:#0f172a}}
small{{color:var(--muted)}}
</style></head><body>
<h2>🎯 QA Jobs - {len(oferty)} ofert | {datetime.now():%d.%m.%Y %H:%M}</h2>
<div class="stats"><span style="color:var(--muted);margin-right:8px">Najczęściej w ogłoszeniach:</span>{stats_html}</div>
<table><thead><tr><th>#</th><th>Oferta</th><th>Pensja</th><th>Wymagane</th><th>Masz</th><th>Opis firmy</th><th>Match</th><th>Akcje</th></tr></thead><tbody>
"""

for i, o in enumerate(oferty, 1):
    m = int(o["match"]); cls = "ok" if m>=70 else "warn" if m>=40 else "bad"
    label = "IDEALNY" if m>=70 else "DOBRY" if m>=40 else "SŁABY"
    html += f"""<tr>
<td style="text-align:center">{i}<br><span class="badge {cls}">{m}%</span></td>
<td><a href="{o['url']}" target="_blank"><b>{o['title']}</b></a><br><small>{o['company']} • {o.get('miasto','')}</small></td>
<td style="color:var(--warn)">{o.get('salary','')}</td>
<td style="font-size:12px">{', '.join(o.get('musts',[])[:6])}</td>
<td style="color:var(--ok);font-size:12px">{', '.join(o.get('masz',[])[:6])}</td>
<td style="font-size:11px;color:var(--muted)">{o.get('firma_opis','')[:160]}...</td>
<td><span class="badge {cls}">{label}</span></td>
<td><button class="btn lm" onclick="gen('lm',{i-1},this)">LM</button><button class="btn cv" onclick="gen('cv',{i-1},this)">CV</button></td>
</tr>"""

html += """</tbody></table>
<script>
const oferty = """ + json.dumps(oferty, ensure_ascii=False) + """;
async function gen(type, idx, btn){
  const o = oferty[idx]; const orig = btn.textContent; btn.textContent='...'; btn.disabled=true;
  try{
    const r = await fetch('http://localhost:8000/'+type, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(o)});
    const d = await r.json();
    const bytes = Uint8Array.from(atob(d.pdf), c=>c.charCodeAt(0));
    const blob = new Blob([bytes], {type:'application/pdf'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = d.filename; a.click();
  }catch(e){alert('Błąd: uruchom server.py i LM Studio')}
  btn.textContent=orig; btn.disabled=false;
}
</script></body></html>"""

with open("raport.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"GOTOWE - {len(oferty)} ofert | Top tech: {', '.join([t for t,c in top_tech[:5]])}")