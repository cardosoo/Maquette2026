"""
Schémas Pydantic pour les MSD et les fonctions du référentiel (RH)
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


# ==================== MSD ====================

class MSDBase(BaseModel):
    code: str = Field(..., max_length=128, description="Code unique de la modification de service dû")
    libelle: str = Field(..., max_length=255, description="Libellé complet")
    multiplicateur: int = Field(-1, description="Multiplicateur du service dû")
    pas_heures_complementaires: bool = Field(
        False,
        description="Le dépassement du service dû ne donne pas lieu à des heures complémentaires"
    )


class MSDCreate(MSDBase):
    pass


class MSDUpdate(BaseModel):
    libelle: Optional[str] = Field(None, max_length=255)
    multiplicateur: Optional[int] = None
    pas_heures_complementaires: Optional[bool] = None


class MSDResponse(MSDBase):
    id: int = Field(..., description="Identifiant technique")

    model_config = ConfigDict(from_attributes=True)


# ==================== FONCTION REF ====================

class FonctionRefBase(BaseModel):
    code: str = Field(..., max_length=128, description="Code unique de la fonction référentielle")
    libelle: str = Field(..., max_length=255, description="Libellé complet")
    libelle_court: Optional[str] = Field(None, max_length=255, description="Libellé court")
    domaine_fonctionnel: Optional[str] = Field(None, max_length=128, description="Domaine fonctionnel")
    structure: Optional[str] = Field(None, max_length=255, description="Structure de rattachement")
    formation_a_preciser: bool = Field(False, description="La formation doit être précisée")
    peut_dans_serv: bool = Field(
        False,
        description="Les heures de cette fonction peuvent être comptées dans le service statutaire"
    )


class FonctionRefCreate(FonctionRefBase):
    pass


class FonctionRefUpdate(BaseModel):
    libelle: Optional[str] = Field(None, max_length=255)
    libelle_court: Optional[str] = Field(None, max_length=255)
    domaine_fonctionnel: Optional[str] = Field(None, max_length=128)
    structure: Optional[str] = Field(None, max_length=255)
    formation_a_preciser: Optional[bool] = None
    peut_dans_serv: Optional[bool] = None


class FonctionRefResponse(FonctionRefBase):
    id: int = Field(..., description="Identifiant technique")

    model_config = ConfigDict(from_attributes=True)
