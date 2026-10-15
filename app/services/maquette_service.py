"""
Service pour la gestion des données de maquettes
Contient la logique métier pour les opérations CRUD et les requêtes complexes
"""

from typing import Optional, List, Tuple, cast
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from app.models.maquette import Composante, Etape, ECUE, ECUE_Etape
from app.schemas.maquette import (
    ComposanteCreate, ComposanteUpdate,
    EtapeCreate, EtapeUpdate,
    ECUECreate, ECUEUpdate,
    ECUEEtapeCreate, ECUEEtapeUpdate
)
from fastapi import HTTPException, status


class MaquetteService:
    """Service principal pour la gestion des maquettes"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # ==================== COMPOSANTE OPERATIONS ====================
    
    def get_composante_by_id(self, composante_id: int) -> Optional[Composante]:
        """Récupère une composante par son ID"""
        return self.db.query(Composante).filter(Composante.id == composante_id).first()
    
    def get_composante_by_code(self, code: str) -> Optional[Composante]:
        """Récupère une composante par son code"""
        return self.db.query(Composante).filter(Composante.code == code).first()
    
    def get_all_composantes(self, skip: int = 0, limit: int = 100) -> Tuple[List[Composante], int]:
        """Récupère toutes les composantes avec pagination"""
        query = self.db.query(Composante)
        total = query.count()
        composantes = query.offset(skip).limit(limit).all()
        return composantes, total
    
    def search_composantes(self, code: Optional[str] = None,
                           skip: int = 0, limit: int = 100) -> Tuple[List[Composante], int]:
        """Recherche des composantes avec filtre par code"""
        query = self.db.query(Composante)
        
        if code:
            query = query.filter(Composante.code == code)
        
        total = query.count()
        composantes = query.offset(skip).limit(limit).all()
        return composantes, total
    
    def create_composante(self, composante_data: ComposanteCreate) -> Composante:
        """Crée une nouvelle composante"""
        # Vérifier si le code existe déjà
        existing = self.db.query(Composante).filter(
            Composante.code == composante_data.code
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Une composante avec le code '{composante_data.code}' existe déjà"
            )

        # Vérifier si le nom existe déjà
        existing = self.db.query(Composante).filter(
            Composante.nom == composante_data.nom
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Une composante avec le nom '{composante_data.nom}' existe déjà"
            )
        
        composante = Composante(**composante_data.model_dump())
        self.db.add(composante)
        self.db.commit()
        self.db.refresh(composante)
        return composante
    
    def update_composante(self, composante_id: int, composante_data: ComposanteUpdate) -> Optional[Composante]:
        """Met à jour une composante existante"""
        composante = self.get_composante_by_id(composante_id)
        if not composante:
            return None
        
        for key, value in composante_data.model_dump(exclude_unset=True).items():
            setattr(composante, key, value)
        
        self.db.commit()
        self.db.refresh(composante)
        return composante
    
    def delete_composante(self, composante_id: int) -> bool:
        """Supprime une composante (et ses étapes et ECUE associées en cascade)"""
        composante = self.get_composante_by_id(composante_id)
        if not composante:
            return False
        
        self.db.delete(composante)
        self.db.commit()
        return True
    
    # ==================== ETAPE OPERATIONS ====================
    
    def get_etape_by_id(self, etape_id: int) -> Optional[Etape]:
        """Récupère une étape par son ID"""
        return self.db.query(Etape).filter(Etape.id == etape_id).first()
    
    def get_etape_by_code(self, code: str) -> Optional[Etape]:
        """Récupère une étape par son code"""
        return self.db.query(Etape).filter(Etape.code == code).first()
    
    def get_etapes_by_composante(self, composante_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Etape], int]:
        """Récupère toutes les étapes d'une composante avec pagination"""
        query = self.db.query(Etape).filter(Etape.composante_id == composante_id)
        total = query.count()
        etapes = query.offset(skip).limit(limit).all()
        return etapes, total
    
    def get_all_etapes(self, skip: int = 0, limit: int = 100) -> Tuple[List[Etape], int]:
        """Récupère toutes les étapes avec pagination"""
        query = self.db.query(Etape)
        total = query.count()
        etapes = query.offset(skip).limit(limit).all()
        return etapes, total
    
    def create_etape(self, etape_data: EtapeCreate) -> Etape:
        """Crée une nouvelle étape"""
        # Vérifier si le code existe déjà
        existing = self.db.query(Etape).filter(
            Etape.code == etape_data.code
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Une étape avec le code '{etape_data.code}' existe déjà"
            )
        
        # Vérifier que la composante existe
        composante = self.get_composante_by_id(etape_data.composante_id)
        if not composante:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La composante avec l'ID {etape_data.composante_id} n'existe pas"
            )
        
        etape = Etape(**etape_data.model_dump())
        self.db.add(etape)
        self.db.commit()
        self.db.refresh(etape)
        return etape
    
    def update_etape(self, etape_id: int, etape_data: EtapeUpdate) -> Optional[Etape]:
        """Met à jour une étape existante"""
        etape = self.get_etape_by_id(etape_id)
        if not etape:
            return None
        
        # Vérifier que la nouvelle composante existe si elle est modifiée
        if etape_data.composante_id and etape.composante_id != etape_data.composante_id:
            composante = self.get_composante_by_id(etape_data.composante_id)
            if not composante:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La composante avec l'ID {etape_data.composante_id} n'existe pas"
                )
        
        for key, value in etape_data.model_dump(exclude_unset=True).items():
            setattr(etape, key, value)
        
        self.db.commit()
        self.db.refresh(etape)
        return etape
    
    def delete_etape(self, etape_id: int) -> bool:
        """Supprime une étape (et ses ECUE associées en cascade)"""
        etape = self.get_etape_by_id(etape_id)
        if not etape:
            return False
        
        self.db.delete(etape)
        self.db.commit()
        return True
    
    # ==================== ECUE OPERATIONS ====================
    
    def get_ecue_by_id(self, ecue_id: int) -> Optional[ECUE]:
        """Récupère une ECUE par son ID"""
        return self.db.query(ECUE).filter(ECUE.id == ecue_id).first()
    
    def get_ecue_by_code(self, code: str) -> Optional[ECUE]:
        """Récupère une ECUE par son code"""
        return self.db.query(ECUE).filter(ECUE.code == code).first()
    
    def get_ecues_by_etape(self, etape_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[ECUE], int]:
        """Récupère toutes les ECUE d'une étape avec pagination"""
        query = self.db.query(ECUE).filter(ECUE.etape_id == etape_id)
        total = query.count()
        ecues = query.offset(skip).limit(limit).all()
        return ecues, total
    
    def get_all_ecues(self, skip: int = 0, limit: int = 100) -> Tuple[List[ECUE], int]:
        """Récupère toutes les ECUE avec pagination"""
        query = self.db.query(ECUE)
        total = query.count()
        ecues = query.offset(skip).limit(limit).all()
        return ecues, total
    
    def create_ecue(self, ecue_data: ECUECreate) -> ECUE:
        """Crée une nouvelle ECUE"""
        # Vérifier si le code existe déjà
        existing = self.db.query(ECUE).filter(
            ECUE.code == ecue_data.code
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Une ECUE avec le code '{ecue_data.code}' existe déjà"
            )
        
        # Vérifier que l'étape existe
        etape = self.get_etape_by_id(ecue_data.etape_id)
        if not etape:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"L'étape avec l'ID {ecue_data.etape_id} n'existe pas"
            )
        
        ecue = ECUE(**ecue_data.model_dump())
        self.db.add(ecue)
        self.db.commit()
        self.db.refresh(ecue)
        return ecue
    
    def update_ecue(self, ecue_id: int, ecue_data: ECUEUpdate) -> Optional[ECUE]:
        """Met à jour une ECUE existante"""
        ecue = self.get_ecue_by_id(ecue_id)
        if not ecue:
            return None
        
        # Vérifier que la nouvelle étape existe si elle est modifiée
        if ecue_data.etape_id and ecue.etape_id != ecue_data.etape_id:
            etape = self.get_etape_by_id(ecue_data.etape_id)
            if not etape:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"L'étape avec l'ID {ecue_data.etape_id} n'existe pas"
                )
        
        for key, value in ecue_data.model_dump(exclude_unset=True).items():
            setattr(ecue, key, value)
        
        self.db.commit()
        self.db.refresh(ecue)
        return ecue
    
    def delete_ecue(self, ecue_id: int) -> bool:
        """Supprime une ECUE (et ses rattachements en cascade)"""
        ecue = self.get_ecue_by_id(ecue_id)
        if not ecue:
            return False
        
        self.db.delete(ecue)
        self.db.commit()
        return True
    
    # ==================== ECUE_ETAPE OPERATIONS ====================
    
    def get_ecue_etape_by_id(self, rattachement_id: int) -> Optional[ECUE_Etape]:
        """Récupère un rattachement ECUE-Étape par son ID"""
        return self.db.query(ECUE_Etape).filter(ECUE_Etape.id == rattachement_id).first()
    
    def get_ecue_etapes_by_ecue(self, ecue_id: int) -> List[ECUE_Etape]:
        """Récupère tous les rattachements d'une ECUE"""
        return self.db.query(ECUE_Etape).filter(
            ECUE_Etape.ecue_id == ecue_id
        ).all()
    
    def get_ecue_etapes_by_etape(self, etape_id: int) -> List[ECUE_Etape]:
        """Récupère tous les rattachements d'une étape"""
        return self.db.query(ECUE_Etape).filter(
            ECUE_Etape.etape_id == etape_id
        ).all()
    
    def create_ecue_etape(self, rattachement_data: ECUEEtapeCreate) -> ECUE_Etape:
        """Crée un nouveau rattachement ECUE-Étape"""
        # Vérifier que l'ECUE existe
        ecue = self.get_ecue_by_id(rattachement_data.ecue_id)
        if not ecue:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"L'ECUE avec l'ID {rattachement_data.ecue_id} n'existe pas"
            )
        
        # Vérifier que l'étape existe
        etape = self.get_etape_by_id(rattachement_data.etape_id)
        if not etape:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"L'étape avec l'ID {rattachement_data.etape_id} n'existe pas"
            )
        
        # Vérifier si le rattachement existe déjà
        existing = self.db.query(ECUE_Etape).filter(
            and_(
                ECUE_Etape.ecue_id == rattachement_data.ecue_id,
                ECUE_Etape.etape_id == rattachement_data.etape_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le rattachement entre ECUE {rattachement_data.ecue_id} et étape {rattachement_data.etape_id} existe déjà"
            )
        
        rattachement = ECUE_Etape(**rattachement_data.model_dump())
        self.db.add(rattachement)
        self.db.commit()
        self.db.refresh(rattachement)
        return rattachement
    
    def delete_ecue_etape(self, rattachement_id: int) -> bool:
        """Supprime un rattachement ECUE-Étape"""
        rattachement = self.get_ecue_etape_by_id(rattachement_id)
        if not rattachement:
            return False
        
        self.db.delete(rattachement)
        self.db.commit()
        return True
    
    # ==================== COMPLEX QUERIES ====================
    
    def get_etapes_by_composante_with_ecues(self, composante_id: int) -> List[Etape]:
        """
        Récupère toutes les étapes d'une composante avec leurs ECUE associées
        """
        return self.db.query(Etape).filter(
            Etape.composante_id == composante_id
        ).options(
            # Chargement eager des relations
        ).all()
    
    def get_ecue_rattachements(self, ecue_id: int) -> dict:
        """
        Récupère tous les rattachements d'une ECUE
        Retourne un dictionnaire avec:
        - etape_principale: l'étape principale (etape_id de l'ECUE)
        - autres_etapes: liste des autres étapes via ecue_etape
        """
        ecue = self.get_ecue_by_id(ecue_id)
        if not ecue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ECUE avec l'ID {ecue_id} non trouvée"
            )
        
        # L'étape principale est celle dans le champ etape_id de l'ECUE
        etape_principale = self.get_etape_by_id(cast(int, ecue.etape_id))
        
        # Les autres étapes sont dans la table ecue_etape
        autres_etapes = []
        rattachements = self.get_ecue_etapes_by_ecue(ecue_id)
        for rattachement in rattachements:
            etape = self.get_etape_by_id(cast(int, rattachement.etape_id))
            if etape and etape.id != ecue.etape_id:  # Exclure l'étape principale
                autres_etapes.append(etape)
        
        return {
            "ecue": ecue,
            "etape_principale": etape_principale,
            "autres_etapes": autres_etapes
        }
    
    def get_etapes_by_ecue(self, ecue_id: int) -> List[Etape]:
        """
        Récupère toutes les étapes auxquelles une ECUE est rattachée
        (y compris l'étape principale)
        """
        ecue = self.get_ecue_by_id(ecue_id)
        if not ecue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ECUE avec l'ID {ecue_id} non trouvée"
            )
        
        etapes = []
        
        # Ajouter l'étape principale
        etape_principale = self.get_etape_by_id(cast(int, ecue.etape_id))
        if etape_principale:
            etapes.append(etape_principale)
        
        # Ajouter les étapes de la table ecue_etape
        rattachements = self.get_ecue_etapes_by_ecue(ecue_id)
        for rattachement in rattachements:
            etape = self.get_etape_by_id(cast(int, rattachement.etape_id))
            if etape and etape.id != ecue.etape_id:
                etapes.append(etape)
        
        return etapes
    
    def search_etapes(self, composante_id: Optional[int] = None, 
                     niveau: Optional[str] = None,
                     domaine: Optional[str] = None,
                     type: Optional[str] = None,
                     code: Optional[str] = None,
                     skip: int = 0, limit: int = 100) -> Tuple[List[Etape], int]:
        """
        Recherche des étapes avec filtres
        """
        query = self.db.query(Etape)
        
        if composante_id:
            query = query.filter(Etape.composante_id == composante_id)
        if niveau:
            query = query.filter(Etape.niveau == niveau)
        if domaine:
            query = query.filter(Etape.domaine == domaine)
        if type:
            query = query.filter(Etape.type == type)
        if code:
            query = query.filter(Etape.code == code)
        
        total = query.count()
        etapes = query.offset(skip).limit(limit).all()
        return etapes, total
    
    def search_ecues(self, etape_id: Optional[int] = None,
                    periode: Optional[str] = None,
                    code: Optional[str] = None,
                    nom: Optional[str] = None,
                    skip: int = 0, limit: int = 100) -> Tuple[List[ECUE], int]:
        """
        Recherche des ECUE avec filtres
        """
        query = self.db.query(ECUE)
        
        if etape_id:
            query = query.filter(ECUE.etape_id == etape_id)
        if periode:
            query = query.filter(ECUE.periode == periode)
        if code:
            query = query.filter(ECUE.code.ilike(f"%{code}%"))
        if nom:
            query = query.filter(ECUE.nom.ilike(f"%{nom}%"))
        
        total = query.count()
        ecues = query.offset(skip).limit(limit).all()
        return ecues, total
