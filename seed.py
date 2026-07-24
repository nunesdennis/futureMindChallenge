"""
Popula o banco de dados com os registros do CSV dataset_finguard_desafio_3.
Execute uma vez: python seed.py
"""

import csv
import os
import sys
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "requirements - documentation", "dataset_finguard_desafio_3.csv")
# Fallback para nome com sufixo numérico
if not os.path.exists(CSV_PATH):
    CSV_PATH = os.path.join(BASE_DIR, "requirements - documentation", "dataset_finguard_desafio_3 (3).csv")

sys.path.insert(0, BASE_DIR)

from app import app
from models import Reclamacao, db


def _parse_date(valor: str):
    if not valor:
        return date.today()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(valor.strip(), fmt).date()
        except ValueError:
            continue
    return date.today()


def seed():
    with app.app_context():
        db.create_all()

        if not os.path.exists(CSV_PATH):
            print(f"ERRO: CSV não encontrado em:\n  {CSV_PATH}")
            sys.exit(1)

        inseridos = 0
        ignorados = 0

        with open(CSV_PATH, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rec_id = row.get("id", "").strip()
                if not rec_id:
                    continue

                existente = db.session.get(Reclamacao, rec_id)
                if existente:
                    ignorados += 1
                    continue

                rec = Reclamacao(
                    id=rec_id,
                    data_reclamacao=_parse_date(row.get("data_reclamacao", "")),
                    canal=row.get("canal", "").strip() or "SAC",
                    texto_reclamacao=row.get("texto_reclamacao", "").strip(),
                    produto=row.get("produto", "").strip() or None,
                    status=row.get("status", "Aberta").strip() or "Aberta",
                )
                db.session.add(rec)
                inseridos += 1

        db.session.commit()
        total = db.session.query(Reclamacao).count()
        print(f"Seed concluído: {inseridos} inseridos, {ignorados} já existiam.")
        print(f"Total na tabela dataset_finguard_desafio_3: {total} registros.")


if __name__ == "__main__":
    seed()
