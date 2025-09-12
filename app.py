import sqlite3
from flask import Flask, render_template, g

DATABASE = "game.db"

app = Flask(__name__)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route("/")
def home():
    db = get_db()
    return render_template("index.html")