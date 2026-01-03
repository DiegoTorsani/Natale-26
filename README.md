# 📚 StudyPlanner - Gestione Ore di Studio

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📖 Descrizione

**StudyPlanner** è un'applicazione web sviluppata con Flask per aiutare gli studenti a tracciare e gestire le proprie sessioni di studio in preparazione all'esame di maturità. L'applicazione permette di organizzare lo studio per materie, registrare le ore dedicate ad ogni argomento e visualizzare statistiche dettagliate sui progressi.

### ✨ Funzionalità Principali

#### 🔐 Livello 1 - Base (Implementato)
- **Autenticazione Completa**: Sistema di registrazione e login con hashing delle password
- **CRUD Sessioni di Studio**: Crea, leggi, aggiorna ed elimina sessioni di studio
- **Gestione Profilo Utente**: Ogni utente ha il proprio spazio personale

#### 📊 Livello 2 - Intermedio (Implementato)
- **Gestione Materie**: Sistema di categorie (relazione 1-a-N)
- **Associazione Sessione-Materia**: Ogni sessione è collegata a una specifica materia
- **Colori Personalizzati**: Ogni materia ha un colore distintivo per facilitare la visualizzazione

#### 🚀 Livello 3 - Avanzato (Implementato)
- **Dashboard con Statistiche Aggregate**: Utilizza query SQL complesse con `GROUP BY`, `SUM`, `AVG`
- **Ore Totali per Materia**: Visualizzazione del tempo dedicato a ogni materia
- **Grafici Interattivi**: 
  - Grafico a linee per il trend mensile
  - Grafico a torta per la distribuzione delle ore per materia
- **Statistiche Dettagliate**: Conteggio sessioni, ore totali, media ore per sessione

#### 🎯 Funzionalità Bonus
- **Sessioni Recenti**: Vista rapida delle ultime attività di studio
- **Dettaglio Materia**: Pagina dedicata per ogni materia con tutte le sue sessioni
- **Interfaccia Responsiva**: Design moderno con Bootstrap 5
- **Validazione Form**: Controlli lato server per garantire l'integrità dei dati

---

## 🏗️ Architettura del Progetto

Il progetto segue un'architettura professionale come richiesto dalla consegna:

### Struttura Directory
```
Natale-26/
│
├── app/
│   ├── __init__.py              # Application Factory
│   ├── models.py                # Modelli SQLAlchemy
│   ├── repositories.py          # Repository Pattern
│   │
│   ├── auth/                    # Blueprint Autenticazione
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── main/                    # Blueprint Main
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   └── templates/               # Template Jinja2
│       ├── base.html            # Template base
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       └── main/
│           ├── dashboard.html
│           ├── sessions_list.html
│           ├── session_form.html
│           ├── subjects_list.html
│           ├── subject_form.html
│           └── subject_detail.html
│
├── config.py                    # Configurazioni
├── run.py                       # Entry point
├── requirements.txt             # Dipendenze
├── .gitignore                   # File da ignorare
└── README.md                    # Questo file
```

### Pattern Implementati

#### 🏭 Application Factory
```python
def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    # ...
    return app
```

#### 📦 Repository Pattern
Separazione completa tra logica di business e accesso ai dati:
- `UserRepository`: Gestione utenti
- `SubjectRepository`: Gestione materie
- `StudySessionRepository`: Gestione sessioni con query aggregate complesse

#### 🎨 Blueprints
- **auth**: Gestione autenticazione (registrazione, login, logout)
- **main**: Funzionalità principali (dashboard, CRUD sessioni e materie)

---

## 🗄️ Schema del Database

### Tabelle

#### `users`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| id | Integer (PK) | ID univoco |
| username | String(80) | Nome utente (unique) |
| email | String(120) | Email (unique) |
| password_hash | String(200) | Password hashata |
| created_at | DateTime | Data registrazione |

#### `subjects`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| id | Integer (PK) | ID univoco |
| name | String(100) | Nome materia |
| description | Text | Descrizione opzionale |
| color | String(7) | Colore esadecimale |
| user_id | Integer (FK) | Riferimento a users |
| created_at | DateTime | Data creazione |

#### `study_sessions`
| Campo | Tipo | Descrizione |
|-------|------|-------------|
| id | Integer (PK) | ID univoco |
| topic | String(200) | Argomento studiato |
| duration_minutes | Integer | Durata in minuti |
| notes | Text | Note opzionali |
| date | Date | Data della sessione |
| user_id | Integer (FK) | Riferimento a users |
| subject_id | Integer (FK) | Riferimento a subjects |
| created_at | DateTime | Data creazione record |

