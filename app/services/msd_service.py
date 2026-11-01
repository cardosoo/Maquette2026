"""
Service pour la gestion des MSD (Modifications de Service Dû)
et des fonctions du référentiel RH
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models.msd import MSD
from app.schemas.rh import MSDCreate, MSDUpdate, MSDResponse


class MSDService:
    """Logique métier pour les modifications de service dû (MSD)"""

    def __init__(self, db: Session, year: int):
        self.db = db
        self.year = year

    def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[MSD], int]:
        """Liste paginée des MSD"""
        query = self.db.query(MSD).filter(MSD.annee == self.year).order_by(MSD.code)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_code(self, code: str) -> Optional[MSD]:
        """Récupère un MSD par son code"""
        return self.db.query(MSD).filter(MSD.code == code, MSD.annee == self.year).first()

    def create(self, data: MSDCreate) -> MSD:
        """Crée un nouveau MSD"""
        msd = MSD(**data.model_dump(), annee=self.year)
        self.db.add(msd)
        self.db.commit()
        self.db.refresh(msd)
        return msd

    def update(self, msd_id: int, data: MSDUpdate) -> Optional[MSD]:
        """Met à jour un MSD existant (mise à jour partielle)"""
        msd = self.get_by_id(msd_id)
        if not msd:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(msd, field, value)
        self.db.commit()
        self.db.refresh(msd)
        return msd

    def delete(self, msd_id: int) -> bool:
        """Supprime un MSD"""
        msd = self.get_by_id(msd_id)
        if not msd:
            return False
        self.db.delete(msd)
        self.db.commit()
        return True
