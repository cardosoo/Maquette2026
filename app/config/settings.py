"""
Configuration des paramètres de l'application
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional
from functools import lru_cache
import json


class Settings(BaseSettings):
    """Paramètres de configuration de l'application"""
    
    # Configuration de la base de données
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    
    # Années disponibles
    AVAILABLE_YEARS: List[int] = [2024, 2025, 2026]
    DEFAULT_YEAR: int = 2026
    
    # Configuration FastAPI
    APP_NAME: str = "Maquettes API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    APP_PORT: int = 8000
    UVICORN_RELOAD: bool = False
    
    # Payloads autorisés (liste de codes UUID)
    PAYLOAD: Optional[List[str]] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 1000
    
    @field_validator('PAYLOAD', mode='before')
    @classmethod
    def parse_payload(cls, v):
        """Parse le champ PAYLOAD depuis une chaîne JSON"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Si ce n'est pas du JSON, essayer de splitter par virgule
                return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache()
def get_settings() -> Settings:
    """Retourne une instance des paramètres de configuration (mise en cache)"""
    return Settings()
