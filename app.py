# app.py
from flask import Flask
from config import Config
from routes import init_app

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_app(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
