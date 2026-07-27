"""Database, authentication and image-upload helpers for the clinic CMS"""

import os
import secrets
import sqlite3

from functools import wraps
from flask import g, redirect, session, request, url_for, abort, flash
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener

# Registers HEIC/HEIF support with Pillow; primarily to allow iPhone photos
register_heif_opener()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "clinic.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")


def get_db():
    """Return the db connection, creating it if needed"""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row

    return g.db


def login_required(f):
    """Redirect to the login page if not logged in as admin"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin_id") is None:
            return redirect(url_for("admin_login"))

        return f(*args, **kwargs)

    return decorated_function


def valid_password(password):
    """Check that a password has at least 8 characters and has one digit, uppercase letter and special character"""
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
    """Collect and strip the doctor form fields from the request"""
    fields = ("name", "role", "bio", "email", "phone")

    return {field: request.form.get(field, "").strip() for field in fields}


def get_doctor_or_404(db, doctor_id):
    """Look up a doctor by id, aborting with 404 if it doesn't exist"""
    doctor = db.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,)).fetchone()

    if not doctor:
        abort(404)

    return doctor


def get_gallery_item_or_404(db, gallery_id):
    """Look up a gallery item by id, aborting with 404 if it doesn't exist"""
    item = db.execute("SELECT * FROM gallery WHERE id = ?", (gallery_id,)).fetchone()

    if not item:
        abort(404)

    return item


def get_announcement_form_data():
    """Collect and strip the announcement form fields from the request"""
    fields = ("title", "body")

    return {field: request.form.get(field, "").strip() for field in fields}


def get_announcement_or_404(db, announcement_id):
    """Look up an announcement by id, aborting with 404 if it doesn't exist"""
    announcement = db.execute(
        "SELECT * FROM announcements WHERE id = ?", (announcement_id,)
    ).fetchone()

    if not announcement:
        abort(404)

    return announcement


def get_service_form_data():
    """Collect and strip the service form fields from the request"""
    fields = ("name", "details")

    return {field: request.form.get(field, "").strip() for field in fields}


def get_service_or_404(db, service_id):
    """Look up a service by id, aborting with 404 if it doesn't exist"""
    service = db.execute(
        "SELECT * FROM services WHERE id = ?", (service_id,)
    ).fetchone()

    if not service:
        abort(404)

    return service


def truncate_words(text, count=7):
    """Shorten text to the first `count` words, adding `...` if anything was cut"""
    if not text:
        return text

    words = text.split()

    if len(words) <= count:
        return text

    return " ".join(words[:count]) + "..."


def valid_image(file):
    """Check that a file is a real decodable image in an allowed format"""
    image = open_image(file)

    # MPO is what Safari sends for multi-image HEIC (e.g. Portrait mode) photos
    return (
        False
        if image is None
        else image.format in ("JPEG", "PNG", "WEBP", "HEIF", "MPO")
    )


def save_image(file):
    """Validate, process and save an uploaded image returning its new filename, or None if not valid"""
    if not valid_image(file):
        return None

    file.seek(0)
    image = Image.open(file)
    image_format = image.format

    # Corrects phone-camera rotation before the exif metadata gets stripped
    image = ImageOps.exif_transpose(image)

    extension = map_extension(image_format)

    # Server-generated filename for more security
    filename = f"{secrets.token_hex(12)}.{extension}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    path = os.path.join(UPLOAD_DIR, filename)

    if extension == "jpg":
        # HEIC/MPO aren't supported well on browsers so re-encode them as JPEG
        image.save(path, format="JPEG")
    else:
        image.save(path, format=image_format)

    return filename


def process_photo_upload(field_name, existing_filename=None, remove_existing=False):
    """Save a newly uploaded photo, remove the existing one if requested, or keep it unchanged"""
    file = request.files[field_name]

    if not file.filename:
        if remove_existing:
            delete_photo(existing_filename)
            return None, False

        return existing_filename, False

    filename = save_image(file)

    if filename is None:
        flash("Το αρχείο φωτογραφίας δεν είναι έγκυρη εικόνα.", "danger")
        return None, True

    if existing_filename:
        delete_photo(existing_filename)

    return filename, False


def map_extension(image_format):
    """Map a Pillow image format to the file extension it should be saved with"""
    return "jpg" if image_format in ("JPEG", "HEIF", "MPO") else image_format.lower()


def delete_photo(filename):
    """Remove a photo file from disk, ignoring it if missing"""
    if not filename:
        return

    try:
        os.remove(os.path.join(UPLOAD_DIR, filename))
    except OSError:
        pass


def normalize_url(value):
    """Return a URL with a scheme prepended if missing, or None if value itself missing"""
    if not value:
        return None

    if not value.startswith(("http://", "https://")):
        return "https://" + value

    return value


# Guards against decompression bomb images with huge pixel counts
MAX_IMAGE_PIXELS = 50_000_000


def open_image(file):
    """Open and validate a file as a real image, rejecting invalid or oversized ones"""
    try:
        image = Image.open(file)
        image.verify()
    except Exception:
        # Pillow can raise multiple different exceptions
        return None

    if image.width * image.height > MAX_IMAGE_PIXELS:
        return None

    return image
