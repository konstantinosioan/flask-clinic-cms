import os

from datetime import timedelta
from flask import Flask, render_template, g, redirect, flash, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_db, login_required, valid_password, get_doctor_form_data, get_doctor_or_404, get_gallery_item_or_404, truncate_words, save_image, delete_photo

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
app.jinja_env.filters["truncate_words"] = truncate_words

@app.route("/")
def index():
    db = get_db()

    doctors = db.execute("SELECT * FROM doctors").fetchall()
    gallery = db.execute("SELECT * FROM gallery").fetchall()
    clinic_info = db.execute("SELECT * FROM clinic_info").fetchone()

    return render_template("index.html", doctors=doctors, gallery=gallery, clinic_info=clinic_info)


@app.route("/admin")
@login_required
def admin():
    db = get_db()

    doctors = db.execute("SELECT * FROM doctors").fetchall()
    gallery_items = db.execute("SELECT * FROM gallery").fetchall()

    return render_template("dashboard.html", doctors=doctors, gallery_items=gallery_items)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Παρακαλώ συμπληρώστε το όνομα χρήστη σας.", "danger")
            return redirect(url_for("admin_login"))
        elif not request.form.get("password"):
            flash("Παρακαλώ συμπληρώστε τον κωδικό σας.", "danger")
            return redirect(url_for("admin_login"))

        db = get_db()

        rows = db.execute(
            "SELECT * FROM admins WHERE username = ?", (request.form.get("username"),)
        ).fetchall()

        if len(rows) != 1 or not check_password_hash(
            rows[0]["pass_hash"], request.form.get("password")
        ):
            flash("Λανθασμένος συνδυασμός στοιχείων.", "danger")
            return redirect(url_for("admin_login"))

        session.permanent = True
        session["admin_id"] = rows[0]["id"]

        return redirect(url_for("admin"))
    else:
        return render_template("login.html")



@app.route("/admin/logout")
def logout():
    session.clear()

    return redirect(url_for("index"))


@app.route("/admin/password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        curr_password = request.form.get("password")
        new_password = request.form.get("new_password")
        conf_password = request.form.get("confirmation")

        if not curr_password or not new_password or not conf_password:
            flash("Παρακαλώ συμπληρώστε και τα 3 πεδία.", "danger")
            return redirect(url_for("change_password"))

        db = get_db()

        row = db.execute("SELECT pass_hash FROM admins WHERE id = ?", (session["admin_id"],)).fetchone()

        if not check_password_hash(row["pass_hash"], curr_password):
            flash("Λανθασμένος τρέχων κωδικός.", "danger")
            return redirect(url_for("change_password"))

        if not valid_password(new_password):
            flash("Ο καινούριος κωδικός πρέπει να περιέχει τουλάχιστον 8 χαρακτήρες και τουλάχιστον από ένα κεφαλαίο γράμμα, ψηφίο και μη αλφαριθμητικό χαρακτήρα.", "danger")
            return redirect(url_for("change_password"))

        if new_password != conf_password:
            flash("Οι 2 κωδικοί πρέπει να ταιριάζουν.", "danger")
            return redirect(url_for("change_password"))

        db.execute("UPDATE admins SET pass_hash = ? WHERE id = ?",
                   (generate_password_hash(new_password), session["admin_id"]))
        db.commit()

        flash("Ο κωδικός σας άλλαξε επιτυχώς.", "success")

        return redirect(url_for("admin"))
    else:
        return render_template("password.html")


@app.route("/admin/doctors/new", methods=["GET", "POST"])
@login_required
def add_doctor():
    if request.method == "POST":
        data = get_doctor_form_data()

        if not all(data.values()):
            flash("Παρακαλώ συμπληρώστε και τα 5 πεδία.", "danger")
            return render_template("doctor_form.html", values=data)
        
        photo = request.files["photo"]
        photo_filename = save_image(photo)

        if photo.filename and not photo_filename:
            flash("Το αρχείο φωτογραφίας δεν είναι έγκυρη εικόνα.", "danger")
            return render_template("doctor_form.html", values=data)

        db = get_db()
        db.execute("INSERT INTO doctors (name, role, bio, email, phone, photo_filename) VALUES(?, ?, ?, ?, ?, ?)",
                   (data["name"], data["role"], data["bio"], data["email"], data["phone"], photo_filename))
        db.commit()

        flash("Ο ιατρός προστέθηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))
    else:
        return render_template("doctor_form.html")


@app.route("/admin/doctors/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_doctor(id):
    db = get_db()
    doctor = get_doctor_or_404(db, id)

    if request.method == "POST":
        data = get_doctor_form_data()

        if not all(data.values()):
            flash("Παρακαλώ συμπληρώστε και τα 5 πεδία.", "danger")
            return render_template("doctor_form.html", values=data, doctor_id=id)
        
        photo = request.files["photo"]
        photo_filename = save_image(photo) if photo.filename else doctor["photo_filename"]

        if photo.filename and not photo_filename:
            flash("Το αρχείο φωτογραφίας δεν είναι έγκυρη εικόνα.", "danger")
            return render_template("doctor_form.html", values=data, doctor_id=id)

        db.execute("UPDATE doctors SET name = ?, role = ?, bio = ?, email = ?, phone = ?, photo_filename = ? WHERE id = ?",
                   (data["name"], data["role"], data["bio"], data["email"], data["phone"], photo_filename, id))
        db.commit()

        flash("Τα στοιχεία του ιατρού ενημερώθηκαν επιτυχώς.", "success")

        return redirect(url_for("admin"))
    else:
        return render_template("doctor_form.html", values=doctor, doctor_id=id)


@app.route("/admin/doctors/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete_doctor(id):
    db = get_db()
    doctor = get_doctor_or_404(db, id)
    
    if request.method == "POST":
        delete_photo(doctor["photo_filename"])
        
        db.execute("DELETE FROM doctors WHERE id = ?", (id,))
        db.commit()
        
        flash("Ο ιατρός διαγράφηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))
    else:        
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
        db.execute("INSERT INTO gallery (image_filename, caption) VALUES(?, ?)", (image_filename, caption))
        db.commit()

        flash("Η φωτογραφία προστέθηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))
    else:
        return render_template("gallery_form.html")


@app.route("/admin/gallery/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_gallery_item(id):
    db = get_db()
    gallery_item = get_gallery_item_or_404(db, id)

    if request.method == "POST":
        caption = request.form.get("caption")
        image = request.files["image"]
        image_filename = save_image(image) if image.filename else gallery_item["image_filename"]
        
        if image.filename and not image_filename:
            flash("Το αρχείο φωτογραφίας δεν είναι έγκυρη εικόνα.", "danger")
            return render_template("gallery_form.html", values={"caption": caption}, gallery_id=id)

        db.execute("UPDATE gallery SET image_filename = ?, caption = ? WHERE id = ?", (image_filename, caption, id))
        db.commit()

        flash("Η φωτογραφία ενημερώθηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))
    else:
        return render_template("gallery_form.html", values=gallery_item, gallery_id=id)


@app.route("/admin/gallery/<int:id>/delete", methods=["POST"])
@login_required
def delete_gallery_item(id):
    db = get_db()
    gallery_item = get_gallery_item_or_404(db, id)
        
    delete_photo(gallery_item["image_filename"])
    
    db.execute("DELETE FROM gallery WHERE id = ?", (id,))
    db.commit()
    
    flash("Η φωτογραφία διαγράφηκε επιτυχώς.", "success")

    return redirect(url_for("admin"))


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)

    if db is not None:
        db.close()
