"""
Configuration de la base de données PostgreSQL
Gère les connexions aux bases annualisées (maquettes2024, maquettes2025, maquettes2026, etc.)
"""

from typing import Optional, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from contextlib import contextmanager

# Configuration de base
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")

Base = declarative_base()

class DatabaseConfig:
    """Gère les connexions aux différentes bases de données annualisées"""
    
    def __init__(self):
        self._engines = {}
        self._session_makers = {}
    
    def get_engine(self, year: int) -> create_engine:
        """
        Retourne un engine SQLAlchemy pour l'année spécifiée
        
        Args:
            year: Année de la maquette (ex: 2024, 2025, 2026)
        
        Returns:
            Engine SQLAlchemy
        """
        if year not in self._engines:
            db_name = f"maquettes{year}"
            connection_string = (
                f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@"
                f"{DATABASE_HOST}:{DATABASE_PORT}/{db_name}"
            )
            self._engines[year] = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False  # Mettre à True pour le débogage
            )
        return self._engines[year]
    
    def get_session_maker(self, year: int) -> sessionmaker:
        """
        Retourne un SessionMaker pour l'année spécifiée
        
        Args:
            year: Année de la maquette
        
        Returns:
            SessionMaker SQLAlchemy
        """
        if year not in self._session_makers:
            engine = self.get_engine(year)
            self._session_makers[year] = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        return self._session_makers[year]
    
    @contextmanager
    def get_session(self, year: int) -> Generator[Session, None, None]:
        """
        Contexte pour obtenir une session de base de données
        
        Args:
            year: Année de la maquette
        
        Yields:
            Session SQLAlchemy
        """
        session_maker = self.get_session_maker(year)
        session = session_maker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_available_years(self) -> list:
        """
        Retourne la liste des années disponibles (à implémenter selon votre environnement)
        Pour l'instant, retourne une liste par défaut
        """
        # Cela pourrait être implémenté pour interroger PostgreSQL
        # pour lister les bases de données disponibles
        return [2024, 2025, 2026]

# Instance globale de la configuration de la base de données
database_config = DatabaseConfig()

# Fonction utilitaire pour obtenir une session rapidement
def get_db_session(year: int) -> Generator[Session, None, None]:
    """
    Générateur de session pour une année donnée (utilisé par FastAPI Dependency Injection)
    """
    with database_config.get_session(year) as session:
        yield session
