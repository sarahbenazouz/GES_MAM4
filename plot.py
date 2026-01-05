from nicegui import ui
import pandas as pd
import plotly.graph_objects as go

# =============================
# CHARGEMENT & NETTOYAGE
# =============================
df = pd.read_excel("onglet1.xlsx")

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

regions_disponibles = sorted(df["region"].dropna().unique())
secteurs_disponibles = sorted(df["secteur"].dropna().unique())
gaz_disponibles = sorted(df["gaz"].dropna().unique())

# =============================
# FONCTION DE MISE À JOUR (agrégée par région)
# =============================

def update_graph():
    fig = go.Figure()

    # Filtrer les données selon les sélections
    data_filtre = df[
        df["region"].isin(select_region.value) &
        df["secteur"].isin(select_secteurs.value) &
        df["gaz"].isin(select_gaz.value)
    ]

    # Agrégation par région (somme des émissions de tous les pays)
    data_agregee = (
        data_filtre
        .groupby(["region", "secteur", "gaz"])[annees]
        .sum()
        .reset_index()
    )

    # Tracer une seule courbe par région
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
            text="Comparaison des émissions de GES par région",
            x=0.5,
            font=dict(size=22, family="Arial Black")
        ),
        xaxis_title="<b>Année</b>",
        yaxis_title="<b>Émissions totales (MtCO₂e)</b>",
        template="plotly_white",
        legend_title="<b>Région | Secteur | Gaz</b>",
        height=650,
        margin=dict(t=80, l=60, r=40, b=60)
    )

    graph.update_figure(fig)

# =============================
# INTERFACE VISUELLE
# =============================
ui.add_css("""
body {
    background: linear-gradient(135deg, #e0f2fe, #fef9c3);
    font-family: 'Segoe UI', sans-serif;
}
""")

with ui.column().classes("w-full"):

    # Bandeau titre
    with ui.row().classes(
        "w-full px-10 py-6 bg-gradient-to-r from-blue-600 to-indigo-700 shadow-xl"
    ):
        ui.label("DASHBOARD GES").classes(
            "text-white text-4xl font-extrabold tracking-wide"
        )
        ui.label("Analyse régionale – sectorielle – par gaz").classes(
            "text-blue-100 text-lg ml-4 self-end"
        )

    # Barre de filtres
    with ui.card().classes(
        "w-full rounded-none shadow-md bg-white px-8 py-6"
    ):
        ui.label("FILTRES DE SÉLECTION").classes(
            "text-xl font-bold text-indigo-700 mb-4"
        )

        with ui.row().classes("w-full gap-8"):
            select_region = ui.select(
                options=regions_disponibles,
                value=regions_disponibles[:2],
                multiple=True,
                label="🌍 RÉGIONS"
            ).classes("w-1/3")

            select_secteurs = ui.select(
                options=secteurs_disponibles,
                value=secteurs_disponibles[:1],
                multiple=True,
                label="🏭 SECTEURS"
            ).classes("w-1/3")

            select_gaz = ui.select(
                options=gaz_disponibles,
                value=gaz_disponibles[:1],
                multiple=True,
                label="💨 GAZ"
            ).classes("w-1/3")

    # Zone graphique
    with ui.card().classes(
        "w-full p-6 bg-white shadow-xl"
    ):
        graph = ui.plotly(go.Figure()).classes("w-full h-[650px]")

    # Relier filtres à la mise à jour
    select_region.on("update:model-value", lambda e: update_graph())
    select_secteurs.on("update:model-value", lambda e: update_graph())
    select_gaz.on("update:model-value", lambda e: update_graph())

# =============================
# LANCEMENT
# =============================
update_graph()
ui.run()
