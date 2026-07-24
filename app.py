from flask import Flask, render_template, g

from helpers import get_db

app = Flask(__name__)

@app.route("/")
def index():
    db = get_db()
    
    doctors = db.execute("SELECT * FROM doctors").fetchall()
    gallery = db.execute("SELECT * FROM gallery").fetchall()
    clinic_info = db.execute("SELECT * FROM clinic_info").fetchone()
    
    return render_template("index.html", doctors=doctors, gallery=gallery, clinic_info=clinic_info)


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop("db", None)
    
    if db is not None:
        db.close()