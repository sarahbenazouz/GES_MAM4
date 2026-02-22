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
def load_tendance():
    df = pd.read_excel("projections.xlsx", sheet_name="tendance")
    
    # Identifier les colonnes années
    annees = sorted(
        [c for c in df.columns if str(c).isdigit()],
        key=int
    )
    return df, annees


@st.cache_data
def load_proj_15_inter():
    df = pd.read_excel("projections.xlsx", sheet_name="proj 1,5_inter")

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
def load_proj_15():
    df = pd.read_excel("projections.xlsx", sheet_name="proj 1,5")

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
def load_tendance_1_5():
    df = pd.read_excel("projections.xlsx", sheet_name="tendance region1.5")

    # Nettoyer la colonne région : supprimer les NaN et normaliser
    df["région"] = df["région"].astype(str).str.strip()
    df = df[df["région"] != "nan"]  # enlever les lignes sans région

    # Colonnes années = colonnes numériques
    annees = [col for col in df.columns if str(col).isdigit()]

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

    st.title("🌍 Trajectoires des émissions de gaz à effet de serre")
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

        st.markdown("---")

    st.subheader("📘 À propos de cette application")

    st.markdown("""
    Cette interface permet d'explorer différentes trajectoires d'émissions
    de gaz à effet de serre (GES) selon plusieurs scénarios :

    - 📈 Tendance sans action  
    - 🌡️ Objectif compatible avec 1,5°C  
    - 📜 Engagements climatiques nationaux (NDC)  
    - 🧩 Simulation de leviers d'atténuation  

    L'objectif est de comprendre comment les choix politiques
    influencent les trajectoires climatiques à long terme.
    """)
 

    st.info("""
    🔎 Pourquoi c’est important ?

    Pour limiter le réchauffement à 1,5°C, les émissions mondiales
    doivent diminuer rapidement dès cette décennie.
    Les scénarios permettent d’évaluer si les trajectoires actuelles
    sont compatibles avec cet objectif.
    """)

    st.warning("""
    ❓ Question à explorer :

    Les engagements actuels sont-ils suffisants pour respecter
    l'objectif 1,5°C ?

    Testez les scénarios pour le découvrir.
    """)

# =====================================================
# PAGE 1 : TENDANCE SANS ACTION
# =====================================================

elif st.session_state.page == "tendance":

    st.button(
        "⬅️ Retour à l'accueil",
        on_click=lambda: st.session_state.update({"page": "accueil"})
    )

    st.title("📈 Tendance des émissions — Sans action")

    df, annees = load_tendance()

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
# PAGE 2 : OBJECTIF 1.5 °C vs tendance sans action
# =====================================================


