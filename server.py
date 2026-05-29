import os
import urllib.request
import http.server
import socketserver

# --- POPRAWKA: bezpieczne fonty ---
FONTS_DIR = "fonts"
FONTS = {
    "DejaVuSans.ttf": "https://cdn.jsdelivr.net/gh/senotrusov/dejavu-fonts-ttf@master/ttf/DejaVuSans.ttf",
    "DejaVuSans-Bold.ttf": "https://cdn.jsdelivr.net/gh/senotrusov/dejavu-fonts-ttf@master/ttf/DejaVuSans-Bold.ttf",
}

os.makedirs(FONTS_DIR, exist_ok=True)

for name, url in FONTS.items():
    path = os.path.join(FONTS_DIR, name)
    if not os.path.exists(path):
        try:
            print(f"Pobieram font: {name}...")
            urllib.request.urlretrieve(url, path)
            print(f"OK: {path}")
        except Exception as e:
            print(f"UWAGA: Nie udało się pobrać {name}")
            print(f"Błąd: {e}")
            print(f"Pobierz ręcznie z {url} i wrzuć do {FONTS_DIR}/")
    else:
        print(f"Font OK: {path}")

# --- TWÓJ SERWER ---
PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/raport.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

print(f"\nSerwer QA Job Assistant działa na http://localhost:{PORT}")
print("Naciśnij Ctrl+C aby zatrzymać\n")

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nZatrzymano serwer")