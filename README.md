# # Analyse du dynamisme immobilier des communes françaises

*Par Yanis Larré, Tom Croquette et Renan Romariz*

---

## Introduction

Ce travail s'intéresse aux déterminants territoriaux de la demande immobilière en France, à travers l'analyse des variations spatiales du prix au mètre carré et du volume de transactions. Dans un contexte de fortes disparités géographiques que nous illustrons en détail, nous cherchons à comprendre comment certaines caractéristiques locales influencent l'attractivité résidentielle dans les territoires.


## Méthode

Notre analyse repose sur un croisement de plusieurs bases de données couvrant la quasi totalité du territoire français. Les données de transactions immobilières proviennent de la base DVF (Demandes de Valeurs Foncières), qui recense l'intégralité des ventes de biens immobiliers en France hormis certains départements particuliers qui n'utilisent pas ce dispositif.

Le traitement des données implique plusieurs étapes : nettoyage et normalisations, agrégation géographique à l'échelle communale et départementale, calcul de statistiques descriptives (prix médian, nombre de transactions, etc), puis fusion des différentes sources sur la base de codes géographiques harmonisés (permettant ainsi de calculer par exemple le taux de ventes par habitant).

Les données nettoyées nous permettent ainsi d'analyser plus en détail les différentes relations entre les paramètres, et de confirmer des tendances intuitives (ou l'inverse).

L'analyse économétrique proposée en fin de projet permet enfin d'apporter une modélisation du prix au mètre carré moyen par commune en utilisant quelques variables explicatives illustrant le niveau vie (présence de médecins, salaires élevés, etc) ainsi que le taux d'occupation et la densité de population dont le rôle a été explicité dans l'analyse des données.

## Sources de données

Notre travail mobilise plusieurs bases de données publiques :

• Le fichier DVF du ministère de l'Économie et des Finances, qui constitue la référence nationale en matière de transactions immobilières (disponible sur data.gouv.fr), stocké sur SSP Cloud.
• Un fichier de populations par communes produit par le département du Loiret à partir de données INSEE et mis en ligne sur datagouv
• Les référentiels géographiques (codes communes, contours départementaux) fournis par l'INSEE et l'IGN, disponibles au format CSV dans le projet.
• Le "dossier complet" de l'INSEE, disponible sur le site de l'INSEE et rassemblant de nombreux indicateurs communaux
Toutes ces données ont été récupérées au format CSV ou JSON, puis harmonisées pour permettre leur croisement géographique.

## Organisation du dépôt

L'essentiel de notre analyse est contenu dans le notebook principal [`main.ipynb`](main.ipynb), qui présente l'intégralité du traitement, de l'analyse et de la modélisation, accompagné de commentaires et de visualisations. Ce notebook a été exécuté dans son intégralité pour permettre la consultation des résultats sans nécessiter de réexécution.

Le répertoire `scripts/` regroupe l'ensemble des fonctions utilisées et appelées dans le notebook principal, organisées par thématique :

• `get_data.py` : récupération et chargement des données  
• `data_clean.py` : nettoyage des données  
• `data_analysis.py` : statistiques descriptives et visualisations primaires
• `data_visualization.py` : graphiques et visuels pour l'analyse et l'exploration des données 
• `do_ols.py` : modèles de régression
• `global_variables.py` : variables globales utilisées dans le projet

Le dossier `Données/` contient des fichiers CSV et GeoJSON utilisés dans le projet.

Le fichier [`requirements.txt`](requirements.txt) liste les dépendances Python nécessaires à l'exécution du code (pandas, numpy, matplotlib, statsmodels, folium, etc).

## Reproductibilité

Pour reproduire l'analyse dans son intégralité, il suffit d'installer les dépendances listées dans [`requirements.txt`](requirements.txt) puis d'exécuter les cellules du notebook [`main.ipynb`](main.ipynb).

Les scripts du dossier `scripts/` sont importés automatiquement par le notebook principal.

Certaines cartes graphiques dynamiques sont parfois lourdes ou non exécutées : elles ont été préalablement exécutées et téléchargées, et sont disponibles au format HTML dans le projet (fichiers html qui commencent par 'carte'). En cas de problème de visualisation, il suffit de les télécharger et de les ouvrir.
