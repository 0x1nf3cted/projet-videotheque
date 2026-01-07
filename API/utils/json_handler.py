import json
import os

DATA_DIR = os.environ.get('DATA_DIR', '/app/data') # une valeur de backeup en cas ou

def lire_json(fichier):
    chemin = os.path.join(DATA_DIR, fichier)
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

#fonction pour ecrire dans un fichier json (alternatif a la db)
def ecrire_json(fichier, donnees):
    os.makedirs(DATA_DIR, exist_ok=True)
    chemin = os.path.join(DATA_DIR, fichier)
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)
