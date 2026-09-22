"""
Carte interactive des parcelles.
Version enrichie : contours provinces, légende, coloration par valeur.
"""

import streamlit as st
import sys
from pathlib import Path
import pydeck as pdk
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_parcels, load_provinces
from style import render_header, ICONS

render_header(
    title="Carte interactive",
    subtitle="Visualisation géographique des parcelles",
    icon_svg=ICONS["map"],
)

df = load_parcels()
provinces_gdf = load_provinces()

# --- Filtres ---
with st.sidebar:
    st.markdown("## Filtres carte")
    province = st.selectbox("Province", ["Toutes"] + sorted(df["province"].unique()))
    statut = st.selectbox("Statut", ["Tous"] + sorted(df["statut"].unique()))

    color_mode = st.radio(
        "Coloration",
        options=["Par statut", "Par valeur"],
        index=0,
    )

    max_points = st.slider("Nombre max de points", 1000, 20000, 8000, step=1000)

# --- Filtrage ---
df_map = df.copy()
if province != "Toutes":
    df_map = df_map[df_map["province"] == province]
if statut != "Tous":
    df_map = df_map[df_map["statut"] == statut]

df_map = df_map.sample(min(len(df_map), max_points), random_state=42).reset_index(drop=True)

# --- Coloration ---
if color_mode == "Par statut":
    color_map = {
        "formel":    [16, 185, 129, 220],
        "informel":  [245, 158, 11, 220],
        "litigieux": [239, 68, 68, 220],
    }
    df_map["color"] = df_map["statut"].map(color_map)
    legend_html = """
    <div style="display: flex; gap: 20px; margin-bottom: 12px; font-size: 0.813rem;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #10B981;"></span>
            <span>Formel</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #F59E0B;"></span>
            <span>Informel</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #EF4444;"></span>
            <span>Litigieux</span>
        </div>
    </div>
    """
else:  # Par valeur
    vmin = df_map["valeur_usd"].quantile(0.05)
    vmax = df_map["valeur_usd"].quantile(0.95)
    df_map["valeur_norm"] = ((df_map["valeur_usd"] - vmin) / (vmax - vmin + 1e-9)).clip(0, 1)

    def value_to_color(v):
        if v < 0.33:
            return [16, 185, 129, 220]
        elif v < 0.66:
            return [245, 158, 11, 220]
        else:
            return [239, 68, 68, 220]

    df_map["color"] = df_map["valeur_norm"].apply(value_to_color)
    legend_html = f"""
    <div style="display: flex; gap: 20px; margin-bottom: 12px; font-size: 0.813rem;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #10B981;"></span>
            <span>Valeur basse (&lt; {vmin + (vmax-vmin)*0.33:,.0f} USD)</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #F59E0B;"></span>
            <span>Valeur moyenne</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
            <span style="width: 10px; height: 10px; border-radius: 50%; background: #EF4444;"></span>
            <span>Valeur haute (&gt; {vmin + (vmax-vmin)*0.66:,.0f} USD)</span>
        </div>
    </div>
    """

# --- Centre et zoom ---
if len(df_map) > 0:
    center_lat = df_map["latitude"].mean()
    center_lon = df_map["longitude"].mean()
    lat_span = df_map["latitude"].max() - df_map["latitude"].min()
    lon_span = df_map["longitude"].max() - df_map["longitude"].min()
    span = max(lat_span, lon_span)

    if span < 0.5:
        zoom = 11
    elif span < 1:
        zoom = 10
    elif span < 2:
        zoom = 9
    elif span < 5:
        zoom = 8
    else:
        zoom = 7
else:
    center_lat, center_lon, zoom = -10.0, 25.0, 6

# --- Légende ---
st.markdown(legend_html, unsafe_allow_html=True)

# --- Layer contours provinces ---
provinces_layer = pdk.Layer(
    "GeoJsonLayer",
    data=provinces_gdf.__geo_interface__,
    get_fill_color=[14, 159, 110, 15],
    get_line_color=[14, 159, 110, 200],
    line_width_min_pixels=2,
    pickable=False,
)

# --- Layer parcelles ---
parcels_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_map,
    get_position=["longitude", "latitude"],
    get_fill_color="color",
    get_radius=2000,
    pickable=True,
    opacity=0.85,
    stroked=False,
    radius_min_pixels=1.5,
    radius_max_pixels=10,
)

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=zoom,
    pitch=0,
    bearing=0,
)

tooltip = {
    "html": "<b>{id_parcelle}</b><br/>{province} — {profile}<br/>Statut : {statut}<br/>Superficie : {superficie_m2} m²<br/>Valeur : {valeur_usd} USD",
    "style": {
        "backgroundColor": "#111827",
        "color": "white",
        "fontSize": "12px",
        "padding": "8px",
        "borderRadius": "6px",
    },
}

deck = pdk.Deck(
    layers=[provinces_layer, parcels_layer],
    initial_view_state=view_state,
    tooltip=tooltip,  # type: ignore[arg-type]  # pydeck accepts a tooltip configuration dict at runtime
    map_style="https://basemaps.cartocdn.com/gl/positron-gl-style.json",
)

st.pydeck_chart(deck, use_container_width=True, height=600)

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Parcelles affichées", f"{len(df_map):,}")
col2.metric("Province", province)
col3.metric("Statut", statut)
col4.metric(
    "Valeur médiane",
    f"{df_map['valeur_usd'].median():,.0f} USD" if len(df_map) else "—",
)

st.caption(f"{len(df_map):,} parcelles affichées sur {len(df):,}")