import requests
from bs4 import BeautifulSoup
from ftplib import FTP
from datetime import datetime, timedelta
import os

# Configuración FTP
HOST = "46.202.183.73"
PORT = 21
USERNAME = "u731911735"
PASSWORD = "Felarboymarla0610."
REMOTE_PATH = "agenda.html"  # Nombre correcto en el hosting

# Archivos locales
URL = "https://streamtp4.com/eventos.html"
LOCAL_FILE = "agenda.html"  # 👈 ahora usa agenda.html localmente también
BACKUP_FILE = "agenda_anterior.html"  # backup local para detectar cambios

# Función para descargar el HTML
def descargar_eventos():
    print("📥 Descargando eventos...")
    response = requests.get(URL)
    response.encoding = 'utf-8'
    return response.text

# Verificar si hay cambios respecto al archivo anterior
def hay_cambios(nuevo_contenido):
    if not os.path.exists(BACKUP_FILE):
        return True
    with open(BACKUP_FILE, "r", encoding="utf-8") as f:
        anterior = f.read()
    return nuevo_contenido.strip() != anterior.strip()

# Eliminar eventos expirados según data-fecha
def filtrar_eventos_expirados(html):
    print("⏳ Filtrando eventos vencidos...")
    soup = BeautifulSoup(html, "html.parser")
    ahora_colombia = datetime.utcnow() - timedelta(hours=5)

    eventos_filtrados = 0
    for li in soup.find_all("li"):
        span = li.find("span", class_="t")
        if span and span.has_attr("data-fecha"):
            try:
                hora_evento = datetime.fromisoformat(span["data-fecha"])
                if ahora_colombia > hora_evento + timedelta(hours=2, minutes=30):
                    li.decompose()
                    eventos_filtrados += 1
            except ValueError:
                pass

    print(f"🧹 Eventos eliminados: {eventos_filtrados}")
    return str(soup)

# Guardar localmente y subir por FTP
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

# Ejecución principal
def main():
    print(f"[{datetime.now()}] Iniciando actualización de eventos...")
    try:
        contenido = descargar_eventos()
        if hay_cambios(contenido):
            contenido_filtrado = filtrar_eventos_expirados(contenido)
            guardar_y_subir(contenido_filtrado)
        else:
            print("ℹ No hay cambios. No se subió nada.")
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
