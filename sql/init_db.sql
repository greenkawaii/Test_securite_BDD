-- 1. NETTOYAGE (Optionnel, pour repartir à zéro)
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS comptes;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS users;

-- 2. CRÉATION DES TABLES (TP 1 & 2)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE
);

CREATE TABLE comptes (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id),
    solde DECIMAL(10,2) DEFAULT 0.00,
    type_compte TEXT
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_login TEXT,
    action TEXT,
    status TEXT,
    date_action TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. GESTION DES RÔLES (RBAC - TP 1)
-- On supprime les rôles s'ils existent déjà pour éviter les erreurs au lancement
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'directeur') THEN
        CREATE ROLE directeur;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'conseiller') THEN
        CREATE ROLE conseiller;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'analyste') THEN
        CREATE ROLE analyste;
    END IF;
END $$;

-- Attribution des droits (GRANT)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO directeur;
GRANT SELECT, INSERT, UPDATE ON clients, comptes TO conseiller;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyste;

-- 4. CRÉATION DES UTILISATEURS SYSTÈME (Moindre Privilège - TP 1)
-- Utilisateur pour l'application Flask
DROP USER IF EXISTS app_user;
CREATE USER app_user WITH PASSWORD 'app_password';
GRANT SELECT, INSERT, UPDATE ON users, clients, comptes TO app_user;
GRANT INSERT ON audit_logs TO app_user; -- Droit d'écrire les logs
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user; -- Pour les ID auto-incrémentés

-- Utilisateur pour l'audit uniquement
DROP USER IF EXISTS audit_user;
CREATE USER audit_user WITH PASSWORD 'audit_password';
GRANT SELECT ON audit_logs TO audit_user;

-- 5. INSERTION DE DONNÉES DE TEST
INSERT INTO clients (nom, prenom, email) VALUES ('Dupont', 'Jean', 'jean.dupont@email.com');
INSERT INTO comptes (client_id, solde, type_compte) VALUES (1, 1500.50, 'Courant');