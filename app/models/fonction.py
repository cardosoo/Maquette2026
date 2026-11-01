from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint

from app.config.database import Base


class FonctionRef(Base):
    """Fonction du référentiel RH"""
    __tablename__ = "fonction_ref"
    __table_args__ = (UniqueConstraint('code', 'annee', name='uq_fonction_ref_code_annee'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    annee = Column(Integer, nullable=False, index=True)
    code = Column(String(128), nullable=False, index=True)
    libelle = Column(String(255), nullable=False)
    libelle_court = Column(String(255))
    domaine_fonctionnel = Column(String(128))
    structure = Column(String(255))
    formation_a_preciser = Column(Boolean, nullable=False, default=False)
    peut_dans_serv = Column(Boolean, nullable=False, default=False)
