from flask import Flask, request, send_file, jsonify
import json, re, os, urllib.request, hashlib
from datetime import datetime
import requests
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = Flask(__name__)
API = "http://localhost:1234/v1/chat/completions"
DATE = datetime.now().strftime("%y%m%d")

# --- FONT ---
os.makedirs("fonts", exist_ok=True)
if not os.path.exists("fonts/DejaVuSans.ttf"):
    urllib.request.urlretrieve("https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf", "fonts/DejaVuSans.ttf")
    urllib.request.urlretrieve("https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf", "fonts/DejaVuSans-Bold.ttf")
pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuB', 'fonts/DejaVuSans-Bold.ttf'))

style = ParagraphStyle('pl', fontName='DejaVu', fontSize=11, leading=16, spaceAfter=10)
style_t = ParagraphStyle('t', fontName='DejaVuB', fontSize=16, leading=20, spaceAfter=12)

MOJE = json.load(open("moje_skillz.json", encoding="utf-8"))
MOJE = MOJE if isinstance(MOJE, list) else MOJE.get("skills", [])
MOJE_STR = ', '.join(MOJE[:10])

# CACHE w pamięci
cache = {}

def ask(prompt):
    h = hashlib.md5(prompt.encode()).hexdigest()
    if h in cache: return cache[h]
    r = requests.post(API, json={"model":"bielik-11b-v2.3-instruct","messages":[{"role":"user","content":prompt}],"max_tokens":380,"temperature":0.6}, timeout=20)
    txt = r.json()["choices"][0]["message"]["content"]
    cache[h] = txt
    return txt

def make_pdf(path, title, text):
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=50)
    story = [Paragraph(title, style_t), Spacer(1,12)]
    for p in text.split('\n'):
        if p.strip(): story.append(Paragraph(p, style))
    doc.build(story)

@app.route('/pdf')
def pdf():
    typ = request.args.get('type','lm')
    company = request.args.get('company','Firma')
    title = request.args.get('title','Tester')

    os.makedirs(typ, exist_ok=True)
    path = f"{typ}/{typ.upper()}_{company}_{DATE}.pdf"

    # CACHE PLIKU
    if os.path.exists(path):
        print(f"CACHE: {path}")
        return send_file(path, as_attachment=False)

    print(f"GENERUJĘ: {company} - {typ}")
    if typ == 'lm':
        prompt = f"List motywacyjny na {title} w {company}. Umiejętności: {MOJE_STR}. 4 akapity, konkretnie, po polsku."
        text = f"Szanowni Państwo,\n\n{ask(prompt)}\n\nZ poważaniem\n[Imię Nazwisko]"
        make_pdf(path, "List Motywacyjny", text)
    else:
        prompt = f"CV testera QA na {title} w {company}. Sekcje: PROFIL, UMIEJĘTNOŚCI ({MOJE_STR}), DOŚWIADCZENIE. Po polsku."
        text = ask(prompt)
        make_pdf(path, "Curriculum Vitae", text)

    return send_file(path, as_attachment=False)

@app.route('/status')
def status():
    return jsonify({"cache_size": len(cache), "pdfs": len(os.listdir('lm')) + len(os.listdir('cv')) if os.path.exists('lm') else 0})

if __name__ == '__main__':
    app.run(port=5000, debug=False)