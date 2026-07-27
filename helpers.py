import os
import secrets
import sqlite3

from functools import wraps
from flask import g, redirect, session, request, url_for, abort, flash
from PIL import Image, ImageOps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "clinic.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
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
    fields = ("name", "role", "bio", "email", "phone")

    return {field: request.form.get(field, "").strip() for field in fields}


def get_doctor_or_404(db, doctor_id):
    doctor = db.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,)).fetchone()

    if not doctor:
        abort(404)

    return doctor


def get_gallery_item_or_404(db, gallery_id):
    item = db.execute("SELECT * FROM gallery WHERE id = ?", (gallery_id,)).fetchone()

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

    return False if image is None else image.format in ("JPEG", "PNG", "WEBP")


def save_image(file):
    if not valid_image(file):
        return None

    file.seek(0)
    image = Image.open(file)
    image_format = image.format
    image = ImageOps.exif_transpose(image)

    extension = map_extension(image_format)
    filename = f"{secrets.token_hex(12)}.{extension}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, filename)

    image.save(path, format=image_format)

    return filename


def process_photo_upload(field_name, existing_filename=None):
    file = request.files[field_name]
    filename = save_image(file) if file.filename else existing_filename

    if file.filename and filename is None:
        flash("Το αρχείο φωτογραφίας δεν είναι έγκυρη εικόνα.", "danger")
        return None, True

    return filename, False


def map_extension(image_format):
    return "jpg" if image_format == "JPEG" else image_format.lower()


def delete_photo(filename):
    if not filename:
        return

    try:
        os.remove(os.path.join(UPLOAD_DIR, filename))
    except OSError:
        pass


def normalize_url(value):
    if not value:
        return None

    if not value.startswith(("http://", "https://")):
        return "https://" + value

    return value


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
