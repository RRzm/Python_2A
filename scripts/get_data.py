import os
import s3fs
import pandas as pd
import requests
from bs4 import BeautifulSoup
import requests
import geopandas as gpd


def get_cloud_csv(filename, sep=","):
    """
    Charge un fichier CSV depuis S3 et retourne un DataFrame.

    Paramètres:
    -----------
    filename : str
        Nom du fichier à charger (avec ou sans extension .csv)
    sep : str, optional
        Séparateur du fichier CSV (par défaut ",")

    Retourne:
    --------
    pd.DataFrame
        DataFrame contenant les données du fichier
    Exemple:
    --------
    df = get_cloud_csv("dvf")
    df = get_cloud_csv("dossier_complet", sep=";")
    """
    if not filename.endswith(".csv"):
        filename = f"{filename}.csv"

    S3_ENDPOINT_URL = "https://" + os.environ["AWS_S3_ENDPOINT"]
    fs = s3fs.S3FileSystem(
        anon=True,
        client_kwargs={"endpoint_url": S3_ENDPOINT_URL}
    )

    with fs.open(f"renan/diffusion/{filename}", mode="rb") as f:
        df = pd.read_csv(
            f,
            sep=sep,
            dtype={"code_commune": "str"}
        )

    return df


def get_local_csv(filename, sep=','):
    """
    Charge un fichier CSV du dossier Données et retourne un DataFrame.
    Paramètres:
    -----------
    filename : str
        Nom du fichier CSV (avec ou sans l'extension .csv)
    Retourne:
    --------
    pd.DataFrame
        DataFrame contenant les données du CSV
    Exemple:
    --------
    df = get_local_csv('pharmacies_point.csv')
    # ou
    df = get_local_csv('pharmacies_point')
    """
    # Chemin vers le dossier Données (relatif au dossier scripts)
    donnees_path = os.path.join(os.path.dirname(__file__), '..', 'Données')
    # Ajouter .csv si nécessaire
    if not filename.endswith('.csv'):
        filename += '.csv'
    # Chemin complet du fichier
    file_path = os.path.join(donnees_path, filename)
    # Charger et retourner le DataFrame
    return pd.read_csv(file_path, sep=sep)


def get_pop():
    df_pop = pd.read_excel("popcommunes.xlsx")
    df_pop.rename(columns={'codgeo': 'code_commune'}, inplace=True)
    return df_pop



def extract_departement(code_commune):
    code_commune = str(code_commune)
    if code_commune.startswith(("97", "98")):
        return code_commune[:3]   # DOM
    return code_commune[:2]       # Métropole



def get_departements_from_geojson(path="data/departements-100m.geojson"):
    """
    Récupère les départements français et leurs superficies depuis le GeoJSON officiel.
    
    Parameters
    ----------
    path : str
        Chemin vers le fichier GeoJSON téléchargé.

    Returns
    -------
    pd.DataFrame
        DataFrame avec colonnes: departement, nom, superficie (km²)
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Le fichier GeoJSON n'existe pas: {path}")

    # Lire le GeoJSON avec GeoPandas
    gdf = gpd.read_file(path)

    # Calculer la superficie en km²
    # Attention : la projection doit être métrique pour avoir la superficie correcte
    gdf = gdf.to_crs(epsg=2154)  # Lambert-93
    gdf['superficie'] = gdf.geometry.area / 1_000_000  # m² -> km²

    # Sélectionner les colonnes utiles
    df_superficie = gdf[['code', 'nom', 'superficie']].copy()
    df_superficie.rename(columns={'code': 'departement'}, inplace=True)

    return df_superficie[['departement', 'nom', 'superficie']]
