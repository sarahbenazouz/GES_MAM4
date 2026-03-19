# GES_MAM4

# GES_MAM4
# Simulation interactive des trajectoires d'émissions de GES

Application web interactive permettant de visualiser et comparer différentes trajectoires d'émissions de gaz à effet de serre (GES) selon plusieurs scénarios climatiques.

---

##  Présentation

Cet outil propose quatre modules principaux :

- ** Tendance sans action** — projection des émissions selon les dynamiques historiques, sans politique d'atténuation
- **Objectif 1,5 °C** — trajectoire compatible avec la limite de réchauffement de l'Accord de Paris
- **NDC (Engagements nationaux)** — visualisation des trajectoires issues des engagements formels des pays signataires
- ** Leviers d'atténuation** — simulation de l'impact de changements comportementaux (alimentation, transport aérien) sur les émissions européennes

---

##  Structure du projet

```
├── interface.py       # Application principale Streamlit
├── projections.xlsx       # Données sources (Climate Watch)
│   ├── tendance           # Données de projection tendancielle
│   ├── proj 1,5           # Trajectoire objectif 1,5 °C
│   ├── proj 1,5_inter     # Trajectoire 1,5 °C (interpolée)
│   ├── tendance region1.5 # Données régionales pour comparaison
│   └── NDC                # Engagements nationaux par région
└── README.md
```

---

##  Installation

### Prérequis

- Python 3.9 ou supérieur
- pip

### Dépendances

```bash
pip install streamlit pandas plotly openpyxl
```

### Lancement

```bash
streamlit run interface_ndc.py
```

L'application s'ouvre automatiquement dans le navigateur à l'adresse `http://localhost:8501`.

>  Le fichier `projections.xlsx` doit se trouver dans le même répertoire que `interface.py`.

---

##  Données

Les données proviennent de la base **Climate Watch** (téléchargeable au format Excel).

Elles sont organisées par :
- **Pays** 
- **Secteur** (ex : Énergie, Agriculture, Transport…)
- **Gaz** : CO₂, CH₄, N₂O, F-Gas
- **Années** : 1990–2100

Les étapes de prétraitement appliquées au chargement :
- Nettoyage des noms de colonnes
- Conversion des séparateurs décimaux (point → virgule)
- Agrégation multi-gaz (`All GHG`)
- Filtrage des lignes vides ou invalides

---

##  Méthodes de calcul

### Trajectoire tendancielle

Basée sur le **taux de croissance annuel moyen (TCAM)** calculé sur deux périodes historiques :

| Horizon de projection | Période de référence |
|-----------------------|----------------------|
| 2023 – 2032           | 2000 – 2010          |
| 2033 – 2050           | 2010 – 2019          |

```
TCAM = (Vf / Vd)^(1/n) - 1
Vt+1 = Vt × (1 + TCAM)
```

En cas de valeur nulle ou d'erreur de calcul, le TCAM est automatiquement recalculé sur une période ajustée, ou fixé à 0.

### Trajectoire 1,5 °C

Application d'un taux de réduction annuel négatif `r` à partir d'une année de départ :

```
Vt+1 = Vt × (1 + r)
```

Plusieurs rythmes de décarbonation peuvent être simulés.

### NDC

Les trajectoires NDC sont **directement issues des tableaux excel. Elles sont filtrables par région et par substance.

### Leviers d'atténuation (Europe)

Deux leviers sont modélisés :

** Alimentation **

| Type de repas       | Émissions (kg CO₂e) | Source                          |
|---------------------|---------------------|---------------------------------|
| Repas carné moyen   | 2,46                | Calcul pondéré (Eurostat)       |
| Repas végétarien    | 0,51                | ADEME                           |

Baseline : 25 % de repas végétariens (CBS Pays-Bas, 2023).

```
ΔE = (pVG_cible − pVG_actuel) × Nrepas × (EM_viande − EM_VG) / 10⁹
```
** Avion **

## ⚠️ Levier report modal avion-train — Données provisoires

Ce levier est une **démonstration fonctionnelle** de la logique de calcul du site.
La structure est en place, mais **les données sont à considérer comme des estimations approximatives** et ne doivent pas être utilisées pour tirer des conclusions sans révision préalable.

### Facteurs d'émission utilisés

| Mode | kg CO₂e/passager/km | Statut |
|------|---------------------|--------|
| Avion | 0,230 | ⚠️ À consolider |
| Train | 0,012 | ⚠️ À consolider |

source: sncf et ademe

### Tranches de vols

| Seuil | Billets | Distance moyenne | Statut |
|-------|---------|-----------------|--------|
| ≤ 750 km | 250M | 450 km | ⚠️ À consolider |
| ≤ 1 000 km | 250M + 110M | 450 / 875 km | ⚠️ À consolider |
| ≤ 1 500 km | 250M + 110M + 140M | 450 / 875 / 1 250 km | ⚠️ À consolider |



### Formule appliquée
```math
ΔE = Σ (Nᵢ × dᵢ × (EF_avion - EF_train)) / 10⁹  [MtCO₂e]
```

### 🔧 Ce qui reste à faire
- Vérifier et sourcer les facteurs d'émission (avion et train)
- Consolider les volumes de billets par tranche de distance (Eurostat / Eurocontrol)
- Affiner les distances moyennes par tranche
- Valider la segmentation des tranches de distance
##  Fonctionnalités de l'interface

- Navigation multi-pages (accueil + 4 modules)
- **Filtres dynamiques** : région, secteur, gaz (sidebar)
- **Graphiques interactifs** Plotly (zoom)
- Comparaison visuelle entre scénarios sur un même graphique
- Curseurs et paramètres ajustables en temps réel

---

##  Technologies utilisées

| Bibliothèque | Usage                          |
|--------------|--------------------------------|
| `Streamlit`  | Interface web interactive      |
| `Pandas`     | Traitement des données         |
| `Plotly`     | Visualisations interactives    |
| `openpyxl`   | Lecture du fichier Excel       |

---

##  Perspectives d'évolution

- Intégration de nouvelles bases de données
- Ajout de leviers supplémentaires (fast fashion, mobilité urbaine…)
- Modélisation sectorielle personnalisée par l'utilisateur


---
