from flask import Blueprint, render_template, redirect, url_for, session, flash

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def menu_principal():
    if "usuario_id" in session:
        tipo = session.get("rol")  # corregido: debería ser "rol", no "tipo_usuario"
        if tipo == "admin":
            return render_template("admin/menu_admin.html")
        elif tipo == "seguridad":
            return render_template("seguridad/menu_seguridad.html")
        elif tipo == "propietario":
            return render_template("propietario/menu_propietario.html")
        else:
            flash("Rol no válido.", "warning")
            return redirect(url_for("auth.login"))
    else:
        return redirect(url_for("auth.login"))

@main_bp.route("/confirmacion")
def confirmacion():
    return render_template("confirmacion.html")
