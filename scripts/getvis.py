import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt


def plot_log_ols_regression(model, y, X, title="Régression log-OLS", 
                            remove_outliers=True, percentile_threshold=99):
    """
    Trace un graphique des valeurs observées vs valeurs ajustées d'une régression log-OLS.

    Parameters
    ----------
    model : statsmodels.regression.linear_model.RegressionResults
        Résultat de la régression log-OLS
    y : pd.Series
        Variable dépendante originale (non transformée)
    X : pd.DataFrame
        Variables explicatives originales
    title : str
        Titre du graphique
    remove_outliers : bool
        Si True, supprime les valeurs extrêmes pour une meilleure visualisation.
    percentile_threshold : float
        Pourcentage à prendre en compte pour les valeurs aberrantes (par défaut : 99)
    """
    # Aligner y et X de la même manière que dans la régression
    data = pd.concat([y, X], axis=1, join='inner').dropna()
    data = data[data[y.name] > 0]
    y_aligned = data[y.name]
    X_aligned = sm.add_constant(data.drop(columns=[y.name]))

    # Valeurs ajustées (à l'échelle originale)
    y_pred_log = model.predict(X_aligned)
    y_pred = np.exp(y_pred_log)

    # Supprimer les valeurs aberrantes pour la visualisation si demandé
    if remove_outliers:
        threshold_obs = np.percentile(y_aligned, percentile_threshold)
        threshold_pred = np.percentile(y_pred, percentile_threshold)
        
        mask = (y_aligned <= threshold_obs) & (y_pred <= threshold_pred)
        y_plot = y_aligned[mask]
        y_pred_plot = y_pred[mask]
        
        n_removed = len(y_aligned) - len(y_plot)
        if n_removed > 0:
            print(f"Info: {n_removed} valeurs extrêmes retirées pour une meilleure visualisation")
    else:
        y_plot = y_aligned
        y_pred_plot = y_pred

    # Plot
    plt.figure(figsize=(10, 7))
    plt.scatter(y_plot, y_pred_plot, color='blue', alpha=0.5, 
                edgecolors='navy', linewidth=0.5, label='Prédictions')
    
    # Ligne de référence y = y_pred
    min_val = min(y_plot.min(), y_pred_plot.min())
    max_val = max(y_plot.max(), y_pred_plot.max())
    plt.plot([min_val, max_val], [min_val, max_val],
             color='red', linestyle='--', linewidth=2, label='y = y_pred')
    
    plt.xlabel("Valeurs observées", fontsize=12)
    plt.ylabel("prix au m2", fontsize=12)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # Ajouter des statistiques au graphique
    r2 = model.rsquared
    plt.text(0.05, 0.95, f'R² = {r2:.4f}', 
             transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.show()
    
    # Renvoyer des informations sur les données
    return {
        'n_total': len(y_aligned),
        'n_plotted': len(y_plot),
        'y_max': y_aligned.max(),
        'y_pred_max': y_pred.max()
    }