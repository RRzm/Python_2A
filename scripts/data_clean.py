import pandas as pd


def convertir_codes_communes(df):
    """
    Convertit les codes communes en string pour éviter les pertes d'information.
    
    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant une colonne 'code_commune'
    
    Returns
    -------
    pd.DataFrame
        DataFrame avec 'code_commune' convertie en string
    """

    def inttostr(valeur):
        if isinstance(valeur, float):
            return str(valeur)
        if isinstance(valeur, int):
            return str(valeur)
        else:
            # Si c'est déjà de type string, on renvoie directement
            return valeur

    df.loc[:, 'code_commune'] = df['code_commune'].apply(inttostr)
    return df


def filtre_donnes_pop(df_pop):
    """
    Identifie les lignes contenant des valeurs manquantes dans les colonnes
    de population d'intérêt et retourne uniquement ces lignes.

    Paramètres
    ----------
    df_pop : pd.DataFrame
        DataFrame de population (ex ici : INSEE) contenant la colonne 'p19_pop' (population en 2019)

    Retour
    ------
    pd.DataFrame
        Lignes présentant au moins une valeur manquante
    """
    cols = ["p19_pop"]
    df_pop[cols].isna().sum()
    lignes_na = df_pop[df_pop[cols].isna().any(axis=1)]
    return lignes_na


def enleverchiffreDOMs(code):
    """
    Supprime le 3ème chiffre des codes communes DOM à 6 chiffres.
    
    Paramètres
    ----------
    code : str
        Code commune (potentiellement à 6 chiffres)
    
    Returns
    -------
    str
        Code commune harmonisé (5 chiffres)
    """
    if len(code) == 6:
        # retirer le 3ème caractère (index 2) si  concerné
        return code[:2] + code[3:]
    return code


def troncature_lots(df1):
    """
    Tronque les prix aberrants par commune
    
    Calcule les quantiles (2.5% et 97.5%) par commune, puis supprime
    les valeurs en dehors de cet intervalle pour chaque commune.
    
    Paramètres
    ----------
    df_sans_lots : pd.DataFrame
        DataFrame avec colonne 'rapport valeur foncière et surface bâtie'
    
    Returns
    -------
    pd.DataFrame
        DataFrame tronqué
    """
    # Calcul des quantiles 0.025 et 0.975 par commune :
    quantiles_par_commune = (
        df1
        .groupby('code_commune')['rapport valeur foncière et surface bâtie']
        .quantile([0.025, 0.975])
        .unstack()
        .reset_index()
        .rename(columns={0.025: 'quantile_025', 0.975: 'quantile_975'})
    )

    # Fusionner les quantiles avec df_sans_lots
    df2 = df1.merge(
        quantiles_par_commune,
        on='code_commune',
        how='left'
    )

    df2 = df2[
        (df2['rapport valeur foncière et surface bâtie'] > df2['quantile_025']) &
        (df2['rapport valeur foncière et surface bâtie'] < df2['quantile_975'])
    ]

    return df2


def ajout_non_communes(df_sans_lots, communes_df):
    """
    Ajoute le libellé de commune au DataFrame DVF par jointure sur le code
    commune.

    Paramètres
    ----------
    df_sans_lots : pd.DataFrame
        Données DVF filtrées, avec la colonne 'code_commune'.
    communes_df : pd.DataFrame
        Référentiel des communes contenant 'code_commune' et 'nom_commune'.

    Retour
    ------
    pd.DataFrame
        DataFrame enrichi de la colonne 'nom_commune'.
    """
    
    df_sans_lots = df_sans_lots.merge(communes_df[['code_commune', 'nom_commune']],
                                    on='code_commune',
                                    how='left')

    return df_sans_lots
