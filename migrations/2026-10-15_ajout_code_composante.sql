-- Migration : ajout du code (unique) sur la table composante
-- Date : 2026-10-15
-- Contexte : les composantes sont identifiées par leur code, comme les étapes
-- et les ECUE. Les codes sont les codes des structures dans le système OSE
-- (source : export OSE structures.csv, confirmé par les exports d'enseignements
-- tagués par structure).
--
-- À exécuter une fois par base annualisée : maquettes2024, maquettes2025, maquettes2026
--     psql -d maquettes2026 -f migrations/2026-10-15_ajout_code_composante.sql -v ON_ERROR_STOP=1
--
-- Réversible : ALTER TABLE composante DROP COLUMN code;
-- Sauvegarde préalable recommandée : pg_dump <base> > backup.sql

BEGIN;

ALTER TABLE composante ADD COLUMN code VARCHAR(128);

-- Codes OSE des structures
UPDATE composante SET code = 'GHES'       WHERE nom = 'UFR GHES';
UPDATE composante SET code = 'IPGP-DFED'  WHERE nom = 'IPGP-DFED';
UPDATE composante SET code = 'FAC SANTE'  WHERE nom = 'Faculté de Santé';
UPDATE composante SET code = 'PHARMA'     WHERE nom = 'UFR de Pharmacie';
UPDATE composante SET code = 'MÉDECINE'   WHERE nom = 'UFR de Médecine';
UPDATE composante SET code = 'MATHS INFO' WHERE nom = 'UFR Maths-Info';
UPDATE composante SET code = 'SFB'        WHERE nom = 'UFR Sciences Fonda. et Biomédicales';
UPDATE composante SET code = 'SDV'        WHERE nom = 'UFR des Sciences du Vivant';
UPDATE composante SET code = 'MATHS'      WHERE nom = 'UFR de Mathématiques';
UPDATE composante SET code = 'CHIMIE'     WHERE nom = 'UFR de Chimie';
UPDATE composante SET code = 'PHYSIQUE'   WHERE nom = 'UFR de Physique';
UPDATE composante SET code = 'INFO'       WHERE nom = 'UFR d''Informatique';
UPDATE composante SET code = 'IUT PAJOL'  WHERE nom = 'IUT Paris Pajol';
UPDATE composante SET code = 'EIDD'       WHERE nom = 'Ecole d''Ingénieur Denis Diderot (EIDD)';
UPDATE composante SET code = 'IHSS'       WHERE nom = 'UFR IHSS';

-- Lignes hors périmètre OSE (placeholders d'import) : le code reprend le nom
UPDATE composante SET code = 'LIB_CMP'    WHERE nom = 'LIB_CMP';
UPDATE composante SET code = 'DE_RIEN'    WHERE nom = 'DE RIEN';

-- Sécurité : aucune composante ne doit rester sans code
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM composante WHERE code IS NULL) THEN
        RAISE EXCEPTION 'Migration interrompue : des composantes sont sans code';
    END IF;
END $$;

ALTER TABLE composante ALTER COLUMN code SET NOT NULL;
ALTER TABLE composante ADD CONSTRAINT composante_code_key UNIQUE (code);
CREATE INDEX ix_composante_code ON composante (code);

COMMIT;
