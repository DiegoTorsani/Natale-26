from flask import render_template, redirect, url_for, flash, session, request
from datetime import datetime
from app.main import main_bp
from app.auth.routes import login_required
from app.repositories import StudySessionRepository, SubjectRepository


@main_bp.route('/')
def index():
    """Homepage"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principale con statistiche"""
    user_id = session['user_id']
    
    # Statistiche generali
    total_sessions = StudySessionRepository.count_by_user(user_id)
    total_hours = StudySessionRepository.total_hours_by_user(user_id)
    total_subjects = SubjectRepository.count_by_user(user_id)
    
    # Statistiche per materia (LIVELLO 3 - GROUP BY)
    subject_stats = StudySessionRepository.total_hours_by_subject(user_id)
    
    # Sessioni recenti
    recent_sessions = StudySessionRepository.get_recent_sessions(user_id, days=7)
    
    # Trend mensile
    current_year = datetime.utcnow().year
    monthly_trend = StudySessionRepository.study_trend_by_month(user_id, current_year)
    
    # Prepara dati per il grafico (tutti i 12 mesi)
    months_labels = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 
                     'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
    monthly_hours = [0] * 12
    for item in monthly_trend:
        monthly_hours[item['month'] - 1] = item['total_hours']
    
    return render_template('main/dashboard.html',
                         total_sessions=total_sessions,
                         total_hours=total_hours,
                         total_subjects=total_subjects,
                         subject_stats=subject_stats,
                         recent_sessions=recent_sessions,
                         months_labels=months_labels,
                         monthly_hours=monthly_hours,
                         current_year=current_year)


@main_bp.route('/sessions')
@login_required
def sessions_list():
    """Lista di tutte le sessioni di studio"""
    user_id = session['user_id']
    sessions = StudySessionRepository.find_all_by_user(user_id)
    subjects = SubjectRepository.find_all_by_user(user_id)
    
    return render_template('main/sessions_list.html', 
                         sessions=sessions,
                         subjects=subjects)


@main_bp.route('/sessions/new', methods=['GET', 'POST'])
@login_required
def session_create():
    """Crea una nuova sessione di studio"""
    user_id = session['user_id']
    subjects = SubjectRepository.find_all_by_user(user_id)
    
    # Se non ci sono materie, reindirizza alla pagina per crearle
    if not subjects:
        flash('Crea prima almeno una materia!', 'warning')
        return redirect(url_for('main.subject_create'))
    
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        duration_minutes_str = request.form.get('duration_minutes', '')
        subject_id_str = request.form.get('subject_id', '')
        date_str = request.form.get('date')
        notes = request.form.get('notes', '').strip()
        
        # Validazione
        if not topic or not duration_minutes_str or not subject_id_str or not date_str:
            flash('Compila tutti i campi obbligatori.', 'danger')
            return render_template('main/session_form.html', 
                                 subjects=subjects,
                                 today=datetime.utcnow().date())
        
        try:
            duration_minutes = int(duration_minutes_str)
            subject_id = int(subject_id_str)
        except ValueError:
            flash('Formato non valido. Controlla durata e materia.', 'danger')
            return render_template('main/session_form.html', 
                                 subjects=subjects,
                                 today=datetime.utcnow().date())
        
        if duration_minutes <= 0:
            flash('La durata deve essere maggiore di 0 minuti.', 'danger')
            return render_template('main/session_form.html', 
                                 subjects=subjects,
                                 today=datetime.utcnow().date())
        
        # Verifica che la materia appartenga all'utente
        subject = SubjectRepository.find_by_id(subject_id, user_id)
        if not subject:
            flash('Materia non valida.', 'danger')
            return render_template('main/session_form.html', 
                                 subjects=subjects,
                                 today=datetime.utcnow().date())
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            StudySessionRepository.create(
                topic=topic,
                duration_minutes=duration_minutes,
                subject_id=subject_id,
                user_id=user_id,
                date=date,
                notes=notes if notes else None
            )
            flash('Sessione di studio creata con successo!', 'success')
            return redirect(url_for('main.sessions_list'))
        except ValueError as ve:
            flash(f'Data non valida: {str(ve)}', 'danger')
        except Exception as e:
            flash(f'Errore durante la creazione della sessione: {str(e)}', 'danger')
    
    return render_template('main/session_form.html', 
                         subjects=subjects,
                         study_session=None,
                         today=datetime.utcnow().date())


