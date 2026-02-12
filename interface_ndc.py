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
    
    # Identifier les colonnes années
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
        [c for c in df.columns if isinstance(c, int) or (isinstance(c, str) and c.isdigit())],
        key=lambda x: int(x)
    )

    # Conversion virgule → point si nécessaire
    for col in annees:
        if df[col].dtype == object:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .astype(float)
            )

    return df, annees


@st.cache_data
def load_ndc():
    df = pd.read_excel("projections.xlsx", sheet_name="NDC")

    # Colonnes années : détecte celles qui sont numériques et entre 1990-2100
    annees = [c for c in df.columns if (isinstance(c, int) or (isinstance(c, str) and c.isdigit())) and 1990 <= int(c) <= 2100]

    # Colonnes utiles
    cols_utiles = ["Region TIAM", "Substance"] + annees
    df = df[cols_utiles]

    # Conversion virgule -> point et forcer NaN
    for col in annees:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ".", regex=False),
            errors='coerce'
        )

    df["Region TIAM"] = df["Region TIAM"].astype(str)
    df["Substance"] = df["Substance"].astype(str)

    return df, annees


# =====================================================
# PAGE D'ACCUEIL
# =====================================================
if st.session_state.page == "accueil":

    st.title("🌍 Trajectoires des émissions de GES")
    st.markdown("### Choisissez un scénario")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📈 Tendance sans action", use_container_width=True):
            st.session_state.page = "tendance"
            st.rerun()

    with col2:
        if st.button("🌡️ Objectif 1,5 °C", use_container_width=True):
            st.session_state.page = "objectif"
            st.rerun()

    with col3:
        if st.button("📜 NDC (engagements nationaux)", use_container_width=True):
            st.session_state.page = "ndc"
            st.rerun()

    with col4:
        if st.button("🧰 Leviers", use_container_width=True):
            st.session_state.page = "leviers"
            st.rerun()


# =====================================================
# PAGE 1 : TENDANCE SANS ACTION
# =====================================================

elif st.session_state.page == "tendance":

    st.button(
        "⬅️ Retour à l'accueil",
        on_click=lambda: st.session_state.update({"page": "accueil"})
    )

    st.title("📈 Tendance des émissions — Sans action")

    df, annees = load_sheet_0()

    regions = sorted(df["region"].dropna().unique())
    secteurs = sorted(df["Sector"].dropna().unique())
    gazs = sorted(df["Gas"].dropna().unique())

    # ➜ Ajouter option All GHG
    gazs_with_all = ["All GHG"] + gazs

    # =============================
    # SIDEBAR
    # =============================
    with st.sidebar:
        st.header("Filtres")

        reg = st.multiselect(
            "Régions",
            regions,
            default=regions[:2] if len(regions) >= 2 else regions
        )

        sec = st.multiselect(
            "Secteurs",
            secteurs,
            default=secteurs[:1] if len(secteurs) >= 1 else secteurs
        )

        gaz = st.multiselect(
            "Gaz",
            gazs_with_all,
            default=["All GHG"]
        )

    # Sécurité minimale
    if not reg or not sec or not gaz:
        st.warning("Veuillez sélectionner au moins une région, un secteur et un gaz.")
        st.stop()

    # =============================
    # FILTRAGE BASE (sans gaz)
    # =============================
    df_f = df[
        df["region"].isin(reg) &
        df["Sector"].isin(sec)
    ]

    df_list = []

    # =============================
    # 1️⃣ CAS ALL GHG
    # =============================
    if "All GHG" in gaz:

        df_all = (
            df_f.groupby(["region", "Sector"])[annees]
            .sum()
            .reset_index()
        )

        df_all["Gas"] = "All GHG"

        df_list.append(df_all)

    # =============================
    # 2️⃣ GAZ SPÉCIFIQUES
    # =============================
    gaz_specifiques = [g for g in gaz if g != "All GHG"]

    if gaz_specifiques:

        df_spec = df_f[df_f["Gas"].isin(gaz_specifiques)]

        df_spec = (
            df_spec.groupby(["region", "Sector", "Gas"])[annees]
            .sum()
            .reset_index()
        )

        df_list.append(df_spec)

    # Combiner les résultats
    if df_list:
        df_ag = pd.concat(df_list, ignore_index=True)
    else:
        st.warning("Aucune donnée disponible.")
        st.stop()

    # =============================
    # GRAPHIQUE
    # =============================
    fig = go.Figure()

    for _, row in df_ag.iterrows():

        line_width = 4 if row["Gas"] == "All GHG" else 2

        fig.add_trace(go.Scatter(
            x=[int(a) for a in annees],
            y=[row[a] for a in annees],
            mode="lines+markers",
            name=f"{row['region']} | {row['Sector']} | {row['Gas']}",
            line=dict(width=line_width)
        ))

    fig.update_layout(
        title="Évolution des émissions — scénario sans action",
        xaxis_title="Année",
        yaxis_title="MtCO₂e",
        template="plotly_white",
        height=650,
        legend_title="Région | Secteur | Gaz"
    )

    st.plotly_chart(fig, use_container_width=True)



