from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, List
from baseclass.planning_parser import AstreinteInfo

Base = declarative_base()

class Astreinte(Base):
    __tablename__ = 'Astreinte'
    id = Column(Integer, primary_key=True, autoincrement=True)
    trigram = Column(String(10), nullable=False)
    week_number = Column(Integer, nullable=False)
    company = Column(String(100), nullable=False)
    level = Column(String(10), nullable=False)

    __table_args__ = (
        UniqueConstraint('trigram', 'week_number', 'company', 'level', name='unique_astreinte'),
    )


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
    def __init__(self, db_url='sqlite:///data/database.db'):
        """
        Initialise la connexion à la base de données et configure le moteur et la session.
        """
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

    def add_astreinte(self, trigram, week_number, company, level):
        """
        Ajoute une nouvelle astreinte à la base de données.
        """
        with self.Session() as session:
            astreinte = Astreinte(trigram=trigram, week_number=week_number, company=company, level=level)
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


    def update_all_data(self, data: Dict[str, Dict[int, List[AstreinteInfo]]]) -> None:
        with self.Session() as session:
            session.query(Astreinte).delete()
            for trigram, weeks in data.items():
                for week_number, astreintes in weeks.items():
                    for astreinte_info in astreintes:
                        astreinte = Astreinte(trigram=trigram, week_number=week_number, company=astreinte_info.company, level=astreinte_info.level)
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
                        # elif existing.level != astreinte_info.level:
                        #     # Présent mais avec une différence
                        #     modified.setdefault(trigram, {}).setdefault(week_number, []).append(astreinte_info)

            # Vérifier les données en base qui manquent dans le dictionnaire
            all_astreintes = session.query(Astreinte).all()
            for astreinte in all_astreintes:
                trigram, week_number = astreinte.trigram, astreinte.week_number
                if (trigram not in data or
                        week_number not in data[trigram] or
                        not any(
                            astreinte.company == info.company and astreinte.level == info.level
                            for info in data[trigram].get(week_number, [])
                        )):
                    deleted.setdefault(trigram, {}).setdefault(week_number, []).append(
                        AstreinteInfo(
                            company=astreinte.company,
                            level=astreinte.level,
                            week_number=astreinte.week_number
                        )
                    )

            for trigram, weeks in list(deleted.items()):
                for week_number, astreintes in list(weeks.items()):
                    if trigram in added.keys() and week_number in added[trigram].keys():
                        for astreinte in added[trigram][week_number]:
                            modified.setdefault(trigram, {}).setdefault(week_number, []).append(astreinte_info)

                        del added[trigram][week_number]
                        if not added[trigram]:
                            del added[trigram]

                        del deleted[trigram][week_number]
                        if not deleted[trigram]:
                            del deleted[trigram]


        return AstreinteComparisonResult(added=added, deleted=deleted, modified=modified)

    def close(self):
        """
        Ferme le moteur de base de données.
        """
        self.engine.dispose()
