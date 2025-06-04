from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.auth_utils import requiere_rol
from utils.database_utils import registrar_usuario, registrar_vehiculo, registrar_emergencia, get_db_connection
from datetime import datetime
from werkzeug.security import generate_password_hash
import qrcode
from io import BytesIO
import base64

propietario_bp = Blueprint("propietario", __name__)

@propietario_bp.route("/propietario/menu")
@requiere_rol("propietario")
def menu_propietario():
    return render_template("propietario/menu_propietario.html")

@propietario_bp.route("/propietario/nuevo", methods=["GET"])
def nuevo_propietario():
    return redirect(url_for('propietario.nuevo_propietario'))

@propietario_bp.route("/propietario/verificar", methods=["POST"])
def verificar_propietario():
    datos = {
        "nombre": request.form["nombre"],
        "dni": request.form["dni"],
        "telefono": request.form["telefono"],
        "email": request.form["email"],
        "unidad_funcional": request.form["unidad_funcional"],
        "rol": "propietario"
    }
    return render_template("propietario/verificar_propietario.html", datos=datos)

@propietario_bp.route("/propietario/confirmar", methods=["POST"])
def confirmar_propietario():
    datos = {
        "nombre": request.form["nombre"],
        "dni": request.form["dni"],
        "telefono": request.form["telefono"],
        "email": request.form["email"],
        "unidad_funcional": request.form["unidad_funcional"],
        "rol": "propietario"
    }
    registrar_usuario(**datos)
    return render_template("propietario/registro_exitoso.html", datos=datos)

@propietario_bp.route("/nuevo_vehiculo", methods=["GET", "POST"])
@requiere_rol("propietario")
def nuevo_vehiculo():
    if request.method == "POST":
        id_propietario = request.form["id_propietario"]
        marca = request.form["marca"]
        modelo = request.form["modelo"]
        color = request.form["color"]
        patente = request.form["patente"]

        registrar_vehiculo(id_propietario, marca, modelo, color, patente)
        return redirect(url_for("main.menu_propietario"))

    return render_template("propietario/nuevo_vehiculo.html")

@propietario_bp.route("/propietario/nueva_emergencia", methods=["GET", "POST"])
@requiere_rol("propietario")
def nueva_emergencia():
    if request.method == "POST":
        id_propietario = request.form["id_propietario"]
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"]
        ubicacion = request.form.get("ubicacion", "")
        fecha = datetime.now()

        registrar_emergencia(id_propietario, tipo, descripcion, ubicacion, fecha)
        flash("Emergencia reportada. El personal fue notificado.")
        return redirect(url_for("main.menu_principal"))

    return render_template("propietario/nueva_emergencia.html")

@propietario_bp.route("/llave-virtual/generar-qr", methods=["GET", "POST"])
@requiere_rol("propietario")
def generar_qr_llave_virtual():
    if request.method == "POST":
        pin_ingreso = request.form["pin_ingreso"]

        if pin_ingreso != session.get("pin_acceso"):
            return "PIN incorrecto", 403

        id_usuario = session.get("usuario_id")
        tipo_usuario = "propietario"
        timestamp_qr = datetime.now().strftime('%Y%m%d%H%M%S')
        contenido_qr = f"{id_usuario}|{tipo_usuario}|{timestamp_qr}"

        qr = qrcode.make(contenido_qr)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return render_template("mostrar_qr.html", qr_img=qr_base64, contenido_qr=contenido_qr)

    return render_template("propietario/generar_qr.html")

