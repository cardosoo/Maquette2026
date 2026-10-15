"""
Interface utilisateur en HTML pur (sans framework JavaScript) pour parcourir
la structure des enseignements : composante -> étape -> ECUE.

Les id de la base de données ne sont jamais exposés : les composantes, les étapes
et les ECUE sont identifiées par leur code (unique).
"""

from typing import Optional, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config.database import database_config
from app.config.dependencies import get_year_from_header
from app.models.maquette import Composante, Etape, ECUE
from app.services.maquette_service import MaquetteService
from app.ui import pages

router = APIRouter(prefix="/ui", tags=["interface"])

# Nombre maximal de résultats affichés par catégorie dans la recherche
MAX_RESULTATS = 50


async def get_ui_year(
    year: Optional[int] = Query(None, description="Année de la maquette (2024, 2025, 2026)"),
    default_year: int = Depends(get_year_from_header),
) -> int:
    """
    Année de la maquette pour l'interface : paramètre ?year= s'il est fourni
    et valide, sinon en-tête X-Maquette-Year, sinon année par défaut.
    """
    if year is None:
        return default_year
    if year not in database_config.get_available_years():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Année {year} non disponible",
        )
    return year


async def get_ui_session(
    year: int = Depends(get_ui_year),
) -> AsyncGenerator[Session, None]:
    """Session de base de données pour l'interface, selon l'année demandée"""
    session_maker = database_config.get_session_maker(year)
    session = session_maker()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_service(db_session: Session = Depends(get_ui_session)) -> MaquetteService:
    """Dependency pour obtenir le service avec la session de base de données"""
    return MaquetteService(db_session)


def _not_found(message: str, year: int) -> HTMLResponse:
    """Page HTML 404 avec lien de retour"""
    return HTMLResponse(
        content=pages.page_erreur(message, year, database_config.get_available_years()),
        status_code=status.HTTP_404_NOT_FOUND,
    )


@router.get("", response_class=HTMLResponse, include_in_schema=False)
@router.get("/", response_class=HTMLResponse)
async def ui_accueil(
    year: int = Depends(get_ui_year),
    session: Session = Depends(get_ui_session),
):
    """Accueil de l'interface : liste des composantes (point d'entrée)"""
    composantes = session.query(Composante).order_by(Composante.nom).all()
    return pages.page_home(composantes, year, database_config.get_available_years())


@router.get("/recherche", response_class=HTMLResponse)
async def ui_recherche(
    q: str = Query(..., min_length=1, description="Recherche par code ou par nom"),
    year: int = Depends(get_ui_year),
    session: Session = Depends(get_ui_session),
):
    """Recherche par code ou par nom dans les composantes, étapes et ECUE"""
    like = f"%{q}%"
    composantes = (
        session.query(Composante)
        .filter(or_(Composante.code.ilike(like), Composante.nom.ilike(like)))
        .order_by(Composante.code)
        .limit(MAX_RESULTATS)
        .all()
    )
    etapes = (
        session.query(Etape)
        .filter(or_(Etape.code.ilike(like), Etape.nom.ilike(like)))
        .order_by(Etape.code)
        .limit(MAX_RESULTATS)
        .all()
    )
    ecues = (
        session.query(ECUE)
        .filter(or_(ECUE.code.ilike(like), ECUE.nom.ilike(like)))
        .order_by(ECUE.code)
        .limit(MAX_RESULTATS)
        .all()
    )
    return pages.page_recherche(
        q, composantes, etapes, ecues, year, database_config.get_available_years()
    )


@router.get("/composante/{code}", response_class=HTMLResponse)
async def ui_composante(
    code: str,
    year: int = Depends(get_ui_year),
    service: MaquetteService = Depends(get_service),
):
    """Détail d'une composante (identifiée par son code) et liste de ses étapes"""
    composante = service.get_composante_by_code(code)
    if not composante:
        return _not_found(f"Aucune composante avec le code « {code} »", year)
    etapes, _ = service.get_etapes_by_composante(composante.id)
    etapes = sorted(etapes, key=lambda e: e.code)
    return pages.page_composante(
        composante, etapes, year, database_config.get_available_years()
    )


@router.get("/etape/{code}", response_class=HTMLResponse)
async def ui_etape(
    code: str,
    year: int = Depends(get_ui_year),
    service: MaquetteService = Depends(get_service),
):
    """Détail d'une étape (identifiée par son code), sa composante et ses ECUE"""
    etape = service.get_etape_by_code(code)
    if not etape:
        return _not_found(f"Aucune étape avec le code « {code} »", year)
    composante = service.get_composante_by_id(etape.composante_id)
    ecues, _ = service.get_ecues_by_etape(etape.id)
    ecues = sorted(ecues, key=lambda e: e.code)
    return pages.page_etape(
        etape, composante, ecues, year, database_config.get_available_years()
    )


@router.get("/ecue/{code}", response_class=HTMLResponse)
async def ui_ecue(
    code: str,
    year: int = Depends(get_ui_year),
    service: MaquetteService = Depends(get_service),
):
    """Détail d'une ECUE (identifiée par son code) et ses étapes de rattachement"""
    ecue = service.get_ecue_by_code(code)
    if not ecue:
        return _not_found(f"Aucune ECUE avec le code « {code} »", year)
    etape = service.get_etape_by_id(ecue.etape_id)
    composante = service.get_composante_by_id(etape.composante_id)
    rattachements = service.get_ecue_etapes_by_ecue(ecue.id)
    autres_etapes = sorted(
        (
            service.get_etape_by_id(r.etape_id)
            for r in rattachements
            if r.etape_id != ecue.etape_id
        ),
        key=lambda e: e.code,
    )
    return pages.page_ecue(
        ecue, etape, composante, autres_etapes, year, database_config.get_available_years()
    )
