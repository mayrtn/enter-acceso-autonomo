import requests
import sqlite3
from bs4 import BeautifulSoup
import base64
import re

BASE_URL = "http://127.0.0.1:5000"

# 1. Login como propietario
s_prop = requests.Session()
print("🔐 Login como propietario...")
res = s_prop.post(f"{BASE_URL}/login", data={"dni": "34567890", "contraseña": "prop123"})
assert res.status_code in (200, 302), "❌ Falló el login del propietario"
print("✅ Login exitoso.")

# Comprobar que la sesión se mantiene
print(f"🍪 Cookies luego del login: {s_prop.cookies.get_dict()}")
check_session = s_prop.get(f"{BASE_URL}/visitas/nueva")
if "login" in check_session.url:
    raise Exception("⚠️ El propietario fue redirigido al login. La sesión no se mantiene.")

# 2. Crear visita
print("📅 Creando visita...")
datos_visita = {
    "nombre": "Visita Test",
    "dni": "11222333",
    "motivo": "Reunión",
    "marca": "Toyota",
    "modelo": "Corolla",
    "color": "Blanco",
    "patente": "ABC123",
    "fecha_ingreso": "2025-05-25",
    "hora_ingreso": "10:00",
    "hora_salida": "13:00"
}
res = s_prop.post(f"{BASE_URL}/visitas/nueva", data=datos_visita)

# Mostrar detalles si falla
if res.status_code not in (200, 302):
    print(f"⚠️ Código de estado: {res.status_code}")
    print("📄 Contenido de respuesta:")
    print(res.text)
    raise AssertionError("❌ Falló la creación de la visita")

print("✅ Visita creada correctamente.")

# 3. Verificar que el QR esté presente
print("🔎 Verificando QR en el HTML...")
soup = BeautifulSoup(res.text, "html.parser")
qr_img_tag = soup.find("img")
assert qr_img_tag and "data:image/png;base64," in qr_img_tag["src"], "❌ No se encontró el QR en la respuesta"
print("✅ QR encontrado en el HTML.")

# 4. Decodificar contenido del QR
contenido_qr = soup.find("p").text.strip()
print(f"📦 Contenido del QR: {contenido_qr}")
visita_id, tipo_usuario, timestamp, vencimiento = contenido_qr.split("|")

# 5. Confirmar que la visita existe en la base de datos
print("🔍 Verificando visita en la base de datos...")
conn = sqlite3.connect("sistema.db")
cur = conn.cursor()
cur.execute("SELECT * FROM visitas WHERE id = ?", (visita_id,))
visita = cur.fetchone()
assert visita is not None, "❌ La visita no se encontró en la base de datos"
print("✅ Visita confirmada en la base de datos.")
conn.close()

# 6. Simular escaneo de QR (registro de ingreso)
print("🚪 Simulando escaneo del QR...")
res = s_prop.post(f"{BASE_URL}/escanear_qr", data={"contenido_qr": contenido_qr, "pin": "1234"})
assert "acceso registrado" in res.text.lower() or res.status_code == 200, "❌ Falló el registro de acceso"
print("✅ Acceso registrado correctamente.")

# 7. Verificar que seguridad vea los accesos
print("🛂 Login como seguridad...")
s_seg = requests.Session()
res = s_seg.post(f"{BASE_URL}/login", data={"dni": "99999999", "contraseña": "seg123"})
assert res.status_code in (200, 302), "❌ Falló el login del personal de seguridad"
print("✅ Login de seguridad exitoso.")

print("📋 Consultando accesos desde seguridad...")
res = s_seg.get(f"{BASE_URL}/accesos")
assert "Visita Test" in res.text or "11222333" in res.text, "❌ La visita no aparece en los accesos"
print("✅ Acceso visible para seguridad.")
