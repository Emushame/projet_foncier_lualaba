"""
Module de recherche multicritère.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_parcels
from style import render_header, ICONS

render_header(
    title="Recherche multicritère",
    subtitle="Filtrez les 57 000 parcelles selon vos critères",
    icon_svg=ICONS["search"],
)

df = load_parcels()

# --- Sidebar filtres ---
with st.sidebar:
    st.markdown("## Critères")

    provinces = st.multiselect(
        "Province",
        options=sorted(df["province"].unique()),
        default=df["province"].unique().tolist(),
    )
    statuts = st.multiselect(
        "Statut",
        options=sorted(df["statut"].unique()),
        default=df["statut"].unique().tolist(),
    )
    profils = st.multiselect(
        "Profil foncier",
        options=sorted(df["profile"].unique()),
        default=df["profile"].unique().tolist(),
    )
    mining_filter = st.radio(
        "Influence minière",
        options=["Toutes", "Sous influence", "Hors influence"],
        index=0,
    )
    superficie_range = st.slider(
        "Superficie (m²)", 0, 5000, (0, 3000), step=100
    )
    valeur_range = st.slider(
        "Valeur estimée (USD)", 0, 10000, (0, 2000), step=100
    )

# --- Application filtres ---
mask = (
    df["province"].isin(provinces)
    & df["statut"].isin(statuts)
    & df["profile"].isin(profils)
    & df["superficie_m2"].between(*superficie_range)
    & df["valeur_usd"].between(*valeur_range)
)
if mining_filter == "Sous influence":
    mask &= df["sous_influence_miniere"]
elif mining_filter == "Hors influence":
    mask &= ~df["sous_influence_miniere"]

result = df[mask]

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Parcelles trouvées", f"{len(result):,}")
col2.metric(
    "Superficie médiane",
    f"{result['superficie_m2'].median():.0f} m²" if len(result) else "—",
)
col3.metric(
    "Valeur médiane",
    f"{result['valeur_usd'].median():.0f} USD" if len(result) else "—",
)
col4.metric(
    "% litigieux",
    f"{(result['statut'] == 'litigieux').mean()*100:.1f}%" if len(result) else "—",
)

st.markdown("---")

if len(result) > 0:
    cols_display = [
        "id_parcelle", "province", "profile", "superficie_m2",
        "statut", "sous_influence_miniere", "valeur_usd", "type_titre",
    ]
    st.markdown(f"#### {min(len(result), 100)} premières lignes")
    st.dataframe(
        result[cols_display].head(100),
        use_container_width=True,
        hide_index=True,
    )

    csv = result[cols_display].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Télécharger en CSV",
        data=csv,
        file_name="resultats_recherche.csv",
        mime="text/csv",
    )
else:
    st.warning("Aucune parcelle ne correspond aux critères.")