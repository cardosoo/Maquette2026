"""
Router pour les opérations sur les fonctions du référentiel (RH)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.config.dependencies import get_db_session, get_year_from_header
from app.services.fonction_service import FonctionService
from app.schemas.rh import FonctionRefCreate, FonctionRefResponse

router = APIRouter(prefix="/fonctions", tags=["fonctions"])


def get_service(
    db_session: Session = Depends(get_db_session),
    year: int = Depends(get_year_from_header)
) -> FonctionService:
    """Dependency pour obtenir le service avec la session et l'année"""
    return FonctionService(db_session, year)


@router.get("/", response_model=list[FonctionRefResponse])
async def get_fonctions(
    skip: int = Query(0, ge=0, description="Pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Pagination"),
    service: FonctionService = Depends(get_service)
):
    """Récupère la liste des fonctions du référentiel"""
    items, total = service.get_all(skip=skip, limit=limit)
    return items
