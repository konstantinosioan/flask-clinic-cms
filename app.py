from flask import Flask, render_template, g, redirect, flash, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_db, login_required, valid_password

app = Flask(__name__)

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
    """TO-DO"""
    return "TODO"


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    session.clear()
    
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Παρακαλώ συμπληρώστε το username σας.")
            return redirect("/admin/login")
        elif not request.form.get("password"):
            flash("Παρακαλώ όπως συμπληρώσετε τον κωδικό σας.")
            return redirect("/admin/login")
        
        db = get_db()
        
        rows = db.execute(
            "SELECT * FROM admins WHERE username = ?", (request.form.get("username"),)
        ).fetchall()
        
        if len(rows) != 1 or not check_password_hash(
            rows[0]["pass_hash"], request.form.get("password")
        ):
            flash("Λανθασμένος συνδυασμός στοχειών.")
            return redirect("/admin/login")
        
        session["admin_id"] = rows[0]["id"]
        
        return redirect("/admin")
    else:
        return render_template("login.html")
            
    

@app.route("/admin/logout")
def logout():
    session.clear()
    
    return redirect("/")

    
@app.route("/admin/password", methods=["GET", "POST"])
@login_required
def change_password():
    curr_password = request.form.get("password")
    new_password = request.form.get("new_password")
    conf_password = request.form.get("confirmation")
    
    if not curr_password or not new_password or not conf_password:
        flash("Παρακαλώ όπως συμπληρώσετε και τα 3 πεδία.")
        return redirect("/admin/password")
        
    db = get_db()
    
    row = db.execute("SELECT pass_hash FROM admins WHERE id = ?", (session["admin_id"],)).fetchone()

    if not check_password_hash(row["pass_hash"], curr_password):
        flash("Λανθασμένος τρέχον κωδικός.")
        return redirect("/admin/password")
        
    if not valid_password(new_password):
        flash("Ο καινούριος κωδικός πρέπει να περιέχει τουλάχιστον 8 χαρακτήρες και τουλάχιστον απο ένα κεφαλαίο γράμμα, ψηφίο και μη αλφαριθμητικό χαρακτήρα.")
        return redirect("/admin/password")
    
    if new_password != conf_password:
        flash("Οι 2 κωδικοί πρέπει να ταιριάζουν.")
        return redirect("/admin/password")
    
    db.execute("UPDATE admins SET pass_hash = ? WHERE id = ?",
               (generate_password_hash(new_password), session["admin_id"]))
    
    flash("Ο κωδικός σας άλλαξε επιτυχώς.")
    
    return redirect("/admin")
        


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)
    
    if db is not None:
        db.close()