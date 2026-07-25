import os
from datetime import timedelta

from flask import Flask, render_template, g, redirect, flash, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_db, login_required, valid_password, get_doctor_form_data, get_doctor_or_404

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

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

    return render_template("dashboard.html", doctors=doctors)


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

        db = get_db()
        db.execute("INSERT INTO doctors (name, role, bio, email, phone) VALUES(?, ?, ?, ?, ?)",
                   (data["name"], data["role"], data["bio"], data["email"], data["phone"]))
        db.commit()

        flash("Ο ιατρός προστέθηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))
    else:
        return render_template("doctor_form.html")


@app.route("/admin/doctors/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_doctor(id):
    db = get_db()

    if request.method == "POST":
        data = get_doctor_form_data()

        if not all(data.values()):
            flash("Παρακαλώ συμπληρώστε και τα 5 πεδία.", "danger")
            return render_template("doctor_form.html", values=data, doctor_id=id)

        db.execute("UPDATE doctors SET name = ?, role = ?, bio = ?, email = ?, phone = ? WHERE id = ?",
                   (data["name"], data["role"], data["bio"], data["email"], data["phone"], id))
        db.commit()

        flash("Τα στοιχεία του ιατρού ενημερώθηκαν επιτυχώς.", "success")

        return redirect(url_for("admin"))
    else:
        doctor = get_doctor_or_404(db, id)

        return render_template("doctor_form.html", values=doctor, doctor_id=id)


@app.route("/admin/doctors/<int:id>/delete", methods=["GET", "POST"])
@login_required
def delete_doctor(id):
    db = get_db()
    
    if request.method == "POST":
        db.execute("DELETE FROM doctors WHERE id = ?", (id,))
        db.commit()
        
        flash("Ο ιατρός διαγράφηκε επιτυχώς.", "success")

        return redirect(url_for("admin"))
    else:
        doctor = get_doctor_or_404(db, id)
        
        return render_template("delete_confirm.html", doctor=doctor)


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)

    if db is not None:
        db.close()
