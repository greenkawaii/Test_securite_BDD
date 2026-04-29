-- 1. Nettoyage (pour pouvoir relancer le script sans erreur)
DROP TABLE IF EXISTS comptes CASCADE;
DROP TABLE IF EXISTS clients CASCADE;

-- 2. Création des tables bancaires
CREATE TABLE clients (
    id_client SERIAL PRIMARY KEY,
    nom TEXT NOT NULL,
    email TEXT UNIQUE,
    telephone TEXT
);

CREATE TABLE comptes (
    id_compte SERIAL PRIMARY KEY,
    id_client INT REFERENCES clients(id_client),
    solde DECIMAL(15, 2) DEFAULT 0.00,
    type_compte TEXT
);

-- 3. Insertion de données de test
INSERT INTO clients (nom, email, telephone) VALUES ('Jean Dupont', 'jean@email.com', '0102030405');
INSERT INTO comptes (id_client, solde, type_compte) VALUES (1, 1500.00, 'Courant');

-- 4. Création des Rôles (RBAC)
-- On vérifie si les rôles existent avant de les créer (syntaxe Postgres)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'role_directeur') THEN
        CREATE ROLE role_directeur;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'role_conseiller') THEN
        CREATE ROLE role_conseiller;
    END IF;
END $$;

-- 5. Attribution des privilèges (Principe du moindre privilège)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO role_directeur;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO role_conseiller;

-- 6. Création des utilisateurs et liaison aux rôles
-- Note: On utilise 'app_user' pour ton API
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'app_user') THEN
        CREATE USER app_user WITH PASSWORD 'app_pwd_456';
    END IF;
END $$;

GRANT role_conseiller TO app_user;