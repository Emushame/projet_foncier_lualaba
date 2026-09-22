"""
Page d'accueil.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style import render_header

render_header(
    title="Moteur de Recherche Intelligent Foncier",
    subtitle="RDC — Katanga · 57 000 parcelles · Modèle prédictif intégré",
    icon_svg='<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="20" x="4" y="2" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01"/><path d="M16 6h.01"/><path d="M12 6h.01"/></svg>',
)

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown(
        "Cette plateforme démontre un **moteur de recherche intelligent** "
        "appliqué au foncier de la région du Katanga en République Démocratique du Congo."
    )

    st.markdown(
        """
        <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 1rem;">
            <div class="card">
                <div class="card-title">Intégration des données</div>
                <div style="font-size: 0.9rem; color: #4B5563;">
                    Consolidation de 57 000 parcelles synthétiques générées à partir de paramètres
                    réels (population, densité, indices de conflit foncier).
                </div>
            </div>
            <div class="card">
                <div class="card-title">Analyse prédictive</div>
                <div style="font-size: 0.9rem; color: #4B5563;">
                    Modèle Random Forest entraîné pour estimer la valeur foncière
                    (R² = 0.886, erreur moyenne 52 USD).
                </div>
            </div>
            <div class="card">
                <div class="card-title">Restitution décisionnelle</div>
                <div style="font-size: 0.9rem; color: #4B5563;">
                    Interface interactive pour explorer, rechercher et analyser les données
                    foncières selon de multiples critères.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown("#### Périmètre couvert")
    st.markdown(
        """
        <div class="card">
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <div><span class="badge badge-green">Haut-Katanga</span></div>
                <div><span class="badge badge-red">Lualaba</span></div>
                <div><span class="badge badge-orange">Haut-Lomami</span></div>
                <div><span class="badge badge-gray">Tanganyika</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )