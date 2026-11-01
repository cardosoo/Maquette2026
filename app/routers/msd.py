"""
Router pour les opérations sur les MSD (Modifications de Service Dû)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.config.dependencies import get_db_session, get_year_from_header
from app.services.msd_service import MSDService
from app.schemas.rh import MSDCreate, MSDResponse

router = APIRouter(prefix="/msd", tags=["msd"])


def get_service(
    db_session: Session = Depends(get_db_session),
    year: int = Depends(get_year_from_header)
) -> MSDService:
    """Dependency pour obtenir le service avec la session et l'année"""
    return MSDService(db_session, year)


@router.get("/", response_model=list[MSDResponse])
async def get_msds(
    skip: int = Query(0, ge=0, description="Pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Pagination"),
    service: MSDService = Depends(get_service)
):
    """Récupère la liste des modifications de service dû (MSD)"""
    items, total = service.get_all(skip=skip, limit=limit)
    return items
