from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from utils.database_utils import get_db_connection

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('contraseña')

        if not email or not password:
            flash("Faltan datos para iniciar sesión.", "warning")
            return redirect(url_for('auth.login'))

        conn = sqlite3.connect("sistema.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cur.fetchone()
        conn.close()

        if usuario is None:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for('auth.login'))

        if not check_password_hash(usuario['contraseña'], password):
            flash("Contraseña incorrecta.", "danger")
            return redirect(url_for('auth.login'))

        session['usuario_id'] = usuario['id']
        session['rol'] = usuario['rol']

        if usuario['requiere_cambio_password'] == 1:
            return redirect(url_for('auth.cambiar_password'))

        if usuario['rol'] == 'admin':
            return redirect(url_for('admin.menu_admin'))
        elif usuario['rol'] == 'seguridad':
            return redirect(url_for('seguridad.menu_seguridad'))
        elif usuario['rol'] == 'propietario':
            return redirect(url_for('propietario.menu_propietario'))
        else:
            flash("Rol no válido.", "warning")
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for('auth.login'))


@auth_bp.route("/completar_registro", methods=["GET", "POST"])
def completar_registro():
    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT activo, requiere_cambio_password FROM usuarios WHERE id = ?", (session["usuario_id"],))
    datos = cursor.fetchone()

    if not datos:
        conn.close()
        return redirect(url_for("auth.login"))

    activo, requiere_cambio = datos

    if activo == 1 and requiere_cambio == 0:
        conn.close()
        return redirect(url_for("main.menu_principal"))

    if activo == 1 and requiere_cambio == 1:
        conn.close()
        return redirect(url_for("auth.cambiar_password"))

    if request.method == "POST":
        direccion = request.form.get("direccion")
        telefono = request.form.get("telefono")
        patente = request.form.get("patente")
        pin_acceso = request.form.get("pin_acceso")
        pin_seguridad = request.form.get("pin_seguridad")
        tiene_convivientes = request.form.get("tiene_convivientes")

        if not pin_acceso or not pin_seguridad:
            flash("Faltan los PINs.", "warning")
            return redirect(url_for("auth.completar_registro"))

        if pin_acceso == pin_seguridad:
            flash("El PIN de acceso y el de emergencia no pueden ser iguales.", "danger")
            return redirect(url_for("auth.completar_registro"))

        cursor.execute("""
            UPDATE usuarios
            SET direccion = ?, telefono = ?, patente = ?, pin_acceso = ?, pin_seguridad = ?, activo = 1
            WHERE id = ?
        """, (direccion, telefono, patente, pin_acceso, pin_seguridad, session["usuario_id"]))
        conn.commit()

        if tiene_convivientes == "si":
            mayores = zip(
                request.form.getlist("mayores_nombre[]"),
                request.form.getlist("mayores_apellido[]"),
                request.form.getlist("mayores_dni[]"),
                request.form.getlist("mayores_email[]"),
                request.form.getlist("mayores_telefono[]")
            )
            for nombre, apellido, dni, email, telefono in mayores:
                cursor.execute("""
                    INSERT INTO convivientes (usuario_id, nombre, apellido, mayor_edad, dni, email, telefono)
                    VALUES (?, ?, ?, 1, ?, ?, ?)
                """, (session["usuario_id"], nombre, apellido, dni, email, telefono))

            menores = zip(
                request.form.getlist("menores_nombre[]"),
                request.form.getlist("menores_apellido[]"),
                request.form.getlist("menores_relacion[]")
            )
            for nombre, apellido, relacion in menores:
                cursor.execute("""
                    INSERT INTO convivientes (usuario_id, nombre, apellido, mayor_edad, relacion)
                    VALUES (?, ?, ?, 0, ?)
                """, (session["usuario_id"], nombre, apellido, relacion))

        conn.commit()
        conn.close()

        flash("Registro completado. Por seguridad, cambiá tu contraseña.", "info")
        return redirect(url_for("auth.cambiar_password"))

    return render_template("completar_registro.html")

@auth_bp.route("/cambiar_password", methods=["GET", "POST"])
def cambiar_password():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nueva = request.form.get('nueva')
        repetir = request.form.get('repetir')

        if not nueva or not repetir:
            flash("Faltan campos.", "warning")
            return redirect(url_for('auth.cambiar_password'))

        if nueva != repetir:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for('auth.cambiar_password'))

        conn = get_db_connection()
        cursor = conn.cursor()
        hash = generate_password_hash(nueva)
        cursor.execute("""
            UPDATE usuarios SET contraseña = ?, requiere_cambio_password = 0 WHERE id = ?
        """, (hash, session['usuario_id']))
        conn.commit()
        conn.close()

        flash("Contraseña actualizada. Iniciá sesión nuevamente.", "success")
        return redirect(url_for('auth.logout'))

    return render_template("auth/cambiar_password.html")
