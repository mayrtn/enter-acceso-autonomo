from .auth_routes import auth_bp
from .admin_routes import admin_bp
from .propietario_routes import propietario_bp
from .seguridad_routes import seguridad_bp
from .visitas_routes import visitas_bp
from .qr_routes import qr_bp
from .main import main_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(propietario_bp)
    app.register_blueprint(seguridad_bp)
    app.register_blueprint(visitas_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(main_bp)
