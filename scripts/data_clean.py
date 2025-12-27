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
