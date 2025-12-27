import folium
from folium.plugins import HeatMap


def carte_a_densite(df):
    # Vérifier si carte_data existe, sinon recréer les données
    if 'carte_data' not in locals():
        print("Recréation des données nécessaires...")
        
        # Filtrer pour ne garder que les maisons et appartements
        df_filtered = df[df['type_local'].isin(['Maison', 'Appartement'])].copy()
        
        # Compter le nombre de ventes par commune
        ventes_par_commune = df_filtered.groupby(['nom_commune', 'code_commune']).size().reset_index(name='nb_ventes')
        
        # Récupérer les coordonnées moyennes par commune
        coords_par_commune = df_filtered.groupby(['nom_commune', 'code_commune']).agg({
            'latitude': 'mean',
            'longitude': 'mean'
        }).reset_index()
        
        # Fusionner avec le nombre de ventes
        carte_data = ventes_par_commune.merge(coords_par_commune, on=['nom_commune', 'code_commune'])
        
        # Supprimer les lignes avec des coordonnées manquantes
        carte_data = carte_data.dropna(subset=['latitude', 'longitude'])
        
        print(f"✓ Données créées : {len(carte_data)} communes")

    # Préparer les données pour la heatmap (latitude, longitude, intensité)
    heat_data = [[row['latitude'], row['longitude'], row['nb_ventes']] 
                for idx, row in carte_data.iterrows()]

    # Créer une carte centrée sur la France
    m = folium.Map(
        location=[46.5, 2.5],
        zoom_start=6,
        tiles='cartodbpositron'  # Fond clair et épuré
    )

    # Ajouter la heatmap avec un lissage amélioré
    # radius: taille des points (plus grand = plus lisse)
    # blur: niveau de flou (plus grand = plus lisse)
    HeatMap(
        heat_data,
        min_opacity=0.2,
        max_zoom=13,
        radius=30,       # Augmenté de 15 à 25 pour plus de lissage
        blur=25,         # Augmenté de 20 à 35 pour un effet plus fluide
        gradient={
            0.0: 'blue',
            0.3: 'cyan',
            0.5: 'lime',
            0.7: 'yellow',
            0.9: 'orange',
            1.0: 'red'
        }
    ).add_to(m)

    # Afficher la carte
    return m
