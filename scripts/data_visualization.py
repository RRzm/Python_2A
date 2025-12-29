import folium
from folium.plugins import HeatMap
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np
import json
import sys

# Heatmap Folium basée sur df filtré (maisons/appartements) avec lat/lon
# df doit contenir 'nom_commune', 'code_commune', 'latitude', 'longitude'


def carte_a_densite(df_source):
    """
    Génère une carte de chaleur Folium représentant l'intensité des ventes
    par commune à partir de points (latitude/longitude).

    Paramètres
    ----------
    df_source : pd.DataFrame
        Données individuelles avec au minimum 'nom_commune', 'code_commune',
        'latitude' et 'longitude'.

    Retour
    ------
    folium.Map
        Carte Folium avec une couche HeatMap ajoutée.
    """
    df_points = df_source.dropna(subset=['latitude', 'longitude']).copy()

    ventes_par_commune = (
        df_points.groupby(['nom_commune', 'code_commune'])
        .size()
        .reset_index(name='nb_ventes')
    )

    coords_par_commune = (
        df_points.groupby(['nom_commune', 'code_commune'])
        .agg({'latitude': 'mean', 'longitude': 'mean'})
        .reset_index()
    )

    carte_data = ventes_par_commune.merge(
        coords_par_commune,
        on=['nom_commune', 'code_commune']
    )

    heat_data = carte_data[['latitude', 'longitude', 'nb_ventes']].values.tolist()

    m = folium.Map(location=[46.5, 2.5], zoom_start=6, tiles='cartodbpositron')

    HeatMap(
        heat_data,
        min_opacity=0.2,
        max_zoom=13,
        radius=30,
        blur=25,
        gradient={
            0.0: 'blue',
            0.3: 'cyan',
            0.5: 'lime',
            0.7: 'yellow',
            0.9: 'orange',
            1.0: 'red'
        }
    ).add_to(m)

    return m


def carte_repartition_ventes(df):
    """
    Affiche avec Plotly une carte des ventes agrégées par commune
    (taille et couleur proportionnelles au nombre de ventes).

    Paramètres
    ----------
    df : pd.DataFrame
        Données individuelles filtrées (maisons/appartements) contenant
        'nom_commune', 'code_commune', 'latitude', 'longitude'.

    Retour
    ------
    None
    """
    # Utilisation du df déjà filtré (maisons et appartements uniquement)
    # Compter le nombre de ventes par commune
    ventes_par_commune_carte = df.groupby(['nom_commune', 'code_commune']).size().reset_index(name='nb_ventes')

    # Récupérer les coordonnées moyennes par commune
    coords_par_commune = df.groupby(['nom_commune', 'code_commune']).agg({
        'latitude': 'mean',
        'longitude': 'mean'
    }).reset_index()

    # Fusionner avec le nombre de ventes
    carte_data = ventes_par_commune_carte.merge(coords_par_commune, on=['nom_commune', 'code_commune'])

    # Supprimer les lignes avec des coordonnées manquantes
    carte_data = carte_data.dropna(subset=['latitude', 'longitude'])

    print(f"Données créées : {len(carte_data)} communes")

    # Créer une carte interactive avec plotly
    fig = px.scatter_mapbox(
        carte_data,
        lat='latitude',
        lon='longitude',
        size='nb_ventes',
        color='nb_ventes',
        hover_name='nom_commune',
        hover_data={'nb_ventes': True, 'latitude': False, 'longitude': False, 'code_commune': True},
        color_continuous_scale='YlOrRd',
        size_max=30,
        zoom=5,
        title='Densité des ventes de maisons et appartements par commune en France',
        height=800
    )

    fig.update_layout(
        mapbox_style='open-street-map',
        mapbox_center={'lat': 46.5, 'lon': 2.5}
    )

    fig.show()


