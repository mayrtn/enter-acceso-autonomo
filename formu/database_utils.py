import sqlite3
from datetime import datetime

def registrar_propietario(nombre, dni, unidad_funcional, telefono, email):
    conexion = sqlite3.connect('sistema.db')
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO propietarios (nombre, dni, unidad_funcional, telefono, email)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, dni, unidad_funcional, telefono, email))
    conexion.commit()
    conexion.close()

def registrar_vehiculo(propietario_id, marca, modelo, color, patente):
    conexion = sqlite3.connect('sistema.db')
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO vehiculos (propietario_id, marca, modelo, color, patente)
        VALUES (?, ?, ?, ?, ?)
    """, (propietario_id, marca, modelo, color, patente))
    conexion.commit()
    conexion.close()

def registrar_emergencia(propietario_id, tipo, descripcion):
    fecha = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M:%S")
    conexion = sqlite3.connect('sistema.db')
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO emergencias (propietario_id, tipo, descripcion, fecha, hora)
        VALUES (?, ?, ?, ?, ?)
    """, (propietario_id, tipo, descripcion, fecha, hora))
    conexion.commit()
    conexion.close()

def obtener_propietarios_y_vehiculos():
    conexion = sqlite3.connect('sistema.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT p.nombre, p.dni, p.unidad_funcional, v.marca, v.modelo, v.patente
        FROM propietarios p
        LEFT JOIN vehiculos v ON p.id = v.propietario_id
        ORDER BY p.nombre
    """)
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def obtener_emergencias_por_propietario(propietario_id):
    conexion = sqlite3.connect('visitas.db')
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT tipo, descripcion, fecha, hora
        FROM emergencias
        WHERE propietario_id = ?
        ORDER BY fecha DESC, hora DESC
    """, (propietario_id,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def insertar_propietario(nombre, dni, unidad_funcional, telefono, email):
    conexion = sqlite3.connect("sistema.db")
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO propietarios (nombre, dni, unidad_funcional, telefono, email)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, dni, unidad_funcional, telefono, email))
    conexion.commit()
    conexion.close()
    