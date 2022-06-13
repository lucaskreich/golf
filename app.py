import json
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("home.html")


@app.route("/golf/costao-golf/add-player", methods=["GET", "POST"])
def add_player():
    with open("player.json", "r") as data_file:
        data = json.load(data_file)

    if request.method == "POST":
        name = request.form.get("name")
        hcp = request.form.get("hcp")
        hcp_id = request.form.get("hcp_id")
        cat = request.form.get("cat")

        new_data = {
            name:
            {"hcp": hcp, "hcp_id": hcp_id, "cat": cat}
        }
        with open("player.json", "r") as data_file:
            data = json.load(data_file)

            data.update(new_data)
        with open("player.json", "w") as data_file:
            json.dump(data, data_file, indent=4)

        return render_template("cadastro_jogador.html", data=data)
    return render_template("cadastro_jogador.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)
