from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import os
from sqlalchemy.sql import func, select, and_
from hcp_index import calc_hcp_qn, get_index

app = Flask(__name__)

app.config['SECRET_KEY'] = 'randomkeybestkey'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "sqlite:///database.db").replace("s://", "sql://", 1)
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
    clube_id = db.Column(db.Integer)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    permission = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    # clube_id = db.Column(db.Integer)


class Campo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    tee_saida_1 = db.Column(db.String(100))
    slope_1 = db.Column(db.Integer)
    course_rating_1 = db.Column(db.Float)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clube_id = db.Column(db.Integer)
    name = db.Column(db.String(1000))
    email = db.Column(db.String(100))
    hcp_id = db.Column(db.String(100))
    hcp_index = db.Column(db.Float)
    # Hcp Quarta Nobre, modificado qndo joga abaixo do par
    hcp_qn = db.Column(db.Integer)
    # Quantas etapas faltam jogar com o handicap alterado
    rest_hcp_qn = db.Column(db.Integer)
    pt_ranking = db.Column(db.Float)
    cat = db.Column(db.String(10))
    juv = db.Column(db.String(10))
    senior = db.Column(db.String(10))


class Torneios(db.Model):
    clube_id = db.Column(db.Integer)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    date = db.Column(db.String(100))
    type = db.Column(db.String(100))
    cat = db.Column(db.String(100))
    tees_saida = db.Column(db.String(100))
    encerrado = db.Column(db.String(100))


class Torneio_atual(db.Model):
    clube_id = db.Column(db.Integer)
    id = db.Column(db.Integer, primary_key=True)
    torneio_id = db.Column(db.String(100))
    jogador_id = db.Column(db.String(100))
    jogador = db.Column(db.String(100))
    tee_saida = db.Column(db.String(100))
    hcp = db.Column(db.Integer)
    cat = db.Column(db.String(100))
    juv = db.Column(db.String(100))
    senior = db.Column(db.String(100))
    b_saida = db.Column(db.String(100))
    pago = db.Column(db.String(100))
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


class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clube_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    player_id = db.Column(db.String(100))
    ranking_id = db.Column(db.String(100))
    pontos = db.Column(db.Integer)
    torneio_id = db.Column(db.String(1000))


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

        db.session.commit()
        rows = Torneios.query.order_by(Torneios.date.desc()).all()

        return render_template('novo_torneio.html',
                               title='Tourneio',
                               rows=rows, name=current_user.name, logged_in=True)
    rows = Torneios.query.order_by(Torneios.date.desc()).all()
    return render_template('novo_torneio.html',
                           title='Tourneio',
                           rows=rows, name=current_user.name, logged_in=True)


@app.route('/torneio/apuracao/<id>', methods=["GET", "POST"])
@login_required
def torneio_atual(id):
    t = Torneios.query.filter_by(id=id).first()

    if t.encerrado == "sim":
        return resultado_apuracao(id)
    if request.method == "POST":

        inscrito_list = request.form.getlist('checkbox_jogadores')
        # pega lista de ids selecionadas no checkbox
        for i in inscrito_list:

            inscrito = Torneio_atual.query.filter_by(torneio_id=id,
                                                     jogador_id=i).first()
            # transforma id no nome do jogador
            jogador_name = Player.query.filter_by(hcp_id=i).first()
            if jogador_name.rest_hcp_qn == 0:
                hcp = calc_hcp_qn(jogador_name.hcp_index)
            else:
                hcp = jogador_name.hcp_qn

            player = Torneio_atual(
                jogador_id=i,
                jogador=jogador_name.name,
                torneio_id=id,
                pago=request.form.get(i+'_pago'),
                b_saida=request.form.get(i+'_b_saida'),
                hcp=hcp

            )
            if inscrito:

                if request.form.get(i+'_hcp') != "":
                    inscrito.hcp = request.form.get(i+'_hcp')
                if request.form.get(i+'_b_saida') != "":
                    inscrito.b_saida = request.form.get(i+'_b_saida')
                if request.form.get(i+'_pago') != "":
                    inscrito.pago = request.form.get(i+'_pago')
                db.session.commit()

                # Editar Pago
            else:
                db.session.add(player)
                db.session.commit()

    t = Torneios.query.filter_by(id=id).first()
    torneio = Torneio_atual.query.filter_by(
        torneio_id=id).order_by(Torneio_atual.b_saida.asc(), Torneio_atual.jogador).all()

    p = Player.query.filter()

    # checkmark qndo resultado do jogador já tiver sido adicionado( ou mudança de cor)
    # tela separada, resultado do torneio
    # botão finalizar torneio (enviar resultado por email? finalizar ranking, calcular valor premiação)
    # atualizar hcp bluegolf e quarta nobre (botão na aba jogadores?)
    # aba config, incluir slope, tees de saída, categorias
    # Ranking
    # na aba editar jogador, pode desclassificar o jogador e desinscrever
    # ver erro, clicar no jogar sem buracos cadastrados e clicar em cadastrar sem preencher tudo da erro

    return render_template('torneio_atual.html',
                           title='Players',
                           name=current_user.name, t=t, p=p, torneio=torneio, logged_in=True)


