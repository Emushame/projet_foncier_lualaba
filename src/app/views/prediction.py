"""
Module de prédiction de valeur foncière.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_parcels, load_model, load_metadata, predict_value
from style import render_header, ICONS

render_header(
    title="Prédiction de valeur foncière",
    subtitle="Estimez la valeur d'une parcelle à partir de ses caractéristiques",
    icon_svg=ICONS["target"],
)

model = load_model()
metadata = load_metadata()
df = load_parcels()

col_form, col_result = st.columns([2, 1])

with col_form:
    st.markdown("#### Caractéristiques de la parcelle")

    col_a, col_b = st.columns(2)

    with col_a:
        province = st.selectbox("Province", sorted(df["province"].unique()))
        profile = st.selectbox("Profil foncier", sorted(df["profile"].unique()))
        statut = st.selectbox("Statut", sorted(df["statut"].unique()))
        type_titre = st.selectbox("Type de titre", sorted(df["type_titre"].unique()))

    with col_b:
        superficie = st.number_input("Superficie (m²)", min_value=50, max_value=10000, value=500, step=50)
        distance = st.number_input("Distance au centre (km)", min_value=0.0, max_value=500.0, value=50.0, step=5.0)
        mining = st.checkbox("Sous influence minière", value=False)
        annee = st.number_input("Année d'enregistrement", min_value=2015, max_value=2026, value=2022)

    predict_btn = st.button("Estimer la valeur", type="primary", use_container_width=True)

with col_result:
    st.markdown("#### Résultat")

    if predict_btn:
        input_dict = {
            "province": province,
            "profile": profile,
            "statut": statut,
            "type_titre": type_titre,
            "superficie_m2": superficie,
            "distance_centre_km": distance,
            "sous_influence_miniere": mining,
            "annee_enregistrement": annee,
        }
        try:
            value = predict_value(model, input_dict)
            st.markdown(
                f"""
                <div class="card" style="text-align: center; padding: 2rem 1rem;">
                    <div class="card-title">Valeur estimée</div>
                    <div class="card-value" style="font-size: 2.5rem; color: #0E9F6E;">
                        {value:,.0f} USD
                    </div>
                    <div style="font-size: 0.75rem; color: #6B7280; margin-top: 8px;">
                        Modèle {metadata.get('model_name', 'Random Forest')} · R² {metadata.get('r2_test', 0):.3f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(f"Erreur moyenne du modèle : ± {metadata.get('mae_test', 0):.0f} USD")
        except Exception as e:
            st.error(f"Erreur de prédiction : {e}")
    else:
        st.info("Remplis le formulaire et clique sur **Estimer la valeur**.")