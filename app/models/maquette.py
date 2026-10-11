"""
Modèles SQLAlchemy pour les tables de la base de données
"""

from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.config.database import Base


class Composante(Base):
    """
    Modèle pour la table composante
    Représente une composante (faculté, département, etc.)
    """
    __tablename__ = "composante"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(255), nullable=False)
    
    # Relations
    etapes = relationship("Etape", back_populates="composante", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Composante(id={self.id}, nom='{self.nom}')>"


class Etape(Base):
    """
    Modèle pour la table etape
    Représente une étape (année d'étude, semestre, etc.)
    """
    __tablename__ = "etape"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(128), nullable=False)
    code = Column(String(128), nullable=False, index=True)
    type = Column(String(128), nullable=False)  # type: L1, L2, L3, M1, M2, etc.
    niveau = Column(String(128), nullable=False)  # niveau: Licence, Master, Doctorat
    domaine = Column(String(128), nullable=False)  # domaine: Sciences, Lettres, etc.
    effectif = Column(Integer, nullable=False, default=0)
    composante_id = Column(Integer, ForeignKey('composante.id'), nullable=False)
    
    # Relations
    composante = relationship("Composante", back_populates="etapes")
    ecues = relationship("ECUE", back_populates="etape", cascade="all, delete-orphan")
    ecue_etapes = relationship("ECUE_Etape", back_populates="etape", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Etape(id={self.id}, code='{self.code}', nom='{self.nom}')>"


class ECUE(Base):
    """
    Modèle pour la table ecue
    Représente une Unité d'Enseignement (ECUE)
    """
    __tablename__ = "ecue"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String(128), nullable=False)
    code = Column(String(128), nullable=False, index=True)
    periode = Column(String(128), nullable=False)  # S1, S2, etc.
    etape_id = Column(Integer, ForeignKey('etape.id'), nullable=False)
    effectif = Column(Integer, nullable=False, default=0)
    besoins = Column(JSON, nullable=False, default={})  # Champ JSON pour les besoins spécifiques
    
    # Relations
    etape = relationship("Etape", back_populates="ecues")
    ecue_etapes = relationship("ECUE_Etape", back_populates="ecue", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ECUE(id={self.id}, code='{self.code}', nom='{self.nom}')>"


class ECUE_Etape(Base):
    """
    Modèle pour la table ecue_etape (table de jointure)
    Représente le rattachement d'une ECUE à une étape
    """
    __tablename__ = "ecue_etape"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ecue_id = Column(Integer, ForeignKey('ecue.id'), nullable=False)
    etape_id = Column(Integer, ForeignKey('etape.id'), nullable=False)
    effectif = Column(Integer, nullable=False, default=0)
    
    # Relations
    ecue = relationship("ECUE", back_populates="ecue_etapes")
    etape = relationship("Etape", back_populates="ecue_etapes")
    
    def __repr__(self):
        return f"<ECUE_Etape(id={self.id}, ecue_id={self.ecue_id}, etape_id={self.etape_id})>"
