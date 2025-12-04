import pandas as pd

#fichier_dvf = "dvf2025s1.txt"

#df = pd.read_csv(fichier_dvf, sep=";", encoding="utf-8")

#print(df[["Nom commune", "Valeur foncière", "Surface Carrez du 1er lot"]].head())

#print(df.columns.tolist())

#print(df[["Valeur fonciere"]].head())

#le fichier officiel est en txt c'est infâme donc j'ai pris une version en csv. là c'est juste pour 2025, il faudrait plutôt prendre individuellement les trucs de 2020 à 2024 même si c'est pénible


fichier_dvf = "full.csv"
df=pd.read_csv(fichier_dvf, sep=",", encoding="utf-8")
print(df.columns.tolist())
print(df.shape)
print(df.tail)
print(df[["valeur_fonciere"]])