from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from utils.auth_utils import requiere_rol
from utils.database_utils import get_db_connection
from datetime import datetime
import qrcode
from io import BytesIO
import base64

seguridad_bp = Blueprint("seguridad", __name__)

@seguridad_bp.route("/seguridad/menu")
@requiere_rol("seguridad")
def menu_seguridad():
    return render_template("seguridad/menu_seguridad.html")

@seguridad_bp.route("/seguridad/registro_qr", methods=["GET", "POST"])
@requiere_rol("seguridad")
def registro_qr():
    if request.method == "POST":
        id_usuario = request.form["id_usuario"]
        tipo_usuario = request.form["tipo_usuario"]
        timestamp_qr = datetime.now().strftime('%Y%m%d%H%M%S')
        datos_qr = f"{id_usuario}|{tipo_usuario}|{timestamp_qr}"

        qr = qrcode.make(datos_qr)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return render_template("mostrar_qr.html", qr_img=qr_base64, contenido_qr=datos_qr)

    return render_template("seguridad/registro_acceso_qr.html")

@seguridad_bp.route("/panel_accesos_recientes")
@requiere_rol("seguridad")
def panel_accesos_recientes():
    return render_template("seguridad/panel_accesos_recientes.html")

@seguridad_bp.route("/api/accesos_recientes")
@requiere_rol("seguridad")
def api_accesos_recientes():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT a.tipo_usuario, a.tipo_evento, a.timestamp,
               COALESCE(u.nombre, v.nombre, 'Desconocido') AS nombre
        FROM accesos_qr a
        LEFT JOIN usuarios u ON a.tipo_usuario = 'propietario' AND u.id = a.id_usuario
        LEFT JOIN visitas v ON a.tipo_usuario = 'visita' AND v.id = a.id_usuario
        ORDER BY a.timestamp DESC
        LIMIT 10
    """)

    accesos = cursor.fetchall()
    conn.close()

    datos = [
        {
            "tipo_usuario": tipo_usuario,
            "tipo_evento": tipo_evento,
            "timestamp": timestamp,
            "nombre": nombre
        }
        for (tipo_usuario, tipo_evento, timestamp, nombre) in accesos
    ]

    return jsonify(datos)

@seguridad_bp.route("/seguridad/visitas", methods=["GET"])
@requiere_rol("seguridad")
def panel_visitas_seguridad():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT visitas.id, visitas.nombre, visitas.dni, visitas.fecha_ingreso,
               visitas.estado, visitas.hora_ingreso, visitas.hora_salida,
               COALESCE(usuarios.nombre || ' ' || usuarios.apellido, 'Desconocido') AS propietario
        FROM visitas
        JOIN usuarios ON visitas.propietario_id = usuarios.id
        ORDER BY visitas.fecha_ingreso DESC
    """)
    visitas = cursor.fetchall()
    conn.close()

    return render_template("panel_visitas_seguridad.html", visitas=visitas)

@seguridad_bp.route("/seguridad/ingreso/<int:visita_id>")
@requiere_rol("seguridad")
def registrar_ingreso(visita_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE visitas
        SET estado = 'ingresado', hora_ingreso = datetime('now', 'localtime')
        WHERE id = ? AND estado = 'pendiente'
    """, (visita_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("seguridad.panel_visitas_seguridad"))

@seguridad_bp.route("/seguridad/egreso/<int:visita_id>")
@requiere_rol("seguridad")
def registrar_egreso(visita_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE visitas
        SET estado = 'egresado', hora_salida = datetime('now', 'localtime')
        WHERE id = ? AND estado = 'ingresado'
    """, (visita_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("seguridad.panel_visitas_seguridad"))

@seguridad_bp.route("/accesos/propietarios")
@requiere_rol("seguridad")
def listar_accesos_propietario():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM accesos_qr 
        WHERE tipo_usuario = 'propietario' 
        ORDER BY timestamp DESC
    """)
    accesos = cursor.fetchall()
    conn.close()
    return render_template("seguridad/accesos_propietarios.html", accesos=accesos)

@seguridad_bp.route("/accesos/visitas")
@requiere_rol("seguridad")
def listar_accesos_visitas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM accesos_qr 
        WHERE tipo_usuario = 'visita' 
        ORDER BY timestamp DESC
    """)
    accesos = cursor.fetchall()
    conn.close()
    return render_template("seguridad/accesos_visitas.html", accesos=accesos)

@seguridad_bp.route("/escanear_qr_camara")
@requiere_rol("seguridad")
def escanear_qr_camara():
    return render_template("escanear_qr_camara.html")
