import sqlite3

conexion = sqlite3.connect('sistema.db')
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS propietarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    dni TEXT NOT NULL UNIQUE,
    unidad_funcional TEXT NOT NULL,
    telefono TEXT,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    propietario_id INTEGER,
    marca TEXT,
    modelo TEXT,
    color TEXT,
    patente TEXT UNIQUE,
    FOREIGN KEY(propietario_id) REFERENCES propietarios(id)
)
""")

cursor.execute('''
CREATE TABLE IF NOT EXISTS visitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    dni TEXT NOT NULL,
    fecha_ingreso TEXT NOT NULL,
    hora_ingreso TEXT NOT NULL,
    hora_salida TEXT NOT NULL,
    patente TEXT,
    marca TEXT,
    modelo TEXT,
    color TEXT,
    propietario TEXT NOT NULL,
    motivo TEXT NOT NULL
)
''')

cursor.execute("""
CREATE TABLE accesos_qr (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('propietario', 'visita', 'personal')),
    timestamp_ingreso TEXT,
    timestamp_egreso TEXT,
    qr_contenido TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS emergencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    propietario_id INTEGER,
    tipo TEXT NOT NULL,               -- ejemplo: 'médica', 'incendio'
    descripcion TEXT NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    FOREIGN KEY(propietario_id) REFERENCES propietarios(id)
)
""")

conexion.commit()
conexion.close()

print("Base de datos 'sistema.db' y todas las tablas creadas correctamente.")
