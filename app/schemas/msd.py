"""
Schémas Pydantic pour les MSD (Modifications de Service Dû)
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MSDBase(BaseModel):
    code: str = Field(..., max_length=128, description="Code unique de la modification de service dû")
    intitule: str = Field(..., max_length=255, description="Intitulé de la modification")
    multiplicateur: float = Field(-1, description="Multiplicateur appliqué au service")
    pas_heures_complementaires: bool = Field(False, description="Exclut les heures complémentaires")


class MSDCreate(MSDBase):
    pass


class MSDUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=128)
    intitule: Optional[str] = Field(None, max_length=255)
    multiplicateur: Optional[float] = None
    pas_heures_complementaires: Optional[bool] = None


class MSDResponse(MSDBase):
    id: int = Field(..., description="Identifiant technique")

    model_config = ConfigDict(from_attributes=True)
