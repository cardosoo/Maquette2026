"""
Tests de l'interface utilisateur HTML (/ui) pour le parcours des maquettes.

Vérifie notamment :
- la navigation composante -> étape -> ECUE (et retour)
- l'absence d'identifiants de la base de données dans les pages et les URLs
- la recherche par code et par nom
- l'accès public (sans en-tête X-Payload)
"""

import re
from typing import AsyncGenerator, Generator, Optional
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from main import app
from app.config.database import Base
from app.config.dependencies import get_db_session_with_payload, get_year_from_header
from app.routers.frontend import get_ui_session
from app.models.maquette import Composante, Etape, ECUE, ECUE_Etape

# Configuration de la base de données de test (SQLite, comme test_basic.py)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Headers pour les appels API (les routes /ui sont publiques, sans payload)
TEST_HEADERS = {
    "X-Maquette-Year": "2026",
    "X-Payload": "e7b8a803-9a07-40ce-8618-489c31eca10e"
}

COMPOSANTE_NOM = "Faculté des Sciences de Test"


async def override_get_year_from_header() -> int:
    """Override pour get_year_from_header - retourne toujours 2026"""
    return 2026


def override_get_ui_session() -> Generator[Session, None, None]:
    """Override la session de l'UI pour utiliser la base SQLite de test"""
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


async def override_get_db_session_with_payload(
    year: int = 2026,
    x_payload: Optional[str] = None,
) -> AsyncGenerator[Session, None]:
    """Override la session des routes API pour utiliser la base SQLite de test"""
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


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


@pytest.fixture
def test_client():
    """Crée un client de test avec les dépendances override (SQLite)"""
    app.dependency_overrides[get_year_from_header] = override_get_year_from_header
    app.dependency_overrides[get_db_session_with_payload] = override_get_db_session_with_payload
    app.dependency_overrides[get_ui_session] = override_get_ui_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def hierarchie(test_client):
    """Crée une composante, deux étapes et une ECUE rattachée aux deux étapes"""
    comp = test_client.post(
        "/composantes/", json={"nom": COMPOSANTE_NOM}, headers=TEST_HEADERS
    ).json()
    etape1 = test_client.post(
        "/etapes/",
        json={
            "nom": "Licence 1 Test",
            "code": "L1TEST",
            "type": "L1",
            "niveau": "Licence",
            "domaine": "Sciences",
            "effectif": 100,
            "composante_id": comp["id"],
        },
        headers=TEST_HEADERS,
    ).json()
    etape2 = test_client.post(
        "/etapes/",
        json={
            "nom": "Licence 2 Test",
            "code": "L2TEST",
            "type": "L2",
            "niveau": "Licence",
            "domaine": "Sciences",
            "effectif": 80,
            "composante_id": comp["id"],
        },
        headers=TEST_HEADERS,
    ).json()
    ecue = test_client.post(
        "/ecues/",
        json={
            "nom": "Programmation Test",
            "code": "PROG1",
            "periode": "S1",
            "etape_id": etape1["id"],
            "effectif": 50,
            "besoins": {"salles": ["A101"], "heures": 40},
        },
        headers=TEST_HEADERS,
    ).json()
    test_client.post(
        "/rattachements/",
        json={"ecue_id": ecue["id"], "etape_id": etape2["id"], "effectif": 30},
        headers=TEST_HEADERS,
    )
    return {"composante": comp, "etape1": etape1, "etape2": etape2, "ecue": ecue}


def url_composante(nom: str) -> str:
    return f"/ui/composante/{quote(nom)}"


class TestAccueil:
    """Page d'accueil : liste des composantes et formulaire de recherche"""

    def test_accueil_public_sans_payload(self, test_client, hierarchie):
        response = test_client.get("/ui")  # pas d'en-tête X-Payload
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert COMPOSANTE_NOM in response.text

    def test_accueil_avec_annee_en_parametre(self, test_client, hierarchie):
        response = test_client.get("/ui?year=2024")
        assert response.status_code == 200
        assert COMPOSANTE_NOM in response.text

    def test_accueil_annee_invalide(self, test_client):
        response = test_client.get("/ui?year=1999")
        assert response.status_code == 400

    def test_formulaire_recherche_present(self, test_client, hierarchie):
        html = test_client.get("/ui").text
        assert 'action="/ui/recherche"' in html
        assert 'name="q"' in html

    def test_lien_vers_composante_sans_id(self, test_client, hierarchie):
        html = test_client.get("/ui").text
        assert f'href="{url_composante(COMPOSANTE_NOM)}?year=2026"' in html
        # L'id de la composante ne doit pas apparaître dans un lien
        assert f'href="{url_composante(str(hierarchie["composante"]["id"]))}' not in html