elif st.session_state.page == "objectif":

    st.button(
        "⬅️ Retour à l'accueil",
        on_click=lambda: st.session_state.update({"page": "accueil"})
    )

    st.title("🌡️ Objectif 1.5°C - vs Tendance sans action")

    # ---- Chargement des données
    df, annees = load_proj_15_inter()
    df_tendance, annees_tendance = load_tendance_1_5()

    # Colonnes années
    annees = sorted(
        [c for c in df.columns if str(c).isdigit()],
        key=int
    )

    regions = sorted(df["région"].dropna().unique())
    secteurs = sorted(df["Sector"].dropna().unique())
    gazs = sorted(df["Gas"].dropna().unique())

    # =============================
    # SIDEBAR
    # =============================
    with st.sidebar:
        st.header("Paramètres scénario 1.5°C")

        reg = st.multiselect("Régions", regions, default=regions)
        sec = st.multiselect("Secteurs", secteurs, default=[secteurs[0]])
        gaz = st.multiselect("Gaz", gazs, default=[gazs[0]])

        # Bouton affichage tendance
        afficher_tendance = st.toggle("📈 Afficher la tendance sans action", value=True)

        st.markdown("### Paramètres par région")

        params_regions = {}

        for r in reg:
            st.markdown("---")
            st.markdown(f"**{r}**")

            annee_r = st.slider(
                f"Année d'application - {r}",
                2020, 2100, 2030,
                key=f"annee_{r}"
            )

            taux_r = st.number_input(
                f"Taux annuel (%) - {r}",
                min_value=-50.0,
                max_value=50.0,
                value=-2.0,
                step=0.1,
                key=f"taux_{r}"
            )

            ####message de warning si on chosit un taux>0#####
            if taux_r > 0:
                st.warning(f"""
                ⚠️ Attention : avec un taux positif pour {r},
                les émissions continueront d'augmenter.
        
                Cela n’est pas compatible avec une trajectoire 1,5°C.
                """)

            params_regions[r] = {
                "annee": annee_r,
                "taux": taux_r / 100
            }

    if not reg or not sec or not gaz:
        st.warning("Sélectionnez au moins une région, un secteur et un gaz.")
        st.stop()

    # =============================
    # FILTRAGE 1.5 °C
    # =============================
    df_f = df[
        df["région"].isin(reg) &
        df["Sector"].isin(sec) &
        df["Gas"].isin(gaz)
    ]

    if df_f.empty:
        st.warning("Aucune donnée trouvée.")
        st.stop()

    # =============================
    # FILTRAGE TENDANCE
    # =============================
    df_tendance_f = df_tendance[
        df_tendance["région"].isin(reg) &
        df_tendance["Sector"].isin(sec) &
        df_tendance["Gas"].isin(gaz)
    ]

    df_tendance_ag = (
        df_tendance_f
        .groupby("région")[annees_tendance]
        .sum()
        .reset_index()
    )

    # =============================
    # PALETTE DE COULEURS PAR RÉGION
    # =============================
    palette = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
        "#9467bd", "#8c564b", "#e377c2", "#7f7f7f",
        "#bcbd22", "#17becf", "#aec7e8", "#ffbb78"
    ]
    couleur_par_region = {r: palette[i % len(palette)] for i, r in enumerate(sorted(reg))}

    # =============================
    # GRAPHIQUE
    # =============================
    fig = go.Figure()

    for _, row in df_f.iterrows():

        region_row = row["région"]
        couleur = couleur_par_region[region_row]

        # --- TCAM 2010-2019
        val_2010 = row["2010"]
        val_2019 = row["2019"]

        if val_2010 == 0:
            continue

        tcam = ((val_2019 / val_2010) ** (1/9)) - 1

        emissions = row[annees]

        derniere_valeur = emissions.iloc[-1]
        derniere_annee = int(annees[-1])

        annees_proj = list(range(derniere_annee + 1, 2101))

        valeur = derniere_valeur
        proj_vals = []

        annee_changement = params_regions[region_row]["annee"]
        nouveau_taux = params_regions[region_row]["taux"]

        for an in annees_proj:
            if an < annee_changement:
                taux = tcam
            else:
                taux = nouveau_taux

            valeur = valeur * (1 + taux)
            proj_vals.append(valeur)

        ######msg de prevention sur le fait que si la veleur en 2100>à la valeur d'avant =>pb####
        if proj_vals[-1] > emissions.iloc[-1]:
            st.error(f"""
            🚨 Dans le scénario pour {region_row},
            les émissions en 2100 sont supérieures au niveau actuel.
            
            Ce scénario est incompatible avec une stabilisation climatique.
            """)

        # Historique — ligne pleine, même couleur que la projection
        fig.add_trace(go.Scatter(
            x=[int(a) for a in annees],
            y=emissions.values,
            mode="lines",
            line=dict(color=couleur, width=2),
            name=f"{region_row} | {row['Sector']} | {row['Gas']} (hist)"
        ))

        # Projection — tirets, même couleur
        fig.add_trace(go.Scatter(
            x=annees_proj,
            y=proj_vals,
            mode="lines",
            line=dict(color=couleur, width=2, dash="dash"),
            name=f"{region_row} | {row['Sector']} | {row['Gas']} (proj)"
        ))

    # ---------- TENDANCE (conditionnelle) ----------
    if afficher_tendance:
        for _, row in df_tendance_ag.iterrows():
            region_row = row["région"]
            couleur = couleur_par_region.get(region_row, "#888888")

            fig.add_trace(go.Scatter(
                x=[int(a) for a in annees_tendance],
                y=[row[a] for a in annees_tendance],
                mode="lines",
                line=dict(color=couleur, width=3, dash="dot"),
                name=f"{region_row} — tendance"
            ))

    fig.update_layout(
        title="Projection Objectif 1.5°C — Paramètres personnalisés par région vs Tendance sans action",
        xaxis_title="Année",
        yaxis_title="MtCO₂e",
        template="plotly_white",
        height=700
    )

    fig.update_yaxes(rangemode="tozero")

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    with st.expander("ℹ️ Comment est calculée la projection ?"):
        st.write("""
        - Le taux de croissance annuel moyen (TCAM) est calculé sur la période 2010-2019.
        - Un nouveau taux est appliqué à partir de l’année choisie.
        - Formule utilisée :
    
        Emissions(t+1) = Emissions(t) × (1 + taux)
    
        ⚠️ Une trajectoire compatible 1,5°C implique une baisse rapide
        et continue des émissions mondiales.
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
    df_tendance, annees = load_tendance()
    df_objectif, annees_obj = load_proj_15()

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