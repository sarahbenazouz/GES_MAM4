import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =============================
# CONFIG STREAMLIT
# =============================
st.set_page_config(
    page_title="Dashboard GES",
    layout="wide"
)

# =============================
# TITRE
# =============================
st.title("🌍 Dashboard des émissions de GES")
st.subheader("Analyse régionale – sectorielle – par gaz")

st.markdown("---")

# =============================
# CHARGEMENT & NETTOYAGE
# =============================

@st.cache_data
def load_data():
    df = pd.read_excel("projections.xlsx", sheet_name=0)

    df = df.rename(columns={
        "Sector": "secteur",
        "Gas": "gaz",
        "region": "region"
    })

    df["region"] = df["region"].astype(str)
    df["secteur"] = df["secteur"].astype(str)
    df["gaz"] = df["gaz"].astype(str)

    # Colonnes années
    annees = [
        c for c in df.columns
        if isinstance(c, str) and c.isdigit() and 1900 <= int(c) <= 2100
    ]
    annees = sorted(annees, key=int)

    return df, annees


df, annees = load_data()

regions_disponibles = sorted(df["region"].dropna().unique())
secteurs_disponibles = sorted(df["secteur"].dropna().unique())
gaz_disponibles = sorted(df["gaz"].dropna().unique())

# =============================
# SIDEBAR : FILTRES
# =============================

st.sidebar.header("🎛️ Filtres")

select_region = st.sidebar.multiselect(
    "🌍 Régions",
    options=regions_disponibles,
    default=regions_disponibles[:2]
)

select_secteurs = st.sidebar.multiselect(
    "🏭 Secteurs",
    options=secteurs_disponibles,
    default=secteurs_disponibles[:1]
)

select_gaz = st.sidebar.multiselect(
    "💨 Gaz",
    options=gaz_disponibles,
    default=gaz_disponibles[:1]
)

# Sécurité si rien n'est sélectionné
if not select_region or not select_secteurs or not select_gaz:
    st.warning("⚠️ Merci de sélectionner au moins une région, un secteur et un gaz.")
    st.stop()

# =============================
# FILTRAGE & AGRÉGATION
# =============================

data_filtre = df[
    df["region"].isin(select_region) &
    df["secteur"].isin(select_secteurs) &
    df["gaz"].isin(select_gaz)
]

data_agregee = (
    data_filtre
    .groupby(["region", "secteur", "gaz"])[annees]
    .sum()
    .reset_index()
)

# =============================
# GRAPHIQUE
# =============================

fig = go.Figure()

for _, row in data_agregee.iterrows():
    fig.add_trace(go.Scatter(
        x=[int(a) for a in annees],
        y=[row[a] for a in annees],
        mode="lines+markers",
        line=dict(width=3),
        marker=dict(size=7),
        name=f"{row['region']} | {row['secteur']} | {row['gaz']}"
    ))

fig.update_layout(
    title=dict(
        text="Comparaison des émissions de GES",
        x=0.5,
        font=dict(size=22)
    ),
    xaxis_title="Année",
    yaxis_title="Émissions totales (MtCO₂e)",
    template="plotly_white",
    legend_title="Région | Secteur | Gaz",
    height=650
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# INFO PÉDAGOGIQUE
# =============================
with st.expander("ℹ️ À propos de ce graphique"):
    st.write("""
    Ce graphique montre l’évolution des émissions de gaz à effet de serre
    agrégées par **région**, **secteur** et **type de gaz** à partir des données
    de Climate Watch.
    
    L’objectif est de comparer différentes trajectoires selon les choix
    de périmètre d’analyse.
    """)

#pour lancer 
#py -m streamlit run plot_streamlit.py