@app.route('/torneio/apuracao/<id>/<jogador_id>', methods=["GET", "POST"])
@login_required
def add_res_jog(id, jogador_id):
    inscrito = Torneio_atual.query.filter_by(
        jogador_id=jogador_id, torneio_id=id).first()
    t = Torneios.query.filter_by(id=id).first()
    torneio = Torneio_atual.query.filter_by(torneio_id=id).all()
    p = Player.query.all()
    if request.method == "POST":
        if request.form.get('desclassificado') == "desclassificado":
            # verificar para manter box checado se já tiver sido desclassificado

            inscrito.total_gross = inscrito.total_net = inscrito.v1_gross = inscrito.v2_gross = inscrito.v2_net = 999

            db.session.commit()
            return render_template('torneio_atual.html',
                                   title='Players',
                                   name=current_user.name, t=t, p=p, torneio=torneio, logged_in=True)
        # Consertar essa merda
        if request.form.get('hcp') != "":
            inscrito.hcp = request.form.get('hcp')
        if request.form.get('b_saida') != "":
            inscrito.b_saida = request.form.get('b_saida')
        if request.form.get('pago') != "":
            inscrito.pago = request.form.get('pago')
        if request.form.get('b1') != "":
            inscrito.b1 = request.form.get('b1')
        if request.form.get('b2') != "":
            inscrito.b2 = request.form.get('b2')
        if request.form.get('b3') != "":
            inscrito.b3 = request.form.get('b3')
        if request.form.get('b4') != "":
            inscrito.b4 = request.form.get('b4')
        if request.form.get('b5') != "":
            inscrito.b5 = request.form.get('b5')
        if request.form.get('b6') != "":
            inscrito.b6 = request.form.get('b6')
        if request.form.get('b7') != "":
            inscrito.b7 = request.form.get('b7')
        if request.form.get('b8') != "":
            inscrito.b8 = request.form.get('b8')
        if request.form.get('b9') != "":
            inscrito.b9 = request.form.get('b9')
        if request.form.get('b10') != "":
            inscrito.b10 = request.form.get('b10')
        if request.form.get('b11') != "":
            inscrito.b11 = request.form.get('b11')
        if request.form.get('b12') != "":
            inscrito.b12 = request.form.get('b12')
        if request.form.get('b13') != "":
            inscrito.b13 = request.form.get('b13')
        if request.form.get('b14') != "":
            inscrito.b14 = request.form.get('b14')
        if request.form.get('b15') != "":
            inscrito.b15 = request.form.get('b15')
        if request.form.get('b16') != "":
            inscrito.b16 = request.form.get('b16')
        if request.form.get('b17') != "":
            inscrito.b17 = request.form.get('b17')
        if request.form.get('b18') != "":
            inscrito.b18 = request.form.get('b18')
        db.session.commit()

        inscrito.v1_gross = inscrito.b1 + inscrito.b2 + inscrito.b3 + inscrito.b4 + \
            inscrito.b5 + inscrito.b6 + inscrito.b7 + inscrito.b8 + inscrito.b9

        inscrito.v2_gross = inscrito.b10 + inscrito.b11 + inscrito.b12 + inscrito.b13 + \
            inscrito.b14 + inscrito.b15 + inscrito.b16 + inscrito.b17 + inscrito.b18

        inscrito.total_gross = inscrito.v1_gross + inscrito.v2_gross
        inscrito.total_net = inscrito.total_gross - int(inscrito.hcp)
        inscrito.v2_net = inscrito.v2_gross - int(inscrito.hcp)/2
        inscrito.ult_6b_net = (inscrito.v2_gross - inscrito.b10 -
                               inscrito.b11 - inscrito.b12) - (int(inscrito.hcp)/3)
        inscrito.ult_3b_net = (inscrito.b16 + inscrito.b17 +
                               inscrito.b18) - (int(inscrito.hcp)/6)
        inscrito.ult_b_net = inscrito.b18 - (int(inscrito.hcp)/18)
        db.session.commit()
        return render_template('torneio_atual.html',
                               title='Players',
                               name=current_user.name, t=t, p=p, torneio=torneio, logged_in=True)

    db.session.commit()

    return render_template('add_resultado_jog.html',
                           title='Players', id=id, jogador_id=jogador_id, inscrito=inscrito,
                           name=current_user.name, logged_in=True)


