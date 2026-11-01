"""
Modèles SQLAlchemy pour les MSD (Modifications de Service Dû)
Table annualisée : une table msd par base (maquettes2024, maquettes2025, maquettes2026)

Colonnes issues de la page web (DataTables) :
- Code : identifiant (ex: AMENAG)
- Libelle : libellé complet
- Multiplicateur : entier
- Pas d'heures complémentaires : booléen (icône check/xmark)
"""

from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint
from app.config.database import Base


class MSD(Base):
    """Modification de Service Dû (RH)"""
    __tablename__ = "msd"

    __table_args__ = (UniqueConstraint('code', 'annee', name='uq_msd_code_annee'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    annee = Column(Integer, nullable=False, index=True)
    code = Column(String(128), nullable=False, index=True)
    libelle = Column(String(255), nullable=False)
    multiplicateur = Column(Integer, nullable=False, default=-1)
    pas_heures_complementaires = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<MSD(id={self.id}, code='{self.code}', libelle='{self.libelle}')>"
