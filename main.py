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

from fastapi import FastAPI, Depends, HTTPException, status, Query, Header, Request
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
from app.routers import composantes, etapes, ecues, rattachements, frontend, msd, fonctions
from app.config.database import database_config
from app.config.settings import get_settings
from app.config.dependencies import get_db_session, get_db_session_with_payload, payload_middleware

# Création de l'application FastAPI
app = FastAPI(
    title="Maquettes API",
    description="API pour la gestion des maquettes d'enseignement universitaire",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_extra={
        "components": {
            "securitySchemes": {
                "X-Payload": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-Payload",
                    "description": "Code payload pour autorisation"
                }
            }
        },
        "security": [
            {"X-Payload": []}
        ]
    }
)

# Configuration CORS (inclut les headers personnalisés)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["X-Maquette-Year", "X-Payload"]
)

# Middleware pour vérifier le payload
app.middleware("http")(payload_middleware)

# Route pour le favicon
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Servir les fichiers statiques (favicon.ico, etc.)
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Route pour favicon.ico à la racine (avec fallback)
@app.get("/favicon.ico")
async def get_favicon():
    """Retourne le favicon s'il existe dans le dossier static, sinon une réponse vide"""
    favicon_path = static_path / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/x-icon")
    # Retourner un favicon vide (évite le 404)
    return Response(content=b"", media_type="image/x-icon")

from fastapi.responses import FileResponse, Response


# Inclure les routeurs
app.include_router(composantes.router)
app.include_router(etapes.router)
app.include_router(ecues.router)
app.include_router(rattachements.router)
app.include_router(frontend.router)
app.include_router(msd.router)
app.include_router(fonctions.router)


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
    settings = get_settings()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.APP_PORT,
        reload=settings.DEBUG or settings.UVICORN_RELOAD
    )
