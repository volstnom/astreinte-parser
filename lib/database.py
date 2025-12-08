from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, List
from baseclass.planning_parser import AstreinteInfo, EmployeInfo, PrimeAstreinte
from baseclass.environnement import *

Base = declarative_base()

class Clients(Base):
    __tablename__ = 'Clients'
    company = Column(String(100), primary_key=True, nullable=False)
    prime_N1 = Column(Integer, nullable=True)
    prime_N2 = Column(Integer, nullable=True)
    horaires = Column(String(255), nullable=True)
    packAuto = Column(String(255), nullable=True)  
    packInfo = Column(String(255), nullable=True)       

    __table_args__ = (
        UniqueConstraint('company', name='unique_client'),
    )

class Astreinte(Base):
    __tablename__ = 'Astreinte'
    id = Column(Integer, primary_key=True, autoincrement=True)
    trigram = Column(String(10), nullable=False)
    week_number = Column(Integer, nullable=False)
    company = Column(String(100), nullable=False)
    level = Column(String(10), nullable=False)
    binome = Column(String(100), nullable=True)
    commentaire = Column(String(255), nullable=True)    

    __table_args__ = (
        UniqueConstraint('trigram', 'week_number', 'company', 'level', name='unique_astreinte'),
    )

class Employe(Base):
    __tablename__ = 'Utilisateurs'
    trigram = Column(String(10), primary_key=True, nullable=False)
    nom = Column(String(100), nullable=False)
    notification_mail = Column(Integer, nullable=False)
    adresse_mail = Column(String(100), nullable=True)

    __table_args__ = (
        UniqueConstraint('trigram', 'nom', name='unique_utilisateur'),
    )

class ClientsComparisonResult:
    """
    Classe pour représenter les différences entre les clients en base et un dictionnaire donné.
    """
    def __init__(self, added=None, deleted=None, modified=None):
        self.added: Dict[str, PrimeAstreinte]  = added or {}  # Données dans le dictionnaire mais absentes en base
        self.deleted: Dict[str, PrimeAstreinte]  = deleted or {}  # Données en base mais absentes dans le dictionnaire
        self.modified: Dict[str, PrimeAstreinte]  = modified or {}  # Données présentes dans les deux mais avec des différences

    def any(self) -> bool:
        return bool(self.added) or bool(self.deleted) or bool(self.modified)

    def is_added(self, company: str) -> bool:
        return company in self.added.keys() 

    def is_deleted(self, company: str) -> bool:
        return company in self.deleted.keys()

    def is_modified(self, company: str) -> bool:
        return company in self.modified.keys()



class AstreinteComparisonResult:
    """
    Classe pour représenter les différences entre les données en base et un dictionnaire donné.
    """
    def __init__(self, added=None, deleted=None, modified=None):
        self.added: Dict[str, Dict[int, List[AstreinteInfo]]] = added or {}  # Données dans le dictionnaire mais absentes en base
        self.deleted: Dict[str, Dict[int, List[AstreinteInfo]]] = deleted or {}  # Données en base mais absentes dans le dictionnaire
        self.modified: Dict[str, Dict[int, List[AstreinteInfo]]] = modified or {}  # Données présentes dans les deux mais avec des différences

    def any(self) -> bool:
        return bool(self.added) or bool(self.deleted) or bool(self.modified)

    def is_added(self, user: str, week_number: int) -> bool:
        return user in self.added.keys() and week_number in self.added[user].keys()

    def is_deleted(self, user: str, week_number: int) -> bool:
        return user in self.deleted.keys() and week_number in self.deleted[user].keys()

    def is_modified(self, user: str, week_number: int) -> bool:
        return user in self.modified.keys() and week_number in self.modified[user].keys()


