import tkinter as tk
import subprocess
import os
from pathlib import Path
import sys
from baseclass.environnement import *

if getattr(sys, 'frozen', False):
    # Exécution dans l'exécutable PyInstaller
    dossier_root = Path(sys._MEIPASS).resolve()
else:
    # Exécution normale (non packagée)
    dossier_root = Path(__file__).resolve()

print('dossier_root: ' + dossier_root.name)
print(f"conteneur_path: {conteneur_path()}")
print(f"execution_path: {execution_path()}")

def lancementExcelSemaine():
    numeroSemaine = entree.get()
    #commandeScript = "lib/astreinte_par_semaine.py "
    pathScript = os.path.dirname(os.path.abspath(__file__))
    commandeScript = Path(pathScript) / "lib" / "astreinte_par_semaine.py "
    os.environ["ROOT_PATH"] = os.path.dirname(dossier_root) + "/"
    subprocess.run(["python",commandeScript, numeroSemaine])
    
def majDonneesAstreinte():
    print("appel du script parser")
    pathScript = os.path.dirname(os.path.abspath(__file__))
    commandeScript = Path(pathScript) / "astreinte_parser.py "
    subprocess.run(["python",commandeScript],env=os.environ.copy())

def RAZDonneesAstreinte():
    print("appel du script parser avec --clear-all")
    pathScript = os.path.dirname(os.path.abspath(__file__))
    commandeScript = Path(pathScript) / "astreinte_parser.py "
    subprocess.run(["python",commandeScript,"--clear-all"],env=os.environ.copy())

def RegenereDonneesAstreinte():
    print("appel du script parser avec --force")
    pathScript = os.path.dirname(os.path.abspath(__file__))
    commandeScript = Path(pathScript) / "astreinte_parser.py "
    subprocess.run(["python",commandeScript,"--force"],env=os.environ.copy())

#design de la fenêtre
#Titre
window = tk.Tk()
window.title("Gestion des astreintes")
window.geometry("500x150")

frame_libelle = tk.Frame(window, width=400, height=55)
frame_libelle.pack(side="left")



# Generation  excel semaine
texte1 = tk.Label(frame_libelle, text="Numéro de semaine:", anchor="w", width=25,  fg="black", font=("Arial", 10))
texte1.grid(row=0,column=0)

entree = tk.Entry(frame_libelle, width=10,  font=("Arial", 10))
entree.grid(row=0,column=1)

texte2 = tk.Label(frame_libelle, text="Gestion des données d'astreinte", anchor="w", width=25,  fg="black", font=("Arial", 10))
texte2.grid(row=1,column=0, pady=30)

frame_bouton = tk.Frame(window, width=400, height=55)
frame_bouton.pack(side="left")

bouton = tk.Button(frame_bouton, text="Generation excel semaine",
                width=30,
                height=1,
                bg="blue",
                fg="white",
                command=lancementExcelSemaine)
bouton.pack(side="top")



# Update BDD


bouton = tk.Button(frame_bouton, text="Mise à jour des données d'astreinte",
                width=30,
                height=1,
                bg="blue",
                fg="white",
                command=majDonneesAstreinte)
bouton.pack(side="top")

bouton = tk.Button(frame_bouton, text="Regénération des données d'astreinte",
                width=30,
                height=1,
                bg="blue",
                fg="white",
                command=RegenereDonneesAstreinte)
bouton.pack(side="top")



bouton = tk.Button(frame_bouton, text="RAZ des données d'astreinte",
                width=30,
                height=1,
                bg="blue",
                fg="white",
                command=RAZDonneesAstreinte)
bouton.pack(side="top")

#frame = tk.Frame(window, width=400, height=25)
#frame.pack()



window.mainloop()
