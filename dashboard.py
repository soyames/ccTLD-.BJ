# Fichier : dashboard.py 

import json
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import altair as alt

# Sur GitHub Pages, le dashboard tourne dans le navigateur (stlite/Pyodide) : les requêtes DNS/WHOIS y sont impossibles,
# il affiche donc l'instantané des données généré par build_pages.py (GitHub Actions).
EN_NAVIGATEUR = sys.platform == "emscripten"

st.set_page_config(
    page_title="Dashboard .BJ",
    page_icon="🇧🇯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .kpi-card {background-color: #FFFFFF; border-radius: 10px; padding: 25px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; transition: transform 0.2s; height: 140px; display: flex; flex-direction: column; justify-content: center;}
    .kpi-card:hover {transform: scale(1.05);}
    .kpi-card .kpi-title {font-size: 16px; color: #555; font-weight: bold;}
    .kpi-card .kpi-value {font-size: 36px; font-weight: bold; color: #008080;}
    .section-container {background-color: #FFFFFF; border-radius: 10px; padding: 25px; margin-top: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://www.arcep.bj/wp-content/uploads/2021/04/logo-ARCEP-BENIN-HD.png", width=150)
    st.title("Analyse du ccTLD .BJ")
    st.markdown("---")
    st.header("📚 Sources des Données")
    st.info("Ce dashboard agrège des données issues des rapports annuels de l'ARCEP BENIN et d'analyses en temps réel.")
    st.markdown("- **Rapports Annuels ARCEP**\n- **[IANA](https://www.iana.org/domains/root/db/bj.html)** : Informations sur la délégation et les serveurs de noms.**\n- **[DomainNameStat](https://domainnamestat.com/statistics/tld/bj)** : Estimation du nombre de domaines.**\n- **[TLD-List](https://tld-list.com/tld/bj)** : Politiques et informations sur le registre DNS.**\n- **[Qualité de service ARCEP](https://arcep.bj/performances-mtn-et-moov/)** : Mesures QoS des opérateurs mobiles.**")
    st.markdown("---")
    st.link_button("Retour au Dashboard Principal", "/URL_VERS_LE_DASHBOARD_PRINCIPAL", type="primary")
    st.markdown("---")

st.header("ccTLD .BJ")
st.markdown("Analyse de l'infrastructure, des politiques et de l'évolution du domaine national du Bénin.")

@st.cache_data(ttl=3600)
def charger_donnees():
    if EN_NAVIGATEUR:
        data = json.loads((Path(__file__).parent / "bj_snapshot.json").read_text(encoding="utf-8"))
        for cle in data:
            if cle.endswith('_df'):
                data[cle] = pd.DataFrame(data[cle])
        return data
    from collecte_bj_data import get_all_bj_data
    return get_all_bj_data()

with st.spinner('Analyse en cours...'):
    data = charger_donnees()

st.sidebar.success(f"Dernière mise à jour : {data['date_collecte']}")
if EN_NAVIGATEUR:
    st.sidebar.caption("Version GitHub Pages : données collectées chaque jour par GitHub Actions.")

st.markdown("### 🔑 Indicateurs Clés")
cols = st.columns(4)
kpis = [
    {"title": f"Domaines ({data['nb_domaines_live_data']['status'].capitalize()})", "value": f"{data['nb_domaines_live_data']['valeur']:,}".replace(',', ' '), "icon": "🌐"},
    {"title": "Serveurs DNS (NS)", "value": data['ns_total'], "icon": "🖥️"},
    {"title": "Disponibilité IPv6", "value": f"{data['ipv6_availability_percent']:.0f}%", "icon": "📶"},
    {"title": "Statut DNSSEC", "value": data['dnssec_status'].split(' ')[0], "icon": "🛡️"}
]
for i, kpi in enumerate(kpis):
    with cols[i]:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">{kpi["icon"]} {kpi["title"]}</div><div class="kpi-value">{kpi["value"]}</div></div>', unsafe_allow_html=True)


st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("📈 Évolution et Résilience de l'Écosystème")
col_chart, col_resilience = st.columns([2, 1])

with col_chart:
    df_domaines = data['domaines_historique_df']
    if not df_domaines.empty:
        color_scheme = alt.Scale(
            domain=['Officiel', 'Donnée estimée'],
            range=['#00A9E0', '#e0e0e0']
        )
        bars = alt.Chart(df_domaines).mark_bar(opacity=0.8).encode(
            x=alt.X('Année:O', title=None, axis=alt.Axis(labelAngle=0, format='d')),
            y=alt.Y('Nombre de domaines \\.bj:Q', title='Nombre de Domaines'),
            color=alt.Color('Statut:N', scale=color_scheme, legend=None),
            tooltip=[alt.Tooltip('Année:O', title='Année'), alt.Tooltip('commentaires:N', title='Domaines')]
        )
        df_official_data = df_domaines[df_domaines['Statut'] == 'Officiel']
        line = alt.Chart(df_official_data).mark_line(
            color='orange', point={'color': 'darkorange', 'size': 80, 'filled': True}
        ).encode(x=alt.X('Année:O'), y=alt.Y('Nombre de domaines \\.bj:Q'))
        text_labels = alt.Chart(df_official_data).mark_text(
            align='center', baseline='bottom', dy=-8, color='#0A2940', size=12
        ).encode(x=alt.X('Année:O'), y=alt.Y('Nombre de domaines \\.bj:Q'), text=alt.Text('Nombre de domaines \\.bj:Q', format=','))
        
        chart = (bars + line + text_labels).properties(title='Évolution du Nombre de Domaines .BJ (1996-2025)')
        st.altair_chart(chart, use_container_width=True)

with col_resilience:
    st.markdown("**Indicateurs de Résilience**")
    st.metric(label="Taux de Croissance Annuel (Domaines)", value=data['domain_growth'])
    st.caption("Basé sur les données officielles des deux dernières années disponibles.")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("**Répartition Géographique des Serveurs**")
    df_ns = data['ns_details_df']
    if not df_ns.empty and 'pays' in df_ns.columns and df_ns['pays'].notna().any():
        st.dataframe(df_ns['pays'].value_counts(), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("⚙️ Informations Techniques et Administratives")
col_details, col_admin_rules = st.columns(2, gap="large")

with col_details:
    st.markdown("##### **Détails des Serveurs DNS**")
    st.dataframe(data['ns_details_df'], use_container_width=True, hide_index=True)
with col_admin_rules:
    st.markdown("##### **🏢 Organisation**")
    with st.container(border=True):
        admin_data = data['admin_data']
        for key, value in admin_data.items():
            c1, c2 = st.columns([1,2])
            with c1: st.markdown(f"**{key}**")
            with c2: st.markdown(f": {value}")
    st.markdown("---")
    st.markdown("##### **⚖️ Règles d'Enregistrement**")
    with st.container(border=True):
        policy_data = data['policy_data']
        for key, value in policy_data.items():
            c1, c2 = st.columns([1,2])
            with c1: st.markdown(f"**{key}**")
            with c2:
                if value == "Non":
                    st.markdown(f": <span style='color:red; font-weight:bold;'>{value}</span>", unsafe_allow_html=True)
                elif value == "Oui":
                    st.markdown(f": <span style='color:green; font-weight:bold;'>{value}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f": {value}")
st.markdown('</div>', unsafe_allow_html=True)

# --- Marché mobile et Internet, qualité de service et fractures numériques (données ARCEP BENIN, voir donnees_arcep.py) ---
COULEURS_OPERATEURS = alt.Scale(domain=['MTN', 'MOOV', 'CELTIIS'], range=['#ffcc00', '#018cd1', '#3ada74'])

def fmt(nombre, decimales=0):
    """Formate un nombre à la française : espace pour les milliers, virgule pour les décimales."""
    return f"{nombre:,.{decimales}f}".replace(",", " ").replace(".", ",")

df_marche = data['indicateurs_marche_df']

def indicateur(nom, annee=2025, operateur="Tous"):
    return df_marche[(df_marche['indicateur'] == nom) & (df_marche['annee'] == annee) & (df_marche['operateur'] == operateur)].iloc[0]

st.markdown("---")
st.subheader("📱 Internet, SIM et GSM : le marché en 2025")
sim, mobile, internet_mobile, fixe = (indicateur(nom) for nom in ["Cartes SIM actives", "Abonnés mobiles", "Abonnés Internet mobile", "Abonnés Internet fixe"])
penetration_im, penetration_im_2024 = indicateur("Pénétration Internet mobile"), indicateur("Pénétration Internet mobile", 2024)
cols = st.columns(4)
cols[0].metric("📶 Cartes SIM actives", f"{fmt(sim['valeur'], 2)} M", f"{fmt(sim['variation_pct'], 1)} % sur un an")
cols[1].metric("👥 Abonnés mobiles", fmt(mobile['valeur']), f"Pénétration mobile : {fmt(indicateur('Pénétration mobile')['valeur'], 1)} %", delta_color="off", help="Nombre d'abonnés après élimination des multi-SIM.")
cols[2].metric("🌐 Abonnés Internet mobile", fmt(internet_mobile['valeur']), f"+{fmt(penetration_im['valeur'] - penetration_im_2024['valeur'], 1)} pt : pénétration de {fmt(penetration_im['valeur'], 1)} %")
cols[3].metric("🏠 Abonnés Internet fixe", fmt(fixe['valeur']), f"+{fmt(fixe['variation_pct'], 1)} % sur un an", help=f"Pénétration Internet fixe : {fmt(indicateur('Pénétration Internet fixe')['valeur'], 2)} %")

trafic, voix, arpu, bande_passante = (indicateur(nom) for nom in ["Trafic Internet mobile", "Trafic voix mobile", "ARPU mobile", "Bande passante internationale"])
cols = st.columns(4)
cols[0].metric("📊 Trafic Internet mobile", f"{fmt(trafic['valeur'], 1)} M Go", f"+{fmt(trafic['variation_pct'])} % sur un an")
cols[1].metric("📞 Trafic voix mobile", f"{fmt(voix['valeur'], 2)} Md min", f"+{fmt(voix['variation_pct'], 1)} % sur un an")
cols[2].metric("💰 ARPU mobile mensuel", f"{fmt(arpu['valeur'])} FCFA", help="Revenu moyen mensuel par abonné mobile.")
cols[3].metric("🔗 Bande passante internationale", f"{fmt(bande_passante['valeur'])} Gbps")

col_techno, col_parts = st.columns(2, gap="large")
with col_techno:
    st.markdown("**Abonnements Internet mobile par technologie**")
    df_techno = df_marche[df_marche['indicateur'].str.startswith("Abonnements Internet mobile") & (df_marche['annee'] == 2025)].assign(technologie=lambda d: d['indicateur'].str[-2:])
    barres = alt.Chart(df_techno).mark_bar(color='#00A9E0').encode(
        x=alt.X('technologie:N', title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('valeur:Q', title="% des abonnements"),
        tooltip=[alt.Tooltip('technologie:N', title='Technologie'), alt.Tooltip('valeur:Q', title='Part (%)')]
    )
    etiquettes = barres.mark_text(dy=-8, color='#888888').transform_calculate(etiquette="datum.valeur + ' %'").encode(text='etiquette:N')
    st.altair_chart(barres + etiquettes, use_container_width=True)
with col_parts:
    st.markdown("**Parts de marché en valeur des opérateurs mobiles**")
    df_parts = df_marche[(df_marche['indicateur'] == "Part de marché (valeur)") & (df_marche['annee'] == 2025)]
    ordre = df_parts.sort_values('valeur', ascending=False)['operateur'].tolist()  # un tri '-x' serait ignoré dans un graphique à calques
    barres = alt.Chart(df_parts).mark_bar().encode(
        x=alt.X('valeur:Q', title="Part de marché en valeur (%)"),
        y=alt.Y('operateur:N', title=None, sort=ordre),
        color=alt.Color('operateur:N', scale=COULEURS_OPERATEURS, legend=None),
        tooltip=[alt.Tooltip('operateur:N', title='Opérateur'), alt.Tooltip('valeur:Q', title='Part (%)')]
    )
    etiquettes = alt.Chart(df_parts).mark_text(align='left', dx=4, color='#888888').encode(
        x='valeur:Q', y=alt.Y('operateur:N', sort=ordre), text=alt.Text('valeur:Q', format='.1f'))
    st.altair_chart(barres + etiquettes, use_container_width=True)
st.caption("Source : ARCEP BENIN, Rapport annuel d'activités 2025 (situation au 31 décembre 2025). MTN = SPACETEL BENIN, MOOV = MOOV AFRICA BENIN, CELTIIS = SBIN.")

st.markdown("---")
st.subheader("📡 Qualité de service des réseaux mobiles")
df_qos = data['qos_df']
if df_qos.empty:
    st.info("Les mesures de qualité de service de l'ARCEP sont momentanément indisponibles.")
else:
    col_graphe, col_conformite = st.columns([2, 1], gap="large")
    with col_graphe:
        choix = st.selectbox("Indicateur", df_qos['indicateur'].unique())
        df_choix = df_qos[df_qos['indicateur'] == choix]
        unite = df_choix['unite'].iloc[0]
        st.markdown(f"**{choix} ({unite})**, seuil de conformité en pointillés rouges")
        lignes = alt.Chart(df_choix).mark_line(point=True).encode(
            x=alt.X('date:O', title=None, axis=alt.Axis(labelAngle=0, labelExpr="substring(datum.value, 8, 10) + '/' + substring(datum.value, 5, 7)")),
            y=alt.Y('valeur:Q', title=unite, scale=alt.Scale(zero=False)),
            color=alt.Color('operateur:N', scale=COULEURS_OPERATEURS, title=None, legend=alt.Legend(orient='bottom')),
            tooltip=[alt.Tooltip('date:O', title='Date'), alt.Tooltip('operateur:N', title='Opérateur'), alt.Tooltip('valeur:Q', title=unite)]
        )
        seuil = alt.Chart(df_choix).mark_rule(color='red', strokeDash=[6, 4]).encode(
            y='mean(seuil):Q', tooltip=alt.Tooltip('mean(seuil):Q', title='Seuil de conformité'))
        st.altair_chart(lignes + seuil, use_container_width=True)
    with col_conformite:
        st.markdown("**Moyenne sur la période et conformité**")
        moyennes = df_choix.groupby('operateur', as_index=False).agg(moyenne=('valeur', 'mean'), seuil=('seuil', 'mean'))
        # Le taux de blocage doit rester sous le seuil ; les autres indicateurs doivent l'atteindre.
        conforme = moyennes['moyenne'] <= moyennes['seuil'] if 'blocage' in choix else moyennes['moyenne'] >= moyennes['seuil']
        moyennes['conforme'] = conforme.map({True: "✅ Oui", False: "❌ Non"})
        st.dataframe(moyennes.round(2).rename(columns={'operateur': 'Opérateur', 'moyenne': f'Moyenne ({unite})', 'seuil': f'Seuil ({unite})', 'conforme': 'Conforme'}), hide_index=True, use_container_width=True)
    debut, fin = (pd.to_datetime(d).strftime('%d/%m/%Y') for d in (df_qos['date'].min(), df_qos['date'].max()))
    st.caption(f"Source : ARCEP BENIN, suivi de la qualité de service (mesures du {debut} au {fin}).")

st.markdown("---")
st.subheader("⚖️ Fractures numériques et obstacles à l'accès")
col_genre, col_analyse = st.columns(2, gap="large")
with col_genre:
    st.markdown("**Usage des plateformes numériques selon le genre (2025)**")
    parts_genre = data['usage_plateformes_df'].pivot_table(index=['operateur', 'plateforme'], columns='genre', values='utilisateurs', aggfunc='sum').reset_index()
    parts_genre.columns.name = None
    parts_genre['part_femmes'] = parts_genre['Femme'] / (parts_genre['Femme'] + parts_genre['Homme']) * 100
    barres = alt.Chart(parts_genre).mark_bar().encode(
        x=alt.X('part_femmes:Q', title="Part des femmes parmi les utilisateurs (%)", scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('plateforme:N', title=None, sort=['WhatsApp', 'Facebook', 'TikTok', 'Netflix']),
        yOffset='operateur:N',
        color=alt.Color('operateur:N', scale=COULEURS_OPERATEURS, title=None, legend=alt.Legend(orient='bottom')),
        tooltip=[alt.Tooltip('operateur:N', title='Opérateur'), alt.Tooltip('plateforme:N', title='Plateforme'),
                 alt.Tooltip('part_femmes:Q', title='Part des femmes (%)', format='.1f'),
                 alt.Tooltip('Femme:Q', title='Femmes', format=','), alt.Tooltip('Homme:Q', title='Hommes', format=',')]
    )
    parite = alt.Chart(pd.DataFrame({'parite': [50]})).mark_rule(color='gray', strokeDash=[4, 4]).encode(x='parite:Q')
    st.altair_chart(barres + parite, use_container_width=True)
    st.caption("Source : ARCEP BENIN, rapport annuel 2025 (données des opérateurs). Ligne grise : parité. Données CELTIIS non publiées ; TikTok et Netflix publiés pour MTN uniquement.")
with col_analyse:
    st.markdown("##### Qui est laissé pour compte ?")
    st.markdown(
        "- **Genre** : taux de possession de smartphones et d'adoption plus faibles chez les femmes.\n"
        "- **Géographie** : profonde fracture entre villes et campagnes (infrastructures concentrées à Cotonou et Porto-Novo, départements du nord et zones rurales fortement sous-desservis).\n"
        "- **Éducation et langue** : exclusion liée à un faible niveau d'instruction et à une maîtrise limitée du français et du numérique."
    )
    femmes_whatsapp = parts_genre[parts_genre['plateforme'] == 'WhatsApp'].set_index('operateur')['part_femmes']
    st.info(f"Les données des opérateurs le confirment : les femmes ne représentent que {fmt(femmes_whatsapp['MTN'])} % des utilisateurs de WhatsApp chez MTN et {fmt(femmes_whatsapp['MOOV'])} % chez MOOV.")
    st.markdown("##### Les 3 principaux obstacles à l'accès")
    st.markdown(
        "1. Coût élevé des forfaits de données et des appareils connectés par rapport au revenu médian.\n"
        "2. Illettrisme numérique et linguistique (manque de contenus localisés).\n"
        "3. Faible utilité perçue pour les besoins économiques quotidiens, et inquiétudes liées à la sécurité et à la confiance."
    )