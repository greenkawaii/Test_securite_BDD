import psycopg2

# Les coordonnées pour trouver la base de données
conn_params = {
    "host": "localhost",
    "database": "securite_db",
    "user": "admin",
    "password": "password123",
    "port": "5432"
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