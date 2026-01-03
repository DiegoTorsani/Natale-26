import os
from datetime import timedelta


class Config:
    """Configurazione base dell'applicazione"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///studyplanner.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurazione sessione
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """Configurazione per sviluppo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configurazione per produzione"""
    DEBUG = False
    # In produzione, SECRET_KEY deve essere sempre impostata
    SECRET_KEY = os.environ.get('SECRET_KEY')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
