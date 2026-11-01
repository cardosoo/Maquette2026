#!/usr/bin/env python3
"""
Migration des données : bases annualisées -> base unique maquette_rh

Copie composante / etape / ecue / ecue_etape depuis maquettes2024, maquettes2025
et maquettes2026 vers la base maquette_rh (schéma créé au préalable par
migrations/2026-10-31_creation_maquette_rh.sql), en :

- ajoutant la colonne `annee` sur chaque ligne ;
- remappant les identifiants (les IDs des anciennes bases entrent en collision
  dans la base unique : composante, etape et ecue reçoivent de nouveaux IDs et
  les clés étrangères sont réécrites).

Usage :
    venv/bin/python scripts/migrate_to_maquette_rh.py [--annees 2024,2025,2026]

Le script est relançable : il vide les tables cibles avant l'import.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, MetaData, Table, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.config.database import database_config, DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD  # noqa: E402
from app.models.maquette import Composante, Etape, ECUE, ECUE_Etape  # noqa: E402

SOURCE_PREFIX = "maquettes"


def connect_source(year: int):
    url = (
        f"postgresql+psycopg://{DATABASE_USER}:{DATABASE_PASSWORD}@"
        f"{DATABASE_HOST}:{DATABASE_PORT}/{SOURCE_PREFIX}{year}"
    )
    return create_engine(url)


def load_table(engine, name: str):
    metadata = MetaData()
    return Table(name, metadata, autoload_with=engine)


def migrate_year(source_engine, target: Session, year: int) -> dict:
    """Copie les données d'une année. Retourne un compte-rendu."""
    comp_src = load_table(source_engine, "composante")
    etape_src = load_table(source_engine, "etape")
    ecue_src = load_table(source_engine, "ecue")
    ecue_etape_src = load_table(source_engine, "ecue_etape")

    conn = source_engine.connect()

    # 1. Composantes (remappage id -> nouveau id)
    comp_map = {}
    for row in conn.execute(select(comp_src)).mappings():
        c = Composante(annee=year, nom=row["nom"], code=row["code"])
        target.add(c)
        target.flush()
        comp_map[row["id"]] = c.id

    # 2. Étapes
    etape_map = {}
    for row in conn.execute(select(etape_src)).mappings():
        e = Etape(
            annee=year,
            nom=row["nom"], code=row["code"], type=row["type"],
            niveau=row["niveau"], domaine=row["domaine"], effectif=row["effectif"],
            composante_id=comp_map[row["composante_id"]],
        )
        target.add(e)
        target.flush()
        etape_map[row["id"]] = e.id

    # 3. ECUE
    ecue_map = {}
    for row in conn.execute(select(ecue_src)).mappings():
        x = ECUE(
            annee=year,
            nom=row["nom"], code=row["code"], periode=row["periode"],
            effectif=row["effectif"], besoins=row["besoins"],
            etape_id=etape_map[row["etape_id"]],
        )
        target.add(x)
        target.flush()
        ecue_map[row["id"]] = x.id

    # 4. Rattachements
    n_ratt = 0
    for row in conn.execute(select(ecue_etape_src)).mappings():
        target.add(ECUE_Etape(
            annee=year,
            ecue_id=ecue_map[row["ecue_id"]],
            etape_id=etape_map[row["etape_id"]],
            effectif=row["effectif"],
        ))
        n_ratt += 1

    conn.close()
    target.commit()
    return {
        "annee": year,
        "composantes": len(comp_map),
        "etapes": len(etape_map),
        "ecues": len(ecue_map),
        "rattachements": n_ratt,
    }


def main():
    parser = argparse.ArgumentParser(description="Migration vers maquette_rh")
    parser.add_argument(
        "--annees", default="2024,2025,2026",
        help="Années des bases sources, séparées par des virgules"
    )
    args = parser.parse_args()
    years = [int(a) for a in args.annees.split(",")]

    target_engine = database_config.get_engine()
    target = Session(bind=target_engine)

    # Relançable : on vide les tables cibles
    target.query(ECUE_Etape).delete()
    target.query(ECUE).delete()
    target.query(Etape).delete()
    target.query(Composante).delete()
    target.commit()

    try:
        for year in years:
            source_engine = connect_source(year)
            try:
                bilan = migrate_year(source_engine, target, year)
                print(
                    f"{year} : {bilan['composantes']} composantes, "
                    f"{bilan['etapes']} étapes, {bilan['ecues']} ECUE, "
                    f"{bilan['rattachements']} rattachements"
                )
            finally:
                source_engine.dispose()
    except Exception as e:
        target.rollback()
        print(f"ÉCHEC : {e}", file=sys.stderr)
        print("Aucune donnée partielle n'est conservée (rollback).", file=sys.stderr)
        sys.exit(1)
    finally:
        target.close()

    print("Migration terminée.")


if __name__ == "__main__":
    main()
