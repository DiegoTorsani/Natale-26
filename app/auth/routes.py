from flask import render_template, redirect, url_for, flash, session, request
from app.auth import auth_bp
from app.repositories import UserRepository
from functools import wraps


def login_required(f):
    """Decorator per proteggere le rotte che richiedono autenticazione"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Devi effettuare il login per accedere a questa pagina.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registrazione nuovo utente"""
    # Se l'utente è già loggato, reindirizza alla dashboard
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validazione
        if not username or not email or not password:
            flash('Tutti i campi sono obbligatori.', 'danger')
            return render_template('auth/register.html')
        
        if len(username) < 3:
            flash('Il nome utente deve essere di almeno 3 caratteri.', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('La password deve essere di almeno 6 caratteri.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Le password non coincidono.', 'danger')
            return render_template('auth/register.html')
        
        # Verifica se l'utente esiste già
        if UserRepository.exists(username, email):
            flash('Nome utente o email già registrati.', 'danger')
            return render_template('auth/register.html')
        
        # Crea il nuovo utente
        try:
            user = UserRepository.create(username, email, password)
            
            # Login automatico dopo la registrazione
            session.permanent = True
            session['user_id'] = user.id
            session['username'] = user.username
            
            flash(f'Registrazione completata! Benvenuto, {user.username}!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            flash('Errore durante la registrazione. Riprova.', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login utente"""
    # Se l'utente è già loggato, reindirizza alla dashboard
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        if not username or not password:
            flash('Nome utente e password sono obbligatori.', 'danger')
            return render_template('auth/login.html')
        
        # Cerca l'utente
        user = UserRepository.find_by_username(username)
        
        if user and user.check_password(password):
            # Login riuscito
            session.permanent = True
            session['user_id'] = user.id
            session['username'] = user.username
            
            flash(f'Benvenuto, {user.username}!', 'success')
            
            # Redirect alla pagina richiesta o alla dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Nome utente o password errati.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Logout utente"""
    username = session.get('username', 'Utente')
    session.clear()
    flash(f'Arrivederci, {username}!', 'info')
    return redirect(url_for('auth.login'))
