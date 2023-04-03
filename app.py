from datetime import datetime
from flask import Flask, render_template, request, jsonify, make_response
from flask_swagger_ui import get_swaggerui_blueprint
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import validar

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dados.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
app.app_context().push()


class UsuarioParceiro(db.Model):
    uuid = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    dataCriacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    dataAtualizacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"Parceiro('{self.nome}', '{self.cnpj}', '{self.email}')"


class RetornaTodosParceiros(Resource):
    def get(self):
        parceiros = UsuarioParceiro.query.all()
        listaParceiros = []
        for parceiro in parceiros:
            dadosParceiro = {
                "uuid": parceiro.uuid,
                "nome": parceiro.nome,
                "cnpj": parceiro.cnpj,
                "email": parceiro.email,
                "dataCriacao": parceiro.dataCriacao.strftime("%m/%d/%Y"),
                "dataAtualizacao": parceiro.dataAtualizacao.strftime("%m/%d/%Y"),
            }
            listaParceiros.append(dadosParceiro)

        return {"parceiros": listaParceiros}, 200


class RetornarParceiro(Resource):
    def get(self, uuid):
        parceiro = UsuarioParceiro.query.get(uuid)
        if not parceiro:
            return make_response(
                jsonify(
                    {
                        "status": "Ocorreu um erro.",
                        "message": "Parceiro não encontrado.",
                    }
                ),
                404,
            )

        dadosParceiro = {
            "uuid": parceiro.uuid,
            "nome": parceiro.nome,
            "cnpj": parceiro.cnpj,
            "email": parceiro.email,
            "dataCriacao": parceiro.dataCriacao.strftime("%m/%d/%Y"),
            "dataAtualizacao": parceiro.dataAtualizacao.strftime("%m/%d/%Y"),
        }

        return {"parceiro": dadosParceiro}, 200


class RetornaUltimosParceiros(Resource):
    def get(self):
        parceiros = UsuarioParceiro.query.order_by(
            UsuarioParceiro.dataCriacao.desc()
        ).limit(10)
        listaParceiros = []
        for parceiro in parceiros:
            dadosParceiro = {
                "uuid": parceiro.uuid,
                "nome": parceiro.nome,
                "cnpj": parceiro.cnpj,
                "email": parceiro.email,
                "dataCriacao": parceiro.dataCriacao.strftime("%m/%d/%Y"),
                "dataAtualizacao": parceiro.dataAtualizacao.strftime("%m/%d/%Y"),
            }
            listaParceiros.append(dadosParceiro)

        return {"parceiros": listaParceiros}, 200


class AdicionaParceiro(Resource):
    def post(self):
        if not request.is_json:
            return {
                "status": "Ocorreu um erro.",
                "message": "A solicitação deve ser JSON.",
            }, 400

        dados = request.get_json()

        dados["cnpj"] = validar.ValidaCnpj(dados["cnpj"])
        if dados["cnpj"] is None:
            return make_response(
                jsonify(
                    {
                        "status": "Ocorreu um erro.",
                        "message": "O Cnpj informado é inválido.",
                    }
                ),
                400,
            )

        if UsuarioParceiro.query.filter_by(cnpj=dados["cnpj"]).first():
            return make_response(
                jsonify({"status": "Ocorreu um erro.", "message": "O CNPJ já existe."}),
                400,
            )
        if UsuarioParceiro.query.filter_by(nome=dados["nome"]).first():
            return make_response(
                jsonify({"status": "Ocorreu um erro.", "message": "O nome já existe."}),
                400,
            )
        if validar.validaEmail(dados["email"]) is False:
            return make_response(
                jsonify(
                    {
                        "status": "Ocorreu um erro.",
                        "message": "O Email informado é inválido.",
                    }
                ),
                400,
            )
        if UsuarioParceiro.query.filter_by(email=dados["email"]).first():
            return make_response(
                jsonify(
                    {"status": "Ocorreu um erro.", "message": "O Email já existe."}
                ),
                400,
            )

        novoParceiro = UsuarioParceiro(
            nome=dados["nome"],
            cnpj=dados["cnpj"],
            email=dados["email"],
            senha=dados["senha"],
        )
        db.session.add(novoParceiro)
        db.session.commit()
        return make_response(
            jsonify(
                {
                    "status": "Sucesso.",
                    "message": "Parceiro adicionado com sucesso.",
                    "parceiro": dados,
                }
            ),
            201,
        )


