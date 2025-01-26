
from typing import Dict, List
from lib.configuration import Configuration
from baseclass.planning_parser import *
import openpyxl
import pandas
import re
from fnmatch import fnmatch


class AstreintePlanningParser(PlanningParser):

    SHEET_PLANNING = 'Planning'
    SHEET_ASTREINT = 'ListeAstreinte'

    def __init__(self) -> None:
        super().__init__()

    def parse_planning(self, ignore=False) -> None:
        if ignore:
            super().parse_planning()
            return

        df2 = pandas.read_excel(Configuration().PATH_PLANNING_XLS, sheet_name=self.SHEET_ASTREINT)
        line_index: int = 1
        column_name: int = 0
        column_n1: int = 3
        column_n2: int = 4
        company_name = str(df2.iat[line_index, column_name])
        while company_name != "nan":
            prime_n1 = int(df2.iat[line_index, column_n1] if str(df2.iat[line_index, column_n1]) != 'nan' else 0)
            prime_n2 = int(df2.iat[line_index, column_n2] if str(df2.iat[line_index, column_n2]) != 'nan' else 0)
            self.primes_astreinte[company_name] = PrimeAstreinte(company_name, prime_n1, prime_n2)
            line_index += 1
            company_name = str(df2.iat[line_index, column_name])

        df = pandas.read_excel(Configuration().PATH_PLANNING_XLS, sheet_name=self.SHEET_PLANNING)
        print('Récup des astreintes...')
        astreinte_par_colonne = {}
        c=1
    
        for i in range(1,100):
            nme = str(df.iat[0, c])
            n1 = str(df.iat[2, c])
            n2 = str(df.iat[2, c+1])

            if nme == 'nan':
                break

            if nme != None:
                nme = nme.strip()
            if n1 != None:
                n1 = n1.strip()
            if n2 != None:
                n2 = n2.strip()

            if nme == None and n2 == None:
                break

            if nme == None:
                continue

            found = True
            lvls = []
            if n1 == 'N3':
                lvls = ['N3']
            elif n1 == 'N1' and n2=='N2':
                lvls = ['N1','N2']
            elif n2 == 'N1':            
                lvls = ['N1']
            else:
                found = False
                print('ERREUR: Detection site')

            if found == True:                           
                obj={
                    'col':c,
                    'name':nme,
                    'levels':lvls
                    }
            
                astreinte_par_colonne[c]=obj
            
                c+=len(lvls)

        print('Récup des semaines...')
        pattern = re.compile(r'^S([0-9]+)$')
        numero_ligne_par_numero_semaine = {}
        for row_index in range(5,100):
            txt = str(df.iat[row_index, 0])
            match = pattern.match(str(txt))
            if match != None:
            
                numero_semaine = int(match.group(1))
                if numero_semaine in numero_ligne_par_numero_semaine:
                    print('[WARNING] - Doublon de semaine %d dans le fichier source' % (numero_semaine))
                
                numero_ligne_par_numero_semaine[numero_semaine]=row_index

        print('Récup du planning...')
        self.affectation_astreintes: Dict[str, Dict[int, List[AstreinteInfo]]] = dict()
        for week_nbr,row_index in numero_ligne_par_numero_semaine.items():
            lst = []
            for c,ast in astreinte_par_colonne.items():
                inx=0
                for lvl in ast['levels']:
                    item = AstreinteInfo(ast['name'], lvl, week_nbr)
                    trigramme=str(df.iat[row_index, c+inx]).upper()

                    if trigramme not in self.affectation_astreintes.keys():
                        self.affectation_astreintes[trigramme] = dict()

                    if week_nbr not in self.affectation_astreintes[trigramme].keys():
                        self.affectation_astreintes[trigramme][week_nbr] = list()

                    self.affectation_astreintes[trigramme][week_nbr].append(item)

                    inx+=1

        # Retravail du dictionnaire pour ajouter les astreintes affectées à plusieurs personnes
        for trigram, ast_by_week in self.affectation_astreintes.items():
            if len(trigram) <= 6:
                continue
            contained_trigrams = [t for t in self.affectation_astreintes if t in trigram and t != trigram]
            for linked_trigram in contained_trigrams:
                for week_number, list_astreints in ast_by_week.items():
                    if week_number not in self.affectation_astreintes[linked_trigram].items():
                        self.affectation_astreintes[linked_trigram][week_number] = list()

                        for astreint in list_astreints:
                            self.affectation_astreintes[linked_trigram][week_number].append(astreint)

        # Appel à la méthode de base en fin d'import pour mettre à jour les flags internes
        super().parse_planning()

    def check_attendee_constraints(self, ctrl_week_number: int) -> List[str]:
        inconsistencies = list()
        user = Configuration().attendee_trigram
        for constraint in Configuration().attendee_constraints:
            count = 0
            for week_number, astreints in self.get_astreintes(user).items():
                if week_number != ctrl_week_number:
                    continue

                for astreint in astreints:
                    if fnmatch(astreint.company, constraint.company):
                        count += 1
                        if count > constraint.max:
                            print(f"Contrainte non respectée pour la semaine {week_number} : {constraint}")
                            inconsistencies.append(f"Contrainte non respectée pour la semaine {week_number} : {constraint}")
                            break

        # Astreintes limitées à ce qui est listé dans les contraintes
        for week_number, astreints in self.get_astreintes(user).items():
            if week_number != ctrl_week_number:
                continue

            for astreint in astreints:
                not_wanted = [astr for astr in astreints]
                for constraint in Configuration().attendee_constraints:
                    if constraint.company == "*":
                        continue
                    if fnmatch(astreint.company, constraint.company):
                        not_wanted.pop(not_wanted.index(astreint))

            if not_wanted:
                print(f"Contrainte non respectée pour la semaine {week_number} : Entreprise(s) non souhaitée(s) {[item.company for item in not_wanted]}")
                inconsistencies.append(f"Contrainte non respectée pour la semaine {week_number} : Entreprise(s) non souhaitée(s) {[item.company for item in not_wanted]}")
                break

        return inconsistencies