"""
Service pour la gestion des fonctions du référentiel (RH)
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.models.fonction import FonctionRef
from app.schemas.rh import FonctionRefCreate


class FonctionService:
    """Logique métier pour les fonctions du référentiel"""

    def __init__(self, db: Session, year: int):
        self.db = db
        self.year = year

    def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[FonctionRef], int]:
        query = self.db.query(FonctionRef).filter(FonctionRef.annee == self.year).order_by(FonctionRef.code)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, data: FonctionRefCreate) -> FonctionRef:
        fonction = FonctionRef(**data.model_dump(), annee=self.year)
        self.db.add(fonction)
        self.db.commit()
        self.db.refresh(fonction)
        return fonction