### Relazioni
- **User → Subjects**: 1 a N (un utente ha più materie)
- **User → StudySessions**: 1 a N (un utente ha più sessioni)
- **Subject → StudySessions**: 1 a N (una materia ha più sessioni)

---

## 🚀 Installazione e Avvio

### Prerequisiti
- Python 3.8 o superiore
- pip (gestore pacchetti Python)

### Passaggi di Installazione

1. **Clona il repository**
   ```bash
   git clone <url-repository>
   cd Natale-26
   ```

2. **Crea un ambiente virtuale**
   ```bash
   python -m venv .venv
   ```

3. **Attiva l'ambiente virtuale**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

5. **Avvia l'applicazione**
   ```bash
   python run.py
   ```

6. **Apri il browser**
   Naviga su: `http://localhost:5000`

---

## 📊 Query SQL Avanzate (Livello 3)

### Ore Totali per Materia
```python
db.session.query(
    Subject.name,
    Subject.color,
    func.sum(StudySession.duration_minutes).label('total_minutes'),
    func.count(StudySession.id).label('session_count')
).join(StudySession.subject)\
 .filter(StudySession.user_id == user_id)\
 .group_by(Subject.id, Subject.name, Subject.color)\
 .order_by(func.sum(StudySession.duration_minutes).desc())\
 .all()
```

### Trend Mensile
```python
db.session.query(
    extract('month', StudySession.date).label('month'),
    func.sum(StudySession.duration_minutes).label('total_minutes')
).filter(
    StudySession.user_id == user_id,
    extract('year', StudySession.date) == year
).group_by('month')\
 .order_by('month')\
 .all()
```

---

## 🔒 Sicurezza

- **Hashing Password**: Utilizzo di `werkzeug.security` per hash e verifica sicura
- **Protezione Rotte**: Decorator `@login_required` per rotte autenticate
- **Validazione Input**: Controlli server-side su tutti i form
- **Sessioni Sicure**: Cookie HTTP-only con durata limitata
- **SQL Injection Prevention**: Utilizzo di SQLAlchemy ORM

---

## 🎨 Tecnologie Utilizzate

- **Backend**: Flask 3.0.0
- **Database**: SQLite + SQLAlchemy ORM
- **Frontend**: 
  - Bootstrap 5.3
  - Font Awesome 6.4
  - Chart.js 4.4
- **Template Engine**: Jinja2
- **Sicurezza**: Werkzeug Security

---

## 📈 Statistiche del Progetto

- **File Python**: 8
- **Template HTML**: 10
- **Linee di Codice**: ~1500+
- **Funzionalità CRUD**: 2 (Sessioni e Materie)
- **Query Aggregate**: 3
- **Blueprint**: 2
- **Livello Raggiunto**: ⭐⭐⭐ Avanzato

---

## 🎓 Obiettivi Didattici Raggiunti

✅ Struttura a pacchetto con `__init__.py`  
✅ Application Factory Pattern  
✅ Uso di Blueprints per modularità  
✅ Repository Pattern implementato  
✅ Gestione sessioni e autenticazione  
✅ Protezione delle rotte  
✅ Hashing delle password  
✅ Template Jinja2 con ereditarietà  
✅ Relazioni 1-a-N nel database  
✅ Query SQL aggregate complesse (GROUP BY, SUM, AVG)  
✅ Dashboard con statistiche in tempo reale  
✅ Grafici interattivi con Chart.js  

---

## 📝 Possibili Sviluppi Futuri

- 🔔 Sistema di notifiche/reminder per lo studio
- 📅 Calendario interattivo per pianificazione settimanale
- 🎯 Sistema di obiettivi e traguardi da raggiungere
- 📤 Esportazione dati in PDF o Excel
- 📱 Progressive Web App (PWA) per uso mobile
- 👥 Condivisione statistiche con compagni di classe
- 🏆 Sistema di gamification con badge e achievement

---

## 👨‍💻 Autore

**Diego**  
Progetto sviluppato per il corso di Sviluppo Web - Natale 2026

---

## 📄 Licenza

Questo progetto è stato sviluppato a scopo didattico.

---

## 🙏 Ringraziamenti

Grazie al professore per l'opportunità di mettere in pratica le competenze apprese durante il corso!

---

**Buono studio a tutti! 📚✨**