@ app.route('/jogadores', methods=["GET", "POST"])
@ login_required
def jogadores():
    if request.method == "POST":
        if request.form.get('hcp_index') == "":
            # update from bluegolf
            index = get_index(request.form.get('hcp_id'))

        else:
            index = request.form.get('hcp_index')
        new_player = Player(
            email=request.form.get('email'),
            name=request.form.get('name'),
            hcp_id=request.form.get('hcp_id'),
            hcp_index=index,
            rest_hcp_qn=0,
            cat=request.form.get('cat'),
            juv=request.form.get('juv'),
            senior=request.form.get('senior')
        )
        player = Player.query.filter_by(hcp_id=new_player.hcp_id).first()
        if not player:

            db.session.add(new_player)
            db.session.commit()

        else:

            player.name = request.form.get('name')
            player.email = request.form.get('email')
            player.hcp_index = request.form.get('hcp_index')
            player.cat = request.form.get('cat')
            player.juv = request.form.get('juv')
            player.senior = request.form.get('senior')
            db.session.commit()
        # conferir se ranking id e clube id tbm são iguais
        new_ranking = Ranking(

            clube_id=1,
            player_id=request.form.get('hcp_id'),
            name=request.form.get('name'),
            ranking_id=1,
            pontos=0

        )
        rkg = Ranking.query.filter_by(player_id=new_ranking.player_id).first()
        if not rkg:
            db.session.add(new_ranking)
            db.session.commit()

        rows = Player.query.all()

        return render_template('jogadores.html',
                               title='Players',
                               rows=rows, name=current_user.name, logged_in=True)
    rows = Player.query.all()
    return render_template('jogadores.html',
                           title='Players',
                           rows=rows, name=current_user.name, logged_in=True)


@ app.route('/torneio/apuracao/<id>/resultado')
def resultado_apuracao(id):

    t = Torneios.query.filter_by(id=id).first()
    torneio = Torneio_atual.query.filter_by(
        torneio_id=id).order_by(Torneio_atual.total_net, Torneio_atual.v2_net, Torneio_atual.ult_6b_net, Torneio_atual.ult_3b_net, Torneio_atual.ult_b_net).all()

    return render_template('resultado_apuracao.html',
                           title='resultado',
                           t=t, torneio=torneio)


