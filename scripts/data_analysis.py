import matplotlib.pyplot as plt
import pandas as pd


def relation_surface_prix(df_sans_lots_tronqué):
    # Utilisation du df_sans_lots_tronqué déjà créé pour l'analyse du prix au m²
    df_prix_m2 = df_sans_lots_tronqué.copy()

    # Le rapport valeur foncière/surface est déjà calculé dans df_sans_lots
    # On le renomme pour plus de clarté
    df_prix_m2['prix_m2'] = df_prix_m2['rapport valeur foncière et surface bâtie']

    print("Statistiques du prix au m² par type de bien :")
    print("="*70)
    stats_m2 = df_prix_m2.groupby('type_local')['prix_m2'].describe()
    print(stats_m2)

    # Figure 1 : Scatter Surface vs Prix total
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    ax1, ax2 = axes

    for type_bien, color, marker in [('Maison', '#2ecc71', 'o'), ('Appartement', '#e74c3c', 's')]:
        subset = df_prix_m2[df_prix_m2['type_local'] == type_bien]
        if len(subset) > 0:
            sample = subset.sample(min(2000, len(subset)))
            ax1.scatter(sample['surface_reelle_bati'], sample['valeur_fonciere'],
                        alpha=0.4, s=20, label=type_bien, color=color, marker=marker)
    ax1.set_xlabel('Surface (m²)', fontsize=12)
    ax1.set_ylabel('Prix total (€)', fontsize=12)
    ax1.set_title('Relation Surface vs Prix', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}k€'))

    # Figure 2 : Répartition par tranche de prix au m²
    tranches_m2 = [0, 1000, 2000, 3000, 4000, 5000, float('inf')]
    labels_m2 = ['<1k', '1-2k', '2-3k', '3-4k', '4-5k', '>5k']
    df_prix_m2['tranche_m2'] = pd.cut(df_prix_m2['prix_m2'], bins=tranches_m2, labels=labels_m2)
    tranche_m2_stats = df_prix_m2.groupby(['tranche_m2', 'type_local']).size().unstack(fill_value=0)
    tranche_m2_pct = tranche_m2_stats.div(tranche_m2_stats.sum(axis=1), axis=0) * 100
    tranche_m2_pct[['Maison', 'Appartement']].plot(kind='bar', ax=ax2, color=['#2ecc71', '#e74c3c'])
    ax2.set_title('Répartition par tranche de prix au m²', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Pourcentage (%)', fontsize=12)
    ax2.set_xlabel('Tranche de prix au m²', fontsize=12)
    ax2.legend(['Maison', 'Appartement'], fontsize=10)
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.show()
