"""
Configuration de la base de données PostgreSQL unique (maquette_rh)

Toutes les données (structure des enseignements, MSD, fonctions du référentiel)
vivent dans une seule base, annualisées par une colonne `annee`.
"""

from typing import Optional, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.engine import Engine
import os
from contextlib import contextmanager
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Configuration de base
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")
DATABASE_NAME = os.getenv("DATABASE_NAME", "maquette_rh")

Base = declarative_base()

class DatabaseConfig:
    """Gère la connexion à la base unique maquette_rh"""

    def __init__(self):
        self._engine: Optional[Engine] = None
        self._session_maker: Optional[sessionmaker] = None

    def get_engine(self) -> Engine:
        """Retourne l'engine SQLAlchemy de la base unique"""
        if self._engine is None:
            connection_string = (
                f"postgresql+psycopg://{DATABASE_USER}:{DATABASE_PASSWORD}@"
                f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
            )
            self._engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False  # Mettre à True pour le débogage
            )
        return self._engine

    def get_session_maker(self) -> sessionmaker:
        """Retourne le SessionMaker de la base unique"""
        if self._session_maker is None:
            self._session_maker = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.get_engine()
            )
        return self._session_maker

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Contexte pour obtenir une session de base de données"""
        session = self.get_session_maker()()
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
        Retourne la liste des années disponibles.
        Les données sont distinguées par la colonne `annee`, pas par la base.
        """
        # À terme, pourrait interroger la table pour lister les années présentes
        return [2024, 2025, 2026]

# Instance globale de la configuration de la base de données
database_config = DatabaseConfig()

# Fonction utilitaire pour obtenir une session rapidement
def get_db_session() -> Generator[Session, None, None]:
    """
    Générateur de session (utilisé par FastAPI Dependency Injection)
    """
    with database_config.get_session() as session:
        yield session
