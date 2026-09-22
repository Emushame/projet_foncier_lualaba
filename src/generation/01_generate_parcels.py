"""
Génération synthétique de parcelles foncières pour les 4 provinces pilotes.

Version 2 : prix réalistes, distance au chef-lieu réel.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely.geometry import Point
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
gpd.options.io_engine = "pyogrio"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_GPKG = PROJECT_ROOT / "data" / "processed" / "pilot_provinces_enriched.gpkg"
OUTPUT_GPKG = PROJECT_ROOT / "data" / "synthetic" / "parcelles_synthetiques.gpkg"
OUTPUT_PARQUET = PROJECT_ROOT / "data" / "synthetic" / "parcelles_synthetiques.parquet"

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

PARCELS_PER_PROVINCE = {
    "Haut-Katanga": 20_000,
    "Lualaba": 12_000,
    "Haut-Lomami": 13_000,
    "Tanganyika": 12_000,
}

PROVINCE_PREFIX = {
    "Haut-Katanga": "HK",
    "Lualaba": "LU",
    "Haut-Lomami": "HL",
    "Tanganyika": "TA",
}

# --- Chef-lieu de chaque province (lat, lon) ---
CHEF_LIEU = {
    "Haut-Katanga": (-11.66, 27.48),   # Lubumbashi
    "Lualaba":      (-10.71, 25.47),   # Kolwezi
    "Haut-Lomami":  (-8.74, 24.99),    # Kamina
    "Tanganyika":   (-5.94, 29.19),    # Kalemie
}

# --- Prix de base au m² en USD selon le profil foncier ---
PRIX_BASE_USD_M2 = {
    "mining_urban": 45.0,
    "mining_core":  35.0,
    "agro_mining":  12.0,
    "agro_lake":     8.0,
}


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------

def haversine_km(lat1, lon1, lat2, lon2):
    """Distance en km entre deux points GPS (formule de Haversine)."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def generate_point_in_polygon(polygon):
    minx, miny, maxx, maxy = polygon.bounds
    for _ in range(100):
        p = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if polygon.contains(p):
            return p
    return polygon.centroid


def generate_superficie(profile):
    if profile == "mining_urban":
        median, sigma = 400, 0.6
    elif profile == "mining_core":
        median, sigma = 800, 0.8
    elif profile == "agro_mining":
        median, sigma = 1200, 0.9
    else:
        median, sigma = 1500, 0.9
    return round(float(np.random.lognormal(np.log(median), sigma)), 2)


def generate_statut(conflict_index):
    p_litigieux = 0.05 + 0.55 * conflict_index
    p_informel = 0.15 + 0.30 * (1 - conflict_index)
    p_formel = 1 - p_litigieux - p_informel
    return np.random.choice(
        ["formel", "informel", "litigieux"],
        p=[p_formel, p_informel, p_litigieux],
    )


def generate_mining_influence(profile):
    probabilities = {
        "mining_core": 0.85,
        "mining_urban": 0.55,
        "agro_mining": 0.25,
        "agro_lake": 0.05,
    }
    return bool(np.random.rand() < probabilities.get(profile, 0.1))


def distance_factor(distance_km):
    """
    Facteur de décroissance de la valeur selon la distance au chef-lieu.
    Paliers réalistes pour le contexte foncier congolais.
    """
    if distance_km <= 10:
        return 1.00
    elif distance_km <= 30:
        return 1.00 - 0.20 * (distance_km - 10) / 20
    elif distance_km <= 60:
        return 0.80 - 0.25 * (distance_km - 30) / 30
    elif distance_km <= 100:
        return 0.55 - 0.20 * (distance_km - 60) / 40
    else:
        return max(0.20, 0.35 - 0.15 * (distance_km - 100) / 100)


def generate_valeur(superficie, distance_km, statut, mining, profile):
    """
    Valeur estimée en USD, calibrée sur le marché foncier réel du Katanga.

    Base : prix USD/m² selon profil
    Multiplicateur distance : paliers (1.0 → 0.2)
    Multiplicateur statut : formel +40%, informel -30%, litigieux -50%
    Multiplicateur minière : -15% (incertitude)
    Bruit multiplicatif : ±20%
    """
    prix_m2 = PRIX_BASE_USD_M2.get(profile, 10.0)

    # Facteur distance
    d_factor = distance_factor(distance_km)

    # Facteur statut
    statut_factor = {"formel": 1.4, "informel": 0.7, "litigieux": 0.5}[statut]

    # Facteur influence minière
    mining_factor = 0.85 if mining else 1.0

    # Valeur finale
    valeur = prix_m2 * superficie * d_factor * statut_factor * mining_factor

    # Bruit multiplicatif (±20%)
    valeur *= np.random.uniform(0.8, 1.2)

    # Plancher réaliste : 500 USD (une parcelle rurale vaut au moins ça)
    valeur = max(valeur, 500.0)

    return round(float(valeur), 2)


