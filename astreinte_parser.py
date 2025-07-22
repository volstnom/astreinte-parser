from lib.configuration import Configuration
from lib.astreinte_parser import AstreintePlanningParser
from lib.astreinte_calendar_provider import AtreinteCalendarProvider
from lib.database import Database
from typing import Tuple
import argparse
import sys

print(sys.argv)
print(__file__)


def parse_arguments() -> Tuple[bool, bool, bool, bool]:
    # Créer un parseur pour les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Script de traitement du planning d'astreinte")

    # Ajouter l'argument --dry-run
    parser.add_argument(
        "--dry-run",
        action="store_true",  # Indique qu'il s'agit d'un booléen (présent = True, absent = False)
        help="Exécute le script en mode simulation sans appliquer les modifications"
    )

    # Ajouter l'argument --force
    parser.add_argument(
        "--force",
        action="store_true",  # Indique qu'il s'agit d'un booléen (présent = True, absent = False)
        help="Ignore les données stockées en base de donnée et génère la totalité des données"
    )

    # Ajouter l'argument --clear-all
    parser.add_argument(
        "--clear-all",
        action="store_true",  # Indique qu'il s'agit d'un booléen (présent = True, absent = False)
        help="Supprime toutes les invitations existantes et vide la base de données"
    )

    # Ajouter l'argument --ignore-notif
    parser.add_argument(
        "--ignore-notif",
        action="store_true",  # Indique qu'il s'agit d'un booléen (présent = True, absent = False)
        help="Met à jour la base sans envoyer de notifications par mail"
    )

    # Parser les arguments
    args = parser.parse_args()

    # Vérifier si --dry-run est activé
    if args.dry_run:
        print("Mode dry-run activé. Aucune modification ne sera appliquée.")
    else:
        print("Mode normal. Les modifications seront appliquées.")

    # Vérifier si --force est activé
    if args.force:
        print("Mode forcé activé. Les informations de la base de donnée seront ignorées.")

    # Vérifier si --clear-all est activé
    if args.clear_all:
        print("Mode CLEAR activé. Les invitations calendrier seront toutes annulées.")

    # Vérifier si --ignore-notif est activé
    if args.ignore_notif:
        print("Mode sans notification activé. Aucun email ne sera envoyé.")

    return args.dry_run, args.force, args.clear_all, args.ignore_notif
   
def traitementAstreinte(dry_run: bool, ignore_bdd: bool, clear_all: bool, ignore_notif: bool = False):
    # Initialisation configuration
    conf = Configuration("config.yaml")

    # Parsing du planning d'astreinte
    parser = AstreintePlanningParser()
    parser.parse_planning(ignore=clear_all)

    # Comparaison base de données
    database = Database()

    if ignore_bdd:
        diff = parser.affectation_astreintes
        print("Aucun traitement sans BDD.")
    else:
        diff = database.compare_with_database(parser.affectation_astreintes)

        #Mise a jour des utilisateurs
        if(not clear_all):
            database.update_all_utilisateurs(parser.employes)

        if(not ignore_notif):
            if diff.any():
                #processed_attendees = []
                #user = conf.next_attendee()
                utilisateurs = database.get_utilisateurs()
                for trigram in utilisateurs:
                    print(f"Utilisateur {trigram.trigram} trouvé dans la base de données.")
                    print(f"Nom : {trigram.nom}, Notification mail : {trigram.notification_mail}")
                    print(f"Adresse mail : {trigram.adresse_mail}")
                # Parcours des utilisateurs dans la base de données
                #while user not in processed_attendees:
                #    processed_attendees.append(user)
                    user = trigram.trigram
                    infoEmploye = database.get_notif_mail(user)
                    if infoEmploye is None:
                        print(f"Utilisateur {user} non trouvé dans la base de données.")
                        #user = conf.next_attendee()
                        continue
                    if(infoEmploye.notification_mail==1 and infoEmploye.adresse_mail != ''):
                        calendar = AtreinteCalendarProvider(infoEmploye.adresse_mail)

                        for week, astreintes in parser.get_astreintes(user).items():
                            # Contrôle des contraintes
                            #inconsistencies = parser.check_attendee_constraints(week)
                            #if inconsistencies:
                                # Envoyer un mail d'avertissement
                                #calendar.send_email_constraint_ko(week, inconsistencies, dry_run)

                            if diff.is_added(user, week) or diff.is_modified(user, week):
                                # Ajout ou modification, préparation des paramètres pour création de l'évènement calendrier
                                info_sup = ["Création initiale"]
                                if diff.is_modified(user, week):
                                    info_sup = ["Mise à jour / Avant ↓"]
                                    for astreinte in database.get_astreintes(user, week):
                                        info_sup.append(f"{astreinte.company} -> {astreinte.level}")
                                calendar.add_event(week, astreintes, parser, info_sup=info_sup)  

                        # Parcours des suppressions d'astreintes pour création d'un évènement d'annulation du créneau
                        if user in diff.deleted.keys():
                            for week, astreintes in diff.deleted[user].items():
                                if diff.is_deleted(user, week):
                                    calendar.add_event(week, astreintes, parser, cancel=True, info_sup=["Annulation"])  
                    
                        # Envoi de toutes les invitations
                        calendar.send_invites(dry_run)

                    # Préparation de l'utilisateur suivant
                    #user = conf.next_attendee()
            else:
                print("Aucun écart détecté.")
        else:
            print("Pas d'envoi de mails.")
        # Sauvegarde BDD
        database.update_all_data(parser.affectation_astreintes)
        database.close()
        print("Success!")
    


def main():
    # Analyse des arguments de la ligne de commande
    dry_run, ignore_bdd, clear_all, ignore_notif = parse_arguments()

    # Traitement des astreintes
    traitementAstreinte(dry_run, ignore_bdd, clear_all, ignore_notif)

if __name__ == "__main__":
    main()
 