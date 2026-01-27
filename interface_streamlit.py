import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Trajectoires GES", layout="wide")

# =====================================================
# INITIALISATION DE LA PAGE
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "accueil"

# =====================================================
# FONCTIONS DE CHARGEMENT
# =====================================================
@st.cache_data
def load_sheet_0():
    df = pd.read_excel("projections.xlsx", sheet_name=0)

    df = df.rename(columns={
        "Sector": "secteur",
        "Gas": "gaz",
        "region": "region"
    })

    annees = sorted(
        [c for c in df.columns if str(c).isdigit()],
        key=int
    )
    return df, annees


@st.cache_data
def load_sheet_2():
    df = pd.read_excel("projections.xlsx", sheet_name=2)

    # Colonnes années
    annees = sorted(
        [c for c in df.columns if str(c).isdigit()],
        key=int
    )

    # Conversion virgule → point
    for col in annees:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )

    return df, annees

# =====================================================
# PAGE D’ACCUEIL
# =====================================================
if st.session_state.page == "accueil":

    st.title("🌍 Trajectoires des émissions de GES")
    st.markdown("### Choisissez un scénario")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📈 Tendance sans action", use_container_width=True):
            st.session_state.page = "tendance"
            st.rerun()

    with col2:
        if st.button("🌡️ Objectif 1,5 °C", use_container_width=True):
            st.session_state.page = "objectif"
            st.rerun()

# =====================================================
# PAGE 1 : TENDANCE SANS ACTION
# =====================================================
elif st.session_state.page == "tendance":

    st.button("⬅️ Retour à l’accueil", on_click=lambda: st.session_state.update({"page": "accueil"}))

    st.title("📈 Tendance des émissions – Sans action")

    df, annees = load_sheet_0()

    regions = sorted(df["region"].dropna().unique())
    secteurs = sorted(df["secteur"].dropna().unique())
    gazs = sorted(df["gaz"].dropna().unique())

    with st.sidebar:
        st.header("Filtres")
        reg = st.multiselect("Régions", regions, default=regions[:2])
        sec = st.multiselect("Secteurs", secteurs, default=secteurs[:1])
        gaz = st.multiselect("Gaz", gazs, default=gazs[:1])

    df_f = df[
        df["region"].isin(reg) &
        df["secteur"].isin(sec) &
        df["gaz"].isin(gaz)
    ]

    df_ag = df_f.groupby(["region", "secteur", "gaz"])[annees].sum().reset_index()

    fig = go.Figure()

    for _, row in df_ag.iterrows():
        fig.add_trace(go.Scatter(
            x=[int(a) for a in annees],
            y=[row[a] for a in annees],
            mode="lines+markers",
            name=f"{row['region']} | {row['secteur']} | {row['gaz']}"
        ))

    fig.update_layout(
        title="Évolution des émissions – scénario sans action",
        xaxis_title="Année",
        yaxis_title="MtCO₂e",
        template="plotly_white",
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# PAGE 2 : OBJECTIF 1.5 °C
# =====================================================
elif st.session_state.page == "objectif":

    st.button("⬅️ Retour à l’accueil", on_click=lambda: st.session_state.update({"page": "accueil"}))

    st.title("🌡️ Trajectoire compatible avec l’objectif 1,5 °C")

    df, annees = load_sheet_2()

    fig = go.Figure()

    for _, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[int(a) for a in annees],
            y=[row[a] for a in annees],
            mode="lines+markers",
            name=row["Country"]
        ))

    fig.update_layout(
        title="Évolution des émissions – scénario 1,5 °C",
        xaxis_title="Année",
        yaxis_title="MtCO₂e",
        template="plotly_white",
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("ℹ️ Méthodologie"):
        st.write("""
        Cette trajectoire représente une évolution compatible avec l’objectif
        de limitation du réchauffement climatique à **1,5 °C**.
        Les courbes correspondent aux grands ensembles régionaux.
        """)



