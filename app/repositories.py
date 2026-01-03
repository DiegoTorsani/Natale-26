"""
Repository Pattern per l'accesso ai dati
Separa la logica di business dalla logica di accesso al database
"""
from datetime import datetime
from sqlalchemy import func, extract
from app import db
from app.models import User, Subject, StudySession


class UserRepository:
    """Repository per la gestione degli utenti"""
    
    @staticmethod
    def create(username, email, password):
        """Crea un nuovo utente"""
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def find_by_username(username):
        """Trova un utente per username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def find_by_email(email):
        """Trova un utente per email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def find_by_id(user_id):
        """Trova un utente per ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def exists(username, email):
        """Verifica se esiste già un utente con username o email"""
        return User.query.filter(
            (User.username == username) | (User.email == email)
        ).first() is not None


class SubjectRepository:
    """Repository per la gestione delle materie"""
    
    @staticmethod
    def create(name, user_id, description=None, color='#3498db'):
        """Crea una nuova materia"""
        subject = Subject(
            name=name,
            user_id=user_id,
            description=description,
            color=color
        )
        db.session.add(subject)
        db.session.commit()
        return subject
    
    @staticmethod
    def find_all_by_user(user_id):
        """Trova tutte le materie di un utente"""
        return Subject.query.filter_by(user_id=user_id).order_by(Subject.name).all()
    
    @staticmethod
    def find_by_id(subject_id, user_id):
        """Trova una materia per ID (verificando che appartenga all'utente)"""
        return Subject.query.filter_by(id=subject_id, user_id=user_id).first()
    
    @staticmethod
    def update(subject, name, description=None, color=None):
        """Aggiorna una materia"""
        subject.name = name
        if description is not None:
            subject.description = description
        if color:
            subject.color = color
        db.session.commit()
        return subject
    
    @staticmethod
    def delete(subject):
        """Elimina una materia"""
        db.session.delete(subject)
        db.session.commit()
    
    @staticmethod
    def count_by_user(user_id):
        """Conta il numero di materie di un utente"""
        return Subject.query.filter_by(user_id=user_id).count()


class StudySessionRepository:
    """Repository per la gestione delle sessioni di studio"""
    
    @staticmethod
    def create(topic, duration_minutes, subject_id, user_id, date=None, notes=None):
        """Crea una nuova sessione di studio"""
        session = StudySession(
            topic=topic,
            duration_minutes=duration_minutes,
            subject_id=subject_id,
            user_id=user_id,
            date=date or datetime.utcnow().date(),
            notes=notes
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    @staticmethod
    def find_all_by_user(user_id, limit=None):
        """Trova tutte le sessioni di un utente"""
        query = StudySession.query.filter_by(user_id=user_id)\
            .order_by(StudySession.date.desc(), StudySession.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def find_by_id(session_id, user_id):
        """Trova una sessione per ID (verificando che appartenga all'utente)"""
        return StudySession.query.filter_by(id=session_id, user_id=user_id).first()
    
    @staticmethod
    def find_by_subject(subject_id, user_id):
        """Trova tutte le sessioni di una materia"""
        return StudySession.query.filter_by(subject_id=subject_id, user_id=user_id)\
            .order_by(StudySession.date.desc()).all()
    
    @staticmethod
    def update(session, topic, duration_minutes, subject_id, date, notes=None):
        """Aggiorna una sessione di studio"""
        session.topic = topic
        session.duration_minutes = duration_minutes
        session.subject_id = subject_id
        session.date = date
        session.notes = notes
        db.session.commit()
        return session
    
    @staticmethod
    def delete(session):
        """Elimina una sessione di studio"""
        db.session.delete(session)
        db.session.commit()
    
    @staticmethod
    def count_by_user(user_id):
        """Conta il numero totale di sessioni di un utente"""
        return StudySession.query.filter_by(user_id=user_id).count()
    
    @staticmethod
    def total_hours_by_user(user_id):
        """Calcola il totale delle ore studiate da un utente"""
        result = db.session.query(func.sum(StudySession.duration_minutes))\
            .filter_by(user_id=user_id).scalar()
        return round((result or 0) / 60, 2)
    
    @staticmethod
    def total_hours_by_subject(user_id):
        """
        Calcola il totale delle ore per ogni materia (LIVELLO 3 - GROUP BY)
        Restituisce una lista di dizionari con: subject_name, subject_color, total_hours, session_count
        """
        results = db.session.query(
            Subject.name,
            Subject.color,
            func.sum(StudySession.duration_minutes).label('total_minutes'),
            func.count(StudySession.id).label('session_count')
        ).join(StudySession.subject)\
         .filter(StudySession.user_id == user_id)\
         .group_by(Subject.id, Subject.name, Subject.color)\
         .order_by(func.sum(StudySession.duration_minutes).desc())\
         .all()
        
        return [
            {
                'subject_name': r[0],
                'subject_color': r[1],
                'total_hours': round(r[2] / 60, 2),
                'total_minutes': r[2],
                'session_count': r[3]
            }
            for r in results
        ]
    
    @staticmethod
    def study_trend_by_month(user_id, year=None):
        """
        Calcola le ore studiate per mese (per grafico trend)
        Restituisce una lista di dizionari con: month, total_hours
        """
        if not year:
            year = datetime.utcnow().year
        
        results = db.session.query(
            extract('month', StudySession.date).label('month'),
            func.sum(StudySession.duration_minutes).label('total_minutes')
        ).filter(
            StudySession.user_id == user_id,
            extract('year', StudySession.date) == year
        ).group_by('month')\
         .order_by('month')\
         .all()
        
        return [
            {
                'month': int(r[0]),
                'total_hours': round(r[1] / 60, 2)
            }
            for r in results
        ]
    
    @staticmethod
    def get_recent_sessions(user_id, days=7):
        """Ottiene le sessioni degli ultimi N giorni"""
        from datetime import timedelta
        date_threshold = datetime.utcnow().date() - timedelta(days=days)
        
        return StudySession.query.filter(
            StudySession.user_id == user_id,
            StudySession.date >= date_threshold
        ).order_by(StudySession.date.desc()).all()
