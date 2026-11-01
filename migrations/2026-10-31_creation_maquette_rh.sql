-- Migration : création de la base unique maquette_rh
-- Date : 2026-10-31
--
-- Remplace les bases annualisées (maquettes2024, maquettes2025, maquettes2026) :
-- toutes les tables portent une colonne `annee` et l'unicité des codes est
-- ramenée au couple (code, annee).
--
-- Création de la base :
--     createdb maquette_rh
-- Puis :
--     psql -d maquette_rh -f migrations/2026-10-31_creation_maquette_rh.sql -v ON_ERROR_STOP=1
-- Enfin, chargement des données :
--     venv/bin/python scripts/migrate_to_maquette_rh.py
--
-- Les bases annualisées d'origine ne sont pas modifiées : elles servent de
-- sauvegarde jusqu'à validation de la bascule.

BEGIN;

-- ==================== STRUCTURE DES ENSEIGNEMENTS ====================

CREATE TABLE IF NOT EXISTS composante (
    id SERIAL PRIMARY KEY,
    annee INTEGER NOT NULL,
    nom VARCHAR(255) NOT NULL,
    code VARCHAR(128) NOT NULL,
    CONSTRAINT uq_composante_code_annee UNIQUE (code, annee)
);
CREATE INDEX IF NOT EXISTS ix_composante_code ON composante (code);
CREATE INDEX IF NOT EXISTS ix_composante_annee ON composante (annee);

CREATE TABLE IF NOT EXISTS etape (
    id SERIAL PRIMARY KEY,
    annee INTEGER NOT NULL,
    nom VARCHAR(128) NOT NULL,
    code VARCHAR(128) NOT NULL,
    type VARCHAR(128) NOT NULL,
    niveau VARCHAR(128) NOT NULL,
    domaine VARCHAR(128) NOT NULL,
    effectif INTEGER NOT NULL DEFAULT 0,
    composante_id INTEGER NOT NULL REFERENCES composante(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_etape_code ON etape (code);
CREATE INDEX IF NOT EXISTS ix_etape_annee ON etape (annee);

CREATE TABLE IF NOT EXISTS ecue (
    id SERIAL PRIMARY KEY,
    annee INTEGER NOT NULL,
    nom VARCHAR(128) NOT NULL,
    code VARCHAR(128) NOT NULL,
    periode VARCHAR(128) NOT NULL,
    effectif INTEGER NOT NULL DEFAULT 0,
    besoins JSON NOT NULL DEFAULT '{}',
    etape_id INTEGER NOT NULL REFERENCES etape(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS ix_ecue_code ON ecue (code);
CREATE INDEX IF NOT EXISTS ix_ecue_annee ON ecue (annee);

CREATE TABLE IF NOT EXISTS ecue_etape (
    id SERIAL PRIMARY KEY,
    annee INTEGER NOT NULL,
    ecue_id INTEGER NOT NULL REFERENCES ecue(id) ON DELETE CASCADE,
    etape_id INTEGER NOT NULL REFERENCES etape(id) ON DELETE CASCADE,
    effectif INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_ecue_etape_annee ON ecue_etape (annee);

-- ==================== RH ====================

CREATE TABLE IF NOT EXISTS msd (
    id SERIAL PRIMARY KEY,
    annee INTEGER NOT NULL,
    code VARCHAR(128) NOT NULL,
    libelle VARCHAR(255) NOT NULL,
    multiplicateur INTEGER NOT NULL DEFAULT -1,
    pas_heures_complementaires BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_msd_code_annee UNIQUE (code, annee)
);
CREATE INDEX IF NOT EXISTS ix_msd_code ON msd (code);
CREATE INDEX IF NOT EXISTS ix_msd_annee ON msd (annee);

CREATE TABLE IF NOT EXISTS fonction_ref (
    id SERIAL PRIMARY KEY,
    annee INTEGER NOT NULL,
    code VARCHAR(128) NOT NULL,
    libelle VARCHAR(255) NOT NULL,
    libelle_court VARCHAR(255),
    domaine_fonctionnel VARCHAR(128),
    structure VARCHAR(255),
    formation_a_preciser BOOLEAN NOT NULL DEFAULT FALSE,
    peut_dans_serv BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_fonction_ref_code_annee UNIQUE (code, annee)
);
CREATE INDEX IF NOT EXISTS ix_fonction_ref_code ON fonction_ref (code);
CREATE INDEX IF NOT EXISTS ix_fonction_ref_annee ON fonction_ref (annee);

COMMIT;
