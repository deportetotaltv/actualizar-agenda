import requests
from bs4 import BeautifulSoup
from ftplib import FTP
from datetime import datetime, timedelta
import os

# Configuración del FTP (Hostinger)
HOST = "46.202.183.73"
PORT = 21
USERNAME = "u731911735"
PASSWORD = "Felarboymarla0610."
REMOTE_PATH = "agenda.html"

# Fuente y archivos locales
URL = "https://streamtp4.com/eventos.html"
LOCAL_FILE = "agenda.html"
BACKUP_FILE = "agenda_anterior.html"

def descargar_eventos():
    print("📥 Descargando eventos...")
    response = requests.get(URL)
    response.encoding = 'utf-8'
    return response.text

def hay_cambios(nuevo_contenido):
    if not os.path.exists(BACKUP_FILE):
        return True
    with open(BACKUP_FILE, "r", encoding="utf-8") as f:
        anterior = f.read()
    return nuevo_contenido.strip() != anterior.strip()

def filtrar_eventos_expirados(html):
    print("⏳ Filtrando eventos vencidos...")
    soup = BeautifulSoup(html, "html.parser")
    ahora_col = datetime.utcnow() - timedelta(hours=5)

    eliminados = 0
    for li in soup.find_all("li"):
        span = li.find("span", class_="t")
        if span and span.has_attr("data-fecha"):
            try:
                fecha = datetime.fromisoformat(span["data-fecha"])
                if ahora_col > fecha + timedelta(hours=2, minutes=30):
                    li.decompose()
                    eliminados += 1
            except ValueError:
                continue

    print(f"🧹 Eventos eliminados: {eliminados}")
    return str(soup)

def guardar_y_subir(contenido):
    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        f.write(contenido)

    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        f.write(contenido)

    print("🔄 Conectando por FTP...")
    ftp = FTP()
    ftp.connect(HOST, PORT)
    ftp.login(USERNAME, PASSWORD)

    with open(LOCAL_FILE, "rb") as file:
        ftp.storbinary(f"STOR {REMOTE_PATH}", file)

    ftp.quit()
    print("✅ Subido exitosamente.")

def main():
    print(f"\n[{datetime.now()}] 🔄 Iniciando actualización de eventos...")
    try:
        contenido = descargar_eventos()
        if hay_cambios(contenido):
            limpio = filtrar_eventos_expirados(contenido)
            guardar_y_subir(limpio)
        else:
            print("ℹ️ No hay cambios detectados. Todo está actualizado.")
    except Exception as e:
        print("❌ Error durante la ejecución:", e)

if __name__ == "__main__":
    main()
