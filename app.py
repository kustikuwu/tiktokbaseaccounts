
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import shutil
from bot import run_bot

app = Flask(__name__)
DB = "db.sqlite3"
SESSIONS_DIR = "sessions"

def get_db():
    return sqlite3.connect(DB)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/accounts")
def accounts():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM accounts")
    accounts = c.fetchall()
    conn.close()
    return render_template("accounts.html", accounts=accounts)

@app.route("/commands")
def commands():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM commands ORDER BY id DESC")
    commands = c.fetchall()
    conn.close()
    return render_template("commands.html", commands=commands)

@app.route("/add_command", methods=["GET", "POST"])
def add_command():
    conn = get_db()
    c = conn.cursor()
    if request.method == "POST":
        account_id = request.form["account_id"]
        command = request.form["command"]
        target_url = request.form["target_url"]
        c.execute("INSERT INTO commands (account_id, command, target_url) VALUES (?, ?, ?)",
                  (account_id, command, target_url))
        conn.commit()
        conn.close()
        return redirect(url_for("commands"))
    c.execute("SELECT id, name FROM accounts")
    accounts = c.fetchall()
    conn.close()
    return render_template("add_command.html", accounts=accounts)

@app.route("/add_account", methods=["GET", "POST"])
def add_account():
    if request.method == "POST":
        name = request.form["name"]
        file = request.files["session_file"]
        if file:
            os.makedirs(SESSIONS_DIR, exist_ok=True)
            path = os.path.join(SESSIONS_DIR, file.filename)
            file.save(path)

            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO accounts (name, session_path) VALUES (?, ?)", (name, path))
            conn.commit()
            conn.close()
            return redirect(url_for("accounts"))
    return render_template("add_account.html")

@app.route("/run")
def run():
    run_bot()
    return redirect(url_for("commands"))

if __name__ == "__main__":
    app.run(debug=True)
