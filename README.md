# Moteur de Recherche Intelligent Foncier — RDC Katanga

**Projet de mémoire de Master**  
**Auteur** : MWADI MPANGA Taylor  
**Institution** : ISTA — École Doctorale — Département d'Électricité  
**Orientation** : Génie Logiciel  
**Année** : 2026

---

## Contexte

La gestion foncière en République Démocratique du Congo est confrontée à une
fragmentation des données, une absence d'interopérabilité entre les systèmes
existants et une sous-exploitation analytique. Les informations sont dispersées
entre plusieurs institutions (cadastre, domaines, communes, services de fiscalité)
et stockées sous des formats hétérogènes (papier, bases locales, fichiers SIG).

Ce projet propose un **moteur de recherche intelligent** couplé à un système de
**Business Intelligence** pour intégrer, analyser et prédire les données foncières
de la région du Katanga (provinces du Lualaba, Haut-Katanga, Haut-Lomami et
Tanganyika).

---

## Objectifs

1. **Intégrer** des données foncières hétérogènes dans un cadre commun
2. **Indexer** et rechercher efficacement les parcelles selon de multiples critères
3. **Analyser** les tendances et produire des indicateurs décisionnels
4. **Prédire** la valeur foncière à partir de caractéristiques simples
5. **Visualiser** les données sur des cartes interactives

---

## Composantes du projet

### 1. Dataset synthétique

Un jeu de **57 000 parcelles foncières synthétiques** a été généré à partir de
paramètres réels observés dans la région du Katanga.

| Caractéristique | Valeur |
|---|---|
| Parcelles générées | 57 000 |
| Provinces couvertes | 4 (Haut-Katanga, Lualaba, Haut-Lomami, Tanganyika) |
| Attributs par parcelle | 12 |
| Superficie médiane | 650 m² |
| Valeur médiane | 3 350 USD |
| Valeur totale estimée | 0.33 milliards USD |
| Taux de litiges | 39.4 % |
| Parcelles sous influence minière | 43.8 % |

**Méthodologie de génération** :

- Distribution spatiale uniforme dans les polygones administratifs réels
- Statut foncier pondéré par l'indice de conflit provincial documenté (ITIE RDC)
- Influence minière probabiliste selon le profil provincial (mining_core, mining_urban, agro_mining, agro_lake)
- Valeur foncière calculée par régression heuristique :
  - Prix de base au m² selon profil (8 à 45 USD/m²)
  - Décroissance par paliers selon la distance au chef-lieu réel
  - Multiplicateur selon statut (formel +40 %, informel -30 %, litigieux -50 %)
  - Pénalité d'incertitude en zone minière (-15 %)

### 2. Modèle prédictif

Trois modèles ont été comparés pour prédire la valeur foncière.

| Modèle | R² test | RMSE (USD) | MAE (USD) |
|---|---|---|---|
| Ridge Regression | 0.51 | 780 | 281 |
| Random Forest | 0.89 | 379 | 52 |
| **Gradient Boosting** | **0.90** | **380** | **52** |

**Features utilisées** : superficie, log(superficie), distance au chef-lieu,
statut (one-hot), type de titre, province (one-hot), profil foncier, indicateur
d'influence minière, année d'enregistrement.

