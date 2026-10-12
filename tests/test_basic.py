"""
Tests de base pour l'API Maquettes
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, AsyncGenerator
from contextlib import contextmanager
from typing import Optional

from main import app
from app.config.database import Base
from app.config.dependencies import get_db_session, get_db_session_with_payload, get_year_from_header
from app.models.maquette import Composante, Etape, ECUE, ECUE_Etape

# Configuration de la base de données de test
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables pour les tests
Base.metadata.create_all(bind=engine)

# Headers par défaut pour les tests
TEST_HEADERS = {
    "X-Maquette-Year": "2026",
    "X-Payload": "e7b8a803-9a07-40ce-8618-489c31eca10e"
}


# Override pour la dépendance get_year_from_header (toujours retourne 2026)
async def override_get_year_from_header():
    """Override pour get_year_from_header - retourne toujours 2026"""
    return 2026


@contextmanager
def override_get_db_session() -> Generator[Session, None, None]:
    """Override la dépendance get_db_session pour les tests"""
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# Override pour get_db_session_with_payload (doit accepter year et x_payload)
async def override_get_db_session_with_payload(
    year: int = 2026,
    x_payload: Optional[str] = None
) -> AsyncGenerator[Session, None]:
    """Override asynchrone pour get_db_session_with_payload"""
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()



# Fixture pour nettoyer la base de données avant chaque test
@pytest.fixture(autouse=True)
def clean_database():
    """Nettoie la base de données avant chaque test"""
    db = TestingSessionLocal()
    db.query(ECUE_Etape).delete()
    db.query(ECUE).delete()
    db.query(Etape).delete()
    db.query(Composante).delete()
    db.commit()
    db.close()


# Fixture pour créer le client de test avec les dépendances override
@pytest.fixture
def test_client():
    """Crée un client de test avec les dépendances configurées"""
    # Appliquer les overrides
    app.dependency_overrides[get_year_from_header] = override_get_year_from_header
    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_db_session_with_payload] = override_get_db_session_with_payload
    
    with TestClient(app) as client:
        yield client
    
    # Réinitialiser après le test
    app.dependency_overrides.clear()


class TestComposantes:
    """Tests pour les endpoints des composantes"""
    
    def test_create_composante(self, test_client):
        """Test la création d'une composante"""
        response = test_client.post(
            "/composantes/",
            json={"nom": "Faculté de Test"},
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 201
        assert response.json()["nom"] == "Faculté de Test"
        assert "id" in response.json()
    
    def test_get_composantes(self, test_client):
        """Test la récupération de toutes les composantes"""
        # Créer une composante d'abord
        test_client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers=TEST_HEADERS
        )
        
        response = test_client.get(
            "/composantes/",
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1
    
    def test_get_composante_by_id(self, test_client):
        """Test la récupération d'une composante par ID"""
        # Créer une composante
        create_response = test_client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers=TEST_HEADERS
        )
        composante_id = create_response.json()["id"]
        
        response = test_client.get(
            f"/composantes/{composante_id}",
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 200
        assert response.json()["nom"] == "Faculté Test"


class TestEtapes:
    """Tests pour les endpoints des étapes"""
    
    def test_create_etape(self, test_client):
        """Test la création d'une étape"""
        # Créer une composante d'abord
        composante_response = test_client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers=TEST_HEADERS
        )
        composante_id = composante_response.json()["id"]
        
        # Créer une étape
        response = test_client.post(
            "/etapes/",
            json={
                "nom": "Licence Test",
                "code": "L1TEST",
                "type": "L1",
                "niveau": "Licence",
                "domaine": "Sciences",
                "effectif": 100,
                "composante_id": composante_id
            },
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 201
        assert response.json()["code"] == "L1TEST"
        assert response.json()["composante_id"] == composante_id
    
    def test_get_etapes_by_composante(self, test_client):
        """Test la récupération des étapes par composante"""
        # Créer une composante
        composante_response = test_client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers=TEST_HEADERS
        )
        composante_id = composante_response.json()["id"]
        
        # Créer une étape
        test_client.post(
            "/etapes/",
            json={
                "nom": "Licence Test",
                "code": "L1TEST",
                "type": "L1",
                "niveau": "Licence",
                "domaine": "Sciences",
                "effectif": 100,
                "composante_id": composante_id
            },
            headers=TEST_HEADERS
        )
        
        # Récupérer les étapes de la composante
        response = test_client.get(
            f"/etapes/composante/{composante_id}",
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1


class TestECUE:
    """Tests pour les endpoints des ECUE"""
    
    def test_create_ecue(self, test_client):
        """Test la création d'une ECUE"""
        # Créer une composante
        composante_response = test_client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers=TEST_HEADERS
        )
        composante_id = composante_response.json()["id"]
        
        # Créer une étape
        etape_response = test_client.post(
            "/etapes/",
            json={
                "nom": "Licence Test",
                "code": "L1TEST",
                "type": "L1",
                "niveau": "Licence",
                "domaine": "Sciences",
                "effectif": 100,
                "composante_id": composante_id
            },
            headers=TEST_HEADERS
        )
        etape_id = etape_response.json()["id"]
        
        # Créer une ECUE
        response = test_client.post(
            "/ecues/",
            json={
                "nom": "Programmation Test",
                "code": "PROGTEST",
                "periode": "S1",
                "etape_id": etape_id,
                "effectif": 50,
                "besoins": {"salles": ["A101"], "heures": 40}
            },
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 201
        assert response.json()["code"] == "PROGTEST"
        assert response.json()["etape_id"] == etape_id
        assert response.json()["besoins"] == {"salles": ["A101"], "heures": 40}
    
    def test_get_ecues_by_etape(self, test_client):
        """Test la récupération des ECUE par étape"""
        # Créer une composante
        composante_response = test_client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers=TEST_HEADERS
        )
        composante_id = composante_response.json()["id"]
        
        # Créer une étape
        etape_response = test_client.post(
            "/etapes/",
            json={
                "nom": "Licence Test",
                "code": "L1TEST",
                "type": "L1",
                "niveau": "Licence",
                "domaine": "Sciences",
                "effectif": 100,
                "composante_id": composante_id
            },
            headers=TEST_HEADERS
        )
        etape_id = etape_response.json()["id"]
        
        # Créer une ECUE
        test_client.post(
            "/ecues/",
            json={
                "nom": "Programmation Test",
                "code": "PROGTEST",
                "periode": "S1",
                "etape_id": etape_id,
                "effectif": 50,
                "besoins": {}
            },
            headers=TEST_HEADERS
        )
        
        # Récupérer les ECUE de l'étape
        response = test_client.get(
            f"/ecues/etape/{etape_id}",
            headers=TEST_HEADERS
        )
        
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1


class TestGeneral:
    """Tests généraux pour l'API"""
    
    def test_root_endpoint(self, test_client):
        """Test l'endpoint racine"""
        response = test_client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_endpoint(self, test_client):
        """Test l'endpoint de santé"""
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_years_endpoint(self, test_client):
        """Test l'endpoint des années disponibles"""
        response = test_client.get("/years")
        assert response.status_code == 200
        assert "available_years" in response.json()


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
