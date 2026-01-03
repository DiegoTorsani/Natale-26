"""
Script per cancellare tutti i dati dal database
"""
from app import create_app, db
from app.models import User, Subject, StudySession


def clear_database():
    """Cancella tutti i dati dal database"""
    app = create_app()
    
    with app.app_context():
        print("🗑️  Cancellazione dati in corso...")
        
        # Cancella tutte le sessioni di studio
        num_sessions = StudySession.query.count()
        StudySession.query.delete()
        print(f"✅ Eliminate {num_sessions} sessioni di studio")
        
        # Cancella tutte le materie
        num_subjects = Subject.query.count()
        Subject.query.delete()
        print(f"✅ Eliminate {num_subjects} materie")
        
        # Cancella tutti gli utenti
        num_users = User.query.count()
        User.query.delete()
        print(f"✅ Eliminati {num_users} utenti")
        
        # Commit delle modifiche
        db.session.commit()
        
        print("\n✨ Database pulito con successo!")
        print("Puoi ora registrare un nuovo utente.")


if __name__ == '__main__':
    risposta = input("⚠️  Sei sicuro di voler cancellare TUTTI i dati? (si/no): ")
    if risposta.lower() in ['si', 'sì', 'yes', 'y', 's']:
        clear_database()
    else:
        print("❌ Operazione annullata")
