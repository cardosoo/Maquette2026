"""
Router pour les opérations sur les ECUE
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any, cast
from sqlalchemy.orm import Session

from app.config.dependencies import get_db_session_with_payload as get_db_session, get_year_from_header
from app.services.maquette_service import MaquetteService
from app.schemas.maquette import (
    ECUEResponse, ECUECreate, ECUEUpdate,
    ECUEWithEtapeResponse,
    EtapeResponse, ComposanteResponse,
    PaginatedResponse, ErrorResponse
)

router = APIRouter(prefix="/ecues", tags=["ECUE"])


def get_service(
    db_session: Session = Depends(get_db_session),
    year: int = Depends(get_year_from_header)
) -> MaquetteService:
    """Dependency pour obtenir le service avec la session et l'année"""
    return MaquetteService(db_session, year)


@router.get("/", response_model=PaginatedResponse[ECUEResponse], responses={
    200: {"model": PaginatedResponse[ECUEResponse]},
    500: {"model": ErrorResponse}
})
async def get_ecues(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximal d'éléments à retourner"),
    etape_id: Optional[int] = Query(None, description="Filtrer par étape"),
    periode: Optional[str] = Query(None, description="Filtrer par période"),
    code: Optional[str] = Query(None, description="Filtrer par code (contient)"),
    nom: Optional[str] = Query(None, description="Filtrer par nom (contient)"),
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère la liste des ECUE avec filtres optionnels
    
    - **skip**: Nombre d'éléments à sauter pour la pagination
    - **limit**: Nombre maximal d'éléments à retourner
    - **etape_id**: ID de l'étape pour filtrer
    - **periode**: Période (S1, S2, etc.) pour filtrer
    - **code**: Code de l'ECUE (recherche partielle) pour filtrer
    - **nom**: Nom de l'ECUE (recherche partielle) pour filtrer
    """
    ecues, total = service.search_ecues(
        etape_id=etape_id,
        periode=periode,
        code=code,
        nom=nom,
        skip=skip,
        limit=limit
    )
    
    return {
        "items": [ECUEResponse.model_validate(ecue) for ecue in ecues],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/{ecue_id}", response_model=ECUEWithEtapeResponse, responses={
    200: {"model": ECUEWithEtapeResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_ecue_by_id(
    ecue_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère une ECUE spécifique par son ID avec son étape principale
    
    - **ecue_id**: ID de l'ECUE à récupérer
    """
    ecue = service.get_ecue_by_id(ecue_id)
    if not ecue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ECUE avec l'ID {ecue_id} non trouvée"
        )
    
    # Charger l'étape séparément
    etape = service.get_etape_by_id(cast(int, ecue.etape_id))
    
    return ECUEWithEtapeResponse.model_validate({
        **ECUEResponse.model_validate(ecue).model_dump(),
        "etape": EtapeResponse.model_validate(etape)
    })


@router.get("/code/{code}", response_model=ECUEWithEtapeResponse, responses={
    200: {"model": ECUEWithEtapeResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_ecue_by_code(
    code: str,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère une ECUE spécifique par son code avec son étape principale
    
    - **code**: Code de l'ECUE à récupérer
    """
    ecue = service.get_ecue_by_code(code)
    if not ecue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ECUE avec le code '{code}' non trouvée"
        )
    
    # Charger l'étape séparément
    etape = service.get_etape_by_id(cast(int, ecue.etape_id))
    
    return ECUEWithEtapeResponse.model_validate({
        **ECUEResponse.model_validate(ecue).model_dump(),
        "etape": EtapeResponse.model_validate(etape)
    })


@router.get("/etape/{etape_id}", response_model=PaginatedResponse[ECUEResponse], responses={
    200: {"model": PaginatedResponse[ECUEResponse]},
    500: {"model": ErrorResponse}
})
async def get_ecues_by_etape(
    etape_id: int,
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximal d'éléments à retourner"),
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère les ECUE d'une étape spécifique
    
    - **etape_id**: ID de l'étape
    - **skip**: Nombre d'éléments à sauter pour la pagination
    - **limit**: Nombre maximal d'éléments à retourner
    """
    ecues, total = service.get_ecues_by_etape(etape_id, skip=skip, limit=limit)
    
    return {
        "items": [ECUEResponse.model_validate(ecue) for ecue in ecues],
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/{ecue_id}/rattachements", responses={
    200: {"description": "Rattachements de l'ECUE"},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_ecue_rattachements(
    ecue_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère tous les rattachements d'une ECUE
    
    Retourne:
    - etape_principale: L'étape principale (celle dans etape_id de l'ECUE)
    - autres_etapes: Liste des autres étapes via la table ecue_etape
    
    - **ecue_id**: ID de l'ECUE
    """
    try:
        result = service.get_ecue_rattachements(ecue_id)
        
        etape_principale = result["etape_principale"]
        autres_etapes = result["autres_etapes"]
        ecue = result["ecue"]
        
        return {
            "ecue": ECUEResponse.model_validate(ecue),
            "etape_principale": EtapeResponse.model_validate(etape_principale) if etape_principale else None,
            "autres_etapes": [EtapeResponse.model_validate(e) for e in autres_etapes]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{ecue_id}/etapes", response_model=List[EtapeResponse], responses={
    200: {"model": List[EtapeResponse]},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def get_etapes_by_ecue(
    ecue_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Récupère toutes les étapes auxquelles une ECUE est rattachée
    
    - **ecue_id**: ID de l'ECUE
    
    Retourne la liste de toutes les étapes (y compris l'étape principale)
    """
    try:
        etapes = service.get_etapes_by_ecue(ecue_id)
        return [EtapeResponse.model_validate(e) for e in etapes]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", response_model=ECUEResponse, status_code=status.HTTP_201_CREATED, responses={
    201: {"model": ECUEResponse},
    400: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def create_ecue(
    ecue_data: ECUECreate,
    service: MaquetteService = Depends(get_service)
):
    """
    Crée une nouvelle ECUE
    
    - **ecue_data**: Données de l'ECUE à créer
    """
    return ECUEResponse.model_validate(
        service.create_ecue(ecue_data)
    )


@router.put("/{ecue_id}", response_model=ECUEResponse, responses={
    200: {"model": ECUEResponse},
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def update_ecue(
    ecue_id: int,
    ecue_data: ECUEUpdate,
    service: MaquetteService = Depends(get_service)
):
    """
    Met à jour une ECUE existante
    
    - **ecue_id**: ID de l'ECUE à mettre à jour
    - **ecue_data**: Données mises à jour
    """
    ecue = service.update_ecue(ecue_id, ecue_data)
    if not ecue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ECUE avec l'ID {ecue_id} non trouvée"
        )
    return ECUEResponse.model_validate(ecue)


@router.delete("/{ecue_id}", status_code=status.HTTP_204_NO_CONTENT, responses={
    204: {"description": "ECUE supprimée avec succès"},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def delete_ecue(
    ecue_id: int,
    service: MaquetteService = Depends(get_service)
):
    """
    Supprime une ECUE
    
    - **ecue_id**: ID de l'ECUE à supprimer
    
    **Attention**: La suppression est en cascade (tous les rattachements seront également supprimés)
    """
    success = service.delete_ecue(ecue_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ECUE avec l'ID {ecue_id} non trouvée"
        )
    return None