class AtualizaParceiro(Resource):
    def put(self, uuid):
        if not request.is_json:
            return {
                "status": "Ocorreu um erro.",
                "message": "A solicitação deve ser JSON.",
            }, 400

        parceiro = UsuarioParceiro.query.get(uuid)

        if not parceiro:
            return make_response(
                jsonify(
                    {
                        "status": "Ocorreu um erro.",
                        "message": "Parceiro não encontrado.",
                    }
                ),
                404,
            )

        dados = request.get_json()

        dados["cnpj"] = validar.ValidaCnpj(dados["cnpj"])
        if dados["cnpj"] is None:
            return make_response(
                jsonify(
                    {
                        "status": "Ocorreu um erro.",
                        "message": "O CNPJ informado é inválido.",
                    }
                ),
                400,
            )

        if (
            parceiro.cnpj != dados["cnpj"]
            and UsuarioParceiro.query.filter_by(cnpj=dados["cnpj"]).first()
        ):
            return make_response(
                jsonify({"status": "Ocorreu um erro.", "message": "O CNPJ já existe."}),
                400,
            )

        if (
            parceiro.nome != dados["nome"]
            and UsuarioParceiro.query.filter_by(nome=dados["nome"]).first()
        ):
            return make_response(
                jsonify({"status": "Ocorreu um erro.", "message": "Nome já existe."}),
                400,
            )

        if parceiro.email != dados["email"]:
            if validar.validaEmail(dados["email"]) is False:
                return make_response(
                    jsonify(
                        {"status": "Ocorreu um erro.", "message": "O Email é inválido."}
                    ),
                    400,
                )
            if UsuarioParceiro.query.filter_by(email=dados["email"]).first():
                return make_response(
                    jsonify(
                        {"status": "Ocorreu um erro.", "message": "O Email já existe."}
                    ),
                    400,
                )

        parceiro.nome = dados["nome"]
        parceiro.cnpj = dados["cnpj"]
        parceiro.email = dados["email"]
        parceiro.senha = dados["senha"]
        db.session.commit()
        return make_response(
            jsonify(
                {
                    "status": "Sucesso.",
                    "message": "Parceiro atualizado com sucesso.",
                    "parceiro": dados,
                }
            ),
            200,
        )


class DeletaParceiro(Resource):
    def delete(self, uuid):
        parceiro = UsuarioParceiro.query.get(uuid)

        if not parceiro:
            return make_response(
                jsonify(
                    {
                        "status": "Ocorreu um erro.",
                        "message": "Parceiro não encontrado.",
                    }
                ),
                404,
            )

        db.session.delete(parceiro)
        db.session.commit()
        return make_response(
            jsonify(
                {"status": "Sucesso.", "message": "Parceiro deletado com sucesso."}
            ),
            200,
        )


class SWAG(Resource):
    def get(self):
        import json

        with open("swagger.json", "r") as file:
            swag = json.load(file)
        return jsonify(swag)


api.add_resource(SWAG, "/swagger")
api.add_resource(RetornaTodosParceiros, "/parceiros")
api.add_resource(RetornarParceiro, "/parceiros/<uuid>")
api.add_resource(RetornaUltimosParceiros, "/ultimos-parceiros")
api.add_resource(AdicionaParceiro, "/parceiros")
api.add_resource(AtualizaParceiro, "/atualizar-parceiro/<uuid>")
api.add_resource(DeletaParceiro, "/deletar-parceiro/<uuid>")

SWAGGER_URL = "/api/docs"
API_URL = "/swagger"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "My API",
    },
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


class Planta(db.Model):
    uuid = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capacidadeMaxima = db.Column(db.Integer, nullable=False)
    dataCriacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    dataAtualizacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"Planta('{self.nome}', '{self.cep}', '{self.latitude}', '{self.longitude}', '{self.capacidadeMaxima}')"


class RetornaTodasPlantas(Resource):
    def get(self):
        plantas = Planta.query.all()
        listaDePlantas = []
        for planta in plantas:
            dadosPlanta = {
                "uuid": planta.uuid,
                "nome": planta.nome,
                "cep": planta.cep,
                "latitude": planta.latitude,
                "longitude": planta.latitude,
                "capacidadeMaxima": planta.capacidadeMaxima,
                "dataCriacao": planta.dataCriacao.strftime("%m/%d/%Y"),
                "dataAtualizacao": planta.dataAtualizacao.strftime("%m/%d/%Y"),
            }
            listaDePlantas.append(dadosPlanta)

        return {"plantas": listaDePlantas}, 200


