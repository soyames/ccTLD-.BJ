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
    st.markdown("- **Rapports Annuels ARCEP**\n- **[IANA](https://www.iana.org/domains/root/db/bj.html)** : Informations sur la délégation et les serveurs de noms.**\n- **[DomainNameStat](https://domainnamestat.com/statistics/tld/bj)** : Estimation du nombre de domaines.**\n- **[TLD-List](https://tld-list.com/tld/bj)** : Politiques et informations sur le registre DNS.**")
    st.markdown("---")
    st.link_button("Retour au Dashboard Principal", "/URL_VERS_LE_DASHBOARD_PRINCIPAL", type="primary")
    st.markdown("---")

st.header("ccTLD .BJ")
st.markdown("Analyse de l'infrastructure, des politiques et de l'évolution du domaine national du Bénin.")

@st.cache_data(ttl=3600)
def charger_donnees():
    if EN_NAVIGATEUR:
        data = json.loads((Path(__file__).parent / "bj_snapshot.json").read_text(encoding="utf-8"))
        data['domaines_historique_df'] = pd.DataFrame(data['domaines_historique_df'])
        data['ns_details_df'] = pd.DataFrame(data['ns_details_df'])
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