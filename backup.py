import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def run_backup():
    # Nom du fichier de sortie avec la date
    filename = f"backup_safebank_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    # Commande docker pour pg_dump
    # On utilise l'utilisateur admin pour avoir les droits de tout copier
    command = [
        "docker", "exec", "securite_db", 
        "pg_dump", "-U", "admin", "securite_db"
    ]
    
    try:
        print(f"Lancement de la sauvegarde vers {filename}...")
        with open(filename, "w") as f:
            subprocess.run(command, stdout=f, check=True)
        print("Sauvegarde terminée avec succès !")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")

if __name__ == "__main__":
    run_backup()