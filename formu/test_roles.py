import requests

# Cambiá esto según tu entorno local
BASE_URL = "http://127.0.0.1:5000"

usuarios = [
    {"usuario": "admin1", "contrasena": "adminpass", "rol": "admin"},
    {"usuario": "seguridad1", "contrasena": "seguridadpass", "rol": "seguridad"},
    {"usuario": "propietario1", "contrasena": "propietariopass", "rol": "propietario"},
]

session = requests.Session()

for u in usuarios:
    print(f"\n🔐 Probando login como {u['rol']}...")

    login_data = {
        "usuario": u["usuario"],
        "contrasena": u["contrasena"]
    }

    r = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)

    if "Bienvenido" in r.text or r.url.endswith("/dashboard"):
        print(f"✅ Login correcto para rol: {u['rol']}")
    else:
        print(f"❌ Falló login para rol: {u['rol']}")
        continue

    # Verificamos acceso según rol
    if u["rol"] == "admin":
        r2 = session.get(f"{BASE_URL}/usuarios")
        print("👁 Acceso a /usuarios:", "OK" if r2.status_code == 200 else "DENEGADO")

    elif u["rol"] == "seguridad":
        r2 = session.get(f"{BASE_URL}/accesos")
        print("👁 Acceso a /accesos:", "OK" if r2.status_code == 200 else "DENEGADO")

    elif u["rol"] == "propietario":
        r2 = session.get(f"{BASE_URL}/qr/generar")
        print("👁 Acceso a /qr/generar:", "OK" if r2.status_code == 200 else "DENEGADO")