@ app.route('/torneio/apuracao/<id>/ranking')
def add_to_ranking(id):
    ##FINALIZA O TORNEIO##
    t = Torneios.query.filter_by(id=id).first()

    if t.encerrado == "sim":
        return torneio_atual(id)
    torneio = Torneio_atual.query.filter_by(torneio_id=id).order_by(
        Torneio_atual.total_net, Torneio_atual.v2_net, Torneio_atual.ult_6b_net, Torneio_atual.ult_3b_net, Torneio_atual.ult_b_net).all()
    for i in torneio:
        if not i.total_gross:
            return torneio_atual(id)
    pontos_list = [25, 20, 15, 12, 10, 8, 6, 4, 2, 1]
    a = 0
    # regras valor =
    # até 4 jog = primeiro - 100%
    # 5 a 10 jog = primeiro 70, segundo 30
    # acima 10 = 60, 30,10

    # Contar qntos Jo
    qnt_jog = Torneio_atual.query.filter_by(torneio_id=id).count()
    print(qnt_jog)
    insc = 40
    insc_liq = 35
    if qnt_jog < 5:
        valor_list = [1]
    elif qnt_jog >= 5 and qnt_jog <= 10:
        valor_list = [.7, .3]
    else:
        valor_list = [.6, .3, .1]

    for i in torneio:
        p = Player.query.filter_by(hcp_id=i.jogador_id).first()

        if a <= 9:
            if a <= len(valor_list)-1:
                i.ganhos = insc_liq*qnt_jog * valor_list[a]
            else:
                i.ganhos = 0
            if i.total_gross == 999:
                i.ganhos = 0
                i.pt_rkg = 0
                a += 1
                if p.rest_hcp_qn != 0:
                    p.rest_hcp_qn -= 1
                continue
            net = int(i.total_net)
            if int(net) < 72:
                p.rest_hcp_qn = 4
                p.hcp_qn = int(i.total_gross) - 72
                i.pt_rkg = pontos_list[a] + (72-net)*.5
            elif int(net) >= 72:
                i.pt_rkg = pontos_list[a]
                if p.rest_hcp_qn != 0:
                    p.rest_hcp_qn -= 1
            else:
                i.pt_rkg = 0
                if p.rest_hcp_qn != 0:
                    p.rest_hcp_qn -= 1

            a += 1
            r = Ranking.query.filter_by(player_id=i.jogador_id).first()
            r.pontos += i.pt_rkg

    t = Torneios.query.filter_by(id=id).first()
    t.encerrado = "sim"
    db.session.commit()
    # adicionar ranking_id a Torneio_atual e filtrar por ele

    return torneio_atual(id)


@ app.route('/torneio/apuracao/ranking')
def view_ranking():
    rows = Ranking.query.filter(
        Ranking.pontos > 0).order_by(Ranking.pontos.desc()).all()
    p = Player.query.all()
    return render_template('ranking.html', rows=rows, p=p)


@ app.route("/torneio/apuracao/<id>/<jogador_id>/delete")
@ login_required
def desinscrever(id, jogador_id):

    jogador = Torneio_atual.query.filter_by(
        torneio_id=id, jogador_id=jogador_id).first()
    db.session.delete(jogador)
    db.session.commit()

    return torneio_atual(id)


@ app.route("/jogadores/<jogador_id>/delete")
@ login_required
def del_jogador(jogador_id):

    jogador = Player.query.filter_by(
        hcp_id=jogador_id).first()
    db.session.delete(jogador)
    db.session.commit()

    return jogadores()


@ app.route('/logout')
@ login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@ app.route('/config', methods=["GET", "POST"])
@ login_required
def config():
    if request.method == "POST":
        new_campo = Campo(
            name="Costão",
            tee_saida_1=request.form.get('tee'),
            slope_1=request.form.get('slope'),
            course_rating_1=request.form.get("courserating"))
        campo = Campo.query.first()
        if not campo:

            db.session.add(new_campo)
            db.session.commit()

        else:

            campo.tee_saida_1 = request.form.get('tee'),
            campo.slope_1 = request.form.get('slope'),
            campo.course_rating_1 = request.form.get("courserating")

            db.session.commit()

    return render_template('config.html', name=current_user.name, logged_in=True)


if __name__ == "__main__":
    app.run(debug=True)
