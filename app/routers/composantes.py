"""
Router pour les opérations sur les composantes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.config.dependencies import get_db_session_with_payload as get_db_session
from app.services.maquette_service import MaquetteService
from app.schemas.maquette import (
    ComposanteResponse, ComposanteCreate, ComposanteUpdate,
    PaginatedResponse, ErrorResponse
)

router = APIRouter(prefix="/composantes", tags=["composantes"])


def get_service(db_session: Session = Depends(get_db_session)) -> MaquetteService:
    """Dependency pour obtenir le service avec la session de base de données"""
    return MaquetteService(db_session)


@router.get("/", response_model=PaginatedResponse[ComposanteResponse], responses={
    200: {"model": PaginatedResponse[ComposanteResponse]},
    500: {"model": ErrorResponse}
})
async def get_composantes(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximal d'éléments à retourner"),
    code: Optional[str] = Query(None, description="Filtrer par code"),
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère la liste de toutes les composantes
    
    - **skip**: Nombre d'éléments à sauter pour la pagination
    - **limit**: Nombre maximal d'éléments à retourner
    - **code**: Code de la composante pour filtrer
    """
    composantes, total = service.search_composantes(
        code=code,
        skip=skip,
        limit=limit
    )
    
    return {
        "items": [ComposanteResponse.model_validate(composante) for composante in composantes],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/{composante_id}", response_model=ComposanteResponse, responses={
    200: {"model": ComposanteResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_composante_by_id(
    composante_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère une composante spécifique par son ID
    
    - **composante_id**: ID de la composante à récupérer
    """
    composante = service.get_composante_by_id(composante_id)
    if not composante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Composante avec l'ID {composante_id} non trouvée"
        )
    return ComposanteResponse.model_validate(composante)


@router.get("/code/{code}", response_model=ComposanteResponse, responses={
    200: {"model": ComposanteResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_composante_by_code(
    code: str,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère une composante spécifique par son code
    
    - **code**: Code de la composante à récupérer
    """
    composante = service.get_composante_by_code(code)
    if not composante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Composante avec le code '{code}' non trouvée"
        )
    return ComposanteResponse.model_validate(composante)


@router.post("/", response_model=ComposanteResponse, status_code=status.HTTP_201_CREATED, responses={
    201: {"model": ComposanteResponse},
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def create_composante(
    composante_data: ComposanteCreate,
    service: MaquetteService = Depends(get_service)
):
    """
    Crée une nouvelle composante
    
    - **composante_data**: Données de la composante à créer
    """
    return ComposanteResponse.model_validate(
        service.create_composante(composante_data)
    )


@router.put("/{composante_id}", response_model=ComposanteResponse, responses={
    200: {"model": ComposanteResponse},
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def update_composante(
    composante_id: int,
    composante_data: ComposanteUpdate,
    service: MaquetteService = Depends(get_service)
):
    """
    Met à jour une composante existante
    
    - **composante_id**: ID de la composante à mettre à jour
    - **composante_data**: Données mises à jour
    """
    composante = service.update_composante(composante_id, composante_data)
    if not composante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Composante avec l'ID {composante_id} non trouvée"
        )
    return ComposanteResponse.model_validate(composante)


@router.delete("/{composante_id}", status_code=status.HTTP_204_NO_CONTENT, responses={
    204: {"description": "Composante supprimée avec succès"},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def delete_composante(
    composante_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Supprime une composante
    
    - **composante_id**: ID de la composante à supprimer
    
    **Attention**: La suppression est en cascade (toutes les étapes et ECUE associées seront également supprimées)
    """
    success = service.delete_composante(composante_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Composante avec l'ID {composante_id} non trouvée"
        )
    return None
