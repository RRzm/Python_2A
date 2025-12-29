import pandas as pd

def convertir_codes_communes(df):
    """
    Convertit les codes communes en string pour éviter les pertes d'information.
    
    Certains codes communes (2A, 2B en Corse) ne peuvent pas être convertis en int.
    
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
    """
    Supprime le 3ème chiffre des codes communes DOM à 6 chiffres.
    
    Exemple: '974421' (Réunion) -> '97421' (harmonisation avec DVF)
    
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
        # retirer le 3ème caractère (index 2)
        return code[:2] + code[3:]
    return code


def troncature_lots(df1):
    """
    Tronque les prix aberrants par commune (méthode robuste).
    
    Calcule les quantiles (2.5% et 97.5%) par commune, puis supprime
    les valeurs en dehors de cet intervalle pour chaque commune.
    
    Paramètres
    ----------
    df_sans_lots : pd.DataFrame
        DataFrame avec colonne 'rapport valeur foncière et surface bâtie'
    
    Returns
    -------
    pd.DataFrame
        DataFrame tronqué (outliers supprimés)
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


def ajout_non_communes(df_sans_lots, communes_df):
    # Merge avec ton df_sans_lots
    df_sans_lots = df_sans_lots.merge(communes_df[['code_commune', 'nom_commune']],
                                    on='code_commune',
                                    how='left')

    return df_sans_lots


# --- Outils de contrôle qualité ---

def resume_manquants(df, colonnes):
    """
    Retourne un DataFrame avec le nombre et le pourcentage de valeurs manquantes
    pour un sous-ensemble de colonnes.
    """
    resume = (
        df[colonnes]
        .isna()
        .sum()
        .rename("n_manquants")
        .to_frame()
    )
    resume["pct_manquants"] = (resume["n_manquants"] / len(df)) * 100
    resume = resume.sort_values("pct_manquants", ascending=False)
    return resume


def borne_rapide(series, lower=0.01, upper=0.99):
    """
    Calcule rapidement des bornes robustes pour une série numérique.
    """
    q_low, q_hi = series.quantile([lower, upper])
    return q_low, q_hi


def rapport_outliers(series, lower=0.01, upper=0.99):
    """
    Renvoie la part d'observations en dehors des bornes quantiles.
    """
    q_low, q_hi = borne_rapide(series, lower, upper)
    mask = (series < q_low) | (series > q_hi)
    part_outliers = mask.mean() * 100
    return {
        "borne_basse": q_low,
        "borne_haute": q_hi,
        "pct_outliers": part_outliers,
    }