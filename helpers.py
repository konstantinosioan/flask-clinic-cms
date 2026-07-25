import sqlite3

from flask import g, redirect, session
from functools import wraps

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("clinic.db")
        g.db.row_factory = sqlite3.Row
        
    return g.db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin_id") is None:
            return redirect("/admin/login")
        
        return f(*args, **kwargs)
    
    return decorated_function
        
        
def valid_password(password):
    if password is None or len(password) < 8:
        return False
    
    has_number = has_uppercase = has_special = False
    
    for char in password:
        if char.isdigit():
            has_number = True
        elif char.isupper():
            has_uppercase = True
        elif not char.isalnum():
            has_special = True
            
    return has_number and has_uppercase and has_special