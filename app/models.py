from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """Modello per gli utenti dell'applicazione"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    subjects = db.relationship('Subject', backref='user', lazy=True, cascade='all, delete-orphan')
    study_sessions = db.relationship('StudySession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash della password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica della password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Subject(db.Model):
    """Modello per le materie d'esame"""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3498db')  # Colore esadecimale per visualizzazione
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    study_sessions = db.relationship('StudySession', backref='subject', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Subject {self.name}>'


class StudySession(db.Model):
    """Modello per le sessioni di studio"""
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(200), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)  # Durata in minuti
    notes = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chiavi esterne
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    @property
    def duration_hours(self):
        """Restituisce la durata in ore (formato decimale)"""
        return round(self.duration_minutes / 60, 2)
    
    def __repr__(self):
        return f'<StudySession {self.topic} - {self.duration_minutes}min>'