@propietario_bp.route("/visita/generar-qr", methods=["GET", "POST"])
@requiere_rol("propietario")
def generar_qr_visita():
    if request.method == "POST":
        pin_ingreso = request.form["pin_ingreso"]
        vencimiento_str = request.form["vencimiento"]

        if pin_ingreso != session.get("pin_acceso"):
            return "PIN incorrecto", 403

        try:
            datetime.strptime(vencimiento_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return "Formato de vencimiento inválido", 400

        id_usuario = session.get("usuario_id")
        tipo_usuario = "visita"
        timestamp_qr = datetime.now().strftime('%Y%m%d%H%M%S')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM visitas 
            WHERE propietario_id = ? 
            ORDER BY id DESC LIMIT 1
        """, (id_usuario,))
        ultima_visita = cursor.fetchone()
        conn.close()

        if not ultima_visita:
            return "No se encontró una visita reciente para generar el QR.", 400

        id_visita = ultima_visita[0]
        contenido_qr = f"{id_usuario}|{tipo_usuario}|{timestamp_qr}|{vencimiento_str}|{id_visita}"

        qr = qrcode.make(contenido_qr)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return render_template("mostrar_qr.html", qr_img=qr_base64, contenido_qr=contenido_qr)

    return render_template("propietario/generar_qr_visita.html")

@propietario_bp.route("/personal/generar-qr", methods=["GET", "POST"])
@requiere_rol("propietario")
def generar_qr_personal():
    if request.method == "POST":
        pin_ingreso = request.form["pin_ingreso"]
        vencimiento_str = request.form["vencimiento"]

        if pin_ingreso != session.get("pin_acceso"):
            return "PIN incorrecto", 403

        try:
            datetime.strptime(vencimiento_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            return "Formato de vencimiento inválido", 400

        id_usuario = session.get("usuario_id")
        tipo_usuario = "visita"
        timestamp_qr = datetime.now().strftime('%Y%m%d%H%M%S')
        contenido_qr = f"{id_usuario}|{tipo_usuario}|{timestamp_qr}|{vencimiento_str}"

        qr = qrcode.make(contenido_qr)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return render_template("mostrar_qr.html", qr_img=qr_base64, contenido_qr=contenido_qr)

    return render_template("propietario/generar_qr_personal.html")

@propietario_bp.route("/perfil")
def perfil():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (session["usuario_id"],))
    usuario = cursor.fetchone()

    cursor.execute("SELECT * FROM vehiculos WHERE propietario_id = ?", (session["usuario_id"],))
    vehiculos = cursor.fetchall()

    conn.close()

    return render_template("propietario/perfil.html", usuario=usuario, vehiculos=vehiculos)

@propietario_bp.route("/perfil/actualizar_seguridad", methods=["POST"])
def actualizar_seguridad():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    nueva_contraseña = request.form.get("nueva_contraseña")
    pin_acceso = request.form.get("pin_acceso")
    pin_seguridad = request.form.get("pin_seguridad")

    if pin_acceso and pin_seguridad and pin_acceso == pin_seguridad:
        flash("El PIN de acceso y el de emergencia no pueden ser iguales.", "danger")
        return redirect(url_for("propietario.perfil"))

    if nueva_contraseña:
        hash_pwd = generate_password_hash(nueva_contraseña)
        cursor.execute("UPDATE usuarios SET contraseña = ? WHERE id = ?", (hash_pwd, session["usuario_id"]))

    if pin_acceso:
        cursor.execute("UPDATE usuarios SET pin_acceso = ? WHERE id = ?", (pin_acceso, session["usuario_id"]))
    if pin_seguridad:
        cursor.execute("UPDATE usuarios SET pin_seguridad = ? WHERE id = ?", (pin_seguridad, session["usuario_id"]))

    conn.commit()
    conn.close()

    flash("Datos de seguridad actualizados.", "success")
    return redirect(url_for("propietario.perfil"))


@propietario_bp.route("/perfil/verificar", methods=["POST"])
def verificar_perfil():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    datos = {
        "direccion": request.form.get("direccion"),
        "telefono": request.form.get("telefono"),
        "patente": request.form.get("patente"),
        "nueva_contraseña": request.form.get("nueva_contraseña"),
        "pin_acceso": request.form.get("pin_acceso"),
        "pin_seguridad": request.form.get("pin_seguridad"),
        "convivientes": [],
        "vehiculos": []
    }

    # Convivientes
    nombres = request.form.getlist("convivientes_nombres[]")
    apellidos = request.form.getlist("convivientes_apellidos[]")
    edades = request.form.getlist("convivientes_edades[]")
    relaciones = request.form.getlist("convivientes_relaciones[]")

    for nombre, apellido, edad, relacion in zip(nombres, apellidos, edades, relaciones):
        if nombre and apellido:
            datos["convivientes"].append({
                "nombre": nombre,
                "apellido": apellido,
                "edad": edad,
                "relacion": relacion
            })

    # Vehículos
    marcas = request.form.getlist("vehiculos_marcas[]")
    modelos = request.form.getlist("vehiculos_modelos[]")
    colores = request.form.getlist("vehiculos_colores[]")
    patentes = request.form.getlist("vehiculos_patentes[]")

    for marca, modelo, color, patente in zip(marcas, modelos, colores, patentes):
        if marca and modelo and patente:
            datos["vehiculos"].append({
                "marca": marca,
                "modelo": modelo,
                "color": color,
                "patente": patente
            })

    return render_template("propietario/verificar_perfil.html", datos=datos)

@propietario_bp.route("/perfil/guardar", methods=["POST"])
def guardar_perfil():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    direccion = request.form.get("direccion")
    telefono = request.form.get("telefono")
    patente = request.form.get("patente")
    nueva_contraseña = request.form.get("nueva_contraseña")
    pin_acceso = request.form.get("pin_acceso")
    pin_seguridad = request.form.get("pin_seguridad")

    if pin_acceso and pin_seguridad and pin_acceso == pin_seguridad:
        flash("El PIN de acceso y el de emergencia no pueden ser iguales.", "danger")
        return redirect(url_for("propietario.perfil"))

    cursor.execute("""
        UPDATE usuarios SET direccion = ?, telefono = ?, patente = ? 
        WHERE id = ?
    """, (direccion, telefono, patente, session["usuario_id"]))

    if nueva_contraseña:
        hash_pwd = generate_password_hash(nueva_contraseña)
        cursor.execute("UPDATE usuarios SET contraseña = ? WHERE id = ?", (hash_pwd, session["usuario_id"]))

    if pin_acceso:
        cursor.execute("UPDATE usuarios SET pin_acceso = ? WHERE id = ?", (pin_acceso, session["usuario_id"]))
    if pin_seguridad:
        cursor.execute("UPDATE usuarios SET pin_seguridad = ? WHERE id = ?", (pin_seguridad, session["usuario_id"]))

    # Convivientes
    cursor.execute("DELETE FROM convivientes WHERE usuario_id = ?", (session["usuario_id"],))
    i = 0
    while True:
        nombre = request.form.get(f"convivientes[{i}][nombre]")
        apellido = request.form.get(f"convivientes[{i}][apellido]")
        edad = request.form.get(f"convivientes[{i}][edad]")
        relacion = request.form.get(f"convivientes[{i}][relacion]")
        if not nombre:
            break
        cursor.execute("""
            INSERT INTO convivientes (usuario_id, nombre, apellido, edad, relacion)
            VALUES (?, ?, ?, ?, ?)
        """, (session["usuario_id"], nombre, apellido, edad or None, relacion or None))
        i += 1

    # Vehículos
    cursor.execute("DELETE FROM vehiculos WHERE usuario_id = ?", (session["usuario_id"],))
    j = 0
    while True:
        marca = request.form.get(f"vehiculos[{j}][marca]")
        modelo = request.form.get(f"vehiculos[{j}][modelo]")
        color = request.form.get(f"vehiculos[{j}][color]")
        patente_vehiculo = request.form.get(f"vehiculos[{j}][patente]")
        if not marca:
            break
        cursor.execute("""
            INSERT INTO vehiculos (usuario_id, marca, modelo, color, patente)
            VALUES (?, ?, ?, ?, ?)
        """, (session["usuario_id"], marca, modelo, color, patente_vehiculo))
        j += 1

    conn.commit()
    conn.close()

    flash("Los cambios se realizaron correctamente.", "success")
    return redirect(url_for("propietario.perfil"))
