from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Configuration de la connexion
db_config = {
    "host": "localhost",
    "database": "securite_db",
    "user": "admin",
    "password": "password123",
    "port": "5432"
}

@app.route('/user', methods=['GET'])
def get_user():
    # On récupère le paramètre 'name' dans l'URL (ex: /user?name=alice)
    username = request.args.get('name')
    
    if not username:
        return jsonify({"error": "Veuillez fournir un nom"}), 400

    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # --- ZONE DANGEREUSE : CONCATÉNATION DIRECTE ---
        # C'est ici que l'injection SQL se produit. 
        query = f"SELECT * FROM users WHERE username = '{username}'"
        print(f"Exécution de la requête : {query}") # Pour voir ce qui se passe
        
        cur.execute(query)
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            return jsonify({"id": user[0], "username": user[1], "password": user[2]})
        else:
            return jsonify({"message": "Utilisateur non trouvé"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)