"""
Schéma Pydantic pour la validation et la sérialisation des données
"""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

T = TypeVar('T')


# Schémas pour Composante
class ComposanteBase(BaseModel):
    nom: str = Field(..., max_length=255, description="Nom de la composante")
    code: str = Field(..., max_length=128, description="Code unique de la composante (code OSE de la structure)")


class ComposanteCreate(ComposanteBase):
    pass


class ComposanteUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=255, description="Nom de la composante")
    code: Optional[str] = Field(None, max_length=128, description="Code unique de la composante")


class ComposanteResponse(ComposanteBase):
    id: int = Field(..., description="Identifiant unique de la composante")
    annee: int = Field(..., description="Année de la maquette")
    
    model_config = ConfigDict(from_attributes=True)


# Schémas pour Etape
class EtapeBase(BaseModel):
    nom: str = Field(..., max_length=128, description="Nom de l'étape")
    code: str = Field(..., max_length=128, description="Code de l'étape")
    type: str = Field(..., max_length=128, description="Type de l'étape (L1, L2, etc.)")
    niveau: str = Field(..., max_length=128, description="Niveau (Licence, Master, etc.)")
    domaine: str = Field(..., max_length=128, description="Domaine (Sciences, Lettres, etc.)")
    effectif: int = Field(..., description="Effectif de l'étape")


class EtapeCreate(EtapeBase):
    composante_id: int = Field(..., description="ID de la composante associée")


class EtapeUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=128)
    code: Optional[str] = Field(None, max_length=128)
    type: Optional[str] = Field(None, max_length=128)
    niveau: Optional[str] = Field(None, max_length=128)
    domaine: Optional[str] = Field(None, max_length=128)
    effectif: Optional[int] = None
    composante_id: Optional[int] = None


class EtapeResponse(EtapeBase):
    id: int = Field(..., description="Identifiant unique de l'étape")
    annee: int = Field(..., description="Année de la maquette")
    composante_id: int = Field(..., description="ID de la composante")
    
    model_config = ConfigDict(from_attributes=True)


class EtapeWithComposanteResponse(EtapeResponse):
    composante: ComposanteResponse = Field(..., description="Composante associée")


# Schémas pour ECUE
class ECUEBase(BaseModel):
    nom: str = Field(..., max_length=128, description="Nom de l'ECUE")
    code: str = Field(..., max_length=128, description="Code de l'ECUE")
    periode: str = Field(..., max_length=128, description="Période (S1, S2, etc.)")
    effectif: int = Field(..., description="Effectif de l'ECUE")
    besoins: Dict[str, Any] = Field(default_factory=dict, description="Besoins spécifiques (JSON)")


class ECUECreate(ECUEBase):
    etape_id: int = Field(..., description="ID de l'étape principale")


class ECUEUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=128)
    code: Optional[str] = Field(None, max_length=128)
    periode: Optional[str] = Field(None, max_length=128)
    effectif: Optional[int] = None
    besoins: Optional[Dict[str, Any]] = None
    etape_id: Optional[int] = None


class ECUEResponse(ECUEBase):
    id: int = Field(..., description="Identifiant unique de l'ECUE")
    annee: int = Field(..., description="Année de la maquette")
    etape_id: int = Field(..., description="ID de l'étape principale")
    
    model_config = ConfigDict(from_attributes=True)


class ECUEWithEtapeResponse(ECUEResponse):
    etape: EtapeResponse = Field(..., description="Étape principale associée")


# Schémas pour ECUE_Etape (rattachement)
class ECUEEtapeBase(BaseModel):
    ecue_id: int = Field(..., description="ID de l'ECUE")
    etape_id: int = Field(..., description="ID de l'étape")
    effectif: int = Field(..., description="Effectif pour ce rattachement")


class ECUEEtapeCreate(ECUEEtapeBase):
    pass


class ECUEEtapeUpdate(BaseModel):
    effectif: Optional[int] = None


class ECUEEtapeResponse(ECUEEtapeBase):
    id: int = Field(..., description="Identifiant unique du rattachement")
    annee: int = Field(..., description="Année de la maquette")
    
    model_config = ConfigDict(from_attributes=True)


class ECUEEtapeWithDetailsResponse(ECUEEtapeResponse):
    ecue: ECUEResponse = Field(..., description="ECUE associée")
    etape: EtapeResponse = Field(..., description="Étape associée")


# Schémas pour les rattachements d'une ECUE
class ECUERattachementResponse(BaseModel):
    """Schéma pour les informations de rattachement d'une ECUE"""
    ecue: ECUEResponse = Field(..., description="ECUE")
    etape_principale: EtapeResponse = Field(..., description="Étape principale")
    autres_etapes: List[EtapeResponse] = Field(default_factory=list, description="Autres étapes de rattachement")


# Schémas pour les listes et réponses paginées
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(..., description="Liste des éléments")
    total: int = Field(..., description="Nombre total d'éléments")
    page: int = Field(..., description="Numéro de la page")
    page_size: int = Field(..., description="Taille de la page")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Message d'erreur")
