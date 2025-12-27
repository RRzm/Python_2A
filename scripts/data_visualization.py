import folium
from folium.plugins import HeatMap
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

# Heatmap Folium basée sur df filtré (maisons/appartements) avec lat/lon
# df doit contenir 'nom_commune', 'code_commune', 'latitude', 'longitude'


def carte_a_densite(df_source):
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


def correlation_densite_appartements(geo_stats_with_info):
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