"""
Point d'entrée de l'application Streamlit Cloud.
Redirige vers l'application principale dans src/app/app.py
"""

import sys
from pathlib import Path

# Ajouter src/app au PYTHONPATH
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src" / "app"))

# Exécuter l'application principale
with open(ROOT / "src" / "app" / "app.py", "r", encoding="utf-8") as f:
    exec(compile(f.read(), "src/app/app.py", "exec"))