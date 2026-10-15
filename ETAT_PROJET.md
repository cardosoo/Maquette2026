# État du Projet - Maquettes API

*Date: 15 octobre 2026*
*Version: 1.1.0*

---

## Sommaire

1. [Description du Projet](#description-du-projet)
2. [Architecture](#architecture)
3. [Fonctionnalités Implémentées](#fonctionnalités-implémentées)
4. [Structure des Bases de Données](#structure-des-bases-de-données)
5. [Endpoints API](#endpoints-api)
6. [Tests](#tests)
7. [Corrections Récentes](#corrections-récentes)
8. [Points d'Attention](#points-dattention)
9. [Prochaines Étapes](#prochaines-étapes)
10. [Configuration Requise](#configuration-requise)

---

## Description du Projet

**Maquettes API** est une application FastAPI conçue pour gérer les informations sur la structure des enseignements d'une université. L'API permet de:

- Gérer les **composantes** (facultés, départements)
- Gérer les **étapes** (années d'étude, semestres)
- Gérer les **ECUE** (Unités d'Enseignement) avec leurs besoins spécifiques
- Gérer les **rattachements** entre ECUE et étapes
- Travailler avec des bases de données **PostgreSQL annualisées** (maquettes2024, maquettes2025, maquettes2026)
- Consulter la structure des enseignements via une **interface web en HTML pur** (`/ui`) : parcours composante → étape → ECUE, recherche par code ou nom

L'API offre à la fois des opérations de consultation (GET) et de modification (POST, PUT, DELETE) des données.

---

## Architecture

### Structure du Projet

```
Maquette2026/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py      # Configuration SQLAlchemy + bases annualisées
│   │   ├── dependencies.py  # Middleware et dépendances FastAPI
│   │   └── settings.py      # Configuration via variables d'environnement
│   ├── models/
│   │   ├── __init__.py
│   │   └── maquette.py      # Modèles SQLAlchemy
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── maquette.py      # Schémas Pydantic v2
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── composantes.py   # Endpoints /composantes/*
│   │   ├── etapes.py        # Endpoints /etapes/*
│   │   ├── ecues.py         # Endpoints /ecues/*
│   │   ├── rattachements.py # Endpoints /rattachements/*
│   │   └── frontend.py      # Interface web /ui (HTML pur)
│   ├── services/
│   │   ├── __init__.py
│   │   └── maquette_service.py # Logique métier
│   ├── ui/
│   │   ├── __init__.py
│   │   └── pages.py         # Rendu HTML des pages /ui
│   └── utils/
│       ├── __init__.py
│       └── database_init.py # Initialisation des tables
├── tests/
│   ├── __init__.py
│   ├── test_basic.py        # Tests API (13 tests)
│   └── test_frontend.py     # Tests de l'interface web (21 tests)
├── migrations/
│   └── 2026-10-15_ajout_code_composante.sql # Migration : code des composantes
├── main.py                  # Application FastAPI principale
├── requirements.txt         # Dépendances Python
├── .env.example            # Template des variables d'environnement
├── .env                    # Variables d'environnement (non commité)
├── start.sh                # Script de démarrage
├── README.md               # Documentation principale
├── ETAT_PROJET.md          # Ce document
└── static/                 # Fichiers statiques (favicon, etc.)
```

### Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | FastAPI | 0.109.0 |
| ASGI Server | Uvicorn | 0.27.0 |
| ORM | SQLAlchemy | 2.0.25 |
| Validation | Pydantic | 2.5.3 |
| Base de données | PostgreSQL | 15+ |
| Tests | Pytest | 8.0.0 |
| Configuration | python-dotenv | 1.0.0 |

---

## Fonctionnalités Implémentées

### ✅ Complètement Fonctionnel

- **Gestion des composantes** : CRUD complet, identifiées par un code unique (code OSE de la structure)
- **Gestion des étapes** : CRUD complet avec filtres
- **Gestion des ECUE** : CRUD complet avec champ JSON `besoins`
- **Gestion des rattachements** : Création et suppression de rattachements ECUE-étape
- **Bases annualisées** : Sélection dynamique de la base de données via en-tête HTTP
- **Sécurité** : Vérification du payload via en-tête `X-Payload`
- **CORS** : Configuration complète des CORS
- **Documentation** : Swagger UI et ReDoc intégrés
- **Health Check** : Endpoint `/health` pour vérifier l'état de l'API
- **Interface web** : parcours HTML pur des enseignements à `/ui` (composante → étape → ECUE, recherche par code ou nom)

### 🔄 Fonctionnalités Partiellement Implémentées

- **Rattachements** : Consultation des rattachements d'une ECUE ou d'une étape
- **Années disponibles** : Liste des années disponibles via `/years`

### ⚠️ À Implémenter

- **Recherche avancée** : Filtres complexes sur les ECUE et étapes
- **Pagination** : Support de la pagination pour les listes
- **Audit/Logs** : Historique des modifications
- **Import/Export** : Fonctions de masse pour les données

---

## Structure des Bases de Données

### Schéma PostgreSQL

```sql
-- Table des composantes (facultés, départements)
-- Le code est le code de la structure dans le système OSE (unique)
CREATE TABLE composante (
    id SERIAL NOT NULL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    code VARCHAR(128) NOT NULL UNIQUE
);

-- Table des étapes (années d'étude, semestres)
CREATE TABLE etape (
    id SERIAL NOT NULL PRIMARY KEY,
    nom VARCHAR(128) NOT NULL,
    code VARCHAR(128) NOT NULL,
    type VARCHAR(128) NOT NULL,
    niveau VARCHAR(128) NOT NULL,
    domaine VARCHAR(128) NOT NULL,
    effectif INTEGER NOT NULL,
    composante_id INTEGER NOT NULL,
    FOREIGN KEY (composante_id) REFERENCES composante (id) ON DELETE CASCADE
);

-- Table des ECUE (Unités d'Enseignement)
CREATE TABLE ecue (
    id SERIAL NOT NULL PRIMARY KEY,
    nom VARCHAR(128) NOT NULL,
    code VARCHAR(128) NOT NULL,
    periode VARCHAR(128) NOT NULL,
    etape_id INTEGER NOT NULL,
    effectif INTEGER NOT NULL,
    besoins JSON NOT NULL,
    FOREIGN KEY (etape_id) REFERENCES etape (id) ON DELETE CASCADE
);

-- Table de rattachement ECUE-Étape (relation many-to-many)
CREATE TABLE ecue_etape (
    id SERIAL NOT NULL PRIMARY KEY,
    ecue_id INTEGER NOT NULL,
    etape_id INTEGER NOT NULL,
    effectif INTEGER NOT NULL,
    FOREIGN KEY (ecue_id) REFERENCES ecue (id) ON DELETE CASCADE,
    FOREIGN KEY (etape_id) REFERENCES etape (id) ON DELETE CASCADE
);

-- Index pour optimiser les requêtes
CREATE INDEX ix_composante_code ON composante (code);
CREATE INDEX etape_i_4db226 ON etape (code);
CREATE INDEX ecue_i_4db226 ON ecue (code);
```

### Bases Annualisées

L'application travaille avec plusieurs bases de données PostgreSQL, une par année:
- `maquettes2024`
- `maquettes2025`
- `maquettes2026` (par défaut)

La sélection de la base s'effectue via l'en-tête HTTP `X-Maquette-Year`.

### Codes des composantes

La colonne `code` de `composante` contient le code de la structure dans le
système OSE (exemples : `GHES`, `IPGP-DFED`, `PHARMA`, `EIDD`). Elle a été ajoutée
par la migration `migrations/2026-10-15_ajout_code_composante.sql` (15 octobre 2026),
appliquée sur `maquettes2024`, `maquettes2025` et `maquettes2026`.

---

## Endpoints API

### Endpoints Généraux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Page d'accueil avec liens vers la documentation |
| GET | `/health` | Vérifie l'état de santé de l'API |
| GET | `/years` | Liste les années disponibles |
| GET | `/docs` | Documentation Swagger UI |
| GET | `/redoc` | Documentation ReDoc |

### Endpoints Composantes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/composantes/` | Liste toutes les composantes (filtre optionnel `?code=`) |
| GET | `/composantes/{id}` | Récupère une composante par ID |
| GET | `/composantes/code/{code}` | Récupère une composante par son code |
| POST | `/composantes/` | Crée une nouvelle composante (nom et code unique requis) |
| PUT | `/composantes/{id}` | Met à jour une composante |
| DELETE | `/composantes/{id}` | Supprime une composante |

### Endpoints Étapes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/etapes/` | Liste toutes les étapes (avec filtres optionnels) |
| GET | `/etapes/{id}` | Récupère une étape par ID |
| GET | `/etapes/composante/{composante_id}` | Récupère les étapes d'une composante |
| POST | `/etapes/` | Crée une nouvelle étape |
| PUT | `/etapes/{id}` | Met à jour une étape |
| DELETE | `/etapes/{id}` | Supprime une étape |

### Endpoints ECUE

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/ecues/` | Liste toutes les ECUE (avec filtres optionnels) |
| GET | `/ecues/{id}` | Récupère une ECUE par ID |
| GET | `/ecues/etape/{etape_id}` | Récupère les ECUE d'une étape |
| GET | `/ecues/{id}/rattachements` | Récupère tous les rattachements d'une ECUE |
| GET | `/ecues/{id}/etapes` | Récupère toutes les étapes d'une ECUE |
| POST | `/ecues/` | Crée une nouvelle ECUE |
| PUT | `/ecues/{id}` | Met à jour une ECUE |
| DELETE | `/ecues/{id}` | Supprime une ECUE |

### Endpoints Rattachements

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/rattachements/` | Liste tous les rattachements |
| GET | `/rattachements/ecue/{ecue_id}` | Récupère les rattachements d'une ECUE |
| GET | `/rattachements/etape/{etape_id}` | Récupère les rattachements d'une étape |
| POST | `/rattachements/` | Crée un nouveau rattachement |
| DELETE | `/rattachements/{id}` | Supprime un rattachement |

### Interface web (HTML)

Interface utilisateur en HTML pur (sans framework JavaScript) pour parcourir la
structure des enseignements : composante → étape → ECUE. Les id de la base n'y
sont jamais affichés ; les éléments sont identifiés par leur code (unique).
Accessible sans en-tête `X-Payload` (consultation en lecture seule).

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/ui` | Accueil : liste des composantes |
| GET | `/ui/composante/{code}` | Détail d'une composante et liste de ses étapes |
| GET | `/ui/etape/{code}` | Détail d'une étape, sa composante et ses ECUE |
| GET | `/ui/ecue/{code}` | Détail d'une ECUE et ses étapes de rattachement |
| GET | `/ui/recherche?q=...` | Recherche par code ou par nom (composantes, étapes, ECUE) |

L'année de la maquette se choisit via le paramètre `?year=` (2024, 2025, 2026)
ou l'en-tête `X-Maquette-Year`.

---

## Tests

### État des Tests

- **Nombre total de tests** : 34
- **Tests passant** : 34 ✅
- **Tests échouant** : 0 ❌
- **Warnings** : 0 ⚠️

### Couverture des Tests

Les tests utilisent une base **SQLite** (`test.db`) à la place des bases PostgreSQL
annualisées, via les mécanismes d'override des dépendances FastAPI. Les deux
modules de test recréent le schéma à chaque exécution (`drop_all` + `create_all`).

Les tests couvrent actuellement :

#### Tests des Composantes (6 tests)
- ✅ Création d'une composante
- ✅ Récupération de toutes les composantes
- ✅ Récupération d'une composante par ID
- ✅ Récupération d'une composante par code
- ✅ Rejet d'un code en double à la création
- ✅ Code requis à la création

#### Tests des Étapes (2 tests)
- ✅ Création d'une étape
- ✅ Récupération des étapes par composante

#### Tests des ECUE (2 tests)
- ✅ Création d'une ECUE
- ✅ Récupération des ECUE par étape

#### Tests Généraux (3 tests)
- ✅ Endpoint racine `/`
- ✅ Endpoint health `/health`
- ✅ Endpoint years `/years`

#### Tests de l'interface web (21 tests)
- ✅ Accueil `/ui` : liste des composantes, formulaire de recherche, accès public
- ✅ Parcours composante → étape → ECUE et liens de retour (fil d'Ariane)
- ✅ Recherche par code et par nom
- ✅ Pages 404 (composante, étape, ECUE inconnues)
- ✅ Absence des id de la base dans les pages et les liens
- ✅ L'API reste protégée par l'en-tête `X-Payload`

### Exécution des Tests

```bash
# Dans l'environnement virtuel
source venv/bin/activate

# Exécuter tous les tests
python -m pytest tests/ -v

# Exécuter un test spécifique
python -m pytest tests/test_basic.py::TestComposantes::test_create_composante -v

# Avec couverture de code (si pytest-cov est installé)
python -m pytest tests/ --cov=app --cov-report=html
```

---

## Corrections Récentes

### Interface web et code des composantes (15 octobre 2026)

Ajouts de la branche `frontend` :

1. **Interface web `/ui`** : parcours HTML pur (sans framework JavaScript) de la
   structure des enseignements — composante → étape → ECUE — avec fil d'Ariane,
   liens de retour, formulaire de recherche par code ou par nom, et sélection de
   l'année via `?year=`. Les id de la base n'y sont jamais affichés : les éléments
   sont identifiés par leur code (unique). L'interface est publique (lecture seule)
   dans le middleware `X-Payload`.
   - `app/ui/pages.py` : rendu HTML des pages (échappement systématique, CSS inline)
   - `app/routers/frontend.py` : routes `/ui/*`

2. **Code des composantes** : colonne `code` (unique, non null) ajoutée sur
   `composante`, peuplée avec les codes des structures OSE. Le code est requis à la
   création (unicité vérifiée). Les routes `/composantes/code/{code}` et le filtre
   `?code=` de `GET /composantes/`, qui existaient mais ne fonctionnaient pas, sont
   désormais opérationnelles.
   - Migration : `migrations/2026-10-15_ajout_code_composante.sql`, appliquée sur
     `maquettes2024`, `maquettes2025` et `maquettes2026` (sauvegardes `pg_dump`
     conservées dans `/home/olivier/backup/Maquette2026_pre-migration/`)

3. **Tests** : `tests/test_frontend.py` (21 tests) ajouté ; `tests/test_basic.py`
   mis à jour (code requis, lecture par code, doublon rejeté). Les deux modules
   recréent le schéma SQLite à chaque exécution (`drop_all` + `create_all`).

### Résolution des Warnings (12 octobre 2026)

Deux warnings de dépréciation ont été corrigés :

#### 1. Warning SQLAlchemy 2.0

**Fichier** : `app/config/database.py`

**Problème** :
```python
from sqlalchemy.ext.declarative import declarative_base
```

**Solution** :
```python
from sqlalchemy.orm import declarative_base
```

**Explication** : Depuis SQLAlchemy 2.0, `declarative_base()` a été déplacée dans `sqlalchemy.orm` pour une meilleure organisation du code.

#### 2. Warning Pydantic v2.0

**Fichier** : `app/config/settings.py`

**Problème** :
```python
class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"
```

**Solution** :
```python
model_config = ConfigDict(
    env_file=".env",
    env_file_encoding="utf-8"
)
```

**Explication** : Pydantic v2.0 a introduit `ConfigDict` pour remplacer la classe `Config` dépréciée. Cela permet une meilleure intégration avec les typing et offre plus de flexibilité.

---

## Points d'Attention

### ⚠️ Configuration Requise

1. **Bases de données PostgreSQL** : Les bases annualisées (maquettes2024, maquettes2025, maquettes2026) doivent être créées manuellement avant le premier lancement.

2. **Variables d'environnement** : Le fichier `.env` doit contenir les informations de connexion à la base de données et le payload autorisé.

3. **Payload** : L'API vérifie l'en-tête `X-Payload` pour autoriser les requêtes. Les payloads autorisés sont configurés dans le fichier `.env` sous la forme d'un tableau JSON. L'interface web `/ui` est exclue de cette vérification (consultation en lecture seule).

4. **Migration du code des composantes** : la colonne `code` de `composante` doit exister dans les bases annualisées. Pour une base existante, appliquer `migrations/2026-10-15_ajout_code_composante.sql` (déjà fait sur maquettes2024/2025/2026). Les bases `maquettes2022` et `maquettes2023` ne sont pas servies par l'application et n'ont pas été migrées.

### ⚠️ Problèmes Connus

- Aucun problème connu à ce jour

### ⚠️ Limitations

- **Pas de pagination** : Les endpoints de liste ne supportent pas encore la pagination
- **Pas de recherche avancée** : Les filtres sont basiques (par ID principalement)
- **Pas d'historique** : Les modifications ne sont pas traçables
- **Pas de tests d'intégration** : Seuls des tests unitaires sont implémentés

---

## Prochaines Étapes

### Priorité Élevée

1. **Pagination** : Implémenter la pagination pour les endpoints de liste
2. **Tests d'intégration** : Ajouter des tests d'intégration pour valider les interactions entre composants
3. **Documentation API** : Compléter la documentation des schémas et exemples dans Swagger

### Priorité Moyenne

4. **Recherche avancée** : Ajouter des filtres complexes (par nom, code, etc.)
5. **Export/Import** : Créer des endpoints pour exporter/importer des données en masse
6. **Audit** : Ajouter un système de logging des modifications
7. **Sécurité** : Implémenter un système d'authentification plus robuste

### Priorité Basse

8. **Cache** : Ajouter un cache pour les requêtes fréquentes
9. **Rate Limiting** : Implémenter une limitation de débit
10. **Metrics** : Ajouter des métriques de performance

---

## Configuration Requise

### Prérequis

- Python 3.10+
- PostgreSQL 15+
- pip

### Variables d'Environnement

Créer un fichier `.env` à partir du template `.env.example` :

```bash
cp .env.example .env
```

Variables principales :

```ini
# Configuration PostgreSQL
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

# Configuration de l'application
APP_NAME=Maquettes API
APP_VERSION=1.0.0
APP_PORT=8000
DEBUG=False
UVICORN_RELOAD=False

# Payloads autorisés (tableau JSON)
PAYLOAD='["e7b8a803-9a07-40ce-8618-489c31eca10e", "ee9202ff-3bb5-4940-b139-b609ff94033f"]'

# Années disponibles
AVAILABLE_YEARS=[2024, 2025, 2026]
DEFAULT_YEAR=2026
```

### Installation

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Démarrage

```bash
# Développement (avec reload automatique)
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000

# Avec le script de démarrage
./start.sh
```

L'API sera accessible à : `http://localhost:8000` (port par défaut d'uvicorn et de
`./start.sh` ; `python main.py` utilise `APP_PORT` du fichier `.env`, soit 8300).

L'interface web de parcours des enseignements est accessible à :
`http://localhost:8000/ui` (ou `http://localhost:8300/ui` selon le port choisi).

---

## Exemples de Requêtes

### Interface web (navigateur)

Ouvrir dans un navigateur (aucun en-tête requis) :

```
http://localhost:8300/ui
```

(ou `http://localhost:8000/ui` selon le port de lancement — voir Démarrage)

### Créer une composante

```bash
curl -X POST "http://localhost:8000/composantes/" \
  -H "Content-Type: application/json" \
  -H "X-Maquette-Year: 2025" \
  -H "X-Payload: e7b8a803-9a07-40ce-8618-489c31eca10e" \
  -d '{"nom": "Faculté des Sciences", "code": "SCI"}'
```

### Récupérer une composante par son code

```bash
curl -X GET "http://localhost:8000/composantes/code/GHES" \
  -H "X-Maquette-Year: 2026" \
  -H "X-Payload: e7b8a803-9a07-40ce-8618-489c31eca10e"
```

### Créer une étape

```bash
curl -X POST "http://localhost:8000/etapes/" \
  -H "Content-Type: application/json" \
  -H "X-Maquette-Year: 2025" \
  -H "X-Payload: e7b8a803-9a07-40ce-8618-489c31eca10e" \
  -d '{
    "nom": "Licence 1 Informatique",
    "code": "L1INFO",
    "type": "L1",
    "niveau": "Licence",
    "domaine": "Sciences",
    "effectif": 100,
    "composante_id": 1
  }'
```

### Créer une ECUE avec besoins JSON

```bash
curl -X POST "http://localhost:8000/ecues/" \
  -H "Content-Type: application/json" \
  -H "X-Maquette-Year: 2025" \
  -H "X-Payload: e7b8a803-9a07-40ce-8618-489c31eca10e" \
  -d '{
    "nom": "Programmation 1",
    "code": "PROG1",
    "periode": "S1",
    "effectif": 100,
    "etape_id": 1,
    "besoins": {
      "salles": ["A101", "A102"],
      "equipements": ["projecteur", "tableau"],
      "heures": 40,
      "enseignants": ["Dupont", "Martin"]
    }
  }'
```

### Créer un rattachement ECUE-Étape

```bash
curl -X POST "http://localhost:8000/rattachements/" \
  -H "Content-Type: application/json" \
  -H "X-Maquette-Year: 2025" \
  -H "X-Payload: e7b8a803-9a07-40ce-8618-489c31eca10e" \
  -d '{
    "ecue_id": 1,
    "etape_id": 2,
    "effectif": 50
  }'
```

### Récupérer les rattachements d'une ECUE

```bash
curl -X GET "http://localhost:8000/ecues/1/rattachements" \
  -H "X-Maquette-Year: 2025" \
  -H "X-Payload: e7b8a803-9a07-40ce-8618-489c31eca10e"
```

### Récupérer toutes les étapes d'une ECUE

```bash
curl -X GET "http://localhost:8000/ecues/1/etapes" \
  -H "X-Maquette-Year: 2025" \
  -H "X-Payload: e7b8a803-9a07-40ce-8618-489c31eca10e"
```

---

## Historique des Versions

| Version | Date | Auteur | Changements |
|---------|------|--------|-------------|
| 1.0.0 | 11-12 oct. 2026 | - | Création initiale du projet |
| 1.0.0 | 12 oct. 2026 | - | Correction des warnings SQLAlchemy et Pydantic |
| 1.1.0 | 15 oct. 2026 | - | Interface web HTML (`/ui`) et code unique des composantes (codes OSE, migration BDD) |

---

## Contacts

Pour toute question ou problème concernant ce projet, contacter l'équipe de développement.

---

*Document généré le 15 octobre 2026*
