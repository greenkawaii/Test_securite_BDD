import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from flask_bcrypt import Bcrypt # Pour le hachage sécurisé
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
bcrypt = Bcrypt(app)

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

# --- NOUVELLE ROUTE : INSCRIPTION SECURISEE ---
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    # HACHAGE DU MOT DE PASSE (Recommandation PDF)
    # On ne stocke jamais le mot de passe en clair !
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        # Utilisation de requête préparée (%s) pour éviter l'injection à l'inscription
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
        
        conn.commit()
        cur.close()
        conn.close()
        return render_template('index.html', message="Compte créé avec succès ! Connectez-vous.")
    except Exception as e:
        return render_template('index.html', error=f"Erreur d'inscription : {e}")

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    # Pour garder la faille pédagogique, on continue d'injecter sur le username
    
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cur.execute(query)
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            # Succès (Injection réussie ou login ok)
            return redirect(url_for('dashboard', user=row[1]))
        else:
            return render_template('index.html', error="Utilisateur non trouvé.")
    except Exception as e:
        return render_template('index.html', error=f"Erreur SQL : {e}")

@app.route('/dashboard')
def dashboard():
    user_name = request.args.get('user', 'Utilisateur')
    return render_template('dashboard.html', username=user_name)

if __name__ == '__main__':
    app.run(debug=True)