import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn_params = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}

try:
    # 1. On se connecte
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()

    # 2. On crée la table (SANS SÉCURITÉ pour l'instant)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT,
            password TEXT
        );
    """)

    # 3. On insère 5 utilisateurs
    users = [
        ('alice', '12345'),
        ('bob', 'password'),
        ('charlie', 'qwerty'),
        ('admin', 'admin_root'),
        ('eve', 'hacker123')
    ]
    
    for u in users:
        cur.execute(f"INSERT INTO users (username, password) VALUES ('{u[0]}', '{u[1]}')")

    conn.commit()
    print("Base de données initialisée avec succès !")

except Exception as e:
    print(f"Erreur : {e}")
finally:
    if 'conn' in locals():
        cur.close()
        conn.close()