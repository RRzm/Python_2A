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
