import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Configuration pour l'utilisateur d'audit (Moindre Privilège)
db_config = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": "audit_user",        # Utilisateur limité
    "password": "audit_password",
    "port": os.getenv("DB_PORT")
}

def show_audit():
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        print("--- DERNIÈRES TENTATIVES D'ACCÈS (AUDIT) ---")
        cur.execute("SELECT date_action, user_login, action, status FROM audit_logs ORDER BY date_action DESC LIMIT 10;")
        logs = cur.fetchall()
        
        for log in logs:
            print(f"[{log[0]}] User: {log[1]} | Action: {log[2]} | Status: {log[3]}")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la lecture des logs : {e}")

if __name__ == "__main__":
    show_audit()