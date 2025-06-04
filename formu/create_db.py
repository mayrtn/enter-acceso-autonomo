import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

# Conexión
conn = sqlite3.connect("sistema.db")
cursor = conn.cursor()

# Crear tabla 'usuarios'
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    apellido TEXT,
    email TEXT UNIQUE,
    contraseña TEXT,
    dni TEXT,
    rol TEXT,
    pin_acceso TEXT,
    pin_seguridad TEXT,
    intentos_fallidos INTEGER DEFAULT 0,
    bloqueado INTEGER DEFAULT 0,
    activo INTEGER DEFAULT 0
)
""")
print("Tabla 'usuarios' creada o verificada.")

# Crear tabla 'visitas'
cursor.execute("""
CREATE TABLE IF NOT EXISTS visitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    dni TEXT,
    fecha_visita DATE,
    propietario_id INTEGER,
    estado TEXT DEFAULT 'pendiente',
    hora_ingreso DATETIME,
    hora_egreso DATETIME,
    FOREIGN KEY (propietario_id) REFERENCES usuarios(id)
)
""")
print("Tabla 'visitas' creada o verificada.")

# Crear tabla 'vehiculos'
cursor.execute("""
CREATE TABLE IF NOT EXISTS vehiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    propietario_id INTEGER,
    marca TEXT,
    modelo TEXT,
    color TEXT,
    patente TEXT UNIQUE,
    FOREIGN KEY (propietario_id) REFERENCES usuarios(id)
)
""")
print("Tabla 'vehiculos' creada o verificada.")

# Crear tabla 'accesos_qr'
cursor.execute("""
CREATE TABLE IF NOT EXISTS accesos_qr (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    tipo_usuario TEXT,
    tipo_evento TEXT,
    timestamp DATETIME,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")
print("Tabla 'accesos_qr' creada o verificada.")

# Crear tabla 'llaves_virtuales'
cursor.execute("""
CREATE TABLE IF NOT EXISTS llaves_virtuales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    tipo TEXT,
    codigo TEXT,
    fecha_generacion DATETIME,
    expira_en DATETIME,
    usado INTEGER DEFAULT 0,
    visita_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (visita_id) REFERENCES visitas(id)
)
""")
print("Tabla 'llaves_virtuales' creada o verificada.")

# Crear tabla 'emergencias'
cursor.execute("""
CREATE TABLE IF NOT EXISTS emergencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    propietario_id INTEGER,
    tipo TEXT,
    descripcion TEXT,
    ubicacion TEXT,
    fecha DATETIME,
    FOREIGN KEY (propietario_id) REFERENCES usuarios(id)
)
""")
print("Tabla 'emergencias' creada o verificada.")

# Verificar si ya hay un admin
cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'admin'")
existe_admin = cursor.fetchone()[0]

if existe_admin == 0:
    print("No se encontró ningún administrador. Creando usuario admin inicial...")
    cursor.execute("""
        INSERT INTO usuarios (nombre, apellido, email, contraseña, dni, rol, activo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "Admin", "Inicial", "admin@ejemplo.com",
        generate_password_hash("admin123"), 1000000,
        "admin", 1
    ))
    print("Usuario admin creado: admin@ejemplo.com / admin123")
else:
    print("Ya existe al menos un usuario administrador.")

# Confirmar y cerrar
conn.commit()
conn.close()
print("Base de datos inicializada correctamente.")
