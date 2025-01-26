from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from email import encoders
import smtplib
from typing import Dict, Iterable, List, Optional, Tuple
import ics
import uuid


class _SingleEventCalendar:
    """
    (internal) Represents a single event calendar with functionality to create, manage, and send calendar invitations.

    Attributes:
        email_organizer (str): The email address of the event organizer.
        attendees (List[str]): A list of email addresses of attendees.
        calendar (ics.Calendar): The iCalendar object containing the event.
    """

    CSS = """<style>
        /* CSS Proposé */
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f9f9f9;
            color: #333;
        }

        h3 {
            color: #0078d4;
            font-size: 1.5em;
            margin-bottom: 10px;
            border-bottom: 2px solid #0078d4;
            padding-bottom: 5px;
        }

        ul {
            list-style-type: none;
            padding: 0;
        }

        ul li {
            background: #eaf6ff;
            margin: 5px 0;
            padding: 10px;
            border-left: 5px solid #0078d4;
            border-radius: 4px;
            transition: background 0.3s;
        }

        ul li:hover {
            background: #d6ebff;
        }

        h4 {
            font-style: italic;
            font-size: 1.2em;
            color: #555;
            margin-top: 20px;
        }

        h4 + ul li {
            background: #f0f0f0;
            border-left-color: #aaa;
            font-size: 0.9em;
        }
    </style>
    """

    def __init__(self, email_organizer: str, attendees: List[str], cancel: bool = False) -> None:
        """
        Initializes a new instance of _SingleEventCalendar.

        Args:
            email_organizer (str): The email address of the event organizer.
            attendees (List[str]): A list of email addresses of attendees.
        """
        self.email_organizer: str = email_organizer
        self.attendees: List[str] = attendees

        self.calendar: ics.Calendar = ics.Calendar()
        self.calendar.scale = "GREGORIAN"
        self.calendar.method = "CANCEL" if cancel else "REQUEST"
        self.__raw_text = ""
        self.__changed = False

    @property
    def raw_text_lines(self) -> List[str]:
        """
        Returns the serialized calendar text as a list of lines, ensuring proper ordering.

        Returns:
            List[str]: The serialized calendar text.
        """
        if self.__changed:
            self.__raw_text = self.__fix_str_order(self.calendar.serialize_iter())
            self.__changed = False
        return self.__raw_text

    def __fix_str_order(self, values: Iterable[str]) -> List[str]:
        """
        Ensures that the 'METHOD' field appears in the correct order in the calendar serialization.

        Args:
            values (Iterable[str]): The serialized calendar values.

        Returns:
            List[str]: The reordered calendar values.
        """
        index_method = next((index for index in range(0, len(values) - 1) if "METHOD:" in values[index]), -1)
        if index_method != -1:
            instruction = values[index_method]
            values.pop(index_method)
            values.insert(4, instruction)

        return values

    def add_event(self, start_date: datetime, end_date: datetime, title: str, content: str = "", uid: Optional[str] = None) -> None:
        """
        Adds a new event to the calendar. Only one event is allowed.

        Args:
            start_date (datetime): The start date and time of the event.
            end_date (datetime): The end date and time of the event.
            title (str): The title of the event.
            content (str, optional): The event description. Defaults to "".
            uid (Optional[str], optional): A unique identifier for the event. Defaults to None.

        Raises:
            Exception: If an event already exists in the calendar.
        """
        if len(self.calendar.events) > 0:
            raise Exception("Only one event allowed")

        if uid is None:
            uid = uuid.uuid4()

        new_event = ics.Event()
        new_event.transparent = True
        new_event.begin = start_date.isoformat()
        new_event.end = end_date.isoformat()
        new_event.name = title
        new_event.uid = uid
        new_event.location = "Virtual"
        new_event.description = content
        new_event.status = "CONFIRMED"

        for attendee in self.attendees:
            att = ics.Attendee(
                email=attendee,
                cutype="INDIVIDUAL",
                role="REQ-PARTICIPANT",
                partstat="ACCEPTED",
                common_name=attendee
            )
            new_event.add_attendee(att)

        new_event.organizer = ics.Organizer(self.email_organizer, self.email_organizer)

        self.calendar.events.add(new_event)
        self.__changed = True

    def send_calendar_invites(self, emailing_provider_email: str, emailing_provider_password: str, email_subject: Optional[str] = None, email_body: Optional[str] = None, dry_run: bool = False) -> None:
        """
        Sends calendar invites via email to all attendees.

        Args:
            emailing_provider_email (str): The email address of the provider used to send emails.
            emailing_provider_password (str): The password for the provider email account.
            email_subject (Optional[str], optional): The subject of the email. Defaults to current event name.
            email_body (Optional[str], optional): The body of the email. Defaults to current event description.
            dry_run (bool): Enable dry-run mode
        """
        if len(self.calendar.events) == 0:
            return

        first = next(iter(self.calendar.events))

        if email_subject is None:
            email_subject = first.name

        if email_body is None:
            email_body = first.description

        attendees = self.attendees
        fro = f"Moi <{self.email_organizer}>"

        eml_body = self.CSS + email_body
        msg = MIMEMultipart('mixed')
        msg['Reply-To'] = fro
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = email_subject
        msg['From'] = fro
        msg['To'] = ",".join(attendees)

        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)

        ical_full = "".join(self.raw_text_lines)
        part_email = MIMEText(eml_body, "html")
        part_cal = MIMEText(ical_full, f'calendar;method={self.calendar.method}')
        msgAlternative.attach(part_email)
        msgAlternative.attach(part_cal)

        if dry_run:
            print(f"{email_subject} -> {email_body}")
        else:
            mailServer = smtplib.SMTP('smtp.gmail.com', 587)
            mailServer.ehlo()
            mailServer.starttls()
            mailServer.ehlo()
            mailServer.login(emailing_provider_email, emailing_provider_password)
            mailServer.sendmail(fro, attendees, msg.as_string())
            mailServer.close()

    def save(self) -> None:
        """
        Saves the calendar to a local .ics file.
        """
        with open('astreintes.ics', 'w') as my_file:
            my_file.writelines(self.raw_text_lines)


