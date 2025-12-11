from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

class EmployeInfo:
    """
    Classe modèle qui contient les donnes d'un utilisateur/employé d'une astreinte
    """
    def __init__(self, name: str, notif_mail: int, email: str) -> None:
        self.name: str = name
        self.notif_mail: int = notif_mail
        self.email: str = email  # Adresse e-mail de l'employé, peut être None si non spécifiée


class PrimeAstreinte:
    """
    Classe modèle qui synthétise les primes et horaires pour une astreinte
    """
    def __init__(self, company: str, prime_n1: int, prime_n2: int, horaires: str, packAuto: str, packInfo: str) -> None:
        self.company: str = company
        self.prime_n1: int = prime_n1
        self.prime_n2: int = prime_n2
        self.horaires: str = horaires  # Horaires de l'astreinte, formaté en chaîne de caractères
        self.packAuto: str = packAuto  # Nom du pack autom
        self.packInfo: str = packInfo  # Nom du pack info
       

class AstreinteInfo:
    """
    Classe modèle qui synthétise les informations d'une astreinte (niveau, société, N° de semaine)
    """
    N1 = "N1"
    N2 = "N2"
    ExpertAuto = "Auto"
    ExportInfo = "Info"

    def __init__(self, company: str, level: str, binome: str, comment: str = None, week_number: int = None) -> None:
        self.company: str = company
        self.level: str = level
        self.binome: str = binome  # Binôme associé à l'astreinte
        self.week_number: int = week_number
        self.comment: str = comment  # Commentaire associé à l'astreinte

    def __str__(self) -> str:
        return f"Astreinte{{S{self.week_number}: {self.company}->{self.level} (avec {self.binome}) / {self.comment}}}"

    def get_start_date(self, year: int) -> datetime:
        """
        Returns :
            datetime : La date de début de l'astreinte : Vendredi d'avant à 17h
        """
        return datetime.strptime(f"{year}-W{self.week_number-1:02d}-1", "%Y-W%W-%w") - timedelta(days=3) + timedelta(hours=17)

    def get_end_date(self, year: int) -> datetime:
        """
        Returns :
            datetime : La date de fin de l'astreinte : Vendredi suivant à 17h
        """
        return datetime.strptime(f"{year}-W{self.week_number-1:02d}-5", "%Y-W%W-%w") + timedelta(hours=17)

class PackExpert:
    """
    Classe qui contient les données d'une astreinte de type Pack pour un utilisateur et une semaine
    """
    def __init__(self, name: str, comment: str = "") -> None:
        self.name: str = name
        self.clients: List[str] = []
        self.comment: str = comment  # Commentaire associé au pack astreinte
        #self.N1: List[str] = []
        #self.N2: List[str] = []
        
 