class Database:
    def __init__(self):
        """
        Initialise la connexion à la base de données et configure le moteur et la session.
        """
        db_url='sqlite:///' + str(conteneur_path()) + '\data\database.db'
        
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self._initialize_database()

    def _initialize_database(self):
        """
        Crée les tables si elles n'existent pas.
        """
        inspector = inspect(self.engine)
        if not inspector.has_table('Astreinte'):
            Base.metadata.create_all(self.engine)
        if not inspector.has_table('Utilisateurs'):
            Base.metadata.create_all(self.engine)
        if not inspector.has_table('Clients'):
            Base.metadata.create_all(self.engine)

    def get_utilisateurs(self, trigram=None) -> Employe:
        """
        Récupère les utlisateurs de la base de données. Si un trigram est spécifié, filtre par trigram.
        """
        with self.Session() as session:
            query = session.query(Employe)
            if trigram:
                query = query.filter_by(trigram=trigram)
            return query.all()
        
    def add_utilisateur(self, trigram, nom, notification_mail=1, adresse_mail=None):
        """
        Ajoute une nouvelle astreinte à la base de données.
        """
        with self.Session() as session:
            employe = Employe(trigram=trigram, nom=nom, notification_mail=notification_mail, adresse_mail=adresse_mail)
            session.add(employe)
            session.commit()

    def delete_all_utilisateurs(self):
        """
        Supprime tous les utilisateurs de la base de données.
        """
        with self.Session() as session:
            session.delete(Employe)
            session.commit()

    #def update_all_data(self, data: Dict[str, Dict[int, List[AstreinteInfo]]]) -> None:
    def update_all_utilisateurs(self, data: Dict[str, EmployeInfo]) -> None:
        with self.Session() as session:
            session.query(Employe).delete()
            for trigram, info_employe in data.items():
                employe = Employe(trigram=trigram, nom=info_employe.name, notification_mail=info_employe.notif_mail, adresse_mail=info_employe.email)
                session.add(employe)
            session.commit()

    def get_notif_mail(self, trigram) -> Employe:
        """
        Récupère les astreintes de la base de données. Si un trigram est spécifié, filtre par trigram.
        """
        with self.Session() as session:
            query = session.query(Employe)
            if trigram:
                query = query.filter_by(trigram=trigram)
            return query.one_or_none()

    def add_astreinte(self, trigram, week_number, company, level, binome, commentaire):
        """
        Ajoute une nouvelle astreinte à la base de données.
        """
        with self.Session() as session:
            astreinte = Astreinte(trigram=trigram, week_number=week_number, company=company, level=level, binome=binome, commentaire=commentaire)
            session.add(astreinte)
            session.commit()

    def get_astreintes(self, trigram=None, week=None) -> Astreinte:
        """
        Récupère les astreintes de la base de données. Si un trigram est spécifié, filtre par trigram.
        """
        with self.Session() as session:
            query = session.query(Astreinte)
            if trigram:
                query = query.filter_by(trigram=trigram, week_number=week)
            return query.all()

    def get_astreinte(self, trigram=None, week=None, company=None):
        """
        Récupère les astreintes de la base de données. Si un trigram est spécifié, filtre par trigram.
        """
        with self.Session() as session:
            query = session.query(Astreinte)
            if trigram:
                query = query.filter_by(trigram=trigram,
                            week_number=week,
                            company=company)
            return query.all()

    def update_astreinte(self, astreinte_id, **kwargs):
        """
        Met à jour une astreinte existante avec les champs spécifiés.
        """
        with self.Session() as session:
            astreinte = session.query(Astreinte).get(astreinte_id)
            if astreinte:
                for key, value in kwargs.items():
                    if hasattr(astreinte, key):
                        setattr(astreinte, key, value)
                session.commit()

    def delete_astreinte(self, astreinte_id):
        """
        Supprime une astreinte de la base de données par ID.
        """
        with self.Session() as session:
            astreinte = session.query(Astreinte).get(astreinte_id)
            if astreinte:
                session.delete(astreinte)
                session.commit()


    def update_clients(self, data: Dict[str, PrimeAstreinte]) -> None:
        """
        Met à jour les données des clients dans la base de données.
        """
        with self.Session() as session:
            session.query(Clients).delete()
            for company, prime in data.items():
                client = Clients(company=company, prime_N1=prime.prime_n1, prime_N2=prime.prime_n2, horaires=prime.horaires, packAuto=prime.packAuto, packInfo=prime.packInfo)
                session.add(client)
            session.commit()

    def update_all_data(self, data: Dict[str, Dict[int, List[AstreinteInfo]]]) -> None:
        with self.Session() as session:
            session.query(Astreinte).delete()
            for trigram, weeks in data.items():
                for week_number, astreintes in weeks.items():
                    for astreinte_info in astreintes:
                        astreinte = Astreinte(trigram=trigram, week_number=week_number, company=astreinte_info.company, level=astreinte_info.level, binome=astreinte_info.binome, commentaire=astreinte_info.comment)
                        session.add(astreinte)
            session.commit()

    def compare_with_database(self, data: Dict[str, Dict[int, List[AstreinteInfo]]]) -> AstreinteComparisonResult:
        """
        Compare les données du dictionnaire avec celles de la base de données et retourne les différences.

        :param data: Dictionnaire contenant les données à comparer.
        :return: Instance d'AstreinteComparisonResult contenant les différences.
        """
        added = {}
        deleted = {}
        modified = {}

        with self.Session() as session:
            # Vérifier les données dans le dictionnaire qui manquent en base
            for trigram, weeks in data.items():
                for week_number, astreintes in weeks.items():
                    for astreinte_info in astreintes:
                        existing = session.query(Astreinte).filter_by(
                            trigram=trigram,
                            week_number=week_number,
                            company=astreinte_info.company,
                            level=astreinte_info.level
                        ).first()
                        if not existing:
                            # Absent en base
                            added.setdefault(trigram, {}).setdefault(week_number, []).append(astreinte_info)
                        elif  existing.binome != astreinte_info.binome or existing.commentaire != astreinte_info.comment:
                            # Présent mais avec une différence
                            modified.setdefault(trigram, {}).setdefault(week_number, []).append(astreinte_info)

            # Vérifier les données en base qui manquent dans le dictionnaire
            all_astreintes = session.query(Astreinte).all()
            for astreinte in all_astreintes:
                trigram, week_number = astreinte.trigram, astreinte.week_number
                if (trigram not in data or
                        week_number not in data[trigram] or
                        not any(
                            astreinte.company == info.company
                            for info in data[trigram].get(week_number, [])
                        )):
                    deleted.setdefault(trigram, {}).setdefault(week_number, []).append(
                        AstreinteInfo(
                            company=astreinte.company,
                            level=astreinte.level,
                            week_number=astreinte.week_number,
                            binome=astreinte.binome,
                            comment=astreinte.commentaire
                        )
                    )

            #for trigram, weeks in list(deleted.items()):
            #    for week_number, astreintes in list(weeks.items()):
            #        if trigram in added.keys() and week_number in added[trigram].keys():
            #            for astreinte in added[trigram][week_number]:
            #                modified.setdefault(trigram, {}).setdefault(week_number, []).append(astreinte_info)

            #            del added[trigram][week_number]
            #            if not added[trigram]:
            #                del added[trigram]

            #           del deleted[trigram][week_number]
            #            if not deleted[trigram]:
            #                del deleted[trigram]


        return AstreinteComparisonResult(added=added, deleted=deleted, modified=modified)

    def close(self):
        """
        Ferme le moteur de base de données.
        """
        self.engine.dispose()

    
    def compare_clients_with_database(self, data: Dict[str, PrimeAstreinte]) -> ClientsComparisonResult:
        """
        Compare les données des clients du dictionnaire avec celles de la base de données et retourne les différences.

        :param data: Dictionnaire contenant les données des clients à comparer.
        :return: Instance de ClientsComparisonResult contenant les différences.
        """
        added = {}
        deleted = {}
        modified = {}

        with self.Session() as session:
            # Vérifier les données dans le dictionnaire qui manquent en base
            for key, company in data.items():
                existing = session.query(Clients).filter_by(company=company.company).first()
                if not existing:
                    # Absent en base
                    added[key] = company
                else:
                    # Présent mais avec une différence sur les horaires uniquement
                    if (existing.horaires != data[key].horaires):
                        modified[key] = company
            # Vérifier les données en base qui manquent dans le dictionnaire
            all_clients = session.query(Clients).all()
            for client in all_clients:
                if client.company not in data:
                    deleted[client.company] = client
        return ClientsComparisonResult(added=added, deleted=deleted, modified=modified)    

       