def surfaces(df_sans_lots):
    """
    Explore la distribution des surfaces bâties des biens (hors outliers)
    et produit un boxplot par type de bien ainsi qu'un histogramme.

    Paramètres
    ----------
    df_sans_lots : pd.DataFrame
        Données DVF nettoyées avec au minimum 'surface_reelle_bati'
        et 'type_local'.

    Retour
    ------
    None
    """

    # Utilisation du df_sans_lots déjà créé
    df_surface = df_sans_lots[df_sans_lots['surface_reelle_bati'].notna()].copy()
    df_surface = df_surface[df_surface['surface_reelle_bati'] > 0]
    df_surface = df_surface[df_surface['surface_reelle_bati'] < 300]  # Enlever les outliers extrêmes

    print("Statistiques des surfaces par type de bien :")
    print("="*70)
    print(df_surface.groupby('type_local')['surface_reelle_bati'].describe())

    # Visualisation
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Boxplot des surfaces
    df_surface.boxplot(column='surface_reelle_bati', by='type_local', ax=axes[0])
    axes[0].set_title('Distribution des surfaces par type de bien')
    axes[0].set_xlabel('Type de bien')
    axes[0].set_ylabel('Surface (m²)')
    plt.sca(axes[0])
    plt.xticks(rotation=0)

    # Histogramme des surfaces
    for type_bien in ['Maison', 'Appartement']:
        data = df_surface[df_surface['type_local'] == type_bien]['surface_reelle_bati']
        axes[1].hist(data, bins=50, alpha=0.6, label=type_bien, edgecolor='black')
    axes[1].set_title('Distribution des surfaces')
    axes[1].set_xlabel('Surface (m²)')
    axes[1].set_ylabel('Fréquence')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def scatter_prix_densite(geo_stats_with_info, df_final):
    """
    Scatter plot : Prix au m² vs Densité de population par département.
    Avec courbe de tendance linéaire.
    
    Parameters
    ----------
    geo_stats_with_info : pd.DataFrame
        DataFrame avec densité et info départementales
    df_final : pd.DataFrame
        DataFrame avec prix au m² moyen par commune
    """
    import pandas as pd
    from scipy import stats
    
    # Extraire le code département de df_final pour agréger
    def extract_dept(code_commune):
        code_str = str(code_commune)
        return code_str[:2]
    
    df_copy = df_final.reset_index().copy()
    df_copy['departement'] = df_copy['code_commune'].astype(str).apply(extract_dept)
    
    # Calculer prix moyen par département
    prix_par_dept = df_copy.groupby('departement').agg({
        'moyenne tronquée du prix au m2 maisons et appartements': 'mean'
    }).reset_index()
    
    # Fusionner avec densité départementale
    merged = prix_par_dept.merge(
        geo_stats_with_info[['departement', 'densite', 'dept_nom']],
        on='departement',
        how='inner'
    )
    
    merged_clean = merged.dropna(subset=['densite', 'moyenne tronquée du prix au m2 maisons et appartements'])
    
    if len(merged_clean) == 0:
        print("Aucune donnée valide pour le graphique prix vs densité.")
        return
    
    # Calculer la regression linéaire pour la tendance
    x_data = merged_clean['densite'].values
    y_data = merged_clean['moyenne tronquée du prix au m2 maisons et appartements'].values
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
    line = slope * x_data + intercept
    
    # Plot avec plotly
    fig = px.scatter(
        merged_clean,
        x='densite',
        y='moyenne tronquée du prix au m2 maisons et appartements',
        hover_name='dept_nom',
        hover_data={
            'densite': ':.0f',
            'moyenne tronquée du prix au m2 maisons et appartements': ':.0f',
            'departement': True,
            'dept_nom': False
        },
        title='Relation entre Densité de population et Prix au m² par département',
        labels={
            'densite': 'Densité (hab/km²)',
            'moyenne tronquée du prix au m2 maisons et appartements': 'Prix moyen au m² (€)'
        },
        height=600,
        opacity=0.8
    )
    
    # Ajouter la ligne de tendance
    fig.add_scatter(
        x=x_data,
        y=line,
        mode='lines',
        name=f'Tendance (R²={r_value**2:.3f})',
        line=dict(color='red', width=2, dash='dash')
    )
    
    fig.update_layout(
        xaxis_type='log',
        hovermode='closest',
        showlegend=True
    )
    
    fig.show()
    
    # Afficher les stats de la régression
    print(f"Relation Prix/m² vs Densité par département :")
    print(f"  Pente : {slope:.4f} €/m² par hab/km²")
    print(f"  R² : {r_value**2:.4f}")
    print(f"  p-value : {p_value:.4e}")
    print(f"  Départements analysés : {len(merged_clean)}")


def correlation_densite_appartements(geo_stats_with_info):
    """
    Visualise la relation entre la densité de population et la part
    d'appartements par département.

    Paramètres
    ----------
    geo_stats_with_info : pd.DataFrame
        Tableau agrégé par département avec colonnes 'densite',
        'pct_appartement', 'Maison', 'Appartement', 'dept_nom' et 'total'.

    Retour
    ------
    None
    """
    # Visualisation 2 : Relation entre densité et type de logement
    fig2 = px.scatter(geo_stats_with_info.dropna(subset=['densite']), 
                    x='densite', 
                    y='pct_appartement',
                    size='total',
                    color='pct_appartement',
                    hover_name='dept_nom',
                    hover_data={'Maison': True, 'Appartement': True, 'densite': ':.0f'},
                    title='Corrélation : Densité de population vs % Appartements',
                    labels={'densite': 'Densité (hab/km²)', 'pct_appartement': '% Appartements'},
                    color_continuous_scale='Turbo',  # meilleure lisibilité pour les faibles valeurs
                    height=600,
                    size_max=30)

    # Améliorer le contraste visuel des marqueurs
    fig2.update_traces(marker=dict(opacity=0.9,
                                line=dict(width=1, color='rgba(0,0,0,0.3)')))

    fig2.update_layout(
        xaxis_title='Densité de population (habitants/km²)',
        yaxis_title='Pourcentage d\'Appartements (%)',
        xaxis_type='log'  # Échelle logarithmique pour mieux voir la distribution
    )

    fig2.show()


