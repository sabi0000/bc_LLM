import pandas as pd

# načítanie CSV
#df = pd.read_csv("hemorrhage.csv")
#df = pd.read_csv("normall.csv")
#df = pd.read_csv("ventriculal.csv")
#df = pd.read_csv("pericardial.csv")
df = pd.read_csv("acute_stress.csv")

# uloženie do JSON
df.to_json(
    #"hemorrhage.json",
    #"normall.json",
    #"ventriculal.json",
    #"pericardial.json",
    "acute_stress.json",
    orient="records",
    indent=2
)

print("Hotovo: json bol vytvorený.")