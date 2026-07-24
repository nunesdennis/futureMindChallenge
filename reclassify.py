"""
Reclassifica todas as reclamações já salvas no banco usando classifier.classificar.
Execute: python reclassify.py
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import app
from classifier import classificar
from models import Reclamacao, db

# Workers paralelos — equilíbrio entre velocidade e rate limit da API
WORKERS = 4
COMMIT_EVERY = 10


def _classificar_uma(rec_id: str, texto: str, canal: str, produto: str | None) -> tuple[str, dict | None, str | None]:
    try:
        resultado = classificar(texto, canal, produto)
        return rec_id, resultado, None
    except Exception as exc:
        return rec_id, None, str(exc)


def reclassify(apenas_sem_classificacao: bool = True) -> None:
    with app.app_context():
        query = Reclamacao.query.order_by(Reclamacao.id)
        if apenas_sem_classificacao:
            query = query.filter(
                (Reclamacao.categoria.is_(None)) | (Reclamacao.categoria == "")
            )

        reclamações = query.all()
        total = len(reclamações)
        if total == 0:
            print("Nenhuma reclamação para reclassificar.")
            return

        print(f"Reclassificando {total} reclamação(ões) com {WORKERS} workers...", flush=True)
        t0 = time.time()
        ok = 0
        falhas = 0
        pendentes = {
            r.id: (r.texto_reclamacao, r.canal, r.produto) for r in reclamações
        }

        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = {
                executor.submit(_classificar_uma, rid, texto, canal, produto): rid
                for rid, (texto, canal, produto) in pendentes.items()
            }

            processados = 0
            for future in as_completed(futures):
                rec_id, resultado, erro = future.result()
                processados += 1

                rec = db.session.get(Reclamacao, rec_id)
                if rec is None:
                    falhas += 1
                    print(f"[{processados}/{total}] {rec_id}: registro não encontrado", flush=True)
                    continue

                if erro or not resultado:
                    falhas += 1
                    print(f"[{processados}/{total}] {rec_id}: ERRO — {erro}", flush=True)
                    continue

                rec.categoria = resultado.get("categoria")
                rec.sentimento = resultado.get("sentimento")
                rec.urgencia = resultado.get("urgencia")
                rec.resumo = resultado.get("resumo")
                rec.acoes_imediatas = resultado.get("acoes_imediatas")
                rec.responsavel = resultado.get("responsavel")
                rec.prazo_resposta = resultado.get("prazo_resposta")
                # Produto identificado pelo classificador (mantém o original se vier vazio)
                if resultado.get("produto"):
                    rec.produto = resultado["produto"]
                ok += 1

                if ok % COMMIT_EVERY == 0:
                    db.session.commit()

                elapsed = time.time() - t0
                rate = processados / elapsed if elapsed else 0
                eta = (total - processados) / rate if rate else 0
                print(
                    f"[{processados}/{total}] {rec_id}: "
                    f"{rec.urgencia}/{rec.categoria} "
                    f"(ok={ok} falhas={falhas} ~{eta:.0f}s restantes)",
                    flush=True,
                )

            db.session.commit()

        elapsed = time.time() - t0
        print(f"\nConcluído em {elapsed:.1f}s: {ok} atualizados, {falhas} falhas.", flush=True)


if __name__ == "__main__":
    reclassify(apenas_sem_classificacao=True)
