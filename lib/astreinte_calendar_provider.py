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
        if not astreintes:
            return

        year = Configuration().YEAR
        first = astreintes[0]
        content  = f"<h3>Astreintes Semaine {week_number}:</h3>"
        content += "<ul>"
        for astreinte in astreintes:
            content += "<li>"
            content += f"{astreinte.company} : {astreinte.level}"
            prime = parser.get_prime_astreinte(astreinte.company, astreinte.level)
            if prime != 0:
                content += f" ({prime} EUR)"
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

