# Fichier : donnees_arcep.py
# Indicateurs du marché des communications électroniques publiés par l'ARCEP BENIN :
# - chiffres officiels du Rapport annuel d'activités 2025 (situation au 31 décembre 2025) ;
# - mesures quotidiennes de qualité de service (QoS) publiées sur la page "Qualité de service" d'arcep.bj.
# Opérateurs : MTN = SPACETEL BENIN, MOOV = MOOV AFRICA BENIN, CELTIIS = SBIN.

import json
import re
import requests
import pandas as pd

SOURCE_RAPPORT_2025 = "Rapport Annuel d'Activités ARCEP 2025"
URL_QOS = "https://arcep.bj/performances-mtn-et-moov/"

# (année, indicateur, opérateur, valeur, unité, évolution annuelle en % indiquée par le rapport)
INDICATEURS_MARCHE = [
    (2024, "Cartes SIM actives", "Tous", 18.21, "millions", None),
    (2025, "Cartes SIM actives", "Tous", 18.17, "millions", -0.2),
    (2025, "Abonnés mobiles", "Tous", 10328542, "abonnés", None),
    (2025, "Pénétration mobile", "Tous", 78.1, "%", None),
    (2025, "Cartes SIM Internet mobile", "Tous", 10.81, "millions", None),
    (2025, "Abonnés Internet mobile", "Tous", 8594822, "abonnés", None),
    (2024, "Pénétration Internet mobile", "Tous", 63.5, "%", None),
    (2025, "Pénétration Internet mobile", "Tous", 64.9, "%", None),
    (2022, "Abonnements Internet mobile 4G", "Tous", 31, "%", None),
    (2025, "Abonnements Internet mobile 4G", "Tous", 58, "%", None),
    (2025, "Abonnements Internet mobile 3G", "Tous", 17, "%", None),
    (2025, "Abonnements Internet mobile 2G", "Tous", 25, "%", None),
    (2024, "Trafic Internet mobile", "Tous", 375.4, "millions de Go", None),
    (2025, "Trafic Internet mobile", "Tous", 551.6, "millions de Go", 47.0),
    (2025, "Trafic voix mobile", "Tous", 10.374, "milliards de minutes", 51.57),
    (2025, "SMS échangés", "Tous", 603.188, "millions", 39.5),
    (2025, "ARPU mobile", "Tous", 1622, "FCFA par mois", None),
    (2025, "Chiffre d'affaires mobile", "Tous", 350.02, "milliards FCFA", 3.1),
    (2024, "Part de marché (valeur)", "CELTIIS", 16.3, "%", None),
    (2025, "Part de marché (valeur)", "MTN", 40.9, "%", None),
    (2025, "Part de marché (valeur)", "MOOV", 23.5, "%", None),
    (2025, "Part de marché (valeur)", "CELTIIS", 35.6, "%", None),
    (2025, "Abonnés Internet fixe", "Tous", 105715, "abonnés", 163.51),
    (2025, "Pénétration Internet fixe", "Tous", 0.80, "%", None),
    (2025, "Abonnés téléphonie fixe", "Tous", 78938, "abonnés", None),
    (2025, "Fournisseurs d'accès à Internet", "Tous", 27, "FAI", None),
    (2025, "Bande passante internationale", "Tous", 350, "Gbps", None),
]

# Utilisateurs connectés aux plateformes par opérateur et par genre (Tableau 8 du rapport 2025).
# Les données de CELTIIS, et celles de TikTok et Netflix chez MOOV, ne sont pas publiées.
USAGE_PLATEFORMES = [
    ("MTN", "WhatsApp", "Femme", 2240097), ("MTN", "WhatsApp", "Homme", 3960491),
    ("MTN", "Facebook", "Femme", 2602392), ("MTN", "Facebook", "Homme", 4390852),
    ("MTN", "TikTok", "Femme", 1575511), ("MTN", "TikTok", "Homme", 2512204),
    ("MTN", "Netflix", "Femme", 50393), ("MTN", "Netflix", "Homme", 80153),
    ("MOOV", "WhatsApp", "Femme", 850509), ("MOOV", "WhatsApp", "Homme", 2391639),
    ("MOOV", "Facebook", "Femme", 1181573), ("MOOV", "Facebook", "Homme", 3413665),
]

def get_indicateurs_marche():
    df = pd.DataFrame(INDICATEURS_MARCHE, columns=["annee", "indicateur", "operateur", "valeur", "unite", "variation_pct"])
    df["source"] = SOURCE_RAPPORT_2025
    return df

def get_usage_plateformes():
    df = pd.DataFrame(USAGE_PLATEFORMES, columns=["operateur", "plateforme", "genre", "utilisateurs"])
    df.insert(0, "annee", 2025)
    return df

def _indicateur_qos(titre):
    t = titre.upper().replace(" ", "")
    if "SUCCES" in t: return "Taux de succès des appels voix"
    if "BLOCAGE" in t: return "Taux de blocage des appels voix"
    sens = "descendant" if "DOWNLINK" in t else "montant"
    return f"Débit {sens} {'4G' if '4G' in t else '3G'}"

def _unite_qos(nom_serie):
    if "MBPS" in nom_serie: return "Mbps"
    if "KBPS" in nom_serie: return "kbps"
    return "%"

def get_qos_arcep():
    """Extrait les mesures QoS des graphiques (wpDataTables/Highcharts) de la page Qualité de service de l'ARCEP."""
    colonnes = ["date", "operateur", "indicateur", "valeur", "unite", "seuil"]
    try:
        response = requests.get(URL_QOS, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        response.raise_for_status()
        decoder = json.JSONDecoder()
        lignes = []
        for match in re.finditer(r"render_data:\s*", response.text):
            options = decoder.raw_decode(response.text, match.end())[0]["options"]
            axe_x = options["xAxis"][0] if isinstance(options["xAxis"], list) else options["xAxis"]
            dates = pd.to_datetime(axe_x["categories"], format="%d/%m/%Y").strftime("%Y-%m-%d")
            indicateur = _indicateur_qos(options["title"]["text"])
            series = {s["name"].upper(): s["data"] for s in options["series"]}
            seuils = next((v for nom, v in series.items() if "SEUIL" in nom), [None] * len(dates))
            for nom, valeurs in series.items():
                operateur = next((op for op in ("MTN", "MOOV", "CELTIIS") if op in nom), None)
                if operateur:
                    lignes += [(d, operateur, indicateur, v, _unite_qos(nom), s) for d, v, s in zip(dates, valeurs, seuils)]
        return pd.DataFrame(lignes, columns=colonnes)
    except Exception as e:
        print(f"Échec de la récupération des mesures QoS : {e}")
        return pd.DataFrame(columns=colonnes)
