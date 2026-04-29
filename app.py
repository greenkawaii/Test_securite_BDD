import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv # Import pour charger le .env
import psycopg2

# Charge les variables d'environnement du fichier .env
load_dotenv()

app = Flask(__name__)

# On récupère les identifiants via os.getenv
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

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # LA FAILLE : Injection par concaténation
        query = f"SELECT * FROM users WHERE username = '{username}'"
        print(f"DEBUG SQL: {query}")
        
        cur.execute(query)
        row = cur.fetchone()

        cur.close()
        conn.close()

        if row:
            # Succès : On redirige vers la page dashboard en passant le nom
            return redirect(url_for('dashboard', user=row[1]))
        else:
            return render_template('index.html', error="Utilisateur non trouvé.")

    except Exception as e:
        return render_template('index.html', error=f"Erreur SQL : {e}")

@app.route('/dashboard')
def dashboard():
    # On récupère le nom passé dans l'URL pour l'affichage
    user = request.args.get('user', 'Utilisateur')
    return render_template('dashboard.html', username=user)

if __name__ == '__main__':
    app.run(debug=True, port=5000)