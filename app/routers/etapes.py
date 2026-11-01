"""
Router pour les opérations sur les étapes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, cast
from sqlalchemy.orm import Session

from app.config.dependencies import get_db_session_with_payload as get_db_session, get_year_from_header
from app.services.maquette_service import MaquetteService
from app.schemas.maquette import (
    EtapeResponse, EtapeCreate, EtapeUpdate,
    EtapeWithComposanteResponse,
    ComposanteResponse,
    PaginatedResponse, ErrorResponse
)

router = APIRouter(prefix="/etapes", tags=["étapes"])


def get_service(
    db_session: Session = Depends(get_db_session),
    year: int = Depends(get_year_from_header)
) -> MaquetteService:
    """Dependency pour obtenir le service avec la session et l'année"""
    return MaquetteService(db_session, year)


@router.get("/", response_model=PaginatedResponse[EtapeResponse], responses={
    200: {"model": PaginatedResponse[EtapeResponse]},
    500: {"model": ErrorResponse}
})
async def get_etapes(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximal d'éléments à retourner"),
    composante_id: Optional[int] = Query(None, description="Filtrer par composante"),
    niveau: Optional[str] = Query(None, description="Filtrer par niveau"),
    domaine: Optional[str] = Query(None, description="Filtrer par domaine"),
    type: Optional[str] = Query(None, description="Filtrer par type"),
    code: Optional[str] = Query(None, description="Filtrer par code"),
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère la liste des étapes avec filtres optionnels
    
    - **skip**: Nombre d'éléments à sauter pour la pagination
    - **limit**: Nombre maximal d'éléments à retourner
    - **composante_id**: ID de la composante pour filtrer
    - **niveau**: Niveau (Licence, Master, etc.) pour filtrer
    - **domaine**: Domaine pour filtrer
    - **type**: Type (L1, L2, etc.) pour filtrer
    - **code**: Code de l'étape pour filtrer
    """
    etapes, total = service.search_etapes(
        composante_id=composante_id,
        niveau=niveau,
        domaine=domaine,
        type=type,
        code=code,
        skip=skip,
        limit=limit
    )
    
    return {
        "items": [EtapeResponse.model_validate(etape) for etape in etapes],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/{etape_id}", response_model=EtapeWithComposanteResponse, responses={
    200: {"model": EtapeWithComposanteResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_etape_by_id(
    etape_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère une étape spécifique par son ID avec sa composante
    
    - **etape_id**: ID de l'étape à récupérer
    """
    etape = service.get_etape_by_id(etape_id)
    if not etape:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Étape avec l'ID {etape_id} non trouvée"
        )
    
    # Charger la composante séparément pour éviter les problèmes de lazy loading
    composante = service.get_composante_by_id(cast(int, etape.composante_id))
    
    return EtapeWithComposanteResponse.model_validate({
        **EtapeResponse.model_validate(etape).model_dump(),
        "composante": ComposanteResponse.model_validate(composante)
    })


@router.get("/code/{code}", response_model=EtapeWithComposanteResponse, responses={
    200: {"model": EtapeWithComposanteResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_etape_by_code(
    code: str,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère une étape spécifique par son code avec sa composante
    
    - **code**: Code de l'étape à récupérer
    """
    etape = service.get_etape_by_code(code)
    if not etape:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Étape avec le code '{code}' non trouvée"
        )
    
    # Charger la composante séparément pour éviter les problèmes de lazy loading
    composante = service.get_composante_by_id(cast(int, etape.composante_id))
    
    return EtapeWithComposanteResponse.model_validate({
        **EtapeResponse.model_validate(etape).model_dump(),
        "composante": ComposanteResponse.model_validate(composante)
    })


@router.get("/composante/{composante_id}", response_model=PaginatedResponse[EtapeResponse], responses={
    200: {"model": PaginatedResponse[EtapeResponse]},
    500: {"model": ErrorResponse}
})
async def get_etapes_by_composante(
    composante_id: int,
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximal d'éléments à retourner"),
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère les étapes d'une composante spécifique
    
    - **composante_id**: ID de la composante
    - **skip**: Nombre d'éléments à sauter pour la pagination
    - **limit**: Nombre maximal d'éléments à retourner
    """
    etapes, total = service.get_etapes_by_composante(composante_id, skip=skip, limit=limit)
    
    return {
        "items": [EtapeResponse.model_validate(etape) for etape in etapes],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.post("/", response_model=EtapeResponse, status_code=status.HTTP_201_CREATED, responses={
    201: {"model": EtapeResponse},
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def create_etape(
    etape_data: EtapeCreate,
    service: MaquetteService = Depends(get_service)
):
    """
    Crée une nouvelle étape
    
    - **etape_data**: Données de l'étape à créer
    """
    return EtapeResponse.model_validate(
        service.create_etape(etape_data)
    )


@router.put("/{etape_id}", response_model=EtapeResponse, responses={
    200: {"model": EtapeResponse},
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def update_etape(
    etape_id: int,
    etape_data: EtapeUpdate,
    service: MaquetteService = Depends(get_service)
):
    """
    Met à jour une étape existante
    
    - **etape_id**: ID de l'étape à mettre à jour
    - **etape_data**: Données mises à jour
    """
    etape = service.update_etape(etape_id, etape_data)
    if not etape:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Étape avec l'ID {etape_id} non trouvée"
        )
    return EtapeResponse.model_validate(etape)


@router.delete("/{etape_id}", status_code=status.HTTP_204_NO_CONTENT, responses={
    204: {"description": "Étape supprimée avec succès"},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def delete_etape(
    etape_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Supprime une étape
    
    - **etape_id**: ID de l'étape à supprimer
    
    **Attention**: La suppression est en cascade (toutes les ECUE associées seront également supprimées)
    """
    success = service.delete_etape(etape_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Étape avec l'ID {etape_id} non trouvée"
        )
    return None
