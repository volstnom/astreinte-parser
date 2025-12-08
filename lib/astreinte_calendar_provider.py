from datetime import datetime, date, timedelta
from typing import Dict, Iterable, List
from lib.configuration import Configuration
import ics
from lib.astreinte_parser import AstreintePlanningParser
from baseclass.planning_parser import *
from baseclass.calendar_provider import *


class AtreinteCalendarProvider(CalendarProvider):
    """
    Subclass of CalendarProvider with astreints-specific entry points
    Manages multiple event calendars and provides functionality to send invites and save them to files
    """
    def __init__(self, email_organizer: str) -> None:
        super().__init__()
        self.email_organizer = email_organizer

    def add_event(self, week_number: int, astreintes: List[AstreinteInfo], parser: AstreintePlanningParser, cancel: bool = False, info_sup: Optional[List[str]] = None) -> None:
        user = parser.get_name_by_mail(self.email_organizer)
        listPack = parser.get_pack_user_week(user, week_number) # contient les packs expert regroupés par pack par user pour la semaine
        # astreintes contient les autres astreintes du meme user/semaine mais également les packs expert à l'unité par client
        # la notification mail sépare les packs expert des asteintes N1/N2

        # Cas aucune astreinte ni pack expert
        if not astreintes and listPack is None or not listPack:
            astreintes.append(AstreinteInfo(company="", level="Plus d'astreinte pour cette semaine", binome="", comment="", week_number=week_number))

        year = Configuration().YEAR
        first = astreintes[0]
        content  = f"<h3>Astreintes Semaine {week_number}:</h3>"
        content += "<ul>"
        for astreinte in astreintes:
            # bypass les astreintes de type pack expert
            if astreinte.level == 'Auto' or astreinte.level == 'Info':
                continue
            content += "<li>"
            # Format the level and binome level
            currentLevel, binomeLevel = self.format_level_name(astreinte.level)
            content += f"{currentLevel} : {astreinte.company} "
            # info binome si présent
            binome = astreinte.binome
            if binome != '':
                content += f"({binomeLevel}:{binome})"
            horaire = parser.get_horaires_astreinte(astreinte.company)
            if horaire != '':
                content += f" - {horaire}"
            #prime = parser.get_prime_astreinte(astreinte.company, astreinte.level)
            #if prime != 0:
                #content += f" ({prime} EUR)"
            
            commentaire = astreinte.comment
            if commentaire and commentaire != '':
                content += f"<BR> <i> Exceptions : {commentaire}</i> </BR>"
            content += "</li>"
        content += "</ul>"

        # ajout du pack expert dans le mail
        if listPack is not None and listPack:
            content += "<ul>"
            for pack in listPack:
                content += "<li>"
                content += f"{pack.name}: "
                for client in pack.clients:
                    content += f"{client}; "
                content += "</li>"
            content += "</ul>"

        if info_sup is not None and info_sup:
            content += f"<h4 style=\"font-style:italic\">Note de mise à jour :</h4>"
            content += "<ul>"
            for info in info_sup:
                content += f"<li>{info}</li>"
            content += "</ul>"

        CalendarProvider.add_event(self, 
                                   email_organizer=self.email_organizer, 
                                   start_date=first.get_start_date(year), 
                                   end_date=first.get_end_date(year), 
                                   title=f"{'[ANNULATION] ' if cancel else ''}Astreintes {year} - S{week_number}",
                                   content=content,
                                   uid=f"ASTREINT{year}{week_number}",
                                   cancellation=cancel)

    def _get_email_provider_credentials(self) -> Tuple[str]:
        return Configuration().PROVIDER_EMAIL, Configuration().PROVIDER_APP_PWD

    def send_email_constraint_ko(self, week_number: int, inconsistencies: List[str], dry_run: int = False):
        title = f"Astreintes {Configuration().YEAR} S{week_number} - Incohérence"
        content = f"<h3>Contraintes non respectées S{week_number}</h3>"
        content += "<ul>"
        for item in inconsistencies:
            content += f"<li>{item}</li>"
        content += "</ul>"

        self.send_simple_email(self.email_organizer, title, content, dry_run)

    
    def format_level_name(self, level_N1: str) -> tuple[str, str]:
        if level_N1.find('N1') != -1:
            current_level = 'N1'
            binomeLevel = 'N2'
        else:
            if level_N1.find('N2') != -1:
                current_level = 'N2'
                binomeLevel = 'N1'
            else:
                if level_N1.find('Info') != -1:
                    current_level = 'Pack Info'
                    binomeLevel = ''
                else:
                    if level_N1.find('Auto') != -1:
                        current_level = 'Pack Auto'
                        binomeLevel = ''
                    else:
                        current_level = level_N1 # exception pour message sur annulation complete d'une semaine
                        binomeLevel = ''
        return current_level, binomeLevel
