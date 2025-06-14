from flask import Flask, render_template
from scripts.validacion_usuarios import validacion_usuarios
from scripts.partials_admin import * #dejar solo modulos importantes
from scripts.partials_prop import *
from scripts.partials_segu import *

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta_1234567890' #

app.register_blueprint(validacion_usuarios)
app.register_blueprint(partials_admin)
app.register_blueprint(partials_prop)
app.register_blueprint(partials_segu)


@app.route('/')
def home():
    return render_template('home.html') #llama a la validacion desde home

if __name__=='__main__': #si estamos en el main lanzamos la app
    app.run(debug=True) #activa modo debug


    

