import sqlite3

from flask import g

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("clinic.db")
        g.db.row_factory = sqlite3.Row
        
    return g.db
        