# =====================================================
# PAGE 2 : OBJECTIF 1.5 °C
# =====================================================
elif st.session_state.page == "objectif":

    st.button("⬅️ Retour à l'accueil", on_click=lambda: st.session_state.update({"page": "accueil"}))

    st.title("🌡️ Trajectoire compatible avec l'objectif 1,5 °C")

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
        title="Évolution des émissions — scénario 1,5 °C",
        xaxis_title="Année",
        yaxis_title="MtCO₂e",
        template="plotly_white",
        height=650
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("ℹ️ Méthodologie"):
        st.write("""
        Cette trajectoire représente une évolution compatible avec l'objectif
        de limitation du réchauffement climatique à **1,5 °C**.
        Les courbes correspondent aux grands ensembles régionaux.
        """)


# =====================================================
# PAGE 3 : NDC
# =====================================================
elif st.session_state.page == "ndc":

    st.button(
        "⬅️ Retour à l'accueil",
        on_click=lambda: st.session_state.update({"page": "accueil"})
    )

    st.title("📜 Trajectoires des émissions — NDC")

    df, annees = load_ndc()

    regions = sorted(df["Region TIAM"].dropna().unique())
    substances = sorted(df["Substance"].dropna().unique())

    with st.sidebar:
        st.header("Filtres NDC")
        reg = st.multiselect(
            "Régions (TIAM)",
            regions,
            default=regions[:2] if len(regions) >= 2 else regions
        )
        sub = st.multiselect(
            "Substances",
            substances,
            default=substances[:1] if len(substances) >= 1 else substances
        )

    if not reg or not sub:
        st.warning("Veuillez sélectionner au moins une région et une substance.")
        st.stop()

    df_f = df[
        df["Region TIAM"].isin(reg) &
        df["Substance"].isin(sub)
    ]

    fig = go.Figure()

    for _, row in df_f.iterrows():
        fig.add_trace(go.Scatter(
            x=[int(a) for a in annees],
            y=[row[a] for a in annees],
            mode="lines+markers",
            name=f"{row['Region TIAM']} | {row['Substance']}"
        ))

    fig.update_layout(
        title="Évolution des émissions selon les NDC",
        xaxis_title="Année",
        yaxis_title="MtCO₂e",
        template="plotly_white",
        height=650,
        legend_title="Région | Substance"
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("ℹ️ À propos des NDC"):
        st.write("""
        Les **NDC (Nationally Determined Contributions)** représentent
        les engagements climatiques déclarés par les pays.

        Les trajectoires présentées ici traduisent ces engagements
        sans hypothèse supplémentaire de renforcement des politiques.
        """)


# =====================================================
# PAGE 4 : LEVIERS (COMPARAISON WORLD)
# =====================================================
elif st.session_state.page == "leviers":

    st.button(
        "⬅️ Retour à l'accueil",
        on_click=lambda: st.session_state.update({"page": "accueil"})
    )

    st.title("🧩 Leviers d'atténuation — comparaison WORLD")

    # =============================
    # CHARGEMENT DES DONNÉES
    # =============================
    df_tendance, annees = load_sheet_0()
    df_objectif, annees_obj = load_sheet_2()

    # =============================
    # FILTRAGE : WORLD + TOTAL INCLUDING LUCF + 4 GAZ
    # =============================
    
    # Liste des 4 gaz à additionner
    gaz_liste = ["CO2", "CH4", "N2O", "F-Gas"]
    
    # Filtrer : World + Total including LUCF + les 4 gaz
    df_world_tendance = df_tendance[
        (df_tendance["Country"] == "World") &
        (df_tendance["Sector"] == "Total including LUCF") &
        (df_tendance["Gas"].isin(gaz_liste))
    ]

    if df_world_tendance.empty:
        st.error(f"❌ Aucune donnée trouvée pour World / Total including LUCF / {gaz_liste}")
        st.warning("Veuillez vérifier la structure de vos données.")
        st.stop()

    # Afficher les données filtrées pour debug
    st.write(f"**{len(df_world_tendance)} lignes trouvées** (1 par gaz) :")
    st.dataframe(df_world_tendance[["Country", "Sector", "Gas"]])

    # Somme des 4 gaz pour chaque année
    emissions_monde = df_world_tendance[annees].sum()

    # =============================
    # PARAMÈTRES DU LEVIER
    # =============================
    with st.sidebar:
        st.header("Paramètres du levier")
        ANNEE_DEBUT = st.slider("Année de début", 2020, 2030, 2025)
        ANNEE_FIN = st.slider("Année de fin", 2030, 2050, 2040)
        REDUCTION_CIBLE = st.slider("Réduction cible (%)", 0, 100, 30) / 100

    facteurs = []
    for annee in map(int, annees):
        if annee < ANNEE_DEBUT:
            facteurs.append(0)
        elif annee > ANNEE_FIN:
            facteurs.append(REDUCTION_CIBLE)
        else:
            facteurs.append(
                REDUCTION_CIBLE *
                (annee - ANNEE_DEBUT) /
                (ANNEE_FIN - ANNEE_DEBUT)
            )

    facteurs = pd.Series(facteurs, index=annees)
    emissions_avec_levier = emissions_monde * (1 - facteurs)

    # =============================
    # OBJECTIF 1,5 °C — WORLD
    # =============================
    df_world_obj = df_objectif[df_objectif["Country"].str.upper() == "WORLD"]

    if df_world_obj.empty:
        st.warning("⚠️ Ligne 'WORLD' introuvable dans les données objectif 1,5 °C.")
        st.info("Le graphique affichera uniquement la tendance et le levier.")
        objectif_monde = None
    else:
        objectif_monde = df_world_obj[annees_obj].iloc[0]

    # =============================
    # GRAPHIQUE
    # =============================
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[int(a) for a in annees],
        y=emissions_monde.values,
        mode="lines",
        name="WORLD — sans action (tendance)",
        line=dict(width=4, color="red")
    ))

    fig.add_trace(go.Scatter(
        x=[int(a) for a in annees],
        y=emissions_avec_levier.values,
        mode="lines",
        name=f"WORLD — avec levier (-{int(REDUCTION_CIBLE*100)}% en {ANNEE_FIN})",
        line=dict(width=4, dash="dash", color="orange")
    ))

    if objectif_monde is not None:
        fig.add_trace(go.Scatter(
            x=[int(a) for a in annees_obj],
            y=objectif_monde.values,
            mode="lines",
            name="Objectif 1,5 °C — WORLD",
            line=dict(width=5, color="green")
        ))

    fig.update_layout(
        title="Comparaison WORLD — levier vs objectif 1,5 °C",
        xaxis_title="Année",
        yaxis_title="MtCO₂e",
        template="plotly_white",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # =============================
    # INFORMATIONS DÉTAILLÉES
    # =============================
    with st.expander("ℹ️ Détails du calcul"):
        st.write(f"""
        **Données utilisées :**
        - Région : WORLD
        - Catégorie : Total including LUCF
        - Gaz additionnés : {', '.join(gaz_liste)}
        
        **Levier appliqué :**
        - Réduction progressive de {ANNEE_DEBUT} à {ANNEE_FIN}
        - Réduction cible : {REDUCTION_CIBLE*100:.0f}% en {ANNEE_FIN}
        
        **Émissions totales en 2025 :** {emissions_monde.loc['2025']:.2f} MtCO₂e
        **Émissions avec levier en 2040 :** {emissions_avec_levier.loc['2040']:.2f} MtCO₂e
        """)
    
    with st.expander("📊 Données détaillées par gaz"):
        # Créer un tableau récapitulatif par gaz
        recap_gaz = []
        for gaz in gaz_liste:
            ligne_gaz = df_world_tendance[df_world_tendance["Gas"] == gaz]
            if not ligne_gaz.empty:
                recap_gaz.append({
                    "Gaz": gaz,
                    "2025": ligne_gaz['2025'].iloc[0],
                    "2030": ligne_gaz['2030'].iloc[0],
                    "2040": ligne_gaz['2040'].iloc[0],
                    "2050": ligne_gaz['2050'].iloc[0]
                })
        
        df_recap = pd.DataFrame(recap_gaz)
        st.dataframe(df_recap)