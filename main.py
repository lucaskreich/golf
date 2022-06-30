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
    name = db.Column(db.String(1000))
    date = db.Column(db.String(100))
    type = db.Column(db.String(100))
    cat = db.Column(db.String(100))


class Torneio_atual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    torneio_id = db.Column(db.String(100))
    pago = db.Column(db.String(100))
    jogador = db.Column(db.String(100))
    hcp = db.Column(db.String(100))
    cat = db.Column(db.String(100))
    juv = db.Column(db.String(100))
    senior = db.Column(db.String(100))
    b_saida = db.Column(db.String(100))
    b1 = db.Column(db.Integer)
    b2 = db.Column(db.Integer)
    b3 = db.Column(db.Integer)
    b4 = db.Column(db.Integer)
    b5 = db.Column(db.Integer)
    b6 = db.Column(db.Integer)
    b7 = db.Column(db.Integer)
    b8 = db.Column(db.Integer)
    b9 = db.Column(db.Integer)
    b10 = db.Column(db.Integer)
    b11 = db.Column(db.Integer)
    b12 = db.Column(db.Integer)
    b13 = db.Column(db.Integer)
    b14 = db.Column(db.Integer)
    b15 = db.Column(db.Integer)
    b16 = db.Column(db.Integer)
    b17 = db.Column(db.Integer)
    b18 = db.Column(db.Integer)
    v1_gross = db.Column(db.Integer)
    v2_gross = db.Column(db.Integer)
    total_gross = db.Column(db.Integer)
    total_net = db.Column(db.Integer)
    v2_net = db.Column(db.Integer)
    ult_6b_net = db.Column(db.Integer)
    ult_3b_net = db.Column(db.Integer)
    ult_b_net = db.Column(db.Integer)
    ganhos = db.Column(db.Integer)
    pt_rkg = db.Column(db.Integer)
    obs = db.Column(db.String(100))


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

            db.session.add(new_torneio)

        else:
            print("Torneio já existe")
        db.session.commit()
        rows = Torneios.query.all()

        return render_template('novo_torneio.html',
                               title='Tourneio',
                               rows=rows, name=current_user.name, logged_in=True)
    rows = Torneios.query.all()
    return render_template('novo_torneio.html',
                           title='Tourneio',
                           rows=rows, name=current_user.name, logged_in=True)


@app.route('/torneio/apuracao/<id>', methods=["GET", "POST"])
@login_required
def torneio_atual(id):

    if request.method == "POST":

        inscrito_list = request.form.getlist('checkbox_jogadores')

        for i in inscrito_list:
            print(i)
            inscrito = Torneio_atual.query.filter_by(
                jogador=i, torneio_id=id).first()
            player = Torneio_atual(
                jogador=i,
                torneio_id=id,
                pago=request.form.get(i+'_pago'),
                b_saida=request.form.get(i+'_b_saida'),
                hcp=request.form.get(i+'_hcp')

            )
            if inscrito:
                inscrito.hcp = request.form.get(i+'_hcp')
                inscrito.b_saida = request.form.get(i+'_b_saida')
                inscrito.pago = request.form.get(i+'_pago')
                db.session.commit()
                print("já inscrito")

                # Editar Pago
            else:
                db.session.add(player)
                db.session.commit()

    t = Torneios.query.filter_by(id=id).first()
    torneio = Torneio_atual.query.filter_by(torneio_id=id).all()
    print(t)
    p = Player.query.all()
    # Checar se jogador selecionado está inscrito
    # Adicionar Jogador cadastrado a 'Torneio Atual'
    # mostrar jogadores cadastrados, com espaço para adicionar resultado por buraco
    # checkmark qndo resultado do jogador já tiver sido adicionado( ou mudança de cor)
    # tela separada, resultado do torneio
    # verificar para editar handicap (aba do jogador)
    # botão finalizar torneio (enviar resultado por email? finalizar ranking, calcular valor premiação)
    # atualizar hcp bluegolf e quarta nobre (botão na aba jogadores?)
    # aba config, incluir slope, tees de saída, categorias
    # Ranking
    #
    return render_template('torneio_atual.html',
                           title='Players',
                           name=current_user.name, t=t, p=p, torneio=torneio, logged_in=True)


@app.route('/torneio/apuracao/<id>/<jogador>', methods=["GET", "POST"])
@login_required
def add_res_jog(id, jogador):
    inscrito = Torneio_atual.query.filter_by(
        jogador=jogador, torneio_id=id).first()
    print(inscrito.jogador, inscrito.hcp)
    return render_template('add_resultado_jog.html',
                           title='Players', id=id, jogador=jogador, inscrito=inscrito,
                           name=current_user.name, logged_in=True)


@ app.route('/jogadores', methods=["GET", "POST"])
@ login_required
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


@ app.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@ app.route('/config')
@ login_required
def config():

    return render_template('config.html')


if __name__ == "__main__":
    app.run(debug=True)
