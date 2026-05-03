import os
import psycopg2
import bcrypt
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env)
load_dotenv()

app = Flask(__name__)

# Configuration de la base de données
db_config = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

# --- FONCTION D'AUDIT (TP 2) ---
def log_audit(user_login, action, status):
    """Enregistre chaque tentative d'accès dans la table audit_logs"""
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        query = "INSERT INTO audit_logs (user_login, action, status) VALUES (%s, %s, %s)"
        cur.execute(query, (user_login, action, status))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de l'audit : {e}")

@app.route('/')
def index():
    return render_template('index.html')

# --- SECTION INSCRIPTION (C'est celle-ci qui manquait) ---
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        username = request.form.get('username')
        password_tape = request.form.get('password')

        # Hachage du mot de passe (Sécurité demandée au TP 2)
        hashed_password = bcrypt.hashpw(password_tape.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            conn = psycopg2.connect(**db_config)
            cur = conn.cursor()
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cur.execute(query, (username, hashed_password))
            conn.commit()
            cur.close()
            conn.close()
            
            log_audit(username, 'registration', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            log_audit(username, 'registration', f'failed: {e}')
            return f"Erreur lors de l'inscription : {e}"

    return render_template('inscription.html')

# --- VERSION VULNÉRABLE ---
@app.route('/login_vulnerable', methods=['POST'])
def login_vulnerable():
    username = request.form.get('username')
    password_tape = request.form.get('password')
    
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # LA FAILLE : Concaténation directe
        query = f"SELECT username, password FROM users WHERE username = '{username}'"
        cur.execute(query)
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user:
            username_bdd = user[0]
            hash_bdd = user[1]

            # Détection d'injection pour l'audit et le bypass
            is_injection = "'" in username or "OR" in username.upper()
            
            if is_injection:
                log_audit(username, 'sql_injection', 'bypassed')
                return redirect(url_for('dashboard', user=username_bdd))
            
            # Vérification normale du mot de passe haché
            if bcrypt.checkpw(password_tape.encode('utf-8'), hash_bdd.encode('utf-8')):
                log_audit(username_bdd, 'login_vulnerable', 'success')
                return redirect(url_for('dashboard', user=username_bdd))
            else:
                log_audit(username_bdd, 'login_vulnerable', 'failed_password')
                return render_template('index.html', error="Mot de passe incorrect.")
        
        log_audit(username, 'login_vulnerable', 'user_not_found')
        return render_template('index.html', error="Utilisateur inconnu.")
        
    except Exception as e:
        log_audit(username, 'sql_error_attack', 'failed')
        return render_template('index.html', error=f"Erreur SQL : {e}")

# --- VERSION SÉCURISÉE ---
@app.route('/login_secure', methods=['POST'])
def login_secure():
    username = request.form.get('username')
    password_tape = request.form.get('password')
    
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # SÉCURITÉ : Requête préparée (%s)
        query = "SELECT username, password FROM users WHERE username = %s"
        cur.execute(query, (username,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user:
            hash_bdd = user[1]
            if bcrypt.checkpw(password_tape.encode('utf-8'), hash_bdd.encode('utf-8')):
                log_audit(user[0], 'login_secure', 'success')
                return redirect(url_for('dashboard', user=user[0]))
            else:
                log_audit(user[0], 'login_secure', 'failed_password')
                return render_template('index.html', error_secure="Mot de passe incorrect.")
        
        log_audit(username, 'login_secure', 'user_not_found')
        return render_template('index.html', error_secure="Utilisateur inconnu.")
        
    except Exception as e:
        log_audit(username, 'system_error', 'failed')
        return render_template('index.html', error_secure="Une erreur système est survenue.")

@app.route('/dashboard')
def dashboard():
    user = request.args.get('user', 'Invité')
    return render_template('dashboard.html', username=user)

if __name__ == '__main__':
    app.run(debug=True)