@main_bp.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
@login_required
def session_edit(session_id):
    """Modifica una sessione di studio"""
    user_id = session['user_id']
    study_session = StudySessionRepository.find_by_id(session_id, user_id)
    
    if not study_session:
        flash('Sessione non trovata.', 'danger')
        return redirect(url_for('main.sessions_list'))
    
    subjects = SubjectRepository.find_all_by_user(user_id)
    
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        duration_minutes = request.form.get('duration_minutes', type=int)
        subject_id = request.form.get('subject_id', type=int)
        date_str = request.form.get('date')
        notes = request.form.get('notes', '').strip()
        
        # Validazione
        if not topic or not duration_minutes or not subject_id or not date_str:
            flash('Compila tutti i campi obbligatori.', 'danger')
            return render_template('main/session_form.html', 
                                 subjects=subjects, 
                                 session=study_session)
        
        if duration_minutes <= 0:
            flash('La durata deve essere maggiore di 0 minuti.', 'danger')
            return render_template('main/session_form.html', 
                                 subjects=subjects, 
                                 session=study_session)
        
        # Verifica che la materia appartenga all'utente
        subject = SubjectRepository.find_by_id(subject_id, user_id)
        if not subject:
            flash('Materia non valida.', 'danger')
            return render_template('main/session_form.html', 
                                 subjects=subjects, 
                                 session=study_session)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            StudySessionRepository.update(
                study_session,
                topic=topic,
                duration_minutes=duration_minutes,
                subject_id=subject_id,
                date=date,
                notes=notes if notes else None
            )
            flash('Sessione aggiornata con successo!', 'success')
            return redirect(url_for('main.sessions_list'))
        except ValueError:
            flash('Data non valida.', 'danger')
        except Exception as e:
            flash('Errore durante l\'aggiornamento della sessione.', 'danger')
    
    return render_template('main/session_form.html', 
                         subjects=subjects,
                         study_session=study_session,
                         today=datetime.utcnow().date())


@main_bp.route('/sessions/<int:session_id>/delete', methods=['POST'])
@login_required
def session_delete(session_id):
    """Elimina una sessione di studio"""
    user_id = session['user_id']
    study_session = StudySessionRepository.find_by_id(session_id, user_id)
    
    if not study_session:
        flash('Sessione non trovata.', 'danger')
        return redirect(url_for('main.sessions_list'))
    
    try:
        StudySessionRepository.delete(study_session)
        flash('Sessione eliminata con successo.', 'success')
    except Exception as e:
        flash('Errore durante l\'eliminazione della sessione.', 'danger')
    
    return redirect(url_for('main.sessions_list'))


@main_bp.route('/subjects')
@login_required
def subjects_list():
    """Lista di tutte le materie"""
    user_id = session['user_id']
    subjects = SubjectRepository.find_all_by_user(user_id)
    
    return render_template('main/subjects_list.html', subjects=subjects)


@main_bp.route('/subjects/new', methods=['GET', 'POST'])
@login_required
def subject_create():
    """Crea una nuova materia"""
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#3498db')
        
        # Validazione
        if not name:
            flash('Il nome della materia è obbligatorio.', 'danger')
            return render_template('main/subject_form.html', subject=None)
        
        try:
            SubjectRepository.create(
                name=name,
                user_id=user_id,
                description=description if description else None,
                color=color
            )
            flash('Materia creata con successo!', 'success')
            return redirect(url_for('main.subjects_list'))
        except Exception as e:
            flash('Errore durante la creazione della materia.', 'danger')
    
    return render_template('main/subject_form.html', subject=None)


@main_bp.route('/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
@login_required
def subject_edit(subject_id):
    """Modifica una materia"""
    user_id = session['user_id']
    subject = SubjectRepository.find_by_id(subject_id, user_id)
    
    if not subject:
        flash('Materia non trovata.', 'danger')
        return redirect(url_for('main.subjects_list'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#3498db')
        
        # Validazione
        if not name:
            flash('Il nome della materia è obbligatorio.', 'danger')
            return render_template('main/subject_form.html', subject=subject)
        
        try:
            SubjectRepository.update(
                subject,
                name=name,
                description=description if description else None,
                color=color
            )
            flash('Materia aggiornata con successo!', 'success')
            return redirect(url_for('main.subjects_list'))
        except Exception as e:
            flash('Errore durante l\'aggiornamento della materia.', 'danger')
    
    return render_template('main/subject_form.html', subject=subject)


@main_bp.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
def subject_delete(subject_id):
    """Elimina una materia"""
    user_id = session['user_id']
    subject = SubjectRepository.find_by_id(subject_id, user_id)
    
    if not subject:
        flash('Materia non trovata.', 'danger')
        return redirect(url_for('main.subjects_list'))
    
    try:
        SubjectRepository.delete(subject)
        flash('Materia eliminata con successo.', 'success')
    except Exception as e:
        flash('Errore durante l\'eliminazione della materia.', 'danger')
    
    return redirect(url_for('main.subjects_list'))


@main_bp.route('/subjects/<int:subject_id>')
@login_required
def subject_detail(subject_id):
    """Dettaglio di una materia con tutte le sue sessioni"""
    user_id = session['user_id']
    subject = SubjectRepository.find_by_id(subject_id, user_id)
    
    if not subject:
        flash('Materia non trovata.', 'danger')
        return redirect(url_for('main.subjects_list'))
    
    sessions = StudySessionRepository.find_by_subject(subject_id, user_id)
    
    # Calcola il totale ore per questa materia
    total_minutes = sum(s.duration_minutes for s in sessions)
    total_hours = round(total_minutes / 60, 2)
    
    return render_template('main/subject_detail.html',
                         subject=subject,
                         sessions=sessions,
                         total_hours=total_hours,
                         session_count=len(sessions))
