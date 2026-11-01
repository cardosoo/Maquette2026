#!/usr/bin/env python3
"""
Import RH : charge les MSD et les fonctions du référentiel (REF)
à partir de données collées (TSV copié depuis une page web DataTables).

Formats acceptés (autodétecté) :

  MSD  : Code  Libelle  Multiplicateur  Pas d'heures complémentaires
  REF  : Code  Libelle  Libelle court  Domaine Fonctionnel  Structure  Formation à préciser  Peut dans serv.

Usage :
    venv/bin/python scripts/import_rh.py msd     < donnees_msd.tsv
    venv/bin/python scripts/import_rh.py ref     < donnees_ref.tsv
    venv/bin/python scripts/import_rh.py msd fichier.tsv
    venv/bin/python scripts/import_rh.py ref fichier.tsv

L'année cible est passée en option (--annee, défaut 2026) : les lignes sont
stockées dans la base unique maquette_rh avec cette valeur dans la colonne
`annee`, et les lignes existantes de la même année sont mises à jour.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session  # noqa: E402
from app.config.database import database_config  # noqa: E402
from app.models.msd import MSD  # noqa: E402
from app.models.fonction import FonctionRef  # noqa: E402


def parse_bool(cell: str) -> bool:
    """Interprète une cellule booléenne ('Oui', 'oui', 'x', '1', '', ...)"""
    cell = (cell or "").strip().lower()
    return cell in ("oui", "x", "true", "1", "vrai", "yes")


def parse_tsv(text: str):
    """Découpe un texte collé en lignes de cellules (tabulations ou multi-espaces)."""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "\t" in line:
            cells = [c.strip() for c in line.split("\t")]
        else:
            cells = [c.strip() for c in line.split("  ") if c.strip()]
        if cells and cells[0].lower() in ("code",):
            continue  # ligne d'en-tête
        yield cells


def upsert_msd(db: Session, rows, annee: int) -> int:
    count = 0
    for cells in rows:
        code, libelle = cells[0], cells[1]
        multiplicateur = int(cells[2]) if len(cells) > 2 and cells[2] else -1
        pas_hc = parse_bool(cells[3]) if len(cells) > 3 else False
        existing = db.query(MSD).filter(MSD.code == code, MSD.annee == annee).first()
        if existing:
            existing.libelle = libelle
            existing.multiplicateur = multiplicateur
            existing.pas_heures_complementaires = pas_hc
        else:
            db.add(MSD(code=code, libelle=libelle,
                       multiplicateur=multiplicateur,
                       pas_heures_complementaires=pas_hc,
                       annee=annee))
        count += 1
    db.commit()
    return count


def upsert_fonction_ref(db: Session, rows, annee: int) -> int:
    count = 0
    for cells in rows:
        code, libelle = cells[0], cells[1]
        libelle_court = cells[2] if len(cells) > 2 and cells[2] else None
        domaine = cells[3] if len(cells) > 3 and cells[3] else None
        structure = cells[4] if len(cells) > 4 and cells[4] else None
        formation_a_preciser = parse_bool(cells[5]) if len(cells) > 5 else False
        peut_dans_serv = parse_bool(cells[6]) if len(cells) > 6 else False
        existing = db.query(FonctionRef).filter(FonctionRef.code == code, FonctionRef.annee == annee).first()
        if existing:
            existing.libelle = libelle
            existing.libelle_court = libelle_court
            existing.domaine_fonctionnel = domaine
            existing.structure = structure
            existing.formation_a_preciser = formation_a_preciser
            existing.peut_dans_serv = peut_dans_serv
        else:
            db.add(FonctionRef(code=code, libelle=libelle,
                               libelle_court=libelle_court,
                               domaine_fonctionnel=domaine,
                               structure=structure,
                               formation_a_preciser=formation_a_preciser,
                               peut_dans_serv=peut_dans_serv,
                               annee=annee))
        count += 1
    db.commit()
    return count


def main():
    parser = argparse.ArgumentParser(description="Import RH (MSD / REF)")
    parser.add_argument("type", choices=["msd", "ref"], help="Type de données à importer")
    parser.add_argument("fichier", nargs="?", help="Fichier TSV (sinon stdin)")
    parser.add_argument("--annee", type=int, default=2026, help="Année cible (colonne annee de maquette_rh)")
    args = parser.parse_args()

    text = Path(args.fichier).read_text(encoding="utf-8") if args.fichier else sys.stdin.read()
    if not text.strip():
        print("Aucune donnée à importer", file=sys.stderr)
        sys.exit(1)

    engine = database_config.get_engine()
    db = Session(bind=engine)
    try:
        rows = list(parse_tsv(text))
        if args.type == "msd":
            n = upsert_msd(db, rows, args.annee)
        else:
            n = upsert_fonction_ref(db, rows, args.annee)
        print(f"{n} ligne(s) importée(s) pour l'année {args.annee} dans maquette_rh")
    finally:
        db.close()


if __name__ == "__main__":
    main()