**Facteurs les plus influents** (par ordre d'importance) :
1. Distance au chef-lieu
2. Superficie
3. Statut formel
4. Influence minière

### 3. Application Streamlit

Une application web interactive, organisée en 5 modules :

| Module | Fonctionnalité |
|---|---|
| **Accueil** | Vue d'ensemble du projet et du périmètre couvert |
| **Recherche** | Filtres multicritères sur 57 000 parcelles (province, statut, superficie, valeur, influence minière) |
| **Prédiction** | Estimation instantanée de la valeur foncière via le modèle ML |
| **Tableau de bord** | 8 sections d'analyse : KPIs, distributions, heatmaps, top 10, synthèse |
| **Carte** | Visualisation géographique interactive avec coloration par statut ou par valeur |

---

## Architecture technique

```
┌─────────────────────────────────────────────────────────────┐
│  SOURCES DE DONNÉES                                          │
│  Cadastre · Registres fonciers · SIG · Données administratives│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PIPELINE ETL                                                │
│  Extraction · Transformation · Nettoyage · Chargement        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  STOCKAGE                                                    │
│  Parquet (tabulaire) · GeoPackage (spatial)                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  ANALYSE INTELLIGENTE                                        │
│  Modèle ML (Random Forest / Gradient Boosting)               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  INTERFACE DÉCISIONNELLE                                     │
│  Streamlit — Recherche, Prédiction, Dashboard, Carte         │
└─────────────────────────────────────────────────────────────┘
```

---

## Stack technique

| Composant | Technologie | Version |
|---|---|---|
| Langage | Python | 3.14 |
| Données tabulaires | pandas | 3.0.6 |
| Calcul numérique | numpy | 2.5.3 |
| Données spatiales | geopandas | 1.1.4 |
| Géométries | shapely | 2.1.2 |
| I/O spatial | pyogrio | 0.13.0 |
| Machine Learning | scikit-learn | 1.9.1 |
| Visualisation | plotly | 7.1.0 |
| Cartographie | pydeck | 0.9.3 |
| Interface web | streamlit | 1.64.0 |
| Sérialisation modèle | joblib | 1.6.0 |
| Format colonne | pyarrow | 25.0.1 |

---

## Structure du projet

```
projet_foncier_lualaba/
│
├── data/
│   ├── raw/                          # Données brutes (non versionnées)
│   ├── processed/
│   │   └── pilot_provinces_enriched.gpkg   # 4 provinces enrichies
│   ├── synthetic/
│   │   ├── parcelles_synthetiques.gpkg    # Dataset spatial
│   │   ├── parcelles_synthetiques.parquet # Dataset tabulaire
│   │   └── synthese_par_province.csv      # Statistiques
│   └── models/
│       ├── modele_valeur_fonciere.joblib
│       └── modele_valeur_fonciere_metadata.json
│
├── notebooks/
│   ├── 01_exploration_visuelle.ipynb
│   └── 02_modele_predictif.ipynb
│
├── src/
│   ├── etl/
│   │   └── 00_check_data.py           # Vérification des provinces
│   ├── generation/
│   │   └── 01_generate_parcels.py     # Génération synthétique
│   └── app/
│       ├── app.py                     # Contrôleur navigation
│       ├── sidebar.py                 # Sidebar custom
│       ├── style.py                   # Icônes SVG + CSS
│       ├── utils.py                   # Chargement données/modèle
│       └── views/
│           ├── accueil.py
│           ├── recherche.py
│           ├── prediction.py
│           ├── dashboard.py
│           └── carte.py
│
├── .streamlit/
│   ├── config.toml                    # Thème Streamlit
│   └── style.css                      # Style professionnel
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Installation

### Prérequis

- **Python 3.12+** (3.14 recommandé)
- **pip** à jour
- **Système** : Windows, Linux ou macOS

### Étape 1 — Cloner le projet

```bash
git clone https://github.com/<votre-username>/projet_foncier_lualaba.git
cd projet_foncier_lualaba
```

### Étape 2 — Créer l'environnement virtuel

**Windows** :
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS** :
```bash
python -m venv venv
source venv/bin/activate
```

### Étape 3 — Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Étape 4 — Installer Fiona (si nécessaire)

Sur **Python 3.14 + Windows**, `fiona` peut nécessiter une roue précompilée :

```bash
pip install attrs certifi click click-plugins cligj
pip install fiona --index-url https://gisidx.github.io/gwi/
```

### Étape 5 — Lancer l'application

```bash
streamlit run src/app/app.py
```

L'application s'ouvre sur `http://localhost:8501`.

---

## Utilisation

### Régénérer le dataset synthétique

```bash
python src/generation/01_generate_parcels.py
```

Produit :
- `data/synthetic/parcelles_synthetiques.gpkg`
- `data/synthetic/parcelles_synthetiques.parquet`

### Réentraîner le modèle prédictif

Ouvrir `notebooks/02_modele_predictif.ipynb` et exécuter toutes les cellules.

Produit :
- `data/models/modele_valeur_fonciere.joblib`
- `data/models/modele_valeur_fonciere_metadata.json`

### Explorer les données

Ouvrir `notebooks/01_exploration_visuelle.ipynb` pour :
- Cartographier les parcelles
- Analyser les distributions
- Générer les figures du mémoire

---

## Résultats clés

### Distribution des parcelles par province

| Province | Parcelles | Superficie médiane | Valeur médiane | Litiges | Influence minière |
|---|---|---|---|---|---|
| Haut-Katanga | 20 000 | 405 m² | 4 200 USD | 41.0 % | 54.8 % |
| Lualaba | 12 000 | 790 m² | 5 600 USD | 51.5 % | 85.0 % |
| Haut-Lomami | 13 000 | 1 205 m² | 2 800 USD | 29.4 % | 24.7 % |
| Tanganyika | 12 000 | 1 503 m² | 2 100 USD | 35.3 % | 4.8 % |

### Performance du modèle

- **R² test** : 0.90
- **RMSE** : 380 USD
- **MAE** : 52 USD
- **Modèle retenu** : Gradient Boosting

### Insights métier

1. **Lualaba** concentre la plus forte proportion de litiges (51.5 %) et d'influence minière (85 %), confirmant la pression foncière liée à l'exploitation du cobalt et du cuivre.
2. **Haut-Katanga** présente les parcelles les plus petites (405 m² médiane), cohérent avec un profil urbain dense autour de Lubumbashi.
3. **Tanganyika** affiche les valeurs médianes les plus faibles malgré les plus grandes superficies, reflétant un marché foncier agricole moins tendu.
4. Le **statut formel** multiplie la valeur par ~3 par rapport au statut litigieux, illustrant l'impact économique de l'insécurité foncière.

---

## Limites et perspectives

### Limites

- Les données sont **synthétiques**. Elles reproduisent les caractéristiques
  statistiques et spatiales réelles du foncier du Katanga, mais ne représentent
  pas des parcelles existantes.
- Le périmètre couvre **4 provinces** sur les 26 de la RDC.
- Le modèle prédictif est entraîné sur les données synthétiques ; ses performances
  sur des données réelles seraient probablement inférieures.

### Perspectives

1. **Extension nationale** : intégration des 26 provinces
2. **Données réelles** : connexion au cadastre et aux services domaniaux
3. **Indexation avancée** : intégration d'Elasticsearch pour la recherche sémantique
4. **PostgreSQL + PostGIS** : migration vers une base de données spatiale industrielle
5. **API REST** : exposition des données via FastAPI pour interconnexion
6. **Déploiement Cloud** : hébergement sur Streamlit Cloud ou serveur dédié

---

## Auteur

**MWADI MPANGA Taylor**  
Concepteur des systèmes d'information  
Institut Supérieur de Techniques Appliquées (ISTA) — École Doctorale  
Lualaba, République Démocratique du Congo

**Encadrement** :
- Directeur : P.A. KALOMBO SHIMBA VIDJE Daily
- Co-directeur : Dr MWAMBA KASONGO Dahouda
- Encadreur : Pr MUFIND MUKAZ Ebedon

---

## Licence

Projet académique — ISTA 2026.  
Usage pédagogique et de recherche.

---

## Remerciements

Ce travail a bénéficié des données ouvertes fournies par :
- **HDX (Humanitarian Data Exchange)** — limites administratives
- **OpenStreetMap** — réseau routier et données géographiques
- **ITIE RDC** — rapports sur la transparence des industries extractives
- **Christoph Gohlke** — roues géospatiales Windows

---

*Dernière mise à jour : 2026*