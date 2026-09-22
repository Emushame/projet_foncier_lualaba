"""
Tableau de bord décisionnel enrichi.
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from utils import load_parcels
from style import render_header, ICONS

render_header(
    title="Tableau de bord décisionnel",
    subtitle="Indicateurs clés, tendances et analyses du foncier",
    icon_svg=ICONS["dashboard"],
)

df = load_parcels()

# ============================================================
# SECTION 1 — KPIs GLOBAUX
# ============================================================
st.markdown("### Vue d'ensemble")

col1, col2, col3, col4, col5 = st.columns(5)

valeur_totale = df["valeur_usd"].sum()
taux_litiges = (df["statut"] == "litigieux").mean() * 100
pct_minier = df["sous_influence_miniere"].mean() * 100

col1.metric("Parcelles totales", f"{len(df):,}")
col2.metric("Valeur totale estimée", f"{valeur_totale/1e9:.2f} Md USD")
col3.metric("Valeur médiane", f"{df['valeur_usd'].median():,.0f} USD")
col4.metric("Taux de litiges", f"{taux_litiges:.1f}%")
col5.metric("Sous influence minière", f"{pct_minier:.1f}%")

st.markdown("---")

# ============================================================
# SECTION 2 — ANALYSE PAR PROVINCE
# ============================================================
st.markdown("### Analyse par province")

col_a, col_b = st.columns(2)

with col_a:
    # Répartition des parcelles par province
    counts = df["province"].value_counts().reset_index()
    counts.columns = ["province", "nombre"]
    fig = px.bar(
        counts,
        x="province",
        y="nombre",
        color="province",
        color_discrete_sequence=["#0E9F6E", "#3B82F6", "#F59E0B", "#8B5CF6"],
        text="nombre",
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(
        title="Nombre de parcelles",
        showlegend=False,
        height=350,
        margin=dict(t=40, b=20, l=20, r=20),
        plot_bgcolor="white",
        font=dict(family="Inter", size=12),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    # Valeur médiane par province
    median_vals = df.groupby("province")["valeur_usd"].median().reset_index()
    median_vals = median_vals.sort_values("valeur_usd", ascending=True)
    fig = px.bar(
        median_vals,
        x="valeur_usd",
        y="province",
        orientation="h",
        color="province",
        color_discrete_sequence=["#0E9F6E", "#3B82F6", "#F59E0B", "#8B5CF6"],
        text="valeur_usd",
    )
    fig.update_traces(texttemplate="%{text:,.0f} USD", textposition="outside")
    fig.update_layout(
        title="Valeur médiane des parcelles",
        showlegend=False,
        height=350,
        margin=dict(t=40, b=20, l=20, r=20),
        plot_bgcolor="white",
        font=dict(family="Inter", size=12),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# SECTION 3 — STATUTS ET LITIGES
# ============================================================
st.markdown("### Statuts fonciers et litiges")

col_c, col_d = st.columns(2)

with col_c:
    # Répartition par statut
    counts = df["statut"].value_counts().reset_index()
    counts.columns = ["statut", "nombre"]
    fig = px.pie(
        counts,
        names="statut",
        values="nombre",
        color="statut",
        color_discrete_map={
            "formel": "#10B981",
            "informel": "#F59E0B",
            "litigieux": "#EF4444",
        },
        hole=0.5,
    )
    fig.update_traces(textinfo="percent+label", textfont_size=12)
    fig.update_layout(
        title="Répartition globale",
        height=350,
        margin=dict(t=40, b=20, l=20, r=20),
        font=dict(family="Inter", size=12),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_d:
    # Heatmap croisée province × statut
    cross = pd.crosstab(df["province"], df["statut"], normalize="index") * 100
    cross = cross[["formel", "informel", "litigieux"]]

    fig = px.imshow(
        cross.values,
        x=cross.columns,
        y=cross.index,
        color_continuous_scale=["#FEF3C7", "#F59E0B", "#EF4444"],
        aspect="auto",
        text_auto=True,
    )
    fig.update_traces(texttemplate="%{z:.1f}%")
    fig.update_layout(
        title="% de statuts par province",
        height=350,
        margin=dict(t=40, b=20, l=20, r=20),
        coloraxis_showscale=False,
        font=dict(family="Inter", size=12),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# SECTION 4 — DISTRIBUTION DES VALEURS
# ============================================================
st.markdown("### Distribution des valeurs foncières")

col_e, col_f = st.columns(2)

with col_e:
    # Histogramme par province
    fig = px.histogram(
        df,
        x="valeur_usd",
        color="province",
        nbins=80,
        barmode="overlay",
        color_discrete_sequence=["#0E9F6E", "#3B82F6", "#F59E0B", "#8B5CF6"],
    )
    fig.update_traces(opacity=0.7)
    fig.update_layout(
        title="Distribution des valeurs (par province)",
        height=400,
        margin=dict(t=40, b=20, l=20, r=20),
        plot_bgcolor="white",
        font=dict(family="Inter", size=12),
        xaxis_title="Valeur (USD)",
        yaxis_title="Nombre de parcelles",
        xaxis=dict(range=[0, df["valeur_usd"].quantile(0.98)]),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_f:
    # Box plot par province
    fig = px.box(
        df,
        x="province",
        y="valeur_usd",
        color="province",
        color_discrete_sequence=["#0E9F6E", "#3B82F6", "#F59E0B", "#8B5CF6"],
    )
    fig.update_layout(
        title="Distribution par province (boîtes à moustaches)",
        showlegend=False,
        height=400,
        margin=dict(t=40, b=20, l=20, r=20),
        plot_bgcolor="white",
        font=dict(family="Inter", size=12),
        yaxis_title="Valeur (USD)",
        xaxis_title="",
        yaxis=dict(range=[0, df["valeur_usd"].quantile(0.95)]),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# SECTION 5 — INFLUENCE MINIÈRE
# ============================================================
st.markdown("### Impact de l'influence minière")

col_g, col_h = st.columns(2)

with col_g:
    # Valeur médiane : sous influence vs hors influence
    mining_stats = df.groupby(["province", "sous_influence_miniere"])["valeur_usd"].median().reset_index()
    mining_stats["influence"] = mining_stats["sous_influence_miniere"].map({True: "Sous influence", False: "Hors influence"})

    fig = px.bar(
        mining_stats,
        x="province",
        y="valeur_usd",
        color="influence",
        barmode="group",
        color_discrete_map={
            "Sous influence": "#EF4444",
            "Hors influence": "#10B981",
        },
        text="valeur_usd",
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(
        title="Valeur médiane : impact de l'influence minière",
        height=380,
        margin=dict(t=40, b=20, l=20, r=20),
        plot_bgcolor="white",
        font=dict(family="Inter", size=12),
        yaxis_title="Valeur médiane (USD)",
        xaxis_title="",
        legend_title="",
    )
    st.plotly_chart(fig, use_container_width=True)

with col_h:
    # Taux de litiges sous influence vs hors
    litige_stats = df.groupby(["province", "sous_influence_miniere"]).apply(
        lambda x: (x["statut"] == "litigieux").mean() * 100
    ).reset_index(name="taux_litiges")
    litige_stats["influence"] = litige_stats["sous_influence_miniere"].map({True: "Sous influence", False: "Hors influence"})

    fig = px.bar(
        litige_stats,
        x="province",
        y="taux_litiges",
        color="influence",
        barmode="group",
        color_discrete_map={
            "Sous influence": "#EF4444",
            "Hors influence": "#10B981",
        },
        text="taux_litiges",
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        title="Taux de litiges : impact de l'influence minière",
        height=380,
        margin=dict(t=40, b=20, l=20, r=20),
        plot_bgcolor="white",
        font=dict(family="Inter", size=12),
        yaxis_title="Taux de litiges (%)",
        xaxis_title="",
        legend_title="",
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# SECTION 6 — ÉVOLUTION TEMPORELLE
# ============================================================
st.markdown("### Évolution des enregistrements")

df["annee"] = pd.to_datetime(df["date_enregistrement"]).dt.year
evolution = df.groupby(["annee", "province"]).size().reset_index(name="nombre")

fig = px.line(
    evolution,
    x="annee",
    y="nombre",
    color="province",
    markers=True,
    color_discrete_sequence=["#0E9F6E", "#3B82F6", "#F59E0B", "#8B5CF6"],
)
fig.update_layout(
    title="Nombre de parcelles enregistrées par année",
    height=380,
    margin=dict(t=40, b=20, l=20, r=20),
    plot_bgcolor="white",
    font=dict(family="Inter", size=12),
    xaxis_title="Année",
    yaxis_title="Nombre de parcelles",
    legend_title="",
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ============================================================
# SECTION 7 — TOP 10 PARCELLES LES PLUS CHÈRES
# ============================================================
st.markdown("### Top 10 des parcelles les plus valorisées")

top10 = df.nlargest(10, "valeur_usd")[
    ["id_parcelle", "province", "profile", "superficie_m2",
     "statut", "sous_influence_miniere", "valeur_usd"]
].reset_index(drop=True)

top10.index = top10.index + 1  # Numérotation à partir de 1
st.dataframe(top10, use_container_width=True)

# ============================================================
# SECTION 8 — SYNTHÈSE
# ============================================================
st.markdown("---")
st.markdown("### Synthèse par province")

synthese = df.groupby("province").agg(
    Parcelles=("id_parcelle", "count"),
    Superficie_médiane=("superficie_m2", "median"),
    Valeur_médiane=("valeur_usd", "median"),
    Valeur_totale_M_USD=("valeur_usd", lambda x: x.sum() / 1e6),
    Taux_litiges_pct=("statut", lambda s: (s == "litigieux").mean() * 100),
    Taux_minier_pct=("sous_influence_miniere", lambda s: s.mean() * 100),
).round(2)

synthese.columns = [
    "Parcelles", "Superficie médiane (m²)", "Valeur médiane (USD)",
    "Valeur totale (M USD)", "Litiges (%)", "Minière (%)"
]

st.dataframe(synthese, use_container_width=True)

st.caption(
    f"Analyse produite sur {len(df):,} parcelles synthétiques — "
    f"Valeur totale estimée : {df['valeur_usd'].sum()/1e9:.2f} milliards USD"
)