# Fichier : build_pages.py
# Prépare la version GitHub Pages du dashboard dans le dossier _site/ :
# la page stlite (web/index.html), dashboard.py et un instantané JSON des données.
# Le navigateur ne pouvant pas faire de requêtes DNS/WHOIS, les données sont collectées ici
# (par GitHub Actions, voir .github/workflows/pages.yml) puis lues par le dashboard.

import json
import shutil
import sys
from pathlib import Path
import pandas as pd
from collecte_bj_data import get_all_bj_data

RACINE = Path(__file__).parent

def construire_site(dossier="_site"):
    data = get_all_bj_data()
    if data['ns_total'] == 0:
        sys.exit("Aucun serveur NS récupéré : site non généré (la version publiée reste inchangée).")

    sortie = Path(dossier)
    sortie.mkdir(parents=True, exist_ok=True)
    shutil.copy(RACINE / "web" / "index.html", sortie)
    shutil.copy(RACINE / "dashboard.py", sortie)

    # Les DataFrames sont convertis en listes d'enregistrements ; dashboard.py les reconstruit.
    snapshot = {
        cle: json.loads(valeur.to_json(orient="records", force_ascii=False)) if isinstance(valeur, pd.DataFrame) else valeur
        for cle, valeur in data.items()
    }
    (sortie / "bj_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Site généré dans {sortie} (données du {data['date_collecte']}, {data['ns_total']} serveurs NS)")

if __name__ == "__main__":
    construire_site(sys.argv[1] if len(sys.argv) > 1 else "_site")
