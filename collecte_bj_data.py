# Fichier : collecte_bj_data.py (Version Finale Corrigée)

import requests
from bs4 import BeautifulSoup
import dns.resolver
from ipwhois import IPWhois
import pandas as pd
from socket import gaierror
import numpy as np
from donnees_arcep import get_indicateurs_marche, get_usage_plateformes, get_qos_arcep

# --- MISE À JOUR : Génération de données estimées pour le graphique ---
def prepare_full_domain_timeseries():
    """
    Prépare un DataFrame complet de 1996 à 2025, en fusionnant les données officielles
    et en créant des estimations plausibles pour les années manquantes.
    """
    official_data = {
        'Année': [2019, 2020, 2021, 2022, 2023, 2024],
        'Nombre de domaines .bj': [1624, 1766, 2690, 3005, 3447, 3382]
    }
    df_official = pd.DataFrame(official_data)

    full_year_range = pd.DataFrame({'Année': range(1996, 2026)})
    df_full = pd.merge(full_year_range, df_official, on='Année', how='left')

    # Création d'une colonne temporaire pour l'interpolation
    df_full['valeur_estimee'] = df_full['Nombre de domaines .bj']
    
    # Définition d'un point de départ bas pour 1996 pour une croissance réaliste
    df_full.loc[df_full['Année'] == 1996, 'valeur_estimee'] = 50
    
    # Étape 1 : Interpolation linéaire pour combler les vides
    df_full['valeur_estimee'] = df_full['valeur_estimee'].interpolate(method='linear')

    # Étape 2 : C'est la ligne clé. On remplit les "trous" de la colonne principale
    # avec les valeurs que nous venons d'estimer.
    df_full['Nombre de domaines .bj'] = df_full['Nombre de domaines .bj'].fillna(df_full['valeur_estimee'])
    
    # Étape 3 : Maintenant qu'il n'y a plus de "trous", on peut convertir en entier sans erreur.
    df_full['Nombre de domaines .bj'] = df_full['Nombre de domaines .bj'].astype(int)
    
    # Étape 4 : Création des colonnes pour le statut et l'infobulle
    df_full['Statut'] = np.where(df_full['Année'].isin(official_data['Année']), 'Officiel', 'Donnée estimée')
    df_full['commentaires'] = np.where(
        df_full['Statut'] == 'Officiel',
        df_full['Nombre de domaines .bj'].apply(lambda x: f'{x:,.0f}'.replace(',', ' ')),
        'Donnée à confirmer'
    )
    return df_full


def get_nombre_domaines_live():
    try:
        url = "https://www.tld-list.com/tld/bj"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        stats_div = soup.find('div', class_='tld-stat')
        if stats_div and "domains" in stats_div.text:
            nombre_str = ''.join(filter(str.isdigit, stats_div.find('h3').text))
            if nombre_str:
                return {"valeur": int(nombre_str), "status": "direct"}
    except Exception as e:
        print(f"Échec de la récupération en direct : {e}")
    return {"valeur": 3382, "status": "estimation"}

def calculate_domain_growth(df_historique):
    df_official = df_historique[df_historique['Statut'] == 'Officiel'].sort_values(by='Année')
    if len(df_official) < 2: return "N/A"
    last_year_data = df_official.iloc[-1]
    previous_year_data = df_official.iloc[-2]
    growth_rate = ((last_year_data['Nombre de domaines .bj'] - previous_year_data['Nombre de domaines .bj']) / previous_year_data['Nombre de domaines .bj']) * 100
    return f"{growth_rate:.2f}% ({int(previous_year_data['Année'])}-{int(last_year_data['Année'])})"

def check_dnssec_status(domain="bj"):
    try:
        dns.resolver.resolve(domain, 'DS'); return "Activé"
    except dns.resolver.NoAnswer: return "Non activé"
    except Exception: return "Erreur"
    
