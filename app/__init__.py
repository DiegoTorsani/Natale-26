from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# Inizializzazione estensioni
db = SQLAlchemy()


def create_app(config_name='default'):
    """
    Application Factory Pattern
    Crea e configura l'applicazione Flask
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inizializza le estensioni con l'app
    db.init_app(app)
    
    # Registrazione dei Blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    # Creazione delle tabelle del database
    with app.app_context():
        db.create_all()
    
    return app
