from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = 'randomkeybestkey'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "sqlite:///database.db")
#
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# CREATE TABLE
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    email = db.Column(db.String(100))
    hcp_id = db.Column(db.Integer, unique=True)
    hcp_index = db.Column(db.Float)
    hcp_qn = db.Column(db.Float)
    pt_ranking = db.Column(db.Float)
    cat = db.Column(db.String(10))
    juv = db.Column(db.String(10))
    senior = db.Column(db.String(10))


class Torneios(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    date = db.Column(db.String(100))
    type = db.Column(db.String(100))
    cat = db.Column(db.String(100))


db.create_all()


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":

        if User.query.filter_by(email=request.form.get('email')).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=request.form.get('email'),
            name=request.form.get('name'),
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("clube"))

    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('clube'))

    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/clube')
@login_required
def clube():
    for t in db.metadata.tables.keys():
        print(t)

    return render_template("clube.html", name=current_user.name, logged_in=True)


@app.route('/criartorneio', methods=["GET", "POST"])
@login_required
def criartorneio():
    if request.method == "POST":
        new_torneio = Torneios(
            name=request.form.get('name'),
            date=request.form.get('date'),
            type=request.form.get('type'),
            cat=request.form.get('cat'),

        )
        torneio = Torneios.query.filter_by(
            name=new_torneio.name, date=new_torneio.date).first()
        if not torneio:
            print(torneio)

            db.session.add(new_torneio)
            db.session.commit()

            class Apuracao_torneio(db.Model):
                __tablename__ = new_torneio.id
                id = db.Column(db.Integer, primary_key=True)
                player = db.Column(db.String(100))
            db.create_all()

        else:
            print("Torneio já existe")
        rows = Torneios.query.all()

        return render_template('novo_torneio.html',
                               title='Tourneio',
                               rows=rows, name=current_user.name, logged_in=True)
    rows = Torneios.query.all()
    return render_template('novo_torneio.html',
                           title='Tourneio',
                           rows=rows, name=current_user.name, logged_in=True)


@app.route('/torneio/<id>', methods=["GET", "POST"])
@login_required
def torneio_atual(id):

    # tables_dict = {
    #     table.__tablename__: table for table in db.Model.__subclasses__()}
    # print(tables_dict)
    for t in db.metadata.tables.keys():
        print(t)

    # Adicionar multiplos jogadores a um torneio
    # if request.method == "POST":
    #     list = request.form.getlist("name")
    #     for item in list:
    #         inscrito = torneio_atual(name=item)
    #         player = torneio_atual.query.filter_by(name=inscrito.name).first()
    #         if not player:
    #             print(player)
    #             db.session.add(inscrito)
    #         else:
    #             print("Já inscrito")

    #     db.session.commit()

    jogadores = Player.query.all()
    return render_template("torneio_atual.html", j=jogadores, t=1, name=current_user.name, logged_in=True)


@app.route('/jogadores', methods=["GET", "POST"])
@login_required
def jogadores():
    if request.method == "POST":
        new_player = Player(
            email=request.form.get('email'),
            name=request.form.get('name'),
            hcp_id=request.form.get('hcp_id'),
            hcp_index=request.form.get('hcp_index'),
            cat=request.form.get('cat'),
            juv=request.form.get('juv'),
            senior=request.form.get('senior'),
        )
        player = Player.query.filter_by(hcp_id=new_player.hcp_id).first()
        if not player:
            print(player)
            db.session.add(new_player)
            db.session.commit()

        else:
            print("id já existe")
            player.name = request.form.get('name')
            player.email = request.form.get('email')
            player.hcp_index = request.form.get('hcp_index')
            player.cat = request.form.get('cat')
            player.juv = request.form.get('juv')
            player.senior = request.form.get('senior')
            db.session.commit()
        rows = Player.query.all()

        return render_template('jogadores.html',
                               title='Players',
                               rows=rows, name=current_user.name, logged_in=True)
    rows = Player.query.all()
    return render_template('jogadores.html',
                           title='Players',
                           rows=rows, name=current_user.name, logged_in=True)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/config')
@login_required
def config():

    return render_template('config.html')


if __name__ == "__main__":
    app.run(debug=True)
