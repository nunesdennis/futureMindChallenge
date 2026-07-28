import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import func

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


@app.route("/dashboard")
def dashboard():
    total = Reclamacao.query.count()

    criticas = Reclamacao.query.filter(Reclamacao.urgencia == "Crítica").count()

    sla_risco = Reclamacao.query.filter(
        Reclamacao.urgencia.in_(["Crítica", "Alta"]),
        Reclamacao.status == "Aberta",
    ).count()

    resolvidas = Reclamacao.query.filter(Reclamacao.status == "Resolvida").count()
    taxa_resolucao = round((resolvidas / total * 100) if total else 0)

    por_canal = (
        db.session.query(Reclamacao.canal, func.count(Reclamacao.id))
        .group_by(Reclamacao.canal)
        .all()
    )
    canal_labels = [r[0] for r in por_canal]
    canal_valores = [r[1] for r in por_canal]

    por_produto = (
        db.session.query(Reclamacao.produto, func.count(Reclamacao.id))
        .filter(Reclamacao.produto.isnot(None))
        .group_by(Reclamacao.produto)
        .order_by(func.count(Reclamacao.id).desc())
        .limit(3)
        .all()
    )
    produto_labels = [r[0] for r in por_produto]
    produto_valores = [r[1] for r in por_produto]

    pendentes = (
        Reclamacao.query.filter(Reclamacao.status.in_(["Aberta", "Em análise"]))
        .order_by(Reclamacao.urgencia.desc(), Reclamacao.data_reclamacao.asc())
        .limit(10)
        .all()
    )

    urgencia_pct_critica = (
        db.session.query(func.count(Reclamacao.id))
        .filter(Reclamacao.urgencia == "Crítica")
        .scalar() or 0
    )
    urgencia_pct_alta = (
        db.session.query(func.count(Reclamacao.id))
        .filter(Reclamacao.urgencia == "Alta")
        .scalar() or 0
    )
    urgencia_pct_media = (
        db.session.query(func.count(Reclamacao.id))
        .filter(Reclamacao.urgencia == "Média")
        .scalar() or 0
    )
    urgencia_pct_baixa = (
        db.session.query(func.count(Reclamacao.id))
        .filter(Reclamacao.urgencia == "Baixa")
        .scalar() or 0
    )

    return render_template(
        "dashboard.html",
        total=total,
        criticas=criticas,
        sla_risco=sla_risco,
        taxa_resolucao=taxa_resolucao,
        canal_labels=canal_labels,
        canal_valores=canal_valores,
        produto_labels=produto_labels,
        produto_valores=produto_valores,
        pendentes=pendentes,
        urgencia_critica=urgencia_pct_critica,
        urgencia_alta=urgencia_pct_alta,
        urgencia_media=urgencia_pct_media,
        urgencia_baixa=urgencia_pct_baixa,
    )


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
