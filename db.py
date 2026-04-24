"""
DuckDB — efemerys crystallizacji.
"""

import duckdb
import json
from pathlib import Path

DB_PATH = Path.home() / ".qsim" / "qsim.duckdb"

SCHEMA = """
CREATE SEQUENCE IF NOT EXISTS seq_cryst START 1;
CREATE TABLE IF NOT EXISTS crystallizations (
    id            BIGINT    DEFAULT nextval('seq_cryst') PRIMARY KEY,
    ts            TIMESTAMP DEFAULT current_timestamp,
    question      TEXT,
    mode          TEXT,
    status        TEXT,
    ipq_qual      TEXT,
    Q             FLOAT,
    gamma         FLOAT,
    aniso         FLOAT,
    Q_renyi       FLOAT,
    dominant      TEXT,
    chroma        TEXT,
    strengths     JSON,
    fids          JSON,
    t_ms          FLOAT,
    confidence    FLOAT,
    c6_ok         BOOLEAN,
    sch_freq      FLOAT,
    sch_kp        FLOAT,
    sch_source    TEXT,
    sch_sigma_mod FLOAT,
    sch_local_h   FLOAT,
    sch_weather   TEXT,
    sch_wx_mod    FLOAT,
    pl_source     TEXT,
    pl_strengths  JSON,
    pl_dominant   TEXT,
    S_total_exp   FLOAT
);
"""

_ALTER_SCHUMANN = [
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS sch_freq      FLOAT",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS sch_kp        FLOAT",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS sch_source    TEXT",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS sch_sigma_mod FLOAT",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS sch_local_h   FLOAT",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS sch_weather   TEXT",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS sch_wx_mod    FLOAT",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS pl_source     TEXT",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS pl_strengths  JSON",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS pl_dominant   TEXT",
    "ALTER TABLE crystallizations ADD COLUMN IF NOT EXISTS S_total_exp   FLOAT",
]


def get_conn() -> duckdb.DuckDBPyConnection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    conn.execute(SCHEMA)
    for alt in _ALTER_SCHUMANN:
        try:
            conn.execute(alt)
        except Exception:
            pass  # kolumna już istnieje
    return conn


def insert(conn: duckdb.DuckDBPyConnection, row: dict) -> int:
    sch = row.get("schumann") or {}
    pl = row.get("planets") or {}
    pl_strs = pl.get("strengths")
    pl_dom = None
    if pl_strs:
        import numpy as _np
        from hexagon import HEXAGON as _H
        pl_dom = _H[int(_np.argmax(pl_strs))]

    conn.execute("""
        INSERT INTO crystallizations
            (question, mode, status, ipq_qual, Q, gamma, aniso, Q_renyi,
             dominant, chroma, strengths, fids, t_ms, confidence, c6_ok,
             sch_freq, sch_kp, sch_source, sch_sigma_mod, sch_local_h,
             sch_weather, sch_wx_mod,
             pl_source, pl_strengths, pl_dominant, S_total_exp)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        RETURNING id
    """, [
        row["question"], row["mode"], row["status"], row["ipq_qual"],
        row["Q"], row["gamma"], row["aniso"], row["Q_renyi"],
        row["dominant"], row["chroma"],
        json.dumps(row["strengths"]), json.dumps(row["fids"]),
        row["t_ms"], row["confidence"], row["c6_ok"],
        sch.get("freq"), sch.get("kp"), sch.get("source"),
        sch.get("sigma_mod"), sch.get("local_hour"),
        sch.get("weather_label"), sch.get("weather_mod"),
        pl.get("source"), json.dumps(pl_strs) if pl_strs else None, pl_dom,
        row.get("S_total_experimental"),
    ])
    return conn.fetchone()[0]


def last_n(conn: duckdb.DuckDBPyConnection, n: int = 5) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM crystallizations ORDER BY id DESC LIMIT ?", [n]
    ).fetchall()
    cols = [d[0] for d in conn.description]
    return [dict(zip(cols, r)) for r in rows]


def stats(conn: duckdb.DuckDBPyConnection) -> dict:
    row = conn.execute(
        "SELECT COUNT(*), AVG(Q), AVG(aniso) FROM crystallizations"
    ).fetchone()
    return {"count": row[0], "avg_q": row[1], "avg_aniso": row[2]}
