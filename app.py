import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from classifier import classificar
from models import Reclamacao, db

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finguard.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY", "finguard-dev-secret")

db.init_app(app)

CANAIS = ["SAC", "Ouvidoria", "Banco Central", "Redes Sociais", "Reclame Aqui"]
PRODUTOS = ["Cartão de Crédito", "Conta Corrente", "Empréstimo", "Investimentos", "Seguros"]
STATUS_OPCOES = ["Aberta", "Em análise", "Resolvida"]

URGENCIA_COR = {
    "Baixa": "#28a745",
    "Média": "#fd7e14",
    "Alta": "#dc3545",
    "Crítica": "#6f0000",
}


def _gerar_id() -> str:
    ano = date.today().year
    ultimo = (
        db.session.query(Reclamacao)
        .filter(Reclamacao.id.like(f"REC-{ano}-%"))
        .order_by(Reclamacao.id.desc())
        .first()
    )
    if ultimo:
        seq = int(ultimo.id.split("-")[-1]) + 1
    else:
        seq = 1
    return f"REC-{ano}-{seq:05d}"


@app.route("/")
def index():
    pagina = request.args.get("pagina", 1, type=int)
    canal_filtro = request.args.get("canal", "")
    urgencia_filtro = request.args.get("urgencia", "")
    status_filtro = request.args.get("status", "")

    query = Reclamacao.query.order_by(Reclamacao.data_reclamacao.desc(), Reclamacao.id.desc())

    if canal_filtro:
        query = query.filter(Reclamacao.canal == canal_filtro)
    if urgencia_filtro:
        query = query.filter(Reclamacao.urgencia == urgencia_filtro)
    if status_filtro:
        query = query.filter(Reclamacao.status == status_filtro)

    paginacao = query.paginate(page=pagina, per_page=20, error_out=False)

    return render_template(
        "index.html",
        reclamacoes=paginacao.items,
        paginacao=paginacao,
        canais=CANAIS,
        urgencia_cor=URGENCIA_COR,
        canal_filtro=canal_filtro,
        urgencia_filtro=urgencia_filtro,
        status_filtro=status_filtro,
        status_opcoes=STATUS_OPCOES,
    )


@app.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        canal = request.form.get("canal", "").strip()
        produto = request.form.get("produto", "").strip()
        texto = request.form.get("texto_reclamacao", "").strip()

        if not canal or not texto:
            flash("Canal e texto da reclamação são obrigatórios.", "erro")
            return render_template("nova.html", canais=CANAIS, produtos=PRODUTOS)

        data_str = request.form.get("data_reclamacao", "").strip()
        try:
            data_rec = date.fromisoformat(data_str) if data_str else date.today()
        except ValueError:
            data_rec = date.today()

        rec = Reclamacao(
            id=_gerar_id(),
            data_reclamacao=data_rec,
            canal=canal,
            produto=produto or None,
            texto_reclamacao=texto,
            status="Aberta",
        )
        db.session.add(rec)
        db.session.flush()

        multiplas_ocorrencias = request.form.get("primeira_ocorrencia") == "nao"

        try:
            resultado = classificar(texto, canal, produto or None, multiplas_ocorrencias=multiplas_ocorrencias)
            rec.categoria = resultado.get("categoria")
            rec.sentimento = resultado.get("sentimento")
            rec.urgencia = resultado.get("urgencia")
            rec.resumo = resultado.get("resumo")
            rec.acoes_imediatas = resultado.get("acoes_imediatas")
            rec.responsavel = resultado.get("responsavel")
            rec.prazo_resposta = resultado.get("prazo_resposta")
        except Exception:
            pass

        db.session.commit()
        flash(f"Reclamação {rec.id} registrada com sucesso!", "sucesso")
        return redirect(url_for("detalhe", rec_id=rec.id))

    return render_template("nova.html", canais=CANAIS, produtos=PRODUTOS)


@app.route("/reclamacao/<rec_id>")
def detalhe(rec_id):
    rec = db.get_or_404(Reclamacao, rec_id)
    return render_template("detalhe.html", rec=rec, urgencia_cor=URGENCIA_COR)


@app.route("/reclamacao/<rec_id>/apagar", methods=["POST"])
def apagar(rec_id):
    rec = db.get_or_404(Reclamacao, rec_id)
    db.session.delete(rec)
    db.session.commit()
    flash(f"Reclamação {rec_id} apagada.", "sucesso")
    return redirect(url_for("index"))


@app.route("/reclamacao/<rec_id>/status", methods=["POST"])
def atualizar_status(rec_id):
    rec = db.get_or_404(Reclamacao, rec_id)
    novo_status = request.form.get("status")
    if novo_status in STATUS_OPCOES:
        rec.status = novo_status
        db.session.commit()
        flash("Status atualizado.", "sucesso")
    return redirect(url_for("detalhe", rec_id=rec_id))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
