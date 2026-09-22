"""
Moteur de recherche intelligent foncier — Contrôleur de navigation.
"""

import streamlit as st
import sys
from pathlib import Path

# Ajouter src/app au path
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

from style import apply_style
from sidebar import render_sidebar

# --- Configuration globale (une seule fois) ---
st.set_page_config(
    page_title="Moteur Foncier Intelligent",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_style()

# --- Récupérer la page active depuis les query params ---
page_slug = st.query_params.get("page", "accueil")

# --- Afficher la sidebar custom ---
render_sidebar(current_page=page_slug)

# --- Router vers la bonne page ---
PAGES = {
    "accueil": "views/accueil.py",
    "recherche": "views/recherche.py",
    "prediction": "views/prediction.py",
    "dashboard": "views/dashboard.py",
    "carte": "views/carte.py",
}

page_file = PAGES.get(page_slug, "views/accueil.py")
page_path = APP_DIR / page_file

if page_path.exists():
    exec(compile(page_path.read_text(encoding="utf-8"), str(page_path), "exec"))
else:
    st.error(f"Page introuvable : {page_slug}")