class CalendarProvider:
    """
    Manages multiple event calendars and provides functionality to send invites and save them to files.
    It is advised to create a subclass of CalendarProvider to perform custom operations
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of CalendarProvider.
        """
        self.__schedules: List[_SingleEventCalendar] = []

    def add_event(self, email_organizer: str, start_date: datetime, end_date: datetime, title: str, content: str = "", attendees: Optional[List[str]] = None, uid: Optional[str] = None, cancellation: bool = False) -> None:
        """
        Adds a new event to the provider's list of schedules.

        Args:
            email_organizer (str): The email address of the event organizer.
            start_date (datetime): The start date and time of the event.
            end_date (datetime): The end date and time of the event.
            title (str): The title of the event.
            content (str, optional): The event description. Defaults to "".
            attendees (Optional[List[str]], optional): A list of attendees. Defaults to email_organizer value.
            uid (Optional[str], optional): A unique identifier for the event. Defaults to autogenerated Guid.
        """
        if attendees is None:
            attendees = [email_organizer]

        schedule = _SingleEventCalendar(email_organizer, attendees, cancel=cancellation)
        schedule.add_event(start_date, end_date, title, content, uid)
        self.__schedules.append(schedule)

    def send_invites(self, dry_run: bool = False) -> None:
        """
        Sends calendar invites for all schedules.

        Args:
            dry_run (bool): Enable dry-run mode
        """
        for schedule in self.__schedules:
            usr, pwd = self._get_email_provider_credentials()
            schedule.send_calendar_invites(usr, pwd, dry_run=dry_run)

    def send_simple_email(self, email_organizer: str, title: str, content: str, dry_run: bool = False) -> None:
        """
        Sends simple email
        """
        email_subject = title
        email_body = content

        attendees = [email_organizer]
        fro = f"astreinte-automation <{self.email_organizer}>"

        eml_body = email_body
        msg = MIMEMultipart('mixed')
        msg['Reply-To'] = fro
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = email_subject
        msg['From'] = fro
        msg['To'] = ",".join(attendees)

        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)

        part_email = MIMEText(eml_body, "html")
        msgAlternative.attach(part_email)

        if dry_run:
            print(f"{email_subject} -> {email_body}")
        else:
            usr, pwd = self._get_email_provider_credentials()
            mailServer = smtplib.SMTP('smtp.gmail.com', 587)
            mailServer.ehlo()
            mailServer.starttls()
            mailServer.ehlo()
            mailServer.login(usr, pwd)
            mailServer.sendmail(fro, attendees, msg.as_string())
            mailServer.close()

    def _get_email_provider_credentials(self) -> Tuple[str, str]:
        """
        Retrieves email provider credentials. Should be overridden by subclasses.

        Returns:
            Tuple[str, str]: The email address and password.
        """
        return "", ""

    def save_file(self, filename: str) -> None:
        """
        Saves all events from schedules into a single .ics file.

        Args:
            filename (str): The name of the file to save.
        """
        calendar = ics.Calendar()
        for schedule in self.__schedules:
            if schedule.calendar.events:
                calendar.events.add(schedule.calendar.events[0])

        with open(filename, 'w') as my_file:
            my_file.writelines(calendar.serialize_iter())
