from datetime import date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Reclamacao(db.Model):
    __tablename__ = "dataset_finguard_desafio_3"

    id = db.Column(db.String(20), primary_key=True)
    data_reclamacao = db.Column(db.Date, nullable=False, default=date.today)
    canal = db.Column(db.String(50), nullable=False)
    texto_reclamacao = db.Column(db.Text, nullable=False)
    produto = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Aberta")

    # Campos preenchidos pelo agente classificador
    categoria = db.Column(db.String(50), nullable=True)
    sentimento = db.Column(db.String(20), nullable=True)
    urgencia = db.Column(db.String(20), nullable=True)
    resumo = db.Column(db.Text, nullable=True)
    acoes_imediatas = db.Column(db.Text, nullable=True)
    responsavel = db.Column(db.String(50), nullable=True)
    prazo_resposta = db.Column(db.String(50), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "data_reclamacao": self.data_reclamacao.isoformat() if self.data_reclamacao else None,
            "canal": self.canal,
            "texto_reclamacao": self.texto_reclamacao,
            "produto": self.produto,
            "status": self.status,
            "categoria": self.categoria,
            "sentimento": self.sentimento,
            "urgencia": self.urgencia,
            "resumo": self.resumo,
            "acoes_imediatas": self.acoes_imediatas,
            "responsavel": self.responsavel,
            "prazo_resposta": self.prazo_resposta,
        }
