import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LassoCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def run_log_ols_regression(y, X):
    """
    Estime une régression linéaire avec transformation logarithmique de Y.

    Parameters
    ----------
    y : pd.Series
        Variable dépendante (strictement positive)
    X : pd.DataFrame
        Variables explicatives

    Returns
    -------
    model : statsmodels.regression.linear_model.RegressionResults
        Résultat de la régression OLS sur log(Y)
    """

    # Garantir un index unique pour éviter InvalidIndexError lors de la concat
    if not y.index.is_unique:
        y = y.groupby(level=0).mean()
    if not X.index.is_unique:
        X = X.groupby(level=0).mean()

    # Concaténation interne sur l'index entre Y et X
    data = pd.concat([y, X], axis=1, join='inner')

    # Suppression des valeurs manquantes
    data = data.dropna()

    # Suppression des valeurs non positives de Y (log impossible)
    data = data[data[y.name] > 0]

    # Séparation de Y et X
    y_aligned = np.log(data[y.name])
    X_aligned = data.drop(columns=[y.name])

    # Ajout de la constante (intercept)
    X_aligned = sm.add_constant(X_aligned)

    # Estimation du modèle OLS
    model = sm.OLS(y_aligned, X_aligned).fit()

    return model