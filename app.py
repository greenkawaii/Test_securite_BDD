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

@app.route('/')
def index():
    return render_template('index.html')

# --- VERSION VULNÉRABLE ---
@app.route('/login_vulnerable', methods=['POST'])
def login_vulnerable():
    username = request.form.get('username')
    password_tape = request.form.get('password')
    
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # 1. LA FAILLE : Concaténation directe (f-string)
        # Si tu tapes : ' OR 1=1 --
        # La requête devient : SELECT * FROM users WHERE username = '' OR 1=1 --'
        query = f"SELECT username, password FROM users WHERE username = '{username}'"
        cur.execute(query)
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user:
            username_bdd = user[0]
            hash_bdd = user[1]

            # 2. LOGIQUE DE VÉRIFICATION
            # On laisse passer si :
            # - C'est une injection (présence de ' ou OR)
            # - OU si le mot de passe est correct via Bcrypt
            is_injection = "'" in username or "OR" in username.upper()
            
            if is_injection:
                # L'injection a "cassé" la barrière du mot de passe
                return redirect(url_for('dashboard', user=username_bdd))
            
            # Sinon, on vérifie normalement le hash
            if bcrypt.checkpw(password_tape.encode('utf-8'), hash_bdd.encode('utf-8')):
                return redirect(url_for('dashboard', user=username_bdd))
            else:
                return render_template('index.html', error="Mot de passe incorrect.")
        
        return render_template('index.html', error="Utilisateur inconnu.")
        
    except Exception as e:
        # On affiche l'erreur SQL pour aider l'attaquant (caractéristique du mode vulnérable)
        return render_template('index.html', error=f"Erreur SQL : {e}")

# --- VERSION SÉCURISÉE ---
@app.route('/login_secure', methods=['POST'])
def login_secure():
    username = request.form.get('username')
    password_tape = request.form.get('password')
    
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # 1. SÉCURITÉ : Requête préparée (%s)
        # L'injection est impossible car l'entrée est traitée comme du texte pur.
        query = "SELECT username, password FROM users WHERE username = %s"
        cur.execute(query, (username,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user:
            hash_bdd = user[1]
            # 2. VÉRIFICATION STRICTE DU HASH
            if bcrypt.checkpw(password_tape.encode('utf-8'), hash_bdd.encode('utf-8')):
                return redirect(url_for('dashboard', user=user[0]))
            else:
                return render_template('index.html', error_secure="Mot de passe incorrect.")
        
        return render_template('index.html', error_secure="Utilisateur inconnu.")
        
    except Exception as e:
        # On ne montre pas l'erreur à l'utilisateur par sécurité
        return render_template('index.html', error_secure="Une erreur système est survenue.")

@app.route('/dashboard')
def dashboard():
    user = request.args.get('user', 'Invité')
    return render_template('dashboard.html', username=user)

if __name__ == '__main__':
    app.run(debug=True)