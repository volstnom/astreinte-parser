from typing import Dict, List
import yaml
from threading import Lock


class AstreinteConstraint:
    def __init__(self, src: Dict) -> None:
        self.company: str = src["company"]
        self.max: int = src["max"]

    def __str__(self) -> str:
        return f"{{company={self.company}, max={self.max}}}"

class Configuration:
    _instance = None
    _lock = Lock()  # Pour la gestion des accès concurrentiels

    def __new__(cls, config_path: str = None):
        """
        Crée une seule instance de la classe, même si appelée plusieurs fois.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double vérification pour le thread-safety
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize(config_path)
        return cls._instance

    def _initialize(self, config_path: str):
        """
        Initialise la configuration à partir du fichier YAML.
        """
        if not hasattr(self, "_initialized"):  # Empêche la réinitialisation multiple
            if config_path is None:
                raise ValueError("Le chemin du fichier de configuration doit être fourni à la première instance.")
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            
            self.PATH_PLANNING_XLS = config['path_planning_xls']
            self.YEAR = config['year']
            self.PROVIDER_EMAIL = config['provider']['email']
            self.PROVIDER_APP_PWD = config['provider']['app_password']
            self._attendees = config['attendees']

            if len(self._attendees) == 0:
                raise Exception("Information utilisateur manquante")
            else:
                for attendee in self._attendees:
                    if not "email" in attendee.keys():
                        raise Exception("Clé manquante attendees : \"email\"")
                    if not "trigram" in attendee.keys():
                        raise Exception("Clé manquante attendees : \"trigram\"")

            self._attendee_index = -1
            self._initialized = True

    def next_attendee(self) -> str:
        nb = len(self._attendees)
        if self._attendee_index + 1 >= nb:
            self._attendee_index = 0
        else:
            self._attendee_index += 1

        return self.attendee_trigram

    @property
    def attendee_email(self) -> str:
        return self._attendees[self._attendee_index]["email"]

    @property
    def attendee_trigram(self) -> str:
        return self._attendees[self._attendee_index]["trigram"]

    @property
    def attendee_constraints(self) -> List[AstreinteConstraint]:
        constraints = self._attendees[self._attendee_index]["constraints"] if "constraints" in self._attendees[self._attendee_index] else []
        return [AstreinteConstraint(cst) for cst in constraints if "company" in cst and "max" in cst]


