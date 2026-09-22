"""
Fonctions utilitaires pour l'application Streamlit.
Chargement du dataset et du modèle, avec mise en cache.
"""

import pandas as pd
import geopandas as gpd
import joblib
import json
import numpy as np
from pathlib import Path
import streamlit as st

# Forcer pyogrio
gpd.options.io_engine = "pyogrio"

# Chemins
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PARCELS_PARQUET = PROJECT_ROOT / "data" / "synthetic" / "parcelles_synthetiques.parquet"
PROVINCES_GPKG = PROJECT_ROOT / "data" / "processed" / "pilot_provinces_enriched.gpkg"
MODEL_PATH = PROJECT_ROOT / "data" / "models" / "modele_valeur_fonciere.joblib"
METADATA_PATH = PROJECT_ROOT / "data" / "models" / "modele_valeur_fonciere_metadata.json"


@st.cache_data
def load_parcels():
    """Charge le dataset de parcelles (cache pour performance)."""
    return pd.read_parquet(PARCELS_PARQUET)


@st.cache_data
def load_provinces():
    """Charge les polygones des provinces."""
    return gpd.read_file(PROVINCES_GPKG, layer="provinces")


@st.cache_resource
def load_model():
    """Charge le modèle ML entraîné."""
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_metadata():
    """Charge les métadonnées du modèle."""
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def predict_value(model, input_dict):
    """
    Prédit la valeur foncière à partir d'un dictionnaire d'entrée.
    Effectue le feature engineering nécessaire.
    """
    df = pd.DataFrame([input_dict])
    df["log_superficie"] = np.log1p(df["superficie_m2"])
    df["mining_flag"] = df["sous_influence_miniere"].astype(int)
    df["urbain_flag"] = (df["profile"] == "mining_urban").astype(int)
    return model.predict(df)[0]