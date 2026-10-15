"""
Rendu HTML pur (sans framework JavaScript) pour l'interface de parcours
des maquettes : composante -> étape -> ECUE.

Les identifiants de la base de données (id) ne sont jamais affichés :
les étapes et les ECUE sont identifiées par leur code (unique),
les composantes par leur nom (unique).
"""

import json
from html import escape
from typing import Any, List, Optional, Tuple
from urllib.parse import quote


def _e(value: Any) -> str:
    """Échappe une valeur pour l'affichage HTML"""
    return escape(str(value if value is not None else ""), quote=True)


def _u(path: str, year: Optional[int]) -> str:
    """Construit une URL interne en conservant l'année de la maquette"""
    return f"{path}?year={year}" if year else path


def _breadcrumb(items: List[Tuple[str, Optional[str]]], year: Optional[int]) -> str:
    """Fil d'Ariane cliquable pour monter dans la structure"""
    parts = ['<nav class="ariane" aria-label="Fil d\'Ariane">']
    for index, (label, path) in enumerate(items):
        if index:
            parts.append('<span class="sep">›</span>')
        if path:
            parts.append(f'<a href="{_e(_u(path, year))}">{_e(label)}</a>')
        else:
            parts.append(f'<span class="courant">{_e(label)}</span>')
    parts.append("</nav>")
    return "".join(parts)


_CSS = """
* { box-sizing: border-box; }
body { font-family: system-ui, -apple-system, sans-serif; margin: 0; color: #1a1a1a; background: #f7f7f8; }
header { background: #1f2937; color: #fff; padding: 0.8rem 1.5rem; display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; }
header a { color: #fff; text-decoration: none; }
.brand { font-weight: 700; font-size: 1.1rem; }
form.recherche { display: flex; gap: 0.4rem; flex: 1; min-width: 260px; }
form.recherche input[type="search"] { flex: 1; padding: 0.4rem 0.6rem; border: none; border-radius: 4px; }
form.recherche button { padding: 0.4rem 0.8rem; border: none; border-radius: 4px; background: #2563eb; color: #fff; cursor: pointer; }
nav.annees a { margin-left: 0.5rem; padding: 0.15rem 0.5rem; border-radius: 4px; background: #374151; }
nav.annees a.active { background: #2563eb; }
main { max-width: 960px; margin: 1.5rem auto; padding: 0 1rem; }
.ariane { margin-bottom: 1rem; color: #555; font-size: 0.9rem; }
.ariane a { color: #2563eb; }
.ariane .sep { margin: 0 0.3rem; }
.ariane .courant { font-weight: 600; color: #111; }
h1 { font-size: 1.4rem; }
h2 { font-size: 1.1rem; margin-top: 1.5rem; }
.badge { display: inline-block; background: #e5e7eb; border-radius: 4px; padding: 0.1rem 0.5rem; font-size: 0.8rem; margin-left: 0.5rem; vertical-align: middle; }
ul.liste { list-style: none; padding: 0; }
ul.liste li { background: #fff; border: 1px solid #e5e7eb; border-radius: 6px; padding: 0.7rem 1rem; margin-bottom: 0.5rem; }
ul.liste a { color: #2563eb; text-decoration: none; font-weight: 600; }
ul.liste a:hover { text-decoration: underline; }
.sous { color: #555; font-size: 0.9rem; margin-left: 0.6rem; }
table.details { border-collapse: collapse; margin: 1rem 0; background: #fff; }
table.details th, table.details td { border: 1px solid #e5e7eb; padding: 0.4rem 0.8rem; text-align: left; }
table.details th { background: #f3f4f6; }
.code { font-family: ui-monospace, monospace; background: #f3f4f6; padding: 0.1rem 0.35rem; border-radius: 4px; }
pre { background: #1f2937; color: #e5e7eb; padding: 1rem; border-radius: 6px; overflow-x: auto; }
.retour { display: inline-block; margin: 0.5rem 0 1rem; color: #2563eb; text-decoration: none; }
.retour:hover { text-decoration: underline; }
section.resultats { margin-bottom: 1.5rem; }
section.resultats h2 { margin-bottom: 0.4rem; }
.vide { color: #777; font-style: italic; }
.erreur { background: #fff; border: 1px solid #e5e7eb; border-radius: 6px; padding: 1.5rem; }
footer { text-align: center; color: #777; font-size: 0.85rem; padding: 2rem 0; }
"""