def carte_choropleth_departements_prix_m2(
    df_source,
    *,
    value_col='rapport valeur foncière et surface bâtie',
    agg='median',
    geojson_path='Données/data/departements-100m.geojson',
    tiles='cartodbpositron'
    ):
    """
    Crée une carte choropleth des départements colorés par prix moyen au m².

    Paramètres
    ----------
    df_source : pd.DataFrame
        Données individuelles DVF, avec au minimum 'code_commune' et
        la colonne de valeur spécifiée par `value_col`.
    value_col : str
        Nom de la colonne mesurant le prix/m² (par défaut le rapport
        valeur foncière / surface bâtie).
    agg : {'mean','median'}
        Fonction d'agrégation pour obtenir la métrique par département.
    geojson_path : str
        Chemin vers le GeoJSON des départements (doit contenir
        properties.code pour le code département).
    tiles : str
        Fond de carte Folium.

    Retour
    ------
    folium.Map
        Carte choropleth Folium centrée sur la France.
    """
    if value_col not in df_source.columns:
        raise KeyError(f"La colonne '{value_col}' est absente des données.")

    def extract_departement(code_commune):
        code_commune = str(code_commune)
        return code_commune[:2]
    df = df_source.copy()
    df = df.dropna(subset=['code_commune', value_col])
    df = df[df[value_col] > 0]
    df['departement'] = df['code_commune'].astype(str).apply(extract_departement)

    if agg == 'mean':
        agg_df = df.groupby('departement', as_index=False)[value_col].mean()
    elif agg == 'median':
        agg_df = df.groupby('departement', as_index=False)[value_col].median()
    else:
        raise ValueError("agg doit être 'mean' ou 'median'")

    agg_df.rename(columns={value_col: 'prix_m2'}, inplace=True)

    # Charger le GeoJSON des départements
    with open(geojson_path, 'r', encoding='utf-8') as f:
        departements_geojson = json.load(f)

    m = folium.Map(location=[46.5, 2.5], zoom_start=6, tiles=tiles)

    folium.Choropleth(
        geo_data=departements_geojson,
        name='choropleth',
        data=agg_df,
        columns=['departement', 'prix_m2'],
        key_on='feature.properties.code',
        fill_color='YlOrRd',
        fill_opacity=0.8,
        line_opacity=0.2,
        legend_name='Prix au m² (médiane par département)'
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


def carte_choropleth_departements_surfaces(
    df_source,
    *,
    value_col='surface_reelle_bati',
    agg='median',
    geojson_path='Données/data/departements-100m.geojson',
    tiles='cartodbpositron'
):
    """
    Crée une carte choropleth des départements colorés par surface moyenne/médiane.

    Paramètres
    ----------
    df_source : pd.DataFrame
        Données individuelles DVF, avec au minimum 'code_commune' et
        'surface_reelle_bati'.
    value_col : str
        Nom de la colonne de surface (par défaut 'surface_reelle_bati').
    agg : {'mean','median'}
        Fonction d'agrégation pour obtenir la métrique par département.
    geojson_path : str
        Chemin vers le GeoJSON des départements (doit contenir
        properties.code pour le code département).
    tiles : str
        Fond de carte Folium.

    Retour
    ------
    folium.Map
        Carte choropleth Folium centrée sur la France.
    """
    if value_col not in df_source.columns:
        raise KeyError(f"La colonne '{value_col}' est absente des données.")

    # Extraire le code département (DOM gérés: 3 chiffres, sinon 2)
    def extract_departement(code_commune):
        code_commune = str(code_commune)
        return code_commune[:2]

    df = df_source.copy()
    df = df.dropna(subset=['code_commune', value_col])
    df = df[df[value_col] > 0]
    df['departement'] = df['code_commune'].astype(str).apply(extract_departement)

    if agg == 'mean':
        agg_df = df.groupby('departement', as_index=False)[value_col].mean()
    elif agg == 'median':
        agg_df = df.groupby('departement', as_index=False)[value_col].median()
    else:
        raise ValueError("agg doit être 'mean' ou 'median'")

    agg_df.rename(columns={value_col: 'surface_m2'}, inplace=True)

    # Charger le GeoJSON des départements (import local pour robustesse)
    import json
    with open(geojson_path, 'r', encoding='utf-8') as f:
        departements_geojson = json.load(f)

    m = folium.Map(location=[46.5, 2.5], zoom_start=6, tiles=tiles)

    folium.Choropleth(
        geo_data=departements_geojson,
        name='choropleth',
        data=agg_df,
        columns=['departement', 'surface_m2'],
        key_on='feature.properties.code',
        fill_color='Blues',
        fill_opacity=0.8,
        line_opacity=0.2,
        legend_name='Surface (m², médiane par département)'
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m