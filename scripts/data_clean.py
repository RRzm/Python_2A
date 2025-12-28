import pandas as pd

def convertir_codes_communes(df):

    def inttostr(valeur):
        if isinstance(valeur, float):
            return str(valeur)
        if isinstance(valeur, int):
            return str(valeur)
        else:
            # Si c'est déjà une str, None, float, etc., on le retourne tel quel
            return valeur

    df.loc[:, 'code_commune'] = df['code_commune'].apply(inttostr)
    return df


def filtre_donnes_pop(df_pop):
    cols = ["p19_pop"]
    df_pop[cols].isna().sum()
    lignes_na = df_pop[df_pop[cols].isna().any(axis=1)]
    return lignes_na


def enleverchiffreDOMs(code):
    if len(code) == 6:
        # retirer le 3ème caractère (index 2)
        return code[:2] + code[3:]
    return code


def troncature_lots(df_sans_lots):

    # Calcul des quantiles 0.025 et 0.975 par commune :
    quantiles_par_commune = (
        df_sans_lots
        .groupby('code_commune')['rapport valeur foncière et surface bâtie']
        .quantile([0.025, 0.975])
        .unstack()
        .reset_index()
        .rename(columns={0.025: 'quantile_025', 0.975: 'quantile_975'})
    )

    # Fusionner les quantiles avec df_sans_lots
    df_sans_lots_tronqué = df_sans_lots.merge(
        quantiles_par_commune,
        on='code_commune',
        how='left'
    )

    df_sans_lots_tronqué = df_sans_lots_tronqué[
        (df_sans_lots_tronqué['rapport valeur foncière et surface bâtie'] >= df_sans_lots_tronqué['quantile_025']) &
        (df_sans_lots_tronqué['rapport valeur foncière et surface bâtie'] <= df_sans_lots_tronqué['quantile_975'])
    ]

    return df_sans_lots_tronqué


###

def prepare_regression_dataset(df, colonnes):
    """
    Sélectionne les colonnes nécessaires à la régression
    et supprime toutes les lignes contenant des valeurs manquantes (NaN).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame original contenant toutes les variables
    colonnes : list
        Liste des noms de colonnes à conserver

    Returns
    -------
    pd.DataFrame
        DataFrame nettoyé, prêt pour une régression linéaire
    """
    # Sélection des colonnes d'intérêt
    df_selection = df[colonnes].copy()
    # Suppression des lignes avec au moins une valeur manquante
    df_clean = df_selection.dropna()
    # Retourne le DataFrame final
    return df_clean


def ajout_non_communes(df_sans_lots):
    # Chargement de la table code_commune -> nom_commune
    communes_df = pd.read_csv('liste_communes.csv', dtype={'code_commune': str})

    # Merge avec ton df_sans_lots
    df_sans_lots = df_sans_lots.merge(communes_df[['code_commune', 'nom_commune']],
                                    on='code_commune',
                                    how='left')

    return df_sans_lots
