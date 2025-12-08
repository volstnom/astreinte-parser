import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from pathlib import Path
import sys
from baseclass.environnement import *
import astreinte_parser
import lib.astreinte_par_semaine


print('programme lancé:' + sys.argv[0])
print('fichier source associé: ' + __file__)

if getattr(sys, 'frozen', False):
    # Exécution dans l'exécutable PyInstaller
    dossier_root = Path(sys._MEIPASS).resolve()
else:
    # Exécution normale (non packagée)
    dossier_root = Path(__file__).resolve()

print('dossier_root: ' + dossier_root.name)
print(f"conteneur_path: {conteneur_path()}")
print(f"execution_path: {execution_path()}")
print('sys.executable: ' + sys.executable)

def lancementExcelSemaine():
    print("appel du script astreinte_par_semaine")
    numeroSemaine = entree.get()
    #commandeScript = "lib/astreinte_par_semaine.py "
    pathScript = conteneur_path()
    #pathScript = os.path.dirname(os.path.abspath(__file__))
    commandeScript = Path(pathScript) / "lib" / "astreinte_par_semaine.py"
    commandeExe = Path(pathScript) / "astreinte_par_semaine.exe"
    os.environ["ROOT_PATH"] = os.path.dirname(dossier_root) + "/"
    subprocess.run([sys.executable,commandeScript, numeroSemaine])
    #subprocess.run([commandeExe, numeroSemaine])
    
def majDonneesAstreinte():
    print("appel du script parser")
    pathScript = conteneur_path()
    #pathScript = os.path.dirname(os.path.abspath(__file__))
    commandeScript = Path(pathScript) / "astreinte_parser.py"
    subprocess.run([sys.executable,commandeScript],env=os.environ.copy())

def RAZDonneesAstreinte():
    
    reponse = messagebox.askyesno("Confirmation", "Voulez-vous vraiment réinitialiser les données d'astreinte ?")
    if reponse:
        print("appel du script parser avec --clear-all")
        pathScript = conteneur_path()
        #pathScript = os.path.dirname(os.path.abspath(__file__))
        commandeScript = Path(pathScript) / "astreinte_parser.py"
        subprocess.run([sys.executable,commandeScript,"--clear-all"],env=os.environ.copy())

def majDonneesSansNotif():
    print("appel du script parser avec --ignore-notif")
    pathScript = conteneur_path()
    #pathScript = os.path.dirname(os.path.abspath(__file__))
    commandeScript = Path(pathScript) / "astreinte_parser.py"
    subprocess.run([sys.executable,commandeScript,"--ignore-notif"],env=os.environ.copy())

if __name__ == "__main__":
    
    if len(sys.argv) == 1:

        print("Lancement principal")

        #design de la fenêtre
        #Titre
        window = tk.Tk()
        window.title("Gestion des astreintes")
        window.geometry("500x150")

        frame_libelle = tk.Frame(window, width=400, height=55)
        frame_libelle.pack(side="left")

        texte0 = tk.Label(frame_libelle, text="Depuis Excel vers BDD:", anchor="w", width=25,  fg="black", font=("Arial", 10))
        texte0.grid(row=0,column=0)

        texte1 = tk.Label(frame_libelle, text="Depuis Excel vers BDD:", anchor="w", width=25,  fg="black", font=("Arial", 10))
        texte1.grid(row=1,column=0, pady=5)

        # Generation  excel semaine
        texte2 = tk.Label(frame_libelle, text="Numéro de semaine:", anchor="w", width=25,  fg="black", font=("Arial", 10))
        texte2.grid(row=2,column=0)

        texte3 = tk.Label(frame_libelle, text="Purge des données d'astreinte:", anchor="w", width=25,  fg="black", font=("Arial", 10))
        texte3.grid(row=3,column=0, pady=5)

        entree = tk.Entry(frame_libelle, width=10,  font=("Arial", 10))
        entree.grid(row=2,column=1)

        frame_bouton = tk.Frame(window, width=400, height=55)
        frame_bouton.pack(side="left")

        



        # Update BDD


        bouton = tk.Button(frame_bouton, text="Mise à jour AVEC notifications",
                        width=30,
                        height=1,
                        bg="blue",
                        fg="white",
                        command=majDonneesAstreinte)
        bouton.pack(side="top")

        bouton = tk.Button(frame_bouton, text="Mise à jour SANS notification",
                        width=30,
                        height=1,
                        bg="blue",
                        fg="white",
                        command=majDonneesSansNotif)
        bouton.pack(side="top")

        bouton = tk.Button(frame_bouton, text="Generation Excel semaine",
                        width=30,
                        height=1,
                        bg="blue",
                        fg="white",
                        command=lancementExcelSemaine)
        bouton.pack(side="top")

        bouton = tk.Button(frame_bouton, text="Reset BDD",
                        width=30,
                        height=1,
                        bg="blue",
                        fg="white",
                        command=RAZDonneesAstreinte)
        bouton.pack(side="top")

        #frame = tk.Frame(window, width=400, height=25)
        #frame.pack()



        window.mainloop()
    else:
        tacheA_Lancer = sys.argv[1]
        print("Lancement secondaire de " + tacheA_Lancer)
        # Lancement secondaire, on ne fait que lancer le script de génération des astreintes par semaine
        if Path(tacheA_Lancer).name == "astreinte_par_semaine.py":
            numeroSemaine = sys.argv[2]
            lib.astreinte_par_semaine.genereSemaineExcel(numeroSemaine)
        else:
            if Path(tacheA_Lancer).name == "astreinte_parser.py":
                if len(sys.argv) > 2:
                    if sys.argv[2] == "--clear-all":
                        astreinte_parser.traitementAstreinte(False, False, True)
                    elif sys.argv[2] == "--ignore-notif":
                        astreinte_parser.traitementAstreinte(False, False, False, True)
                else:
                    astreinte_parser.traitementAstreinte(False, False, False)
            else:
                print("Erreur: script inconnu:" + Path(tacheA_Lancer).name)