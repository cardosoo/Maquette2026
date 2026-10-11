"""
Router pour les opérations sur les rattachements ECUE-Étape
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session

from app.config.database import get_db_session
from app.services.maquette_service import MaquetteService
from app.schemas.maquette import (
    ECUEEtapeResponse, ECUEEtapeCreate, ECUEEtapeUpdate,
    ECUEEtapeWithDetailsResponse,
    PaginatedResponse, ErrorResponse,
    ECUEResponse, EtapeResponse
)
from app.models.maquette import ECUE_Etape

router = APIRouter(prefix="/rattachements", tags=["rattachements"])


def get_service(db_session: Session = Depends(get_db_session)) -> MaquetteService:
    """Dependency pour obtenir le service avec la session de base de données"""
    return MaquetteService(db_session)


@router.get("/", response_model=PaginatedResponse, responses={
    200: {"model": PaginatedResponse},
    500: {"model": ErrorResponse}
})
async def get_all_rattachements(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximal d'éléments à retourner"),
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère tous les rattachements ECUE-Étape
    
    - **skip**: Nombre d'éléments à sauter pour la pagination
    - **limit**: Nombre maximal d'éléments à retourner
    """
    # Pour l'instant, on récupère tous les rattachements
    # On pourrait optimiser avec une requête directe
    rattachements = service.db.query(ECUE_Etape).offset(skip).limit(limit).all()
    total = service.db.query(ECUE_Etape).count()
    
    return {
        "items": [ECUEEtapeResponse.model_validate(r) for r in rattachements],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/ecue/{ecue_id}", response_model=List[ECUEEtapeWithDetailsResponse], responses={
    200: {"model": List[ECUEEtapeWithDetailsResponse]},
    500: {"model": ErrorResponse}
})
async def get_rattachements_by_ecue(
    ecue_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère tous les rattachements pour une ECUE spécifique
    
    - **ecue_id**: ID de l'ECUE
    """
    rattachements = service.get_ecue_etapes_by_ecue(ecue_id)
    
    # Charger les détails pour chaque rattachement
    result = []
    for rattachement in rattachements:
        ecue = service.get_ecue_by_id(rattachement.ecue_id)
        etape = service.get_etape_by_id(rattachement.etape_id)
        
        if ecue and etape:
            result.append(ECUEEtapeWithDetailsResponse.model_validate({
                **ECUEEtapeResponse.model_validate(rattachement).model_dump(),
                "ecue": ECUEResponse.model_validate(ecue),
                "etape": EtapeResponse.model_validate(etape)
            }))
    
    return result


@router.get("/etape/{etape_id}", response_model=List[ECUEEtapeWithDetailsResponse], responses={
    200: {"model": List[ECUEEtapeWithDetailsResponse]},
    500: {"model": ErrorResponse}
})
async def get_rattachements_by_etape(
    etape_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère tous les rattachements pour une étape spécifique
    
    - **etape_id**: ID de l'étape
    """
    rattachements = service.get_ecue_etapes_by_etape(etape_id)
    
    # Charger les détails pour chaque rattachement
    result = []
    for rattachement in rattachements:
        ecue = service.get_ecue_by_id(rattachement.ecue_id)
        etape = service.get_etape_by_id(rattachement.etape_id)
        
        if ecue and etape:
            result.append(ECUEEtapeWithDetailsResponse.model_validate({
                **ECUEEtapeResponse.model_validate(rattachement).model_dump(),
                "ecue": ECUEResponse.model_validate(ecue),
                "etape": EtapeResponse.model_validate(etape)
            }))
    
    return result


@router.post("/", response_model=ECUEEtapeResponse, status_code=status.HTTP_201_CREATED, responses={
    201: {"model": ECUEEtapeResponse},
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def create_rattachement(
    rattachement_data: ECUEEtapeCreate,
    service: MaquetteService = Depends(get_service)
):
    """
    Crée un nouveau rattachement ECUE-Étape
    
    - **rattachement_data**: Données du rattachement à créer
    """
    return ECUEEtapeResponse.model_validate(
        service.create_ecue_etape(rattachement_data)
    )


@router.delete("/{rattachement_id}", status_code=status.HTTP_204_NO_CONTENT, responses={
    204: {"description": "Rattachement supprimé avec succès"},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def delete_rattachement(
    rattachement_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Supprime un rattachement ECUE-Étape
    
    - **rattachement_id**: ID du rattachement à supprimer
    """
    success = service.delete_ecue_etape(rattachement_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rattachement avec l'ID {rattachement_id} non trouvé"
        )
    return None
