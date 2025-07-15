import sqlite3
import pandas as pd
import argparse
import os
from pathlib import Path

def main():
    
    # Configuration de argparse pour gérer les arguments de ligne de commande
    parser = argparse.ArgumentParser(description='Exécuter une requête SQL sur une base de données SQLite.')
    parser.add_argument('week_number', type=int, help='Le numéro de la semaine à rechercher')

    # Analyse des arguments
    args = parser.parse_args()
    genereSemaineExcel(args.week_number)

def genereSemaineExcel(numeroSemaine):
    # Fonction pour générer le fichier Excel des astreintes par semaine
    

    # Détermination du path dossier_racine pour les fichiers résultats
    pathExecution = os.environ.get("ROOT_PATH")
    if not pathExecution:
        # lancement du script tout seul => resultats en local
        dossier_racine = os.path.dirname(os.path.abspath(__file__))
    else:
        # le script parent est soit un autre script, soit un executable dans environnement package
        print(os.path.dirname(pathExecution))
        dossier_racine = pathExecution
    print(os.path.dirname(dossier_racine))
    # Connexion à la base de données SQLite
    # La BDD se trouve toujours dans le repertoire data au meme niveau que le repertoire lib dabs le quel se trouve ce script (astreinte_par_semaine.py)
    pathBase = os.path.dirname(os.path.abspath(__file__)) + "/../data/database.db"
    conn = sqlite3.connect(pathBase)

    # Définir le paramètre
    #week_number_param = 18

    # Exécution de la requête SQL avec un paramètre
    query = """
    select 
            A1.week_number AS Semaine,
            A1.company As Client,
            MAX(
        CASE
            WHEN level = 'N1' THEN Utilisateurs.nom 
            ELSE '?'
        END)
            AS N1,
        MAX(
            CASE
            WHEN level = 'N2' THEN Utilisateurs.nom 
            ELSE '?'
        END) 
        AS N2,
        MAX(
        CASE
            WHEN level = 'E_N1' THEN Utilisateurs.nom 
            ELSE NULL
        END)
            AS 'Exception N1',
        MAX(
            CASE
            WHEN level = 'E_N2' THEN Utilisateurs.nom 
            ELSE NULL
        END) 
        AS 'Exception N2'
    FROM Astreinte A1
    LEFT JOIN Utilisateurs ON A1.trigram = Utilisateurs.trigram
    WHERE A1.week_number = :week_number
    GROUP BY A1.week_number,        A1.company;
    """
    df = pd.read_sql_query(query, conn, params={"week_number": numeroSemaine})

    # Affichage des résultats
    #print(df)


    #dossier_sortie = os.path.dirname(os.path.abspath(__file__)) + "\AstreintesParSemaine"
    dossier_sortie = Path(dossier_racine) / "AstreintesParSemaine"
    Path(dossier_sortie).mkdir(parents=True, exist_ok=True)

    print(f"Les résultats seront enregistrés dans le dossier : {dossier_sortie}")
    # Formattage des variables
    #numeroSemaine = args.week_number
    libelleSemaine = f"S{numeroSemaine} Astreinte"
    nomFichierExcel = Path(dossier_sortie) / f"{libelleSemaine}.xlsx"

    # Exportation des résultats vers un fichier Excel
    df.to_excel(nomFichierExcel, sheet_name=libelleSemaine ,index=False)

    # Fermeture de la connexion
    conn.close()


if __name__ == "__main__":
    main()