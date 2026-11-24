"""Data shared by every page (navigation menus, publications)."""

import hashlib
from functools import cache
from pathlib import Path

from django.utils.translation import gettext_lazy as _

from .catalog import PROBLEMS_BY_SLUG, STRATEGY_BY_THEORY, sidebar_menu

PUBLICATIONS = [  # titles exactly as listed on the original site
    ("A new variable step size algorithm for Cauchy problem", "ScienceDirect",
     "https://www.sciencedirect.com/science/article/abs/pii/S0096300306006217"),
    ("Step Size Strategies Based on Error Analysis", "DergiPark",
     "http://dergipark.gov.tr/download/article-file/214950"),
    ("Step Size Strategy for The Numerical Integration of Systems of The Linear Systems", "ResearchGate",
     "https://www.researchgate.net/publication/260391200_Step_Size_Strategies_Based_On_Error_Analysis_For_The_Linear_Systems"),
    ("Step Size Strategy for The Numerical Integration of Systems of Differential Equations", "ScienceDirect",
     "https://www.sciencedirect.com/science/article/pii/S0377042711003682"),
    ("Analysis with Variable Step Size Strategy of Some SIR Epidemic Models", "fbd.beun.edu.tr",
     "http://fbd.beun.edu.tr/index.php/zkufbd/article/viewFile/394/192"),
    ("The Analysis of The Effect of The Norms in The Step Size Selection for The Numerical Integration", "DergiPark",
     "http://dergipark.gov.tr/download/article-file/436436"),
]

CONFERENCES = [  # newest first
    {
        "event": "ICMME-2021",
        "title": "Analysis of Covid-19 Epidemic in Turkey Using Generalized SEIR Model",
        "place": _("Gazi University, Ankara, September 2021"),
        "authors": "",
    },
    {
        "event": "ICMME-2019",
        "title": "An Advanced Interactive Web Interface for Step Size Strategies",
        "place": _("Selçuk University, Konya, July 2019"),
        "authors": "Ersan ERDEM, Gülnur ÇELİK KIZILKAN, Ali Osman ÇIBIKDİKEN",
    },
    {
        "event": "ICMME-2017",
        "title": "Creating a Web Interface for Step Size Strategies",
        "place": _("Harran University, Şanlıurfa, May 11–13, 2017"),
        "authors": "Ersan ERDEM, Gülnur ÇELİK KIZILKAN, Ali Osman ÇIBIKDİKEN",
    },
]

TEAM = [
    {
        "name": "Ersan ERDEM",
        "role": _("Master's student (2017), Necmettin Erbakan University, Institute of Science, Department of Mathematics, Konya"),
        "email": "ersanerdem.ee@gmail.com",
        "photo": "site/img/team/ersan-erdem.jpg",
    },
    {
        "name": "Gülnur ÇELİK KIZILKAN",
        "role": _("Assistant Professor (2017), Necmettin Erbakan University, Faculty of Science, Department of Mathematics and Computer Science, Konya"),
        "email": "gckizilkan@erbakan.edu.tr",
        "photo": "",
    },
    {
        "name": "Ali Osman ÇIBIKDİKEN",
        "role": _("Assistant Professor (2017), Necmettin Erbakan University, Faculty of Engineering and Architecture, Department of Computer Engineering, Konya"),
        "email": "aocdiken@erbakan.edu.tr",
        "photo": "graphics/images/aliosman_cibikdiken.jpeg",
    },
]


STATIC_DIR = Path(__file__).resolve().parent / "static"
VERSIONED_ASSETS = ("site/css/site.css", "site/js/site.js", "site/js/solver.js")


@cache
def asset_version() -> str:
    """Short hash of our CSS/JS files, added as ``?v=`` so browsers fetch them again after every update."""
    digest = hashlib.sha256()
    for name in VERSIONED_ASSETS:
        path = STATIC_DIR / name
        if path.exists():
            digest.update(path.read_bytes())
    return digest.hexdigest()[:10]


def navigation(request):
    match = getattr(request, "resolver_match", None)
    active = match.url_name if match else ""
    problem = PROBLEMS_BY_SLUG.get(active)
    if problem is not None:
        active = problem.sim_slug  # the table view (...clf) belongs to the chart view's menu entry
        section = "solver"
    elif active in STRATEGY_BY_THEORY:
        section = "theory"
    else:
        section = active
    return {
        "asset_version": asset_version(),
        "nav_sidebar": sidebar_menu(),
        "nav_active": active,
        "nav_section": section,
        "publications": PUBLICATIONS,
        "team": TEAM,
        "conferences": CONFERENCES,
    }