def _layout(
    title: str,
    content: str,
    year: Optional[int],
    years: List[int],
    breadcrumb: str = "",
    q: str = "",
) -> str:
    """Structure de page commune (en-tête avec recherche, fil d'Ariane, pied de page)"""
    selecteur_annees = " ".join(
        f'<a href="{_e(_u("/ui", y))}"{" class=\"active\"" if y == year else ""}>{y}</a>'
        for y in years
    )
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_e(title)} - Maquettes</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <a class="brand" href="{_e(_u("/ui", year))}">Maquettes</a>
  <form class="recherche" method="get" action="/ui/recherche" role="search">
    <input type="search" name="q" placeholder="Rechercher par code ou par nom..." value="{_e(q)}" required>
    <input type="hidden" name="year" value="{_e(year)}">
    <button type="submit">Rechercher</button>
  </form>
  <nav class="annees" aria-label="Année de la maquette">{selecteur_annees}</nav>
</header>
<main>
{breadcrumb}
{content}
</main>
<footer>Consultation des maquettes d'enseignement - année {year}</footer>
</body>
</html>"""


def page_home(composantes: list, year: Optional[int], years: List[int]) -> str:
    """Accueil : liste des composantes (point d'entrée de la structure)"""
    items = "".join(
        f'<li><a href="{_e(_u("/ui/composante/" + quote(c.nom), year))}">{_e(c.nom)}</a></li>'
        for c in composantes
    )
    content = f"""
<h1>Composantes <span class="badge">{len(composantes)}</span></h1>
<p>Parcourez la structure des enseignements : choisissez une composante pour voir ses
étapes, puis les ECUE de chaque étape. Vous pouvez aussi rechercher directement un
enseignement par son code ou par son nom.</p>
<ul class="liste">
{items}
</ul>"""
    return _layout(
        "Accueil",
        content,
        year,
        years,
        _breadcrumb([("Accueil", None)], year),
    )


def page_composante(composante, etapes: list, year: Optional[int], years: List[int]) -> str:
    """Détail d'une composante et liste de ses étapes"""
    items = "".join(
        f'<li><a href="{_e(_u("/ui/etape/" + quote(e.code), year))}"><span class="code">{_e(e.code)}</span></a>'
        f'<span class="sous">{_e(e.nom)}</span><br>'
        f'<span class="sous">{_e(e.type)} &middot; {_e(e.niveau)} &middot; {_e(e.domaine)} &middot; effectif : {e.effectif}</span></li>'
        for e in etapes
    )
    liste = items if items else '<li class="vide">Aucune étape dans cette composante.</li>'
    content = f"""
<a class="retour" href="{_e(_u("/ui", year))}">&larr; Toutes les composantes</a>
<h1>{_e(composante.nom)} <span class="badge">Composante</span></h1>
<h2>Étapes <span class="badge">{len(etapes)}</span></h2>
<ul class="liste">
{liste}
</ul>"""
    return _layout(
        composante.nom,
        content,
        year,
        years,
        _breadcrumb([("Accueil", "/ui"), (composante.nom, None)], year),
    )


def page_etape(etape, composante, ecues: list, year: Optional[int], years: List[int]) -> str:
    """Détail d'une étape, lien vers sa composante et liste de ses ECUE"""
    items = "".join(
        f'<li><a href="{_e(_u("/ui/ecue/" + quote(e.code), year))}"><span class="code">{_e(e.code)}</span></a>'
        f'<span class="sous">{_e(e.nom)}</span>'
        f'<span class="sous">période {_e(e.periode)} &middot; effectif : {e.effectif}</span></li>'
        for e in ecues
    )
    liste = items if items else '<li class="vide">Aucune ECUE dans cette étape.</li>'
    content = f"""
<a class="retour" href="{_e(_u("/ui/composante/" + quote(composante.nom), year))}">&larr; {_e(composante.nom)}</a>
<h1><span class="code">{_e(etape.code)}</span> {_e(etape.nom)} <span class="badge">Étape</span></h1>
<table class="details">
  <tr><th>Type</th><td>{_e(etape.type)}</td></tr>
  <tr><th>Niveau</th><td>{_e(etape.niveau)}</td></tr>
  <tr><th>Domaine</th><td>{_e(etape.domaine)}</td></tr>
  <tr><th>Effectif</th><td>{etape.effectif}</td></tr>
  <tr><th>Composante</th><td><a href="{_e(_u("/ui/composante/" + quote(composante.nom), year))}">{_e(composante.nom)}</a></td></tr>
</table>
<h2>ECUE <span class="badge">{len(ecues)}</span></h2>
<ul class="liste">
{liste}
</ul>"""
    return _layout(
        f"{etape.code} - {etape.nom}",
        content,
        year,
        years,
        _breadcrumb(
            [("Accueil", "/ui"), (composante.nom, "/ui/composante/" + quote(composante.nom)), (etape.code, None)],
            year,
        ),
    )


def page_ecue(ecue, etape, composante, autres_etapes: list, year: Optional[int], years: List[int]) -> str:
    """Détail d'une ECUE et liens vers ses étapes de rattachement"""
    if ecue.besoins:
        besoins = f"<pre>{_e(json.dumps(ecue.besoins, indent=2, ensure_ascii=False))}</pre>"
    else:
        besoins = '<p class="vide">Aucun besoin renseigné.</p>'
    autres = "".join(
        f'<li><a href="{_e(_u("/ui/etape/" + quote(e.code), year))}"><span class="code">{_e(e.code)}</span></a>'
        f'<span class="sous">{_e(e.nom)}</span></li>'
        for e in autres_etapes
    )
    section_autres = ""
    if autres_etapes:
        section_autres = f"""
<h2>Autres étapes de rattachement <span class="badge">{len(autres_etapes)}</span></h2>
<ul class="liste">
{autres}
</ul>"""
    content = f"""
<a class="retour" href="{_e(_u("/ui/etape/" + quote(etape.code), year))}">&larr; {_e(etape.code)} - {_e(etape.nom)}</a>
<h1><span class="code">{_e(ecue.code)}</span> {_e(ecue.nom)} <span class="badge">ECUE</span></h1>
<table class="details">
  <tr><th>Période</th><td>{_e(ecue.periode)}</td></tr>
  <tr><th>Effectif</th><td>{ecue.effectif}</td></tr>
  <tr><th>Étape principale</th><td><a href="{_e(_u("/ui/etape/" + quote(etape.code), year))}"><span class="code">{_e(etape.code)}</span> {_e(etape.nom)}</a></td></tr>
  <tr><th>Composante</th><td><a href="{_e(_u("/ui/composante/" + quote(composante.nom), year))}">{_e(composante.nom)}</a></td></tr>
</table>
{section_autres}
<h2>Besoins</h2>
{besoins}"""
    return _layout(
        f"{ecue.code} - {ecue.nom}",
        content,
        year,
        years,
        _breadcrumb(
            [
                ("Accueil", "/ui"),
                (composante.nom, "/ui/composante/" + quote(composante.nom)),
                (etape.code, "/ui/etape/" + quote(etape.code)),
                (ecue.code, None),
            ],
            year,
        ),
    )


def page_recherche(q: str, composantes: list, etapes: list, ecues: list, year: Optional[int], years: List[int]) -> str:
    """Résultats de recherche (par code ou par nom) groupés par type"""
    items_comp = "".join(
        f'<li><a href="{_e(_u("/ui/composante/" + quote(c.nom), year))}">{_e(c.nom)}</a></li>'
        for c in composantes
    )
    items_etapes = "".join(
        f'<li><a href="{_e(_u("/ui/etape/" + quote(e.code), year))}"><span class="code">{_e(e.code)}</span></a>'
        f'<span class="sous">{_e(e.nom)}</span></li>'
        for e in etapes
    )
    items_ecues = "".join(
        f'<li><a href="{_e(_u("/ui/ecue/" + quote(e.code), year))}"><span class="code">{_e(e.code)}</span></a>'
        f'<span class="sous">{_e(e.nom)}</span></li>'
        for e in ecues
    )
    section_comp = f"""
<section class="resultats">
<h2>Composantes <span class="badge">{len(composantes)}</span></h2>
<ul class="liste">{items_comp}</ul>
</section>""" if composantes else ""
    section_etapes = f"""
<section class="resultats">
<h2>Étapes <span class="badge">{len(etapes)}</span></h2>
<ul class="liste">{items_etapes}</ul>
</section>""" if etapes else ""
    section_ecues = f"""
<section class="resultats">
<h2>ECUE <span class="badge">{len(ecues)}</span></h2>
<ul class="liste">{items_ecues}</ul>
</section>""" if ecues else ""
    if not (composantes or etapes or ecues):
        resultat = '<p class="vide">Aucun résultat pour cette recherche.</p>'
    else:
        resultat = section_comp + section_etapes + section_ecues
    content = f"""
<h1>Résultats pour &laquo;&nbsp;{_e(q)}&nbsp;&raquo;</h1>
{resultat}"""
    return _layout(
        f"Recherche : {q}",
        content,
        year,
        years,
        _breadcrumb([("Accueil", "/ui"), ("Recherche", None)], year),
        q=q,
    )


def page_erreur(message: str, year: Optional[int], years: List[int], status_code: int = 404) -> str:
    """Page d'erreur (élément introuvable, etc.)"""
    content = f"""
<div class="erreur">
<h1>Oups</h1>
<p>{_e(message)}</p>
<p><a class="retour" href="{_e(_u("/ui", year))}">&larr; Retour à l'accueil</a></p>
</div>"""
    return _layout(
        f"Erreur {status_code}",
        content,
        year,
        years,
        _breadcrumb([("Accueil", "/ui"), ("Erreur", None)], year),
    )
