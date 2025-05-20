import sys
import os
from pathlib import Path

def is_frozen():
    return getattr(sys, 'frozen', False)

def conteneur_path():
    if is_frozen():
        return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve()))
    else:
        return Path(__file__).resolve().parent.parent
    
def execution_path():
    if is_frozen():
        return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve()))
    else:
        return Path(__file__).resolve().parent.parent

def get_db_path():
    return base_path() / 'data' / 'database.db'
