from flask import Blueprint, render_template, request, redirect, url_for, session
from utils.database_utils import get_db_connection
from datetime import datetime
import qrcode
from io import BytesIO
import base64

visitas_bp = Blueprint("visitas", __name__)

@visitas_bp.route("/visitas/menu")
def menu_visitas():
    return render_template("visitas/menu_visitas.html")

@visitas_bp.route("/visitas/nueva", methods=["GET", "POST"])
def formulario_visita():
    if "usuario_id" not in session or session.get("rol") != "propietario":
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        propietario_id = session["usuario_id"]

        visita = (
            request.form["nombre"],
            request.form["dni"],
            propietario_id,
            request.form["motivo"],
            request.form["marca"],
            request.form["modelo"],
            request.form["color"],
            request.form["patente"],
            request.form["fecha_ingreso"],
            request.form["hora_ingreso"],
            request.form["hora_salida"],
            "pendiente"
        )

        conn = get_db_connection()
        cursor = conn.cursor()

        # No es necesario recrear la tabla en producción
        # Solo dejarlo en create_db.py
        cursor.execute("""
            INSERT INTO visitas (
                nombre, dni, propietario_id, motivo,
                marca, modelo, color, patente,
                fecha_ingreso, hora_ingreso, hora_salida, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, visita)

        visita_id = cursor.lastrowid

        # Generar QR automáticamente
        tipo_usuario = "visita"
        timestamp_qr = datetime.now().strftime('%Y%m%d%H%M%S')
        vencimiento = f"{request.form['fecha_ingreso']}T{request.form['hora_salida']}"
        contenido_qr = f"{visita_id}|{tipo_usuario}|{timestamp_qr}|{vencimiento}"

        qr = qrcode.make(contenido_qr)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        conn.commit()
        conn.close()

        return render_template("mostrar_qr.html", qr_img=qr_base64, contenido_qr=contenido_qr)

    return render_template("visitas/formulario_visita.html")

@visitas_bp.route("/visitas/listar")
def listar_visitas():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario_id = session["usuario_id"]
    rol = session.get("rol")

    conn = get_db_connection()
    cursor = conn.cursor()

    if rol == "propietario":
        cursor.execute("""
            SELECT 
                nombre, dni, '' AS propietario, motivo, marca, modelo, color,
                patente, fecha_ingreso, hora_ingreso, hora_salida
            FROM visitas
            WHERE propietario_id = ?
        """, (usuario_id,))
    elif rol in ("seguridad", "admin"):
        cursor.execute("""
            SELECT 
                v.nombre, v.dni, u.nombre AS propietario,
                v.marca, v.modelo, v.color, v.patente,
                v.fecha_ingreso, v.hora_ingreso, v.hora_salida
            FROM visitas v
            JOIN usuarios u ON v.propietario_id = u.id
        """)
    else:
        conn.close()
        return redirect(url_for("auth.login"))

    visitas = cursor.fetchall()
    conn.close()

    return render_template("visitas/listar_visitas.html", visitas=visitas)
