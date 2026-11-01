"""
Dependencies FastAPI pour l'application
"""

from fastapi import Depends, Header, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from typing import Optional, List, Callable, AsyncGenerator
from contextlib import contextmanager
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from app.config.database import database_config, Base
from app.config.settings import get_settings

# Définir le header X-Payload comme schéma de sécurité pour OpenAPI
# (X-Maquette-Year sera géré comme un paramètre classique, pas un security scheme)
x_payload_header = APIKeyHeader(name="X-Payload", description="Code payload pour autorisation")


async def get_year_from_header(
    x_maquette_year: Optional[int] = Header(None, description="Année de la maquette (2024, 2025, 2026)")
) -> int:
    """
    Récupère l'année de la maquette depuis l'en-tête HTTP X-Maquette-Year
    Si non spécifiée, utilise l'année par défaut (2026)
    """
    settings = get_settings()
    available_years = database_config.get_available_years()
    
    if x_maquette_year and x_maquette_year in available_years:
        return x_maquette_year
    
    # Année par défaut
    default_year = settings.DEFAULT_YEAR
    if default_year in available_years:
        return default_year
    
    # Si aucune année disponible, retourner la première de la liste
    if available_years:
        return available_years[0]
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Aucune base de données disponible"
    )


async def get_db_session(
    year: int = Depends(get_year_from_header)
) -> AsyncGenerator[Session, None]:
    """
    Dependency pour obtenir une session sur la base unique maquette_rh.
    L'année (header X-Maquette-Year) est conservée dans la signature pour
    la compatibilité des overrides ; le filtrage par année se fait dans les services.
    """
    session_maker = database_config.get_session_maker()
    session = session_maker()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


async def verify_payload(
    x_payload: Optional[str] = Depends(x_payload_header)
) -> str:
    """
    Vérifie que le payload fourni correspond à l'un des codes autorisés dans .env
    Retourne le payload s'il est valide
    """
    settings = get_settings()
    
    # Si PAYLOAD n'est pas configuré, on autorise tout
    if not hasattr(settings, 'PAYLOAD') or not settings.PAYLOAD:
        return x_payload or ""
    
    if not x_payload:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payload manquant"
        )
    
    if x_payload not in settings.PAYLOAD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payload invalide ou non autorisé"
        )
    
    return x_payload


async def get_db_session_with_payload(
    year: int = Depends(get_year_from_header),
    x_payload: Optional[str] = Depends(x_payload_header)
) -> AsyncGenerator[Session, None]:
    """
    Dependency pour obtenir une session de base de données avec vérification du payload
    """
    # Vérifier le payload
    settings = get_settings()
    if hasattr(settings, 'PAYLOAD') and settings.PAYLOAD:
        if not x_payload or x_payload not in settings.PAYLOAD:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Payload invalide ou non autorisé"
            )
    
    session_maker = database_config.get_session_maker()
    session = session_maker()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Middleware pour vérifier le payload sur toutes les requêtes
async def payload_middleware(request: Request, call_next: Callable):
    """
    Middleware qui vérifie que le header X-Payload contient un code autorisé
    Certaines routes sont exclues (docs, health, interface, etc.)
    La vérification tolère le préfixe du reverse-proxy : /maquette/docs
    est traitée comme /docs.
    """
    # Routes publiques qui ne nécessitent pas de payload
    public_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/", "/favicon.ico", "/years"]
    # Préfixes publics (interface utilisateur en lecture seule)
    public_prefixes = ["/ui", "/static"]

    def est_publique(path: str) -> bool:
        if path in public_paths:
            return True
        if any(path == prefix or path.startswith(prefix + "/") for prefix in public_prefixes):
            return True
        # Derrière un reverse-proxy qui ne strippe pas le préfixe
        # (ex: /maquette/docs) : on teste le chemin sans son premier segment
        parts = path.strip("/").split("/", 1)
        if len(parts) == 2:
            sub = "/" + parts[1]
            if sub in public_paths:
                return True
            if any(sub == prefix or sub.startswith(prefix + "/") for prefix in public_prefixes):
                return True
        return False

    path = request.url.path
    if est_publique(path):
        response = await call_next(request)
        return response
    
    settings = get_settings()
    
    # Si PAYLOAD est configuré, vérifier le header
    if hasattr(settings, 'PAYLOAD') and settings.PAYLOAD:
        x_payload = request.headers.get('X-Payload')
        if not x_payload or x_payload not in settings.PAYLOAD:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Payload invalide ou non autorisé"}
            )
    
    response = await call_next(request)
    return response
