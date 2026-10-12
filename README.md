# Maquettes API

API FastAPI pour la gestion des maquettes d'enseignement universitaire.

## 📋 Description

Maquettes API permet de gérer et consulter les informations sur la structure des enseignements d'une université. L'application offre un accès complet (CRUD) aux composantes, étapes, ECUE et leurs rattachements, avec support des bases de données PostgreSQL annualisées.

## ✨ Fonctionnalités

- **Gestion des composantes** (facultés, départements)
- **Gestion des étapes** (années d'étude, semestres)
- **Gestion des ECUE** (Unités d'Enseignement) avec champ JSON `besoins` pour les informations spécifiques
- **Gestion des rattachements** entre ECUE et étapes
- **Support des bases de données annualisées** (maquettes2024, maquettes2025, maquettes2026)
- **Sélection dynamique de l'année** via en-tête HTTP `X-Maquette-Year`
- **Documentation interactive** (Swagger UI et ReDoc)
- **Vérification de payload** via en-tête `X-Payload`

## 🏗️ Structure du Projet

```
Maquette2026/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py         # Configuration SQLAlchemy + bases annualisées
│   │   ├── dependencies.py     # Middleware et dépendances FastAPI
│   │   └── settings.py         # Configuration via variables d'environnement
│   ├── models/
│   │   ├── __init__.py
│   │   └── maquette.py         # Modèles SQLAlchemy
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── maquette.py         # Schémas Pydantic v2
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── composantes.py      # Endpoints /composantes/*
│   │   ├── etapes.py           # Endpoints /etapes/*
│   │   ├── ecues.py            # Endpoints /ecues/*
│   │   └── rattachements.py    # Endpoints /rattachements/*
│   ├── services/
│   │   ├── __init__.py
│   │   └── maquette_service.py # Logique métier
│   └── utils/
│       ├── __init__.py
│       └── database_init.py    # Initialisation des tables
├── tests/
│   ├── __init__.py
│   └── test_basic.py           # Tests unitaires (10 tests)
├── main.py                    # Application FastAPI principale
├── start.sh                   # Script de démarrage
├── requirements.txt            # Dépendances Python
├── .env.example               # Template des variables d'environnement
├── .env                       # Variables d'environnement (non commité)
├── README.md                  # Documentation principale
└── static/                    # Fichiers statiques (favicon, etc.)
```

## 🛠️ Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Framework | FastAPI | 0.109.0 |
| ASGI Server | Uvicorn | 0.27.0 |
| ORM | SQLAlchemy | 2.0.25 |
| Validation | Pydantic | 2.5.3 |
| Base de données | PostgreSQL | 15+ |
| Tests | Pytest | 8.0.0 |
| Configuration | python-dotenv | 1.0.0 |

## 📥 Installation

### Prérequis

- Python 3.10 ou supérieur
- PostgreSQL 15 ou supérieur
- pip

### Étapes d'Installation

1. **Cloner le dépôt** :
   ```bash
   git clone <url-du-depot>
   cd Maquette2026
   ```

2. **Créer un environnement virtuel** :
   ```bash
   python -m venv venv
   ```

3. **Activer l'environnement** :
   ```bash
   # Sur Linux/Mac
   source venv/bin/activate
   
   # Sur Windows
   venv\Scripts\activate
   ```

4. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurer les variables d'environnement** :
   ```bash
   cp .env.example .env
   # Modifier .env avec vos informations de base de données et payload
   ```

6. **Créer les bases de données PostgreSQL annualisées** :
   ```sql
   CREATE DATABASE maquettes2024;
   CREATE DATABASE maquettes2025;
   CREATE DATABASE maquettes2026;
   ```
   Puis créer les tables dans chaque base (voir [Schéma de la base de données](#-schéma-de-la-base-de-données))

## ⚙️ Configuration

### Variables d'Environnement

Le fichier `.env` doit contenir les configurations suivantes :

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

# CORS
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]
```

## 🚀 Exécution

### Développement

```bash
uvicorn main:app --reload --port 8000
```

L'API sera accessible à : `http://localhost:8000`

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Avec le script de démarrage

```bash
./start.sh
```

## 📡 Utilisation

### Sélection de l'année

L'API permet de travailler avec différentes bases de données annualisées. Pour spécifier l'année, utilisez l'en-tête HTTP :

```
X-Maquette-Year: 2025
```

Si aucune année n'est spécifiée, l'API utilisera **2026** par défaut.

**⚠️ Important** : Vous devez également fournir un payload valide via l'en-tête `X-Payload` pour toutes les requêtes (sauf `/`, `/health` et `/years`).

### Endpoints API

#### 📁 Général

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Page d'accueil avec liens vers la documentation |
| GET | `/health` | Vérifie l'état de santé de l'API |
| GET | `/years` | Liste les années disponibles |
| GET | `/docs` | Documentation Swagger UI |
| GET | `/redoc` | Documentation ReDoc |

#### 🏢 Composantes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/composantes/` | Liste toutes les composantes |
| GET | `/composantes/{id}` | Récupère une composante par ID |
| POST | `/composantes/` | Crée une nouvelle composante |
| PUT | `/composantes/{id}` | Met à jour une composante |
| DELETE | `/composantes/{id}` | Supprime une composante |

#### 📚 Étapes

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/etapes/` | Liste toutes les étapes |
| GET | `/etapes/{id}` | Récupère une étape par ID |
| GET | `/etapes/composante/{composante_id}` | Récupère les étapes d'une composante |
| POST | `/etapes/` | Crée une nouvelle étape |
| PUT | `/etapes/{id}` | Met à jour une étape |
| DELETE | `/etapes/{id}` | Supprime une étape |

#### 📖 ECUE

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/ecues/` | Liste toutes les ECUE |
| GET | `/ecues/{id}` | Récupère une ECUE par ID |
| GET | `/ecues/etape/{etape_id}` | Récupère les ECUE d'une étape |
| GET | `/ecues/{id}/rattachements` | Récupère tous les rattachements d'une ECUE |
| GET | `/ecues/{id}/etapes` | Récupère toutes les étapes d'une ECUE |
| POST | `/ecues/` | Crée une nouvelle ECUE |
| PUT | `/ecues/{id}` | Met à jour une ECUE |
| DELETE | `/ecues/{id}` | Supprime une ECUE |

#### 🔗 Rattachements

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/rattachements/` | Liste tous les rattachements |
| GET | `/rattachements/ecue/{ecue_id}` | Récupère les rattachements d'une ECUE |
| GET | `/rattachements/etape/{etape_id}` | Récupère les rattachements d'une étape |
| POST | `/rattachements/` | Crée un nouveau rattachement |
| DELETE | `/rattachements/{id}` | Supprime un rattachement |

## 🗃️ Schéma de la Base de Données

```sql
-- Table des composantes (facultés, départements)
CREATE TABLE composante (
    id SERIAL NOT NULL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL
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
CREATE INDEX etape_i_4db226 ON etape (code);
CREATE INDEX ecue_i_4db226 ON ecue (code);
```

## 🧪 Tests

### État des Tests

- **Nombre total de tests** : 10
- **Tests passant** : 10 ✅
- **Tests échouant** : 0 ❌
- **Warnings** : 0 ⚠️

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

### Couverture des Tests

Les tests couvrent actuellement :
- Création et consultation des composantes
- Création et consultation des étapes
- Création et consultation des ECUE
- Endpoints généraux (racine, health, years)

## 📝 Exemples de Requêtes

### Créer une composante

```bash
curl -X POST "http://localhost:8000/composantes/" \
  -H "Content-Type: application/json" \
  -H "X-Maquette-Year: 2025" \
  -H "X-Payload: e7b8a803-9a07-40ce-8618-489c31eca10e" \
  -d '{"nom": "Faculté des Sciences"}'
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

## 📊 État du Projet

Pour un point d'étape complet, voir le fichier **[ETAT_PROJET.md](ETAT_PROJET.md)**.

### Résumé

- ✅ Toutes les fonctionnalités de base implémentées
- ✅ Tous les tests passent (10/10)
- ✅ Aucun warning dans les tests
- ✅ Documentation complète
- ⚠️ Pas de pagination (à implémenter)
- ⚠️ Pas de recherche avancée (à implémenter)
- ⚠️ Pas de tests d'intégration (à implémenter)

## 🤝 Contribution

1. Forker le projet
2. Créer une branche de fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalité`)
3. Committer vos changements (`git commit -am 'Ajout de la nouvelle fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/nouvelle-fonctionnalité`)
5. Ouvrir une Pull Request

## 📄 Documentation Complémentaire

- **[ETAT_PROJET.md](ETAT_PROJET.md)** : Point d'étape complet du projet
- **Documentation Swagger** : Disponible à `/docs` lors de l'exécution de l'API
- **Documentation ReDoc** : Disponible à `/redoc` lors de l'exécution de l'API

## 📜 Licence

Ce projet est sous licence MIT.
