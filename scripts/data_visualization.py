import folium
from folium.plugins import HeatMap

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