# routes/__init__.py
from routes.data_api import api_bp as data_api_bp
from routes.admin_api import admin_bp as admin_bp

def init_app(app):
    app.register_blueprint(data_api_bp)
    app.register_blueprint(admin_bp)
