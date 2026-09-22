"""
Point d'entrée de l'application Streamlit Cloud.

Ce fichier est le "main module" détecté par Streamlit Cloud.
Il ajoute le dossier src/app au PYTHONPATH puis exécute app.py
comme s'il était lancé directement.
"""

import sys
import runpy
from pathlib import Path

# Racine du projet (dossier contenant ce fichier)
ROOT = Path(__file__).resolve().parent

# Ajouter src/app au PYTHONPATH pour que les imports relatifs fonctionnent
APP_DIR = ROOT / "src" / "app"
sys.path.insert(0, str(APP_DIR))

# Exécuter app.py comme s'il était lancé directement
runpy.run_path(str(APP_DIR / "app.py"), run_name="__main__")