class RetornaPlanta(Resource):
    def get(self, uuid):
        planta = Planta.query.get(uuid)
        if not planta:
            return make_response(
                jsonify(
                    {"status": "Ocorreu um erro.", "message": "Planta não encontrada."}
                ),
                404,
            )

        dadosPlanta = {
            "uuid": planta.uuid,
            "nome": planta.nome,
            "cep": planta.cep,
            "latitude": planta.latitude,
            "longitude": planta.latitude,
            "capacidadeMaxima": planta.capacidadeMaxima,
            "dataCriacao": planta.dataCriacao.strftime("%m/%d/%Y"),
            "dataAtualizacao": planta.dataAtualizacao.strftime("%m/%d/%Y"),
        }

        return {"planta": dadosPlanta}, 200


class RetornaTopPlantas(Resource):
    def get(self):
        plantas = Planta.query.order_by(Planta.capacidadeMaxima.desc()).limit(10)
        listaPlantas = []
        for planta in plantas:
            dadosPlanta = {
                "uuid": planta.uuid,
                "nome": planta.nome,
                "cep": planta.cep,
                "latitude": planta.latitude,
                "longitude": planta.longitude,
                "capacidadeMaxima": planta.capacidadeMaxima,
                "dataCriacao": planta.dataCriacao.strftime("%m/%d/%Y"),
                "dataAtualizacao": planta.dataAtualizacao.strftime("%m/%d/%Y"),
            }
            listaPlantas.append(dadosPlanta)

        return {"plantas": listaPlantas}, 200


class AdicionaPlanta(Resource):
    def post(self):
        if not request.is_json:
            return {
                "status": "Ocorreu um erro.",
                "message": "A solicitação deve ser JSON.",
            }, 400

        dados = request.get_json()

        dados["cep"] = validar.validaCep(dados["cep"])
        if dados["cep"] is None:
            return make_response(
                jsonify({"status": "Ocorreu um erro.", "message": "CEP inválido."}), 400
            )

        if Planta.query.filter_by(nome=dados["nome"]).first():
            return make_response(
                jsonify({"status": "Ocorreu um erro.", "message": "Nome já existe."}),
                400,
            )

        novaPlanta = Planta(
            nome=dados["nome"],
            cep=dados["cep"],
            latitude=dados["latitude"],
            longitude=dados["longitude"],
            capacidadeMaxima=dados["capacidadeMaxima"],
        )
        db.session.add(novaPlanta)
        db.session.commit()
        return make_response(
            jsonify(
                {
                    "status": "Sucesso.",
                    "message": "Planta adicionada com sucesso.",
                    "planta": dados,
                }
            ),
            201,
        )


class AtualizaPanta(Resource):
    def put(self, uuid):
        if not request.is_json:
            return {
                "status": "Ocorreu um erro.",
                "message": "A solicitação deve ser JSON.",
            }, 400

        planta = Planta.query.get(uuid)

        if not planta:
            return make_response(
                jsonify(
                    {"status": "Ocorreu um erro.", "message": "Planta não encontrada."}
                ),
                404,
            )

        dados = request.get_json()

        dados["cep"] = validar.validaCep(dados["cep"])
        if dados["cep"] is None:
            return make_response(
                jsonify({"status": "Ocorreu um erro.", "message": "CEP Invalido."}), 400
            )
        if (
            dados["nome"] != planta.nome
            and Planta.query.filter_by(nome=dados["nome"]).first()
        ):
            return make_response(
                jsonify({"status": "Ocorreu um erro.", "message": "Nome já existe."}),
                400,
            )

        planta.nome = dados["nome"]
        planta.cep = dados["cep"]
        planta.latitude = dados["latitude"]
        planta.longitude = dados["longitude"]
        planta.capacidadeMaxima = dados["capacidadeMaxima"]
        db.session.commit()
        return make_response(
            jsonify(
                {
                    "status": "Sucesso.",
                    "message": "Planta atualizada com sucesso!",
                    "planta": dados,
                }
            ),
            200,
        )


class ApagarPlanta(Resource):
    def delete(self, uuid):
        planta = Planta.query.get(uuid)

        if not planta:
            return make_response(jsonify({"message": "Planta não encontrada."}), 404)

        db.session.delete(planta)
        db.session.commit()
        return make_response(
            jsonify({"message": "Planta foi deletada com sucesso!"}),
            200,
        )


api.add_resource(RetornaTodasPlantas, "/plantas")
api.add_resource(RetornaPlanta, "/plantas/<uuid>")
api.add_resource(RetornaTopPlantas, "/plantas-maior-capacidade")
api.add_resource(AdicionaPlanta, "/plantas")
api.add_resource(AtualizaPanta, "/atualizar-planta/<uuid>")
api.add_resource(ApagarPlanta, "/deletar-planta/<uuid>")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
