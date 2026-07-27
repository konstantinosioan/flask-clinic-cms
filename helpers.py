import sqlite3
import secrets
import os

from flask import g, redirect, session, request, url_for, abort
from functools import wraps
from PIL import Image

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect("clinic.db")
        g.db.row_factory = sqlite3.Row
        
    return g.db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin_id") is None:
            return redirect(url_for("admin_login"))
        
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


def get_doctor_form_data():
    name = request.form.get("name", "").strip()
    role = request.form.get("role", "").strip()
    bio = request.form.get("bio", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()

    return {"name": name, "role": role, "bio": bio, "email": email, "phone": phone}


def get_doctor_or_404(db, id):
    doctor = db.execute("SELECT * FROM doctors WHERE id = ?", (id,)).fetchone()

    if not doctor:
        abort(404)
        
    return doctor


def get_gallery_item_or_404(db, id):
    item = db.execute("SELECT * FROM gallery WHERE id = ?", (id,)).fetchone()

    if not item:
        abort(404)

    return item


def truncate_words(text, count=7):
    if not text:
        return text

    words = text.split()

    if len(words) <= count:
        return text

    return " ".join(words[:count]) + "..."


def valid_image(file):
    image = open_image(file)

    return False if image is None else image.format in ('JPEG', 'PNG', 'WEBP')


def save_image(file):
    if not valid_image(file):
        return None

    file.seek(0)
    image = Image.open(file)

    extension = map_extension(image.format)
    filename = f"{secrets.token_hex(12)}.{extension}"
    path = os.path.join('static', 'uploads', filename)

    image.save(path, format=image.format)

    return filename


def map_extension(image_format):
    return 'jpg' if image_format == 'JPEG' else image_format.lower()


def delete_photo(filename):
    if not filename:
        return

    try:
        os.remove(os.path.join('static', 'uploads', filename))
    except OSError:
        pass


MAX_IMAGE_PIXELS = 50_000_000


def open_image(file):
    try:
        image = Image.open(file)
        image.verify()
    except Exception:
        return None

    if image.width * image.height > MAX_IMAGE_PIXELS:
        return None

    return image
