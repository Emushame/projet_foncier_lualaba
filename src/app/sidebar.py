"""
Sidebar personnalisée professionnelle avec navigation.
"""

import streamlit as st


# --- Icônes SVG (Lucide) ---
ICON_HOME = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
ICON_SEARCH = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>'
ICON_TARGET = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
ICON_DASH = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>'
ICON_MAP = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z"/></svg>'
ICON_LOGO = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6"/><path d="M10 9h.01"/><path d="M14 9h.01"/></svg>'

MENU_ITEMS = [
    ("Accueil", ICON_HOME, "accueil"),
    ("Recherche", ICON_SEARCH, "recherche"),
    ("Prédiction", ICON_TARGET, "prediction"),
    ("Tableau de bord", ICON_DASH, "dashboard"),
    ("Carte", ICON_MAP, "carte"),
]


def render_sidebar(current_page: str):
    """
    Affiche la sidebar personnalisée.
    current_page : identifiant de la page active (pour surligner).
    """
    with st.sidebar:
        # --- Logo et titre ---
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px;
                        padding: 0 0 20px 0; margin-bottom: 20px;
                        border-bottom: 1px solid #E5E7EB;">
                <div style="width: 36px; height: 36px; border-radius: 8px;
                            background: linear-gradient(135deg, #0E9F6E 0%, #057A55 100%);
                            display: flex; align-items: center; justify-content: center;
                            color: white;">{ICON_LOGO}</div>
                <div>
                    <div style="font-size: 0.875rem; font-weight: 700;
                                color: #111827; letter-spacing: -0.02em;">
                        Foncier Intelligent
                    </div>
                    <div style="font-size: 0.688rem; color: #6B7280;">
                        RDC · Katanga
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --- Section Navigation ---
        st.markdown(
            '<div style="font-size: 0.688rem; font-weight: 600; '
            'text-transform: uppercase; letter-spacing: 0.08em; '
            'color: #9CA3AF; margin-bottom: 10px;">Navigation</div>',
            unsafe_allow_html=True,
        )

        # Utiliser st.button pour la navigation (plus fiable que <a href>)
        for label, icon, slug in MENU_ITEMS:
            is_active = (slug == current_page)

            # Style conditionnel
            if is_active:
                bg_color = "#ECFDF5"
                text_color = "#0E9F6E"
                font_weight = "600"
                border_left = "3px solid #0E9F6E"
            else:
                bg_color = "transparent"
                text_color = "#4B5563"
                font_weight = "500"
                border_left = "3px solid transparent"

            # Bouton cliquable stylisé
            col_icon, col_label = st.columns([1, 5], gap="small")

            with col_icon:
                st.markdown(
                    f'<div style="padding-top: 8px; color: {text_color};">{icon}</div>',
                    unsafe_allow_html=True,
                )

            with col_label:
                clicked = st.button(
                    label,
                    key=f"nav_{slug}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                )
                if clicked and not is_active:
                    st.query_params["page"] = slug
                    st.rerun()

        # --- Section Statut système ---
        st.markdown(
            """
            <div style="margin-top: 32px; padding: 12px;
                        background-color: #FFFFFF;
                        border: 1px solid #E5E7EB;
                        border-radius: 8px;">
                <div style="font-size: 0.688rem; font-weight: 600;
                            text-transform: uppercase; letter-spacing: 0.08em;
                            color: #9CA3AF; margin-bottom: 10px;">
                    État du système
                </div>
                <div style="display: flex; align-items: center; gap: 8px;
                            font-size: 0.75rem; color: #374151; margin-bottom: 6px;">
                    <span style="color: #10B981; font-size: 0.5rem;">●</span>
                    <span>57 000 parcelles</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;
                            font-size: 0.75rem; color: #374151; margin-bottom: 6px;">
                    <span style="color: #10B981; font-size: 0.5rem;">●</span>
                    <span>Modèle R² 0.886</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;
                            font-size: 0.75rem; color: #374151;">
                    <span style="color: #10B981; font-size: 0.5rem;">●</span>
                    <span>4 provinces</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --- Footer ---
        st.markdown(
            """
            <div style="margin-top: 24px; padding-top: 16px;
                        border-top: 1px solid #E5E7EB;
                        font-size: 0.688rem; color: #9CA3AF; line-height: 1.6;">
                Projet de mémoire<br>
                MWADI MPANGA Taylor<br>
                ISTA · 2026
            </div>
            """,
            unsafe_allow_html=True,
        )