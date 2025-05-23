from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3

#crea el blueprint para llamarlo desde app.py
validacion_usuarios = Blueprint('validacion_usuarios', __name__)

# Función para obtener usuario por email y password
#TODO hashear password

def get_user(email, password):
    conn = sqlite3.connect('users.db') #inicia la conexion
    cursor = conn.cursor() 
    cursor.execute("SELECT id, username, email, password, user_type FROM users WHERE email = ? AND password = ?", (email, password))
    #apunta el cursor a el usuario si coinciden pass y email
    user = cursor.fetchone() #crea la variable user y le da el valor del usuario al que apunta el cursor
    conn.close() #cierra la conexion
    return user

@validacion_usuarios.route('/', methods=['GET', 'POST'])
#recibe solicitudes HTTP del tipo GET y POST
def validar_usuario():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')  #toma los datos del formulario
        user = get_user(email, password) #llama al metodo con esos parametros

        if user: #si el usuario existe :
            session['user_id'] = user[0] #userID en la tabla
            session['user_type'] = user[4] #Rol de usuario en la tabla
            #durante toda la sesión se recuerda quién está logueado y qué permisos tiene.

            if user[4] == 'admin':
                    return redirect(url_for('validacion_usuarios.dashboard_admin'))
            elif user[4] == 'prop':
                    return redirect(url_for('validacion_usuarios.dashboard_prop'))
            elif user[4] == 'segu':
                    return redirect(url_for('validacion_usuarios.dashboard_seguridad'))
            else:
                return render_template('home.html', error="Tipo de usuario desconocido")
        else:
               return render_template('home.html', error="Credenciales inválidas")
    return render_template('home.html') # si el usuario no envio datos o fallo la autenticacion, vuelve al home
              
@validacion_usuarios.route('/logout')
def logout():
    session.clear()  # Borra toda la información del usuario en la sesión
    return redirect(url_for('validacion_usuarios.home'))  # Redirige a la página /home

# Rutas para los dashboards y home
# definen los endpoints que se usan en los redirects y renderiza el template correspondiente

@validacion_usuarios.route('/dashboard-admin')
def dashboard_admin():
    return render_template('dashboard-admin.html')

@validacion_usuarios.route('/dashboard-prop')
def dashboard_prop():
    return render_template('dashboard-prop.html')

@validacion_usuarios.route('/dashboard-seguridad')
def dashboard_seguridad():
    return render_template('dashboard-seguridad.html')

@validacion_usuarios.route('/home')
def home():
    return render_template('home.html')