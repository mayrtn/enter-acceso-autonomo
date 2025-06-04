from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.auth_utils import requiere_rol
from werkzeug.security import generate_password_hash
from utils.database_utils import get_db_connection
import sqlite3

admin_bp = Blueprint("admin", __name__)

import random
import string

def generar_password_temporal(longitud=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

@admin_bp.route("/admin/crear_usuario", methods=["GET", "POST"])
@requiere_rol("admin")
def crear_usuario():
    if request.method == "POST":
        rol = request.form["rol"]

        if rol == "propietario":
            nombre = request.form["nombre"]
            dni = request.form["dni"]
            unidad_funcional = request.form["unidad_funcional"]
            telefono = request.form["telefono"]
            email = request.form["email"]
            apellido = ""  # No se usa
        else:
            nombre = request.form["nombre"]
            apellido = request.form["apellido"]
            dni = request.form["dni"]
            email = request.form["email"]
            unidad_funcional = ""
            telefono = ""

        # Generar contraseña temporal
        contrasena = generar_password_temporal()
        hash_contrasena = generate_password_hash(contrasena)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO usuarios (nombre, apellido, dni, email, contraseña, rol, activo, requiere_cambio_password,
                                      unidad_funcional, telefono)
                VALUES (?, ?, ?, ?, ?, ?, 0, 1, ?, ?)
            """, (nombre, apellido, dni, email, hash_contrasena, rol, unidad_funcional, telefono))
            conn.commit()
            flash(f"Usuario creado exitosamente. Contraseña temporal: {contrasena}", "success")
        except sqlite3.IntegrityError:
            flash("Error: el DNI o email ya existen.", "danger")
        conn.close()
        return redirect(url_for("admin.crear_usuario"))

    return render_template("admin/crear_usuario_dinamico.html")

@admin_bp.route("/admin/menu_admin")
@requiere_rol('admin')
def menu_admin():
    return render_template("admin/menu_admin.html")
