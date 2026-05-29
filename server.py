import json, base64, io
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- fonty ---
pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuB', 'fonts/DejaVuSans-Bold.ttf'))
print("Font OK: fonts\\DejaVuSans.ttf")
print("Font OK: fonts\\DejaVuSans-Bold.ttf")

BIELIK = "http://localhost:1234/v1/chat/completions"

def make_pdf(title, company, role, content):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=50, rightMargin=50, topMargin=60, bottomMargin=50)

    style_title = ParagraphStyle('t', fontName='DejaVuB', fontSize=18, leading=22, spaceAfter=6)
    style_sub = ParagraphStyle('s', fontName='DejaVu', fontSize=11, leading=14, textColor='#555555', spaceAfter=18)
    style_body = ParagraphStyle('b', fontName='DejaVu', fontSize=11, leading=16, spaceAfter=10, alignment=4)

    story = []
    story.append(Paragraph(title, style_title))
    story.append(Paragraph(f"{company} • {role}", style_sub))

    # podziel na akapity
    for para in content.split('\n'):
        para = para.strip()
        if not para:
            story.append(Spacer(1, 8))
            continue
        story.append(Paragraph(para, style_body))

    story.append(Spacer(1, 24))
    story.append(Paragraph("Wygenerowano przez Bielik QA Assistant", ParagraphStyle('f', fontName='DejaVu', fontSize=8, textColor='#999999')))

    doc.build(story)
    return base64.b64encode(buf.getvalue()).decode()

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length).decode())

        is_lm = self.path == "/lm"
        title = "List Motywacyjny" if is_lm else "CV – dopasowanie do oferty"

        if is_lm:
            prompt = f"""Napisz list motywacyjny (400-500 słów, 4 akapity) na stanowisko {data['title']} w {data['company']}.
Wymagania z ogłoszenia: {', '.join(data.get('musts', []))}
Moje doświadczenie: testy manualne i automatyczne, Selenium, Playwright, API, Postman, JIRA, SQL, Python.
Napisz konkretnie, użyj przykładów, unikaj frazesów. Podziel na akapity. Po polsku."""
        else:
            prompt = f"""Stwórz profesjonalną sekcję CV "Kluczowe kompetencje dla {data['company']}" (8-10 punktów).
Stanowisko: {data['title']}
Wymagania: {', '.join(data.get('musts', []))}
Każdy punkt zacznij od czasownika, dodaj narzędzie i efekt. Pisz po polsku. Formatuj jako lista z myślnikami, każdy w nowej linii."""

        r = requests.post(BIELIK, json={
            "model": "bielik-11b-v2.3-instruct",
            "messages": [
                {"role": "system", "content": "Jesteś senior rekruterem IT. Pisz szczegółowo i profesjonalnie."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 900,
            "temperature": 0.7
        }, timeout=90)

        text = r.json()["choices"][0]["message"]["content"].strip()
        pdf = make_pdf(title, data['company'], data['title'], text)

        self._set_headers()
        self.wfile.write(json.dumps({
            "pdf": pdf,
            "filename": f"{'LM' if is_lm else 'CV'}_{data['company'].replace(' ','_')}.pdf"
        }, ensure_ascii=False).encode())

print("\nSerwer QA Job Assistant działa na http://localhost:8000")
HTTPServer(("localhost", 8000), Handler).serve_forever()