"""
Servidor Flask - Clipping de Imprensa - Renan Santos
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, abort, render_template

from clipping import PESSOA, buscar_noticias

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", "clippings.db")
HORA_AGENDAMENTO = int(os.environ.get("HORA_CLIPPING", "8"))


# ── Banco de dados ────────────────────────────────────────────────────────────

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clippings (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                data      TEXT    UNIQUE NOT NULL,
                total     INTEGER NOT NULL DEFAULT 0,
                fontes    INTEGER NOT NULL DEFAULT 0,
                noticias  TEXT    NOT NULL,
                criado_em TEXT    NOT NULL
            )
        """)


# ── Geração de clipping ───────────────────────────────────────────────────────

def gerar_clipping():
    hoje = date.today().isoformat()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Gerando clipping {hoje}...")

    noticias = buscar_noticias()
    total = sum(len(v) for v in noticias.values())

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO clippings (data, total, fontes, noticias, criado_em)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(data) DO UPDATE SET
                total     = excluded.total,
                fontes    = excluded.fontes,
                noticias  = excluded.noticias,
                criado_em = excluded.criado_em
            """,
            (hoje, total, len(noticias), json.dumps(noticias, ensure_ascii=False),
             datetime.now().isoformat()),
        )
    print(f"  → {total} notícia(s) em {len(noticias)} fonte(s) salvas.")


# ── Rotas ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT data, total, fontes, criado_em FROM clippings ORDER BY data DESC"
        ).fetchall()
    return render_template("index.html", clippings=rows, pessoa=PESSOA)


@app.route("/clipping/<data>")
def ver_clipping(data):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM clippings WHERE data = ?", (data,)
        ).fetchone()
    if not row:
        abort(404)
    noticias = json.loads(row["noticias"])
    return render_template("clipping.html", row=row, noticias=noticias, pessoa=PESSOA)


@app.route("/gerar", methods=["POST"])
def forcar_geracao():
    gerar_clipping()
    return {"ok": True, "data": date.today().isoformat()}


@app.route("/health")
def health():
    return {"status": "ok"}


# ── Inicialização ─────────────────────────────────────────────────────────────

def gerar_se_necessario():
    hoje = date.today().isoformat()
    with get_db() as conn:
        existe = conn.execute(
            "SELECT 1 FROM clippings WHERE data = ?", (hoje,)
        ).fetchone()
    if not existe:
        gerar_clipping()


def main():
    init_db()

    # Agenda geração diária + dispara busca inicial em background
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(gerar_clipping, "cron", hour=HORA_AGENDAMENTO, minute=0)
    scheduler.add_job(gerar_se_necessario, "date")  # roda imediatamente em thread
    scheduler.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
