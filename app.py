from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/golf/costao-golf/add-torneio", methods=["GET", "POST"])
def add_torneio():
    return render_template("cadastro_torneio.html")


@app.route("/golf/costao-golf/add-player", methods=["GET", "POST"])
def add_player():
    return render_template("cadastro_jogador.html")


@app.route("/golf/costao-golf/torneio", methods=["GET", "POST"])
def torneio():
    return render_template("torneio.html")


if __name__ == "__main__":
    app.run(debug=True)
