import os
import s3fs
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_dvf():
    """
    Charge les données DVF géolocalisées depuis S3 et retourne un DataFrame.
    Retourne:
    --------
    pd.DataFrame
        DataFrame contenant les données DVF
    Exemple:
    --------
    df = get_dvf()
    """
    S3_ENDPOINT_URL = "https://" + os.environ["AWS_S3_ENDPOINT"]
    fs = s3fs.S3FileSystem(
        anon=True,
        client_kwargs={"endpoint_url": S3_ENDPOINT_URL}
    )
    with fs.open("renan/diffusion/dvf.csv", mode="rb") as f:
        df = pd.read_csv(f, dtype={'code_commune': "str"})
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
