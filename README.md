# Demande immobilière en France

*Par Yanis Larré, Tom Croquette et Renan Romariz*

---

## Introduction

Ce travail s'intéresse aux déterminants territoriaux de la demande immobilière en France, à travers l'analyse des variations spatiales du prix au mètre carré et du volume de transactions. Dans un contexte de fortes disparités géographiques, nous cherchons à comprendre comment certaines caractéristiques locales (développement humain, criminalité) influencent l'attractivité résidentielle des territoires.

L'enjeu est de dépasser les approches macroéconomiques traditionnelles pour intégrer des variables reflétant plus directement la qualité de vie et l'environnement socio-économique à l'échelle communale et départementale. Nous testons l'hypothèse selon laquelle un niveau de développement humain élevé et un environnement plus sûr stimulent la demande immobilière, tandis qu'une criminalité élevée la freine.

## Méthode

Notre analyse repose sur un croisement de plusieurs bases de données géolocalisées couvrant la quasi totalité du territoire français. Les données de transactions immobilières proviennent de la base DVF (Demandes de Valeurs Foncières), qui recense l'intégralité des ventes de biens immobiliers en France. 

Le traitement des données implique plusieurs étapes : nettoyage et normalisation des adresses, agrégation géographique à l'échelle communale et départementale, calcul de statistiques descriptives (prix médian, nombre de transactions, taux de ventes par habitant), puis fusion des différentes sources sur la base de codes géographiques harmonisés.

L'analyse économétrique repose sur des régressions linéaires multiples (OLS).

## Sources de données

Notre travail mobilise plusieurs bases de données publiques :

• Le fichier DVF du ministère de l'Économie et des Finances, qui constitue la référence nationale en matière de transactions immobilières (disponible sur data.gouv.fr), stocké sur SSP Cloud.

• Les référentiels géographiques (codes communes, contours départementaux) fournis par l'INSEE et l'IGN, disponibles au format CSV dans le projet.

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

Le dossier `Données/` contient l'ensemble des fichiers CSV et GeoJSON utilisés.

Le fichier [`requirements.txt`](requirements.txt) liste les dépendances Python nécessaires à l'exécution du code (pandas, numpy, matplotlib, statsmodels, folium, etc).

## Reproductibilité

Pour reproduire l'analyse dans son intégralité, il suffit d'installer les dépendances listées dans [`requirements.txt`](requirements.txt) puis d'exécuter séquentiellement les cellules du notebook [`main.ipynb`](main.ipynb).

Les scripts du dossier `scripts/` sont importés automatiquement par le notebook principal.

## Principaux résultats

A COMPLETER