# Maquettes API

API FastAPI pour la gestion des maquettes d'enseignement universitaire.

## Fonctionnalités

- Gestion des **composantes** (facultés, départements)
- Gestion des **étapes** (années d'étude, semestres)
- Gestion des **ECUE** (Unités d'Enseignement)
- Gestion des **rattachements** entre ECUE et étapes
- Support des bases de données **annualisées** (maquettes2024, maquettes2025, maquettes2026)
- Champ **besoins** JSON pour les informations spécifiques des ECUE

## Structure du projet

```
.
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py         # Configuration des bases de données
│   ├── models/
│   │   ├── __init__.py
│   │   └── maquette.py         # Modèles SQLAlchemy
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── maquette.py         # Schémas Pydantic
│   ├── services/
│   │   ├── __init__.py
│   │   └── maquette_service.py # Logique métier
│   └── routers/
│       ├── __init__.py
│       ├── composantes.py      # Endpoints pour les composantes
│       ├── etapes.py           # Endpoints pour les étapes
│       ├── ecues.py            # Endpoints pour les ECUE
│       └── rattachements.py    # Endpoints pour les rattachements
├── main.py                     # Application FastAPI principale
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

1. Cloner le dépôt :
   ```bash
   git clone <url-du-depot>
   cd Maquette2026
   ```

2. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Linux/Mac
   # ou
   venv\Scripts\activate  # Sur Windows
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurer les variables d'environnement :
   ```bash
   cp .env.example .env
   # Modifier .env avec vos informations de base de données
   ```

5. Créer les bases de données PostgreSQL annualisées (maquettes2024, maquettes2025, maquettes2026) avec le schéma fourni.

## Exécution

### Développement
```bash
uvicorn main:app --reload
```

L'API sera accessible à : `http://localhost:8000`

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Utilisation

### Sélection de l'année

L'API permet de travailler avec différentes bases de données annualisées. Pour spécifier l'année, utilisez l'en-tête HTTP :

```
X-Maquette-Year: 2025
```

Si aucune année n'est spécifiée, l'API utilisera 2026 par défaut.

### Endpoints principaux

#### Composantes
- `GET /composantes/` - Liste toutes les composantes
- `GET /composantes/{id}` - Récupère une composante spécifique
- `POST /composantes/` - Crée une nouvelle composante
- `PUT /composantes/{id}` - Met à jour une composante
- `DELETE /composantes/{id}` - Supprime une composante

#### Étapes
- `GET /etapes/` - Liste toutes les étapes (avec filtres optionnels)
- `GET /etapes/{id}` - Récupère une étape spécifique
- `GET /etapes/composante/{composante_id}` - Récupère les étapes d'une composante
- `POST /etapes/` - Crée une nouvelle étape
- `PUT /etapes/{id}` - Met à jour une étape
- `DELETE /etapes/{id}` - Supprime une étape

#### ECUE
- `GET /ecues/` - Liste toutes les ECUE (avec filtres optionnels)
- `GET /ecues/{id}` - Récupère une ECUE spécifique
- `GET /ecues/etape/{etape_id}` - Récupère les ECUE d'une étape
- `GET /ecues/{id}/rattachements` - Récupère tous les rattachements d'une ECUE
- `GET /ecues/{id}/etapes` - Récupère toutes les étapes d'une ECUE
- `POST /ecues/` - Crée une nouvelle ECUE
- `PUT /ecues/{id}` - Met à jour une ECUE
- `DELETE /ecues/{id}` - Supprime une ECUE

#### Rattachements
- `GET /rattachements/` - Liste tous les rattachements
- `GET /rattachements/ecue/{ecue_id}` - Récupère les rattachements d'une ECUE
- `GET /rattachements/etape/{etape_id}` - Récupère les rattachements d'une étape
- `POST /rattachements/` - Crée un nouveau rattachement
- `DELETE /rattachements/{id}` - Supprime un rattachement

#### Général
- `GET /` - Page d'accueil
- `GET /health` - Vérifie l'état de santé
- `GET /years` - Liste les années disponibles

### Documentation

La documentation interactive Swagger UI est disponible à :
`http://localhost:8000/docs`

La documentation ReDoc est disponible à :
`http://localhost:8000/redoc`

## Exemples de requêtes

### Créer une composante
```bash
curl -X POST "http://localhost:8000/composantes/" \
  -H "Content-Type: application/json" \
  -H "X-Maquette-Year: 2025" \
  -d '{"nom": "Faculté des Sciences"}'
```

### Créer une étape
```bash
curl -X POST "http://localhost:8000/etapes/" \
  -H "Content-Type: application/json" \
  -H "X-Maquette-Year: 2025" \
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
  -d '{
    "ecue_id": 1,
    "etape_id": 2,
    "effectif": 50
  }'
```

### Récupérer les rattachements d'une ECUE
```bash
curl -X GET "http://localhost:8000/ecues/1/rattachements" \
  -H "X-Maquette-Year: 2025"
```

### Récupérer toutes les étapes d'une ECUE
```bash
curl -X GET "http://localhost:8000/ecues/1/etapes" \
  -H "X-Maquette-Year: 2025"
```

## Modèle de données

Voir le fichier `main.py` ou la documentation Swagger pour le schéma complet.

### Tables principales

- **composante** : ID, nom
- **etape** : ID, nom, code, type, niveau, domaine, effectif, composante_id
- **ecue** : ID, nom, code, periode, etape_id (principale), effectif, besoins (JSON)
- **ecue_etape** : ID, ecue_id, etape_id, effectif

## Déploiement

Pour un déploiement en production :

1. Configurer les variables d'environnement
2. Créer les bases de données PostgreSQL
3. Utiliser un serveur WSGI comme Gunicorn avec Uvicorn :
   ```bash
   gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 main:app
   ```

## Contribution

1. Forker le projet
2. Créer une branche de fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalité`)
3. Committer vos changements (`git commit -am 'Ajout de la nouvelle fonctionnalité'`)
4. Pousser vers la branche (`git push origin feature/nouvelle-fonctionnalité`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT.
