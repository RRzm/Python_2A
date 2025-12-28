import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.linear_model import LassoCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def run_log_ols_regression(y, X):
    """
    Estime une régression linéaire avec transformation logarithmique de Y.
    L'alignement entre Y et X est effectué par jointure interne sur l'index.

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


def run_log_lasso_cv(
    y,
    X,
    *,
    alphas=None,
    cv=5,
    max_iter=5000,
    random_state=0,
):
    """
    Estime une régression LASSO (L1) sur log(Y) avec validation croisée
    pour sélectionner automatiquement le paramètre de pénalisation et
    obtenir un modèle plus parcimonieux.

    Paramètres
    ----------
    y : pd.Series
        Variable dépendante (strictement positive)
    X : pd.DataFrame
        Variables explicatives
    alphas : array-like | None
        Grille d'alphas testés par LassoCV. Si None, la grille par défaut
        de scikit-learn est utilisée. Une grille logarithmique type
        np.logspace(-4, 1, 30) convient généralement.
    cv : int
        Nombre de plis pour la validation croisée.
    max_iter : int
        Nombre maximal d'itérations de l'optimiseur coordinate descent.
    random_state : int
        Graine pour la reproductibilité.

    Retour
    ------
    dict
        - pipeline : objet Pipeline entraîné (StandardScaler + LassoCV)
        - alpha_ : alpha retenu par la CV
        - coefficients : pd.Series des coefficients (échelle normalisée)
        - n_features_selected : nombre de coefficients non nuls
        - intercept : intercept du modèle LASSO
    """

    # Garantir un index unique pour éviter InvalidIndexError lors de la concat
    if not y.index.is_unique:
        y = y.groupby(level=0).mean()
    if not X.index.is_unique:
        X = X.groupby(level=0).mean()

    data = pd.concat([y, X], axis=1, join="inner").dropna()
    data = data[data[y.name] > 0]

    y_log = np.log(data[y.name])
    X_aligned = data.drop(columns=[y.name])

    feature_names = X_aligned.columns

    pipeline = make_pipeline(
        StandardScaler(with_mean=True, with_std=True),
        LassoCV(
            alphas=alphas,
            cv=cv,
            max_iter=max_iter,
            random_state=random_state,
            n_jobs=None,
        ),
    )

    pipeline.fit(X_aligned, y_log)

    lasso = pipeline.named_steps["lassocv"]
    coefficients = pd.Series(lasso.coef_, index=feature_names, name="coef")

    return {
        "pipeline": pipeline,
        "alpha_": lasso.alpha_,
        "coefficients": coefficients,
        "n_features_selected": int((coefficients != 0).sum()),
        "intercept": float(lasso.intercept_),
    }