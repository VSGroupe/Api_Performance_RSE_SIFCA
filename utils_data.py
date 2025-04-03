import json
import os
from supabase import create_client

# Configuration Supabase
url = "https://djlcnowdwysqbrggekme.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRqbGNub3dkd3lzcWJyZ2dla21lIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTIxNzc1NjcsImV4cCI6MjAwNzc1MzU2N30.UxvLKjDhQ4ghsGTTY7Sy1Q75YCktx2nXR2pHuLeIMF4"
supabase = create_client(url, key)

def saveDataInJson(dataList, entite, fileName):
    """Sauvegarde des données dans un fichier JSON"""
    try:
        directory_path = f'donnees/{entite}'
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        file_path = os.path.join(directory_path, fileName)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(dataList, file, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {str(e)}")
        raise

def readDataJson(entite, fileName):
    """Lecture des données depuis un fichier JSON"""
    try:
        directory_path = f'donnees/{entite}'
        file_path = os.path.join(directory_path, fileName)

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
            
    except Exception as e:
        print(f"Erreur lors de la lecture: {str(e)}")
        return None

# Configuration des années et modèle de ligne
annees = [2021, 2022, 2023, 2024, 2025, 2026]
COLONNES_PAR_LIGNE = 13  # 12 mois + réalisé

def dataListGen():
    """Génère une nouvelle structure de données vide"""
    return [
        [None for _ in range(COLONNES_PAR_LIGNE)]  # Nouvelle liste pour chaque ligne
        for _ in range(288)  # 288 lignes
    ]
