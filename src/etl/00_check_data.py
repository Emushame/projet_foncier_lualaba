"""
Vérification de la couche des 4 provinces pilotes.
Lit spécifiquement la couche 'provinces'.
"""

import geopandas as gpd
from pathlib import Path

# Forcer pyogrio comme moteur par défaut
gpd.options.io_engine = "pyogrio"

# Chemins
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_GPKG = PROJECT_ROOT / "data" / "processed" / "pilot_provinces_enriched.gpkg"

# Nom explicite de la couche
LAYER_NAME = "provinces"


def main():
    print(f"Lecture de : {INPUT_GPKG}")
    print(f"Fichier existe : {INPUT_GPKG.exists()}")

    # Lister les couches
    layers_df = gpd.list_layers(INPUT_GPKG)
    print(f"\nCouches disponibles :")
    print(layers_df)

    # Charger la bonne couche
    print(f"\nCouche utilisée : {LAYER_NAME}")
    gdf = gpd.read_file(INPUT_GPKG, layer=LAYER_NAME)

    print(f"\nNombre de provinces : {len(gdf)}")
    print(f"Colonnes : {list(gdf.columns)}")
    print(f"CRS : {gdf.crs}")
    print(f"Types de géométrie : {gdf.geometry.geom_type.unique()}")

    # Attributs clés — noms en minuscules maintenant
    print("\n=== Attributs par province ===")
    cols = ["adm1_name", "profile", "population", "urban_rate",
            "density_km2", "conflict_index", "area_sqkm"]
    print(gdf[cols].to_string(index=False))

    # Validation géométrique
    print(f"\nGéométries valides : {gdf.geometry.is_valid.all()}")
    area_total = gdf.geometry.area.sum() / 1e6
    print(f"Superficie totale (km²) : {area_total:,.0f}")


if __name__ == "__main__":
    main()