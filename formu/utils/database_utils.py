import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

DB_NAME = 'sistema.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def registrar_usuario(nombre, dni, unidad_funcional, telefono, email, rol, contraseña="123456"):
    try:
        with sqlite3.connect(DB_NAME) as conexion:
            cursor = conexion.cursor()

            cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
            if cursor.fetchone():
                raise ValueError("El email ya está registrado")

            contraseña_hash = generate_password_hash(contraseña)

            cursor.execute("""
                INSERT INTO usuarios (nombre, dni, unidad_funcional, telefono, email, rol, contraseña)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nombre, dni, unidad_funcional, telefono, email, rol, contraseña_hash))
            
            conexion.commit()
    except sqlite3.IntegrityError as e:
        print(f"Error de integridad: {e}")
        raise
    except Exception as e:
        print(f"Error al registrar usuario: {e}")
        raise


def registrar_vehiculo(propietario_id, marca, modelo, color, patente):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO vehiculos (usuario_id, marca, modelo, color, patente)
            VALUES (?, ?, ?, ?, ?)
        """, (propietario_id, marca, modelo, color, patente))


def registrar_emergencia(usuario_id, tipo, descripcion, ubicacion, fecha):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emergencias (propietario_id, tipo, descripcion, ubicacion, fecha)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario_id, tipo, descripcion, ubicacion, fecha))


def obtener_usuarios_y_vehiculos():
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT u.nombre, u.dni, u.unidad_funcional, u.rol,
                   v.marca, v.modelo, v.color, v.patente
            FROM usuarios u
            LEFT JOIN vehiculos v ON u.id = v.usuario_id
            ORDER BY u.nombre
        """)
        return cursor.fetchall()


def obtener_emergencias_por_usuario(usuario_id):
    with sqlite3.connect(DB_NAME) as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT tipo, descripcion, fecha
            FROM emergencias
            WHERE propietario_id = ?
            ORDER BY fecha DESC
        """, (usuario_id,))
        return cursor.fetchall()

def dict_from_row(row):
    return {k: row[k] for k in row.keys()}