class TestParcours:
    """Navigation dans la structure : composante -> étape -> ECUE et retour"""

    def test_page_composante(self, test_client, hierarchie):
        response = test_client.get(url_composante(COMPOSANTE_NOM))
        assert response.status_code == 200
        html = response.text
        assert COMPOSANTE_NOM in html
        # Les étapes de la composante sont listées avec leur code
        assert "L1TEST" in html
        assert "L2TEST" in html
        assert 'href="/ui/etape/L1TEST?year=2026"' in html
        # Lien pour remonter à l'accueil
        assert 'href="/ui?year=2026"' in html

    def test_page_etape(self, test_client, hierarchie):
        response = test_client.get("/ui/etape/L1TEST")
        assert response.status_code == 200
        html = response.text
        assert "Licence 1 Test" in html
        assert "PROG1" in html
        assert 'href="/ui/ecue/PROG1?year=2026"' in html
        # Lien pour remonter vers la composante (par son nom, pas son id)
        assert f'href="{url_composante(COMPOSANTE_NOM)}?year=2026"' in html
        # Fil d'Ariane complet
        assert "Accueil" in html

    def test_page_ecue(self, test_client, hierarchie):
        response = test_client.get("/ui/ecue/PROG1")
        assert response.status_code == 200
        html = response.text
        assert "Programmation Test" in html
        assert "S1" in html
        # Besoins affichés
        assert "A101" in html
        assert "40" in html
        # Liens pour remonter : étape principale + composante
        assert 'href="/ui/etape/L1TEST?year=2026"' in html
        assert f'href="{url_composante(COMPOSANTE_NOM)}?year=2026"' in html
        # Autre étape de rattachement affichée
        assert "L2TEST" in html

    def test_composante_inconnue_404(self, test_client):
        response = test_client.get(url_composante("Nulle Part"))
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("text/html")

    def test_etape_inconnue_404(self, test_client):
        response = test_client.get("/ui/etape/INCONNU")
        assert response.status_code == 404

    def test_ecue_inconnue_404(self, test_client):
        response = test_client.get("/ui/ecue/INCONNU")
        assert response.status_code == 404


class TestRecherche:
    """Formulaire de recherche par code ou par nom"""

    def test_recherche_par_code_ecue(self, test_client, hierarchie):
        response = test_client.get("/ui/recherche", params={"q": "PROG1"})
        assert response.status_code == 200
        html = response.text
        assert "Programmation Test" in html
        assert 'href="/ui/ecue/PROG1?year=2026"' in html

    def test_recherche_par_code_etape(self, test_client, hierarchie):
        response = test_client.get("/ui/recherche", params={"q": "L1TEST"})
        assert response.status_code == 200
        html = response.text
        assert "Licence 1 Test" in html
        assert 'href="/ui/etape/L1TEST?year=2026"' in html

    def test_recherche_par_nom(self, test_client, hierarchie):
        response = test_client.get("/ui/recherche", params={"q": "Programmation"})
        assert response.status_code == 200
        assert "PROG1" in response.text

    def test_recherche_par_nom_composante(self, test_client, hierarchie):
        response = test_client.get("/ui/recherche", params={"q": "Sciences de Test"})
        assert response.status_code == 200
        html = response.text
        assert COMPOSANTE_NOM in html
        assert f'href="{url_composante(COMPOSANTE_NOM)}?year=2026"' in html

    def test_recherche_sans_resultat(self, test_client, hierarchie):
        response = test_client.get("/ui/recherche", params={"q": "zzzzzz"})
        assert response.status_code == 200
        assert "Aucun résultat" in response.text

    def test_recherche_requiert_un_terme(self, test_client):
        response = test_client.get("/ui/recherche", params={"q": ""})
        assert response.status_code == 422


class TestSecuriteEtIds:
    """Les id de la base ne doivent pas fuiter ; l'API reste protégée par payload"""

    def test_ids_non_visibles_dans_les_pages(self, test_client, hierarchie):
        comp_id = hierarchie["composante"]["id"]
        etape_id = hierarchie["etape1"]["id"]
        ecue_id = hierarchie["ecue"]["id"]
        urls = [
            "/ui",
            url_composante(COMPOSANTE_NOM),
            "/ui/etape/L1TEST",
            "/ui/ecue/PROG1",
            "/ui/recherche?q=test",
        ]
        for url in urls:
            html = test_client.get(url).text
            # Aucun lien ne pointe vers un segment numérique pur (id de la base)
            assert not re.search(r'href="[^"]*/(\d+)(\?|")', html), f"id exposé dans un lien sur {url}"
            # Aucun paramètre id= dans les liens
            assert not re.search(r'href="[^"]*[?&]id=\d+', html), f"paramètre id exposé sur {url}"
            # Les id eux-mêmes ne figurent dans aucun lien de la page
            for db_id in (comp_id, etape_id, ecue_id):
                assert not re.search(rf'href="[^"]*\b{db_id}\b[^"]*"', html), (
                    f"id {db_id} présent dans un lien sur {url}"
                )

    def test_api_toujours_protegee_par_payload(self, test_client, hierarchie):
        """Le middleware payload continue de protéger les routes API"""
        response = test_client.get("/composantes/")
        assert response.status_code == 403
        response = test_client.get("/composantes/", headers=TEST_HEADERS)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
