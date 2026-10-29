###Analyse du ccTLD .BJ pour le Projet BIM'HACK###
Ce projet s'inscrit dans le cadre du Benin Internet Measurement Hackathon (BIM’HACK), une initiative du chapitre Bénin de l'Internet Society. Il constitue une solution technique spécialisée visant à analyser la résilience, la performance et l'évolution du domaine de premier niveau national (ccTLD) du Bénin : le .bj.

###Contexte
Le projet BIM'HACK a pour mission de réunir des experts pour concevoir des outils innovants de mesure de l'Internet au Bénin. Souvent, les données permettant d'évaluer la santé de l'infrastructure Internet nationale sont dispersées ou inexploitées.

Notre projet répond directement à cet enjeu en se concentrant sur un pilier fondamental de l'écosystème Internet national : le système des noms de domaine (DNS) du .bj. En fournissant des données claires et exploitables sur ce ccTLD, nous apportons une contribution directe à l'objectif de "mesurer la performance de l’Internet au Bénin".

###Fonctionnalités###
Cet outil est un dashboard web interactif qui fournit une analyse complète et automatisée du domaine .bj. Il permet de :

Visualiser les Indicateurs Clés : Nombre de domaines enregistrés, nombre de serveurs de noms (NS), disponibilité en IPv6 et statut DNSSEC.

Analyser l'Évolution Historique : Un graphique présente la croissance du nombre de domaines .bj enregistrés, en se basant sur les données officielles des rapports annuels de l'ARCEP BENIN.

Évaluer la Résilience : Le dashboard analyse la répartition géographique des serveurs de noms, un facteur clé de la robustesse du domaine face aux pannes.

Suivre le Marché Mobile et Internet : Cartes SIM actives, abonnés mobiles et Internet, taux de pénétration, trafic et parts de marché (rapport annuel 2025 de l'ARCEP BENIN), qualité de service des réseaux MTN, MOOV et CELTIIS, et fractures numériques (genre, géographie, éducation).

Préparer les Données pour l'Export : Les scripts sont conçus pour formater les informations collectées en vue d'une migration facile vers une base de données PostgreSQL.

###Technologies Utilisées###
Langage : Python

Dashboard : Streamlit

Manipulation de données : Pandas

Visualisation de données : Altair

Requêtes DNS : dnspython

Géolocalisation IP : ipwhois

###Structure du Projet
collecte_bj_data.py : Le script principal contenant les fonctions pour collecter les données depuis des sources publiques (IANA, Rapports ARCEP, etc.) et les préparer pour l'affichage ou l'export.

donnees_arcep.py : Les indicateurs du marché mobile et Internet issus du rapport annuel 2025 de l'ARCEP, et la collecte des mesures de qualité de service publiées sur arcep.bj.

dashboard.py : Le script de l'application web Streamlit qui met en forme et affiche les données collectées.

schema_postgresql.txt : Le fichier contenant le schéma SQL pour créer les tables nécessaires dans une base de données PostgreSQL.

requirements.txt : La liste des dépendances Python nécessaires pour exécuter le projet.

build_pages.py : Génère la version GitHub Pages du dashboard dans le dossier _site/ (collecte des données et instantané bj_snapshot.json).

web/index.html : La page qui exécute le dashboard dans le navigateur avec stlite (version GitHub Pages).

.github/workflows/pages.yml : Le workflow GitHub Actions qui publie le dashboard sur GitHub Pages.

###Installation et Lancement
Clonez le dépôt

Bash

git clone https://github.com/canst/ccTLD-.BJ.git
git remote add origin https://github.com/canst/ccTLD-.BJ.git
git branch -M main
git push -u origin main

###Créez un environnement virtuel et activez-le

Bash

python -m venv .venv
# Sur Windows
.\.venv\Scripts\Activate
# Sur MacOS/Linux
source .venv/bin/activate

##Installez les dépendances

pip install -r requirements.txt

##Lancez le dashboard
python -m streamlit run dashboard.py

L'application s'ouvrira automatiquement dans votre navigateur.

### Version en ligne (GitHub Pages)
Le dashboard est publié sur GitHub Pages : https://soyames.github.io/ccTLD-.BJ/

GitHub Pages n'héberge que des fichiers statiques : le dashboard y tourne directement dans le navigateur grâce à [stlite](https://github.com/whitphx/stlite), qui exécute Streamlit en WebAssembly. Un navigateur ne pouvant pas interroger le DNS ni les serveurs WHOIS, le workflow `.github/workflows/pages.yml` collecte les données avec `build_pages.py` à chaque push sur `main` et chaque jour à 06:00 (heure de Porto-Novo), puis publie le site.

Activation (une seule fois) : **Settings → Pages → Build and deployment → Source : GitHub Actions**. GitHub suspend les workflows planifiés après 60 jours sans activité sur le dépôt : relancez-le si besoin depuis l'onglet **Actions** (bouton *Run workflow*).

Prévisualiser la version GitHub Pages en local, puis ouvrir http://localhost:8000 :

```
python build_pages.py
python -m http.server 8000 --directory _site
```

###Contribution au Projet BIM'HACK
Cet outil est une solution pertinente et directement exploitable qui répond aux objectifs du BIM'HACK :

Mesurer la performance : Il offre des métriques précises sur la santé et la robustesse de l'infrastructure DNS du .bj.

Analyser les données collectées : Le dashboard présente les informations de manière visuelle et intuitive.

Produire des rapports exploitables : Les données affichées peuvent être utilisées par les acteurs de l'écosystème (régulateurs, opérateurs, chercheurs) pour prendre des décisions éclairées.

En tant que projet abouti, cet outil pourra être présenté lors d'événements internationaux tels que l’

Africa DNS Forum, l’ICANN Tech Day et l’Africa Internet Summit pour illustrer une application concrète de la mesure de l'Internet au niveau national.