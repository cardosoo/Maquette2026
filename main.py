"""
Application FastAPI pour la gestion des maquettes d'enseignement

Cette application permet de:
- Gérer les composantes, étapes et ECUE
- Consulter les rattachements entre ECUE et étapes
- Travailler avec des bases de données annualisées (maquettes2024, maquettes2025, maquettes2026)

Pour démarrer l'application:
uvicorn main:app --reload

Pour accéder à la documentation:
http://localhost:8000/docs
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import des routeurs
from app.routers import composantes, etapes, ecues, rattachements
from app.config.database import database_config

# Création de l'application FastAPI
app = FastAPI(
    title="Maquettes API",
    description="API pour la gestion des maquettes d'enseignement universitaire",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware pour gérer l'année de la maquette
from fastapi import Request
from contextlib import contextmanager
from sqlalchemy.orm import Session

async def get_year_from_header(
    x_maquette_year: Optional[int] = Header(None, description="Année de la maquette (2024, 2025, 2026)")
) -> int:
    """
    Récupère l'année de la maquette depuis l'en-tête HTTP
    Si non spécifiée, utilise l'année par défaut (2026)
    """
    if x_maquette_year and x_maquette_year in database_config.get_available_years():
        return x_maquette_year
    
    # Année par défaut
    default_year = 2026
    if default_year in database_config.get_available_years():
        return default_year
    
    # Si aucune année disponible, retourner la première de la liste
    available_years = database_config.get_available_years()
    if available_years:
        return available_years[0]
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Aucune base de données disponible"
    )


@contextmanager
def get_db_session_for_year(year: int):
    """
    Contexte pour obtenir une session de base de données pour une année donnée
    """
    with database_config.get_session(year) as session:
        yield session


# Dependency pour obtenir la session de la bonne année
async def get_db_session(
    year: int = Depends(get_year_from_header)
) -> Session:
    """
    Dependency pour obtenir une session de base de données en fonction de l'année
    """
    # Créer une session pour l'année spécifiée
    session_maker = database_config.get_session_maker(year)
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Inclure les routeurs
app.include_router(composantes.router)
app.include_router(etapes.router)
app.include_router(ecues.router)
app.include_router(rattachements.router)


# Endpoint racine
@app.get("/", tags=["general"])
async def root():
    """Endpoint racine"""
    return {
        "message": "Bienvenue sur l'API Maquettes",
        "documentation": "/docs",
        "health_check": "/health"
    }


# Health check
@app.get("/health", tags=["general"])
async def health_check():
    """Vérifie l'état de santé de l'API"""
    available_years = database_config.get_available_years()
    return {
        "status": "healthy",
        "available_years": available_years,
        "message": f"API fonctionnelle avec {len(available_years)} année(s) disponible(s)"
    }


# Endpoint pour lister les années disponibles
@app.get("/years", tags=["general"])
async def get_available_years():
    """Liste les années de maquettes disponibles"""
    available_years = database_config.get_available_years()
    return {
        "available_years": available_years,
        "count": len(available_years)
    }


# Gestion des erreurs globales
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal Server Error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Une erreur interne est survenue"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
