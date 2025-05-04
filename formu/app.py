from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime
from database_utils import (
    registrar_propietario,
    registrar_vehiculo,
    registrar_emergencia,
    obtener_propietarios_y_vehiculos,
    obtener_emergencias_por_propietario,
    insertar_propietario
)
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)

app.secret_key = "clave_segura_123"

def inicializar_db():
    if not os.path.exists('sistema.db'):
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
        cursor.execute("""
            CREATE TABLE visitas (
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
        """)
        cursor.execute("""
            CREATE TABLE accesos_qr (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('propietario', 'visita', 'personal')),
                tipo_evento TEXT NOT NULL CHECK(tipo_evento IN ('ingreso', 'egreso')),
                timestamp TEXT NOT NULL
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

inicializar_db()

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")  

@app.route("/registrar_visita", methods=["POST"])
def registrar_visita():
    datos = (
        request.form['nombre'],
        request.form['dni'],
        request.form['propietario'],
        request.form['motivo'],
        request.form.get('marca', ''),
        request.form.get('modelo', ''),
        request.form.get('color', ''),
        request.form.get('patente', ''),
        request.form['fecha_ingreso'],
        request.form.get('hora_ingreso', ''),
        request.form.get('hora_salida', '')
     )

    conexion = sqlite3.connect('sistema.db')
    cursor = conexion.cursor()
    print("Datos a insertar:", datos)
    cursor.execute("""
        INSERT INTO visitas (nombre, dni, propietario, motivo, marca, modelo, color, patente, fecha_ingreso, hora_ingreso, hora_salida)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conexion.commit()
    conexion.close()

    return redirect("/confirmacion")

@app.route("/confirmacion")
def confirmacion():
    return render_template("confirmacion.html")

@app.route("/listar_visitas")
def listar_visitas():
    conexion = sqlite3.connect('sistema.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, dni, propietario, motivo, marca, modelo, color, patente, fecha_ingreso, hora_salida, hora_ingreso FROM visitas ORDER BY fecha_ingreso DESC, id DESC")
    visitas = cursor.fetchall()
    conexion.close()
    return render_template("listar_visitas.html", visitas=visitas)

@app.route("/")
def menu_principal():
    return render_template("menu.html")

@app.route("/registrar_acceso")
def mostrar_formulario_acceso():
    return render_template("registro_acceso.html")

@app.route("/registrar_acceso_qr", methods=["POST"])
def registrar_acceso_qr():
    id_usuario = request.form["id_usuario"]
    tipo_usuario = request.form["tipo_usuario"]
    tipo_evento = request.form["tipo_evento"]
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conexion = sqlite3.connect("sistema.db")
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO accesos_qr (id_usuario, tipo_usuario, tipo_evento, timestamp)
        VALUES (?, ?, ?, ?)
    """, (id_usuario, tipo_usuario, tipo_evento, timestamp))
    conexion.commit()
    conexion.close()

    return redirect("/listar_accesos")

@app.route("/listar_accesos")
def listar_accesos_qr():
    conexion = sqlite3.connect("sistema.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM accesos_qr ORDER BY timestamp DESC")
    accesos = cursor.fetchall()
    conexion.close()
    return render_template("listar_accesos_qr.html", accesos=accesos)

@app.route("/nuevo_propietario", methods=["GET", "POST"])
def nuevo_propietario():
    if request.method == "POST":
        datos = {
            "nombre": request.form["nombre"],
            "dni": request.form["dni"],
            "unidad_funcional": request.form["unidad_funcional"],
            "telefono": request.form["telefono"],
            "email": request.form["email"]
        }
        session["propietario_temp"] = datos
        return redirect("/verificar_propietario")

    datos_precargados = session.pop("propietario_temp", {
        "nombre": "",
        "dni": "",
        "unidad_funcional": "",
        "telefono": "",
        "email": ""
    })
    return render_template("nuevo_propietario.html", datos=datos_precargados)

@app.route("/nuevo_vehiculo", methods=["GET", "POST"])
def nuevo_vehiculo():
    if request.method == "POST":
        id_prop = request.form["id_propietario"]
        marca = request.form["marca"]
        modelo = request.form["modelo"]
        color = request.form["color"]
        patente = request.form["patente"]
        registrar_vehiculo(id_prop, marca, modelo, color, patente)
        return redirect("/confirmacion")
    return render_template("nuevo_vehiculo.html")

@app.route("/nueva_emergencia", methods=["GET", "POST"])
def nueva_emergencia():
    if request.method == "POST":
        id_prop = request.form["id_propietario"]
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        relacion = request.form["relacion"]
        registrar_emergencia(id_prop, nombre, telefono, relacion)
        return redirect("/confirmacion")
    return render_template("nueva_emergencia.html")

@app.route("/menu_visitas")
def menu_visitas():
    return render_template("menu_visitas.html")


@app.route("/registrar_propietario", methods=["POST"])
def confirmar_registrar_propietario():
    nombre = request.form["nombre"]
    dni = request.form["dni"]
    unidad_funcional = request.form["unidad_funcional"]
    telefono = request.form["telefono"]
    email = request.form["email"]

    insertar_propietario(nombre, dni, unidad_funcional, telefono, email)

    return render_template("registro_exitoso.html", nombre=nombre, dni=dni,
                           unidad_funcional=unidad_funcional, telefono=telefono, email=email)

@app.route("/verificar_propietario", methods=["POST"])
def verificar_propietario():
    datos = {
        "nombre": request.form["nombre"],
        "dni": request.form["dni"],
        "unidad_funcional": request.form["unidad_funcional"],
        "telefono": request.form["telefono"],
        "email": request.form["email"]
    }
    session["propietario_temp"] = datos
    return render_template("verificar_propietario.html", datos=datos)

@app.route("/confirmar_registro_propietario", methods=["POST"])
def confirmar_registro_propietario():
    datos = session.get("propietario_temp")
    if datos:
        insertar_propietario(
            datos["nombre"],
            datos["dni"],
            datos["unidad_funcional"],
            datos["telefono"],
            datos["email"]
        )
        session.pop("propietario_temp", None)
        return render_template("registro_exitoso.html", **datos)
    else:
        return redirect("/nuevo_propietario")
    
@app.route("/corregir_datos_propietario", methods=["POST"])
def corregir_datos_propietario():
    datos = {
        "nombre": request.form["nombre"],
        "dni": request.form["dni"],
        "unidad_funcional": request.form["unidad_funcional"],
        "telefono": request.form["telefono"],
        "email": request.form["email"]
    }
    return render_template("nuevo_propietario.html", datos=datos)

@app.route("/generar_qr_acceso", methods=["POST"])
def generar_qr_acceso():
    id_usuario = request.form["id_usuario"]
    tipo_usuario = request.form["tipo_usuario"]

    datos_qr = f"{id_usuario}|{tipo_usuario}"

    qr = qrcode.make(datos_qr)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render_template(
        "mostrar_qr.html",
        qr_img=qr_base64,
        contenido_qr=datos_qr  
    )

@app.route("/escanear_qr", methods=["POST"])
def escanear_qr():
    contenido_qr = request.form["contenido_qr"]
    
    try:
        id_usuario, tipo_usuario, timestamp_qr = contenido_qr.split("|")
    except ValueError:
        return "Contenido del QR inválido", 400

    conexion = sqlite3.connect("sistema.db")
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT tipo_evento FROM accesos_qr
        WHERE id_usuario = ? AND tipo_usuario = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (id_usuario, tipo_usuario))
    
    ultimo_evento = cursor.fetchone()
    
    if not ultimo_evento or ultimo_evento[0] == "egreso":
        tipo_evento = "ingreso"
    else:
        tipo_evento = "egreso"
    
    timestamp_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        INSERT INTO accesos_qr (id_usuario, tipo_usuario, tipo_evento, timestamp)
        VALUES (?, ?, ?, ?)
    """, (id_usuario, tipo_usuario, tipo_evento, timestamp_actual))
    
    conexion.commit()
    conexion.close()

    return render_template("mensaje_qr.html", tipo_evento=tipo_evento, id_usuario=id_usuario, timestamp=timestamp_actual)


if __name__ == "__main__":
    app.run(debug=True)
