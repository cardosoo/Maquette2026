"""
Utilitaires pour l'initialisation de la base de données
"""

import logging
from typing import Optional, List, Dict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config.database import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, Base
from app.models.maquette import Composante, Etape, ECUE, ECUE_Etape

logger = logging.getLogger(__name__)


def get_engine_for_year(year: int):
    """Crée un engine pour une année spécifique"""
    db_name = f"maquettes{year}"
    connection_string = (
        f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@"
        f"{DATABASE_HOST}:{DATABASE_PORT}/{db_name}"
    )
    return create_engine(connection_string, echo=True)


def database_exists(year: int) -> bool:
    """Vérifie si la base de données pour l'année existe"""
    try:
        # Se connecter à la base de données par défaut pour vérifier
        connection_string = (
            f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@"
            f"{DATABASE_HOST}:{DATABASE_PORT}/postgres"
        )
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            db_name = f"maquettes{year}"
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :db_name"
            ), {"db_name": db_name})
            
            return result.fetchone() is not None
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de la base de données {year}: {e}")
        return False


def create_database(year: int) -> bool:
    """Crée la base de données pour une année spécifique"""
    try:
        # Se connecter à la base de données par défaut
        connection_string = (
            f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@"
            f"{DATABASE_HOST}:{DATABASE_PORT}/postgres"
        )
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            db_name = f"maquettes{year}"
            
            # Vérifier si la base existe déjà
            result = conn.execute(text(
                "SELECT 1 FROM pg_database WHERE datname = :db_name"
            ), {"db_name": db_name})
            
            if result.fetchone():
                logger.warning(f"La base de données {db_name} existe déjà")
                return False
            
            # Créer la base de données
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            logger.info(f"Base de données {db_name} créée avec succès")
            return True
            
    except Exception as e:
        logger.error(f"Erreur lors de la création de la base de données {year}: {e}")
        return False


def init_database_tables(year: int) -> bool:
    """Initialise les tables dans la base de données pour une année spécifique"""
    try:
        engine = get_engine_for_year(year)
        
        # Créer toutes les tables
        Base.metadata.create_all(engine)
        
        logger.info(f"Tables créées avec succès pour maquettes{year}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables pour {year}: {e}")
        return False


def create_sample_data(year: int) -> bool:
    """Crée des données d'exemple pour une année spécifique"""
    try:
        engine = get_engine_for_year(year)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Vérifier si des données existent déjà
        if session.query(Composante).first():
            logger.warning(f"Des données existent déjà pour maquettes{year}")
            session.close()
            return False
        
        # Créer des composantes d'exemple
        composantes = [
            Composante(nom="Faculté des Sciences", code="SCI"),
            Composante(nom="Faculté des Lettres", code="LET"),
            Composante(nom="Faculté de Médecine", code="MED")
        ]
        
        for comp in composantes:
            session.add(comp)
        session.commit()
        
        # Créer des étapes d'exemple
        etapes = [
            Etape(
                nom="Licence 1 Informatique",
                code="L1INFO",
                type="L1",
                niveau="Licence",
                domaine="Sciences",
                effectif=100,
                composante_id=1
            ),
            Etape(
                nom="Licence 2 Informatique",
                code="L2INFO",
                type="L2",
                niveau="Licence",
                domaine="Sciences",
                effectif=80,
                composante_id=1
            ),
            Etape(
                nom="Licence 3 Mathématiques",
                code="L3MATH",
                type="L3",
                niveau="Licence",
                domaine="Sciences",
                effectif=60,
                composante_id=1
            )
        ]
        
        for etape in etapes:
            session.add(etape)
        session.commit()
        
        # Créer des ECUE d'exemple
        ecues = [
            ECUE(
                nom="Programmation 1",
                code="PROG1",
                periode="S1",
                etape_id=1,
                effectif=100,
                besoins={
                    "salles": ["A101", "A102"],
                    "equipements": ["projecteur", "tableau"],
                    "heures": 40,
                    "enseignants": ["Dupont", "Martin"]
                }
            ),
            ECUE(
                nom="Algorithmes",
                code="ALGO1",
                periode="S1",
                etape_id=1,
                effectif=100,
                besoins={
                    "salles": ["A101"],
                    "equipements": ["tableau"],
                    "heures": 30
                }
            ),
            ECUE(
                nom="Bases de données",
                code="BDD1",
                periode="S2",
                etape_id=2,
                effectif=80,
                besoins={
                    "salles": ["B201"],
                    "equipements": ["ordinateurs", "logiciel SQL"],
                    "heures": 45
                }
            )
        ]
        
        for ecue in ecues:
            session.add(ecue)
        session.commit()
        
        # Créer des rattachements d'exemple
        rattachements = [
            ECUE_Etape(ecue_id=1, etape_id=2, effectif=50),  # PROG1 aussi en L2
            ECUE_Etape(ecue_id=2, etape_id=2, effectif=80)   # ALGO1 aussi en L2
        ]
        
        for rattachement in rattachements:
            session.add(rattachement)
        session.commit()
        
        session.close()
        logger.info(f"Données d'exemple créées pour maquettes{year}")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la création des données d'exemple pour {year}: {e}")
        return False


def init_maquette_database(year: int) -> bool:
    """
    Initialise complètement une base de données de maquette pour une année
    
    - Crée la base de données si elle n'existe pas
    - Crée les tables
    - Crée des données d'exemple (optionnel)
    """
    logger.info(f"Initialisation de la base de données pour l'année {year}")
    
    # Vérifier si la base existe
    if not database_exists(year):
        logger.info(f"Création de la base de données maquettes{year}")
        if not create_database(year):
            return False
    
    # Créer les tables
    if not init_database_tables(year):
        return False
    
    # Créer les données d'exemple
    if not create_sample_data(year):
        logger.warning(f"Impossible de créer les données d'exemple pour {year}")
    
    logger.info(f"Initialisation complète pour maquettes{year}")
    return True


def init_all_databases(years: Optional[List[int]] = None) -> Dict[str, bool]:
    """
    Initialise toutes les bases de données pour les années spécifiées
    
    Args:
        years: Liste des années à initialiser. Si None, utilise [2024, 2025, 2026]
    
    Returns:
        Dictionnaire avec les résultats pour chaque année
    """
    if years is None:
        years = [2024, 2025, 2026]
    
    results = {}
    for year in years:
        results[year] = init_maquette_database(year)
    
    return results


if __name__ == "__main__":
    # Exemple d'utilisation
    import sys
    
    if len(sys.argv) > 1:
        year = int(sys.argv[1])
        success = init_maquette_database(year)
        if success:
            print(f"Base de données maquettes{year} initialisée avec succès")
        else:
            print(f"Échec de l'initialisation de maquettes{year}")
            sys.exit(1)
    else:
        # Initialiser toutes les bases par défaut
        results = init_all_databases()
        for year, success in results.items():
            if success:
                print(f"✓ maquettes{year} initialisée avec succès")
            else:
                print(f"✗ Échec de l'initialisation de maquettes{year}")
