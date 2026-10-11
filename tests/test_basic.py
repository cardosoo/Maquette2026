"""
Tests de base pour l'API Maquettes
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.config.database import Base
from app.models.maquette import Composante, Etape, ECUE, ECUE_Etape

# Créer un client de test
client = TestClient(app)

# Configuration de la base de données de test
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Créer les tables pour les tests
Base.metadata.create_all(bind=engine)


def override_get_db_session():
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


# Injecter l'override dans l'application
def setup_test_db():
    """Configure la base de données de test"""
    db = TestingSessionLocal()
    
    # Nettoyer les tables
    db.query(ECUE_Etape).delete()
    db.query(ECUE).delete()
    db.query(Etape).delete()
    db.query(Composante).delete()
    db.commit()
    
    # Créer des données de test
    composante = Composante(nom="Test Composante")
    db.add(composante)
    db.commit()
    db.refresh(composante)
    
    etape = Etape(
        nom="Test Etape",
        code="TEST001",
        type="TEST",
        niveau="Test",
        domaine="Test",
        effectif=50,
        composante_id=composante.id
    )
    db.add(etape)
    db.commit()
    db.refresh(etape)
    
    ecue = ECUE(
        nom="Test ECUE",
        code="ECUE001",
        periode="S1",
        etape_id=etape.id,
        effectif=50,
        besoins={"test": "value"}
    )
    db.add(ecue)
    db.commit()
    db.refresh(ecue)
    
    db.close()


@pytest.fixture(autouse=True)
def clean_db():
    """Nettoie la base de données avant chaque test"""
    db = TestingSessionLocal()
    db.query(ECUE_Etape).delete()
    db.query(ECUE).delete()
    db.query(Etape).delete()
    db.query(Composante).delete()
    db.commit()
    db.close()


class TestComposantes:
    """Tests pour les endpoints des composantes"""
    
    def test_create_composante(self):
        """Test la création d'une composante"""
        response = client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers={"X-Maquette-Year": "2026"}
        )
        
        assert response.status_code == 201
        assert response.json()["nom"] == "Faculté Test"
        assert "id" in response.json()
    
    def test_get_composantes(self):
        """Test la récupération de toutes les composantes"""
        # Créer une composante d'abord
        client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers={"X-Maquette-Year": "2026"}
        )
        
        response = client.get(
            "/composantes/",
            headers={"X-Maquette-Year": "2026"}
        )
        
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1
    
    def test_get_composante_by_id(self):
        """Test la récupération d'une composante par ID"""
        # Créer une composante
        create_response = client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers={"X-Maquette-Year": "2026"}
        )
        composante_id = create_response.json()["id"]
        
        response = client.get(
            f"/composantes/{composante_id}",
            headers={"X-Maquette-Year": "2026"}
        )
        
        assert response.status_code == 200
        assert response.json()["nom"] == "Faculté Test"


class TestEtapes:
    """Tests pour les endpoints des étapes"""
    
    def test_create_etape(self):
        """Test la création d'une étape"""
        # Créer une composante d'abord
        composante_response = client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers={"X-Maquette-Year": "2026"}
        )
        composante_id = composante_response.json()["id"]
        
        # Créer une étape
        response = client.post(
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
            headers={"X-Maquette-Year": "2026"}
        )
        
        assert response.status_code == 201
        assert response.json()["code"] == "L1TEST"
        assert response.json()["composante_id"] == composante_id
    
    def test_get_etapes_by_composante(self):
        """Test la récupération des étapes par composante"""
        # Créer une composante
        composante_response = client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers={"X-Maquette-Year": "2026"}
        )
        composante_id = composante_response.json()["id"]
        
        # Créer une étape
        client.post(
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
            headers={"X-Maquette-Year": "2026"}
        )
        
        # Récupérer les étapes de la composante
        response = client.get(
            f"/etapes/composante/{composante_id}",
            headers={"X-Maquette-Year": "2026"}
        )
        
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1


class TestECUE:
    """Tests pour les endpoints des ECUE"""
    
    def test_create_ecue(self):
        """Test la création d'une ECUE"""
        # Créer une composante
        composante_response = client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers={"X-Maquette-Year": "2026"}
        )
        composante_id = composante_response.json()["id"]
        
        # Créer une étape
        etape_response = client.post(
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
            headers={"X-Maquette-Year": "2026"}
        )
        etape_id = etape_response.json()["id"]
        
        # Créer une ECUE
        response = client.post(
            "/ecues/",
            json={
                "nom": "Programmation Test",
                "code": "PROGTEST",
                "periode": "S1",
                "etape_id": etape_id,
                "effectif": 50,
                "besoins": {"salles": ["A101"], "heures": 40}
            },
            headers={"X-Maquette-Year": "2026"}
        )
        
        assert response.status_code == 201
        assert response.json()["code"] == "PROGTEST"
        assert response.json()["etape_id"] == etape_id
        assert response.json()["besoins"] == {"salles": ["A101"], "heures": 40}
    
    def test_get_ecues_by_etape(self):
        """Test la récupération des ECUE par étape"""
        # Créer une composante
        composante_response = client.post(
            "/composantes/",
            json={"nom": "Faculté Test"},
            headers={"X-Maquette-Year": "2026"}
        )
        composante_id = composante_response.json()["id"]
        
        # Créer une étape
        etape_response = client.post(
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
            headers={"X-Maquette-Year": "2026"}
        )
        etape_id = etape_response.json()["id"]
        
        # Créer une ECUE
        client.post(
            "/ecues/",
            json={
                "nom": "Programmation Test",
                "code": "PROGTEST",
                "periode": "S1",
                "etape_id": etape_id,
                "effectif": 50,
                "besoins": {}
            },
            headers={"X-Maquette-Year": "2026"}
        )
        
        # Récupérer les ECUE de l'étape
        response = client.get(
            f"/ecues/etape/{etape_id}",
            headers={"X-Maquette-Year": "2026"}
        )
        
        assert response.status_code == 200
        assert len(response.json()["items"]) >= 1


class TestGeneral:
    """Tests généraux pour l'API"""
    
    def test_root_endpoint(self):
        """Test l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_endpoint(self):
        """Test l'endpoint de santé"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_years_endpoint(self):
        """Test l'endpoint des années disponibles"""
        response = client.get("/years")
        assert response.status_code == 200
        assert "available_years" in response.json()


if __name__ == "__main__":
    # Exécuter les tests
    pytest.main([__file__, "-v"])
