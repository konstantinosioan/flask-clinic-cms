import os

from datetime import timedelta
from flask import Flask, render_template, g, redirect, flash, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import (
    get_db,
    login_required,
    valid_password,
    get_doctor_form_data,
    get_doctor_or_404,
    get_gallery_item_or_404,
    truncate_words,
    save_image,
    delete_photo,
    process_photo_upload,
    normalize_url,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.jinja_env.filters["truncate_words"] = truncate_words


@app.route("/")
def index():
    db = get_db()

    doctors = db.execute("SELECT * FROM doctors ORDER BY id").fetchall()
    gallery = db.execute("SELECT * FROM gallery").fetchall()
    clinic_info = db.execute("SELECT * FROM clinic_info").fetchone()

    return render_template(
        "index.html", doctors=doctors, gallery=gallery, clinic_info=clinic_info
    )


@app.route("/admin")
@login_required
def admin():
    db = get_db()

    doctors = db.execute("SELECT * FROM doctors ORDER BY id").fetchall()
    gallery_items = db.execute("SELECT * FROM gallery").fetchall()

    return render_template(
        "dashboard.html", doctors=doctors, gallery_items=gallery_items
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username:
            flash("Παρακαλώ συμπληρώστε το όνομα χρήστη σας.", "danger")
            return redirect(url_for("admin_login"))
        if not password:
            flash("Παρακαλώ συμπληρώστε τον κωδικό σας.", "danger")
            return redirect(url_for("admin_login"))

        db = get_db()

        rows = db.execute(
            "SELECT * FROM admins WHERE username = ?", (username,)
        ).fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["pass_hash"], password):
            flash("Λανθασμένος συνδυασμός στοιχείων.", "danger")
            return redirect(url_for("admin_login"))

        session.permanent = True
        session["admin_id"] = rows[0]["id"]

        return redirect(url_for("admin"))

    return render_template("login.html")


@app.route("/admin/logout")
def logout():
    session.clear()

    return redirect(url_for("index"))


@app.route("/admin/password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        curr_password = request.form.get("password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        conf_password = request.form.get("confirmation", "").strip()

        if not curr_password or not new_password or not conf_password:
            flash("Παρακαλώ συμπληρώστε και τα 3 πεδία.", "danger")
            return redirect(url_for("change_password"))

        db = get_db()

        row = db.execute(
            "SELECT pass_hash FROM admins WHERE id = ?", (session["admin_id"],)
        ).fetchone()

        if not check_password_hash(row["pass_hash"], curr_password):
            flash("Λανθασμένος τρέχων κωδικός.", "danger")
            return redirect(url_for("change_password"))

        if not valid_password(new_password):
            flash(
                "Ο καινούριος κωδικός πρέπει να περιέχει τουλάχιστον 8 χαρακτήρες και τουλάχιστον από ένα κεφαλαίο γράμμα, ψηφίο και μη αλφαριθμητικό χαρακτήρα.",
                "danger",
            )
            return redirect(url_for("change_password"))

        if new_password != conf_password:
            flash("Οι 2 κωδικοί πρέπει να ταιριάζουν.", "danger")
            return redirect(url_for("change_password"))

        db.execute(
            "UPDATE admins SET pass_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), session["admin_id"]),
        )
        db.commit()

        flash("Ο κωδικός σας άλλαξε επιτυχώς.", "success")

        return redirect(url_for("admin"))

    return render_template("password.html")


@app.route("/admin/doctors/new", methods=["GET", "POST"])
@login_required
def add_doctor():
    if request.method == "POST":
        data = get_doctor_form_data()

        if not all(data.values()):
            flash("Παρακαλώ συμπληρώστε και τα 5 πεδία.", "danger")
            return render_template("doctor_form.html", values=data)

        photo_filename, invalid = process_photo_upload("photo")

        if invalid:
            return render_template("doctor_form.html", values=data)

        db = get_db()
        db.execute(
            "INSERT INTO doctors (name, role, bio, email, phone, photo_filename) VALUES(?, ?, ?, ?, ?, ?)",
            (
                data["name"],
                data["role"],
                data["bio"],
                data["email"],
                data["phone"],
                photo_filename,
            ),
        )
        db.commit()

        flash("Ο ιατρός προστέθηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))

    return render_template("doctor_form.html")


@app.route("/admin/doctors/<int:doctor_id>/edit", methods=["GET", "POST"])
@login_required
def edit_doctor(doctor_id):
    db = get_db()
    doctor = get_doctor_or_404(db, doctor_id)

    if request.method == "POST":
        data = get_doctor_form_data()

        if not all(data.values()):
            flash("Παρακαλώ συμπληρώστε και τα 5 πεδία.", "danger")
            return render_template("doctor_form.html", values=data, doctor_id=doctor_id)

        photo_filename, invalid = process_photo_upload(
            "photo", doctor["photo_filename"]
        )

        if invalid:
            return render_template("doctor_form.html", values=data, doctor_id=doctor_id)

        db.execute(
            "UPDATE doctors SET name = ?, role = ?, bio = ?, email = ?, phone = ?, photo_filename = ? WHERE id = ?",
            (
                data["name"],
                data["role"],
                data["bio"],
                data["email"],
                data["phone"],
                photo_filename,
                doctor_id,
            ),
        )
        db.commit()

        flash("Τα στοιχεία του ιατρού ενημερώθηκαν επιτυχώς.", "success")

        return redirect(url_for("admin"))

    return render_template("doctor_form.html", values=doctor, doctor_id=doctor_id)


@app.route("/admin/doctors/<int:doctor_id>/delete", methods=["GET", "POST"])
@login_required
def delete_doctor(doctor_id):
    db = get_db()
    doctor = get_doctor_or_404(db, doctor_id)

    if request.method == "POST":
        delete_photo(doctor["photo_filename"])

        db.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        db.commit()

        flash("Ο ιατρός διαγράφηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))

    return render_template("delete_confirm.html", doctor=doctor)


@app.route("/admin/gallery/new", methods=["GET", "POST"])
@login_required
def add_gallery_item():
    if request.method == "POST":
        caption = request.form.get("caption")
        image = request.files["image"]
        image_filename = save_image(image)

        if not image_filename:
            flash("Παρακαλώ ανεβάστε μια έγκυρη φωτογραφία.", "danger")
            return render_template("gallery_form.html", values={"caption": caption})

        db = get_db()
        db.execute(
            "INSERT INTO gallery (image_filename, caption) VALUES(?, ?)",
            (image_filename, caption),
        )
        db.commit()

        flash("Η φωτογραφία προστέθηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))

    return render_template("gallery_form.html")


@app.route("/admin/gallery/<int:gallery_id>/edit", methods=["GET", "POST"])
@login_required
def edit_gallery_item(gallery_id):
    db = get_db()
    gallery_item = get_gallery_item_or_404(db, gallery_id)

    if request.method == "POST":
        caption = request.form.get("caption")
        image_filename, invalid = process_photo_upload(
            "image", gallery_item["image_filename"]
        )

        if invalid:
            return render_template(
                "gallery_form.html", values={"caption": caption}, gallery_id=gallery_id
            )

        db.execute(
            "UPDATE gallery SET image_filename = ?, caption = ? WHERE id = ?",
            (image_filename, caption, gallery_id),
        )
        db.commit()

        flash("Η φωτογραφία ενημερώθηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))

    return render_template(
        "gallery_form.html", values=gallery_item, gallery_id=gallery_id
    )


@app.route("/admin/gallery/<int:gallery_id>/delete", methods=["POST"])
@login_required
def delete_gallery_item(gallery_id):
    db = get_db()
    gallery_item = get_gallery_item_or_404(db, gallery_id)

    delete_photo(gallery_item["image_filename"])

    db.execute("DELETE FROM gallery WHERE id = ?", (gallery_id,))
    db.commit()

    flash("Η φωτογραφία διαγράφηκε επιτυχώς.", "success")

    return redirect(url_for("admin"))


@app.route("/admin/contact-info", methods=["GET", "POST"])
@login_required
def edit_clinic_info():
    db = get_db()
    clinic_info = db.execute("SELECT * FROM clinic_info").fetchone()

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        instagram_url = normalize_url(request.form.get("instagram_url", "").strip())
        facebook_url = normalize_url(request.form.get("facebook_url", "").strip())

        if not email or not phone:
            flash("Παρακαλώ συμπληρώστε το email και το τηλέφωνο.", "danger")
            return render_template("contact_info_form.html", values=clinic_info)

        db.execute(
            "UPDATE clinic_info SET email = ?, phone = ?, instagram_url = ?, facebook_url = ? WHERE id = ?",
            (email, phone, instagram_url, facebook_url, clinic_info["id"]),
        )
        db.commit()

        flash("Τα στοιχεία ενημερωθήκαν επιτυχώς.", "success")

        return redirect(url_for("admin"))

    return render_template("contact_info_form.html", values=clinic_info)


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)

    if db is not None:
        db.close()
