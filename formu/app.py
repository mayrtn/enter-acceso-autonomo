from flask import Flask
from routes import register_blueprints  

app = Flask(__name__)
app.secret_key = "clave_segura_123"

register_blueprints(app)

if __name__ == "__main__":
    app.run(debug=True)
