from functools import wraps
from flask import session, redirect, url_for, flash

def requiere_rol(rol_requerido):
    def decorador(f):
        @wraps(f)
        def funcion_decorada(*args, **kwargs):
            if 'rol' not in session:
                flash("Debes iniciar sesión para acceder a esta página.", "warning")
                return redirect(url_for('auth.login'))
            if session['rol'] != rol_requerido:
                flash("No tenés permiso para acceder a esta sección.", "danger")
                return redirect(url_for('main.menu_principal'))
            return f(*args, **kwargs)
        return funcion_decorada
    return decorador
