def inttostr(valeur):
    if isinstance(valeur, float):
        return str(valeur)
    if isinstance(valeur, int):
        return str(valeur)
    else:
        # Si c'est déjà une str, None, float, etc., on le retourne tel quel
        return valeur