def get_ns_info(domain="bj"):
    serveurs_info = []
    ipv6_count = 0
    try:
        ns_records = dns.resolver.resolve(domain, 'NS')
        hostnames = sorted([str(ns.target) for ns in ns_records])
        for hostname in hostnames:
            info = {"serveur_ns": hostname, "ipv4": "N/A", "ipv6": "N/A", "pays": "N/A", "asn": "N/A"}
            try:
                ipv4_addr = str(dns.resolver.resolve(hostname, 'A')[0])
                info["ipv4"] = ipv4_addr
                try:
                    obj = IPWhois(ipv4_addr)
                    results = obj.lookup_rdap(depth=1)
                    info["pays"] = results.get('asn_country_code', 'N/A')
                    info["asn"] = f"AS{results.get('asn')} ({results.get('asn_description', 'N/A')})"
                except Exception: info["pays"] = "Erreur Lookup"
            except (dns.resolver.NoAnswer, gaierror): pass
            try:
                ipv6_addr = str(dns.resolver.resolve(hostname, 'AAAA')[0])
                info["ipv6"] = ipv6_addr
                if ipv6_addr and "N/A" not in ipv6_addr: ipv6_count += 1
            except (dns.resolver.NoAnswer, gaierror): pass
            serveurs_info.append(info)
        return pd.DataFrame(serveurs_info), len(hostnames), ipv6_count
    except Exception as e:
        print(f"Erreur majeure NS : {e}")
        return pd.DataFrame(columns=["serveur_ns", "ipv4", "ipv6", "pays", "asn"]), 0, 0

def get_all_bj_data(for_db=False):
    """Appelle toutes les fonctions et retourne un dictionnaire complet."""
    df_ns, ns_total, ipv6_total = get_ns_info()
    df_historique_full = prepare_full_domain_timeseries()
    nb_domaines_live = get_nombre_domaines_live()
    dnssec = check_dnssec_status()
    ipv6_percent = (ipv6_total / ns_total * 100) if ns_total > 0 else 0
    
    data = {
        "date_collecte": pd.Timestamp.now(tz='Africa/Porto-Novo').strftime('%d/%m/%Y %H:%M:%S'),
        "nb_domaines_live_data": nb_domaines_live,
        "domaines_historique_df": df_historique_full,
        "dnssec_status": dnssec,
        "ns_total": ns_total,
        "ipv6_disponible": ipv6_total,
        "ipv6_availability_percent": ipv6_percent,
        "ns_details_df": df_ns,
        "domain_growth": calculate_domain_growth(df_historique_full),
        "admin_data": {
            "Gestionnaire ccTLD": "ARCEP BENIN",
            "Contact Administratif": "Secrétaire Exécutif, ARCEP BENIN",
            "Contact Technique": "Tonouhewa Deo Gratias, JENY SAS",
            "Date d'enregistrement du domaine": "1996-01-18",
            "Dernière mise à jour (IANA)": "2023-04-14",
            "Site web du registre": "http://www.nic.bj",
            "Serveur WHOIS": "whois.nic.bj"
        },
        "policy_data": {"Restrictions": "Un contact administratif au Bénin est requis.", "Présence locale requise": "Non", "Domaines de second niveau": ".com.bj"},
        "indicateurs_marche_df": get_indicateurs_marche(),
        "usage_plateformes_df": get_usage_plateformes(),
        "qos_df": get_qos_arcep()
    }

    if for_db:
        return prepare_data_for_db(data)
    return data

def prepare_data_for_db(data):
    """Formate les données collectées pour une insertion facile en base de données."""
    kpis_data = {
        'live_domain_count': data['nb_domaines_live_data']['valeur'],
        'live_data_status': data['nb_domaines_live_data']['status'],
        'nameserver_count': data['ns_total'],
        'ipv6_availability_percent': data['ipv6_availability_percent'],
        'dnssec_status': data['dnssec_status']
    }
    history_df = data['domaines_historique_df'][data['domaines_historique_df']['Statut'] == 'Officiel']
    history_data = [
        {
            'annee': int(row['Année']),
            'nombre_domaines': int(row['Nombre de domaines .bj']),
            'source': f"Rapport Annuel ARCEP {int(row['Année'])}"
        } for index, row in history_df.iterrows()
    ]
    nameservers_df = data['ns_details_df']
    nameservers_data = [
        {
            'hostname': row['serveur_ns'],
            'ipv4_address': row['ipv4'],
            'ipv6_address': row['ipv6'],
            'country_code': row['pays'],
            'asn_details': row['asn']
        } for index, row in nameservers_df.iterrows()
    ]
    return {
        "bj_kpis": kpis_data,
        "bj_domain_history": history_data,
        "bj_nameservers": nameservers_data
    }