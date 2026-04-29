import psycopg2

db_config = {
    "host": "localhost",
    "database": "securite_db",
    "user": "admin",
    "password": "password123",
    "port": "5432"
}

def run_sql_file(filename):
    try:
        # 1. Connexion à la base
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # 2. Lecture du fichier SQL
        with open(filename, 'r', encoding='utf-8') as f:
            sql_commands = f.read()

        # 3. Exécution de tout le contenu
        print(f"Exécution du fichier {filename}...")
        cur.execute(sql_commands)
        
        conn.commit()
        print("Configuration de sécurité appliquée avec succès !")

    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    run_sql_file('securite_bdd.sql')