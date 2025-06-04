from flask import Blueprint, render_template, request
from datetime import datetime
from utils.database_utils import get_db_connection
import sqlite3

qr_bp = Blueprint("qr", __name__)

@qr_bp.route("/escanear_qr", methods=["POST"])
def escanear_qr():
    contenido_qr = request.form.get("contenido_qr", "")
    partes = contenido_qr.split("|")

    if len(partes) < 3:
        return "<p style='color: red;'>Contenido del QR inválido.</p>"

    id_usuario, tipo_usuario, qr_timestamp = partes[0:3]
    vencimiento_str = partes[3] if len(partes) >= 4 else None

    if vencimiento_str:
        try:
            vencimiento = datetime.strptime(vencimiento_str, "%Y-%m-%dT%H:%M")
            if datetime.now() > vencimiento:
                return "<p style='color: red;'>QR vencido. No se permite el acceso.</p>"
        except ValueError:
            return "<p style='color: red;'>Formato de vencimiento inválido.</p>"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT tipo_evento FROM accesos_qr
        WHERE id_usuario = ? AND tipo_usuario = ? AND qr_timestamp = ?
        ORDER BY timestamp
    """, (id_usuario, tipo_usuario, qr_timestamp))
    eventos = cur.fetchall()

    if len(eventos) >= 2:
        conn.close()
        return "<p style='color: red;'>Este QR ya fue escaneado dos veces (ingreso y egreso).</p>"

    tipo_evento = "ingreso" if not eventos or eventos[-1][0] == "egreso" else "egreso"
    timestamp_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cur.execute("""
        INSERT INTO accesos_qr (id_usuario, tipo_usuario, tipo_evento, timestamp, vencimiento, qr_timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id_usuario, tipo_usuario, tipo_evento, timestamp_actual, vencimiento_str, qr_timestamp))

    conn.commit()
    conn.close()

    return f"""
        <p style='color: green;'>
            Acceso registrado correctamente como <strong>{tipo_evento}</strong><br>
            Usuario ID: {id_usuario}<br>
            Fecha y hora: {timestamp_actual}
        </p>
    """

@qr_bp.route("/listar_accesos")
def listar_accesos_qr():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT a.usuario_id, a.tipo_usuario, a.tipo_evento, a.timestamp, 
               COALESCE(u.nombre, v.nombre, 'Desconocido') AS nombre
        FROM accesos_qr a
        LEFT JOIN usuarios u ON a.tipo_usuario = 'propietario' AND u.id = a.usuario_id
        LEFT JOIN visitas v ON a.tipo_usuario = 'visita' AND v.id = a.usuario_id
        ORDER BY a.timestamp DESC
    """)
    accesos = cur.fetchall()
    conn.close()

    return render_template("seguridad/listar_accesos_qr.html", accesos=accesos)

@qr_bp.route("/llave-virtual/validar-pin", methods=["POST"])
def validar_pin():
    id_usuario = request.form.get("id_usuario")
    pin_ingresado = request.form.get("pin_ingresado")

    if not id_usuario or not pin_ingresado:
        return "Faltan datos requeridos", 400

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM usuarios WHERE id = ?", (id_usuario,))
    usuario = cur.fetchone()

    if not usuario:
        conn.close()
        return "Usuario no encontrado", 404

    if usuario["bloqueado"]:
        conn.close()
        return render_template("llave_virtual/bloqueado.html", nombre=usuario["nombre"])

    if pin_ingresado == usuario["pin_acceso"]:
        cur.execute("UPDATE usuarios SET intentos_fallidos = 0 WHERE id = ?", (id_usuario,))
        conn.commit()
        conn.close()
        return render_template("llave_virtual/pin_valido.html", nombre=usuario["nombre"], id_usuario=id_usuario)

    if pin_ingresado == usuario["pin_seguridad"]:
        cur.execute("UPDATE usuarios SET intentos_fallidos = 0 WHERE id = ?", (id_usuario,))
        conn.commit()
        conn.close()
        return render_template("llave_virtual/pin_seguridad.html", nombre=usuario["nombre"], id_usuario=id_usuario)

    intentos = usuario["intentos_fallidos"] + 1
    bloqueado = 1 if intentos >= 3 else 0

    cur.execute("""
        UPDATE usuarios SET intentos_fallidos = ?, bloqueado = ? WHERE id = ?
    """, (intentos, bloqueado, id_usuario))
    conn.commit()
    conn.close()

    if bloqueado:
        return render_template("llave_virtual/bloqueado.html", nombre=usuario["nombre"])
    else:
        return render_template("llave_virtual/pin_incorrecto.html", nombre=usuario["nombre"], intentos=intentos)