class PlanningParser:
    """
    Classe de base à surcharger pour récupérer les données du planning d'astreintes.

    Cette classe fournit une structure pour stocker et traiter les données relatives aux astreintes,
    telles que les primes et les affectations hebdomadaires. La méthode principale parse_planning doit être 
    surchargée dans une classe dérivée pour implémenter la logique spécifique de parsing.
    
    Attributs :
        primes_astreinte (Dict[str, PrimeAstreinte]) : Un dictionnaire associant chaque entreprise à ses primes d'astreinte.
        affectation_astreintes (Dict[str, Dict[int, List[AstreinteInfo]]]) : Un dictionnaire structuré par trigramme, 
            associant les semaines (int) aux listes d'informations sur les astreintes (AstreinteInfo).
    """

    def __init__(self) -> None:
        """
        Initialise une nouvelle instance de la classe AstreintePlanningParser.

        Attributs initialisés :
            __parsed (bool) : Indique si le planning a été parsé (faux par défaut).
            primes_astreinte (Dict[str, PrimeAstreinte]) : Dictionnaire vide des primes par entreprise.
            affectation_astreintes (Dict[str, Dict[int, List[AstreinteInfo]]]) : 
                Dictionnaire vide des affectations d'astreintes par trigramme.
        """
        self.__parsed = False
        self.primes_astreinte: Dict[str, PrimeAstreinte] = dict()
        self.affectation_astreintes: Dict[str, Dict[int, List[AstreinteInfo]]] = dict()
        self.employes: Dict[str, EmployeInfo] = dict()  # Dictionnaire pour stocker les employés (trigramme -> nom, notification mail) 

    def parse_planning(self) -> None:
        """
        Méthode à surcharger pour lire le contenu du planning.

        Cette méthode doit être implémentée dans une classe dérivée pour extraire les données d'un planning
        et remplir les attributs `primes_astreinte` et `affectation_astreintes`. 
        Une fois le parsing terminé, la variable interne `__parsed` est mise à `True`.
        """
        self.__parsed = True

    def get_astreintes(self, trigramme: str) -> Dict[int, List[AstreinteInfo]]:
        """
        Récupère les données d'astreintes pour une personne donnée selon son trigramme.

        Args :
            trigramme (str) : Le trigramme de la personne concernée.

        Returns :
            Dict[int, List[AstreinteInfo]] : 
                Un dictionnaire où chaque clé est un numéro de semaine (int),
                et chaque valeur est une liste d'informations d'astreinte (AstreinteInfo) pour cette semaine.

        Raises :
            Exception : Si la méthode `parse_planning` n'a pas encore été appelée.

        Note :
            Si le trigramme n'existe pas dans les données, un dictionnaire vide est retourné.
        """
        if not self.__parsed:
            raise Exception("Le planning n'a pas été parsé.")

        if trigramme in self.affectation_astreintes.keys():
            return self.affectation_astreintes[trigramme]
        else:
            return {}
        
    def get_astreintes_week(self, trigramme: str, week_number: int) -> List[AstreinteInfo]:
        """
        Récupère les données d'astreintes pour une personne donnée selon son trigramme.

        Args :
            trigramme (str) : Le trigramme de la personne concernée.

        Returns :
            Dict[int, List[AstreinteInfo]] : 
                Un dictionnaire où chaque clé est un numéro de semaine (int),
                et chaque valeur est une liste d'informations d'astreinte (AstreinteInfo) pour cette semaine.

        Raises :
            Exception : Si la méthode `parse_planning` n'a pas encore été appelée.

        Note :
            Si le trigramme n'existe pas dans les données, un dictionnaire vide est retourné.
        """
        if not self.__parsed:
            raise Exception("Le planning n'a pas été parsé.")

        if trigramme in self.affectation_astreintes.keys():
            return self.affectation_astreintes[trigramme][week_number] if week_number in self.affectation_astreintes[trigramme] else []
        else:
            return {}

    def get_prime_astreinte(self, company: str, level: str) -> int:
        """
        Récupère le montant de la prime d'astreinte pour une entreprise et un niveau donnés.

        Args :
            company (str) : Le nom de l'entreprise concernée.
            level (str) : Le niveau d'astreinte (`N1` ou `N2`).

        Returns :
            int : Le montant de la prime d'astreinte en euros.

        Raises :
            Exception : Si la méthode `parse_planning` n'a pas encore été appelée.

        Note :
            Si l'entreprise n'existe pas dans les données ou si le niveau est invalide,
            un montant de 0 est retourné.
        """
        if not self.__parsed:
            raise Exception("Le planning n'a pas été parsé.")

        montant: int = 0
        if company in self.primes_astreinte.keys():
            if level == AstreinteInfo.N1:
                montant = self.primes_astreinte[company].prime_n1
            elif level == AstreinteInfo.N2:
                montant = self.primes_astreinte[company].prime_n2
        return montant
    
    def get_pack_astreinte(self, company: str, level: str) -> int:
        """
        Récupère le nom du pack expert pour une entreprise et un niveau (info ou autom) donnés.

        Args :
            company (str) : Le nom de l'entreprise concernée.
            level (str) : Le niveau d'astreinte (`N1` ou `N2`).

        Returns :
            int : Le montant de la prime d'astreinte en euros.

        Raises :
            Exception : Si la méthode `parse_planning` n'a pas encore été appelée.

        Note :
            Si l'entreprise n'existe pas dans les données ou si le niveau est invalide,
            un montant de 0 est retourné.
        """
        if not self.__parsed:
            raise Exception("Le planning n'a pas été parsé.")

        nomPack: str = ''
        if company in self.primes_astreinte.keys():
            if level == AstreinteInfo.ExpertAuto:
                nomPack = self.primes_astreinte[company].packAuto
            elif level == AstreinteInfo.ExportInfo:
                nomPack = self.primes_astreinte[company].packInfo
        return nomPack
    
    def get_horaires_astreinte(self, company: str) -> str:
        """
        Récupère le montant de la prime d'astreinte pour une entreprise et un niveau donnés.

        Args :
            company (str) : Le nom de l'entreprise concernée.
            

        Returns :
            str : Les horaires de l'astreinte.

        Raises :
            Exception : Si la méthode `parse_planning` n'a pas encore été appelée.

        Note :
            Si l'entreprise n'existe pas dans les données ou si le niveau est invalide,
            un horaire vide est retourné.
        """
        if not self.__parsed:
            raise Exception("Le planning n'a pas été parsé.")

        horaire: str = ''
        if company in self.primes_astreinte.keys():
            horaire = self.primes_astreinte[company].horaires
        return horaire
    
    def get_pack_user_week(self, trigramme: str, week_number: int) -> List[PackExpert]:
        """
        Récupère les données dun pack expert pour une personne donnée selon son trigramme.

        Args :
            trigramme (str) : Le trigramme de la personne concernée.

        Returns :
            Dict[int, List[AstreinteInfo]] : 
                Un dictionnaire où chaque clé est un numéro de semaine (int),
                et chaque valeur est une liste d'informations d'astreinte (AstreinteInfo) pour cette semaine.

        Raises :
            Exception : Si la méthode `parse_planning` n'a pas encore été appelée.

        Note :
            Si le trigramme n'existe pas dans les données, un dictionnaire vide est retourné.
        """
        if not self.__parsed:
            raise Exception("Le planning n'a pas été parsé.")

        if trigramme in self.affectation_astreintes.keys():
            if week_number in self.affectation_astreintes[trigramme]:
                # Construction du pack expert
                # listPack : List[PackExpert] = []
                listPack : Dict[str, PackExpert] = dict()
                # Regroupement de tous les clients, tous les N1 et tous les N2 par pack
                for astreinte in self.affectation_astreintes[trigramme][week_number]:
                    if astreinte.level == 'Info' or astreinte.level == 'Auto':
                        nomPack = self.get_pack_astreinte(astreinte.company, astreinte.level)
                        # Ajout du pack à la liste si pas encore présent
                        if nomPack in listPack.keys():
                            pack = listPack[nomPack]                    
                        else:
                            pack = PackExpert(nomPack)
                            listPack[nomPack] = pack
                        # Ajout des autres éléments à ce pack: client et commentaire (uniquement si variante)
                        if astreinte.company not in pack.clients:
                            pack.clients.append(astreinte.company)  
                        if astreinte.comment != pack.comment:
                            pack.comment += f"{astreinte.comment}/"  
                return [listPack[name] for name in sorted(listPack)]
            else:
                return {}
        else:
            return {}

    def get_name_by_mail(self, email: str) -> str:
        if not self.__parsed:
            raise Exception("Le planning n'a pas été parsé.")    

        key = next((k for k, v in self.employes.items() if v.email == email), None)
        return key