def generate_type_titre(statut):
    if statut == "formel":
        return np.random.choice(["titre_definitif", "certificat"], p=[0.7, 0.3])
    elif statut == "informel":
        return "occupation"
    return np.random.choice(["occupation", "certificat"], p=[0.6, 0.4])


def generate_date_enregistrement():
    today = date.today()
    days_back = np.random.randint(0, 365 * 10)
    return today - timedelta(days=int(days_back))


# ---------------------------------------------------------------------------
# Génération
# ---------------------------------------------------------------------------

def generate_parcels_for_province(row):
    province = row["adm1_name"]
    profile = row["profile"]
    conflict = row["conflict_index"]
    n = PARCELS_PER_PROVINCE[province]
    prefix = PROVINCE_PREFIX[province]
    chef_lat, chef_lon = CHEF_LIEU[province]

    print(f"  → {province:15s} | profil={profile:14s} | "
          f"conflit={conflict:.2f} | cible={n:>6,} parcelles")

    polygon = row["geometry"]

    parcels = []
    for i in range(n):
        point = generate_point_in_polygon(polygon)
        superficie = generate_superficie(profile)
        statut = generate_statut(conflict)
        mining = generate_mining_influence(profile)

        # Distance au chef-lieu réel
        distance_km = haversine_km(point.y, point.x, chef_lat, chef_lon)

        valeur = generate_valeur(superficie, distance_km, statut, mining, profile)
        type_titre = generate_type_titre(statut)
        date_enr = generate_date_enregistrement()

        parcels.append({
            "id_parcelle": f"{prefix}-{i + 1:06d}",
            "province": province,
            "profile": profile,
            "latitude": round(point.y, 6),
            "longitude": round(point.x, 6),
            "superficie_m2": superficie,
            "statut": statut,
            "sous_influence_miniere": mining,
            "distance_centre_km": round(distance_km, 2),
            "valeur_usd": valeur,
            "type_titre": type_titre,
            "date_enregistrement": date_enr,
            "geometry": point,
        })

    return parcels


def main():
    print("=" * 70)
    print("GÉNÉRATION SYNTHÉTIQUE DE PARCELLES FONCIÈRES — v2")
    print("=" * 70)

    print(f"\n[1/4] Lecture de {INPUT_GPKG.name}")
    provinces = gpd.read_file(INPUT_GPKG, layer="provinces")
    print(f"       {len(provinces)} provinces chargées")

    print("\n[2/4] Génération des parcelles")
    all_parcels = []
    for _, row in provinces.iterrows():
        all_parcels.extend(generate_parcels_for_province(row))
    print(f"\n       Total : {len(all_parcels):,} parcelles générées")

    print("\n[3/4] Construction du GeoDataFrame")
    gdf = gpd.GeoDataFrame(all_parcels, crs="EPSG:4326")

    print("\n       Statistiques par province :")
    stats = gdf.groupby("province").agg(
        n=("id_parcelle", "count"),
        superficie_med=("superficie_m2", "median"),
        valeur_med=("valeur_usd", "median"),
        valeur_moy=("valeur_usd", "mean"),
        dist_med_km=("distance_centre_km", "median"),
        pct_litigieux=("statut", lambda s: (s == "litigieux").mean() * 100),
    ).round(2)
    print(stats.to_string())

    print(f"\n[4/4] Export")
    OUTPUT_GPKG.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(OUTPUT_GPKG, layer="parcelles", driver="GPKG")
    print(f"       → {OUTPUT_GPKG}")

    df_tab = pd.DataFrame(gdf.drop(columns="geometry"))
    df_tab.to_parquet(OUTPUT_PARQUET, index=False)
    print(f"       → {OUTPUT_PARQUET}")

    print("\n" + "=" * 70)
    print("GÉNÉRATION TERMINÉE")
    print("=" * 70)


if __name__ == "__main__":
    main()