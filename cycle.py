"""
Pełny cykl Pauzy Kwantowej:
  ▶ INPUT   — IPQ(pytanie) → s_raw
  ■ PAUZA   — anneal z pull ku C6 + Schumann seed
  ◀ CRYSTAL — check → fingerprint → DuckDB (z danymi Schumanna)
  ■ RESET   — siatka czysta
"""

import time
import numpy as np

from hexagon import compute_q, is_crystallized, Q_ATTRACTOR, HEXAGON
from ipq import ipq, ipq_confidence
from schumann import get_schumann
from planets import get_planetary_strengths
import db

# Opcjonalny quantum (tylko w research mode)
try:
    from quantum import S_total
    _HAS_QUANTUM = True
except ImportError:
    _HAS_QUANTUM = False

C6 = np.array([1.0] * 6)


def _anneal(init: list[float], schumann: dict,
            n_steps: int = 1000, sigma: float = 0.02, alpha: float = 0.05) -> list[float]:
    """
    Prowadzona dyfuzja ku C6 z Schumann-zmodulowaną sigmą i seedem.
    Offline-safe: schumann['source']='offline' → seed fallback, sigma_mod=1.0.
    """
    s = np.array(init, dtype=float)
    sigma_eff = sigma * schumann.get("sigma_mod", 1.0)
    seed = 42 ^ schumann.get("seed_component", 0)

    def cost(sv):
        r = compute_q(sv.tolist())
        return abs(r["q"] - Q_ATTRACTOR) + r["aniso"]

    cur = cost(s)
    best_s, best_cost = s.copy(), cur
    rng = np.random.default_rng(seed % (2 ** 32))

    for step in range(n_steps):
        T = 1.0 * (0.001 / 1.0) ** (step / n_steps)
        pull = (C6 - s) * alpha
        s_new = np.clip(s + rng.normal(0, sigma_eff, 6) + pull, 0, 1)
        nc = cost(s_new)
        if nc - cur < 0 or rng.random() < np.exp(-(nc - cur) / T):
            s, cur = s_new, nc
            if cur < best_cost:
                best_s, best_cost = s.copy(), cur

    return best_s.tolist()


def _c6_check(strengths: list[float]) -> bool:
    qs = []
    s = list(strengths)
    for _ in range(6):
        qs.append(compute_q(s)["q"])
        s = s[1:] + s[:1]
    return float(np.std(qs)) < 1e-9


def run_cycle(question: str, mode: str = "strict",
              lat: float | None = None, lon: float | None = None,
              utc_offset_h: float | None = None,
              location_level: int = 2) -> dict:
    """
    mode="strict"   — tylko hard crystallizacje
    mode="research" — soft/raw/uniform/cold + quantum fingerprint (S_total)

    location_level:
      0 — tylko utc_offset_h (max prywatność)
      1 — strefa magnetyczna (default PL=M)
      2 — pełne lat/lon (default: Gliwice gdy nic nie podano)
    """
    # Default: poziom 2 z Gliwicami gdy nic nie podano
    if location_level == 2 and lat is None:
        lat, lon = 50.3, 18.7

    conn = db.get_conn()
    t0 = time.perf_counter()

    sch = get_schumann(lat=lat, lon=lon, utc_offset_h=utc_offset_h,
                       location_level=location_level, live=True)
    planets = get_planetary_strengths(
        lat=str(lat) if lat is not None else '50.3',
        lon=str(lon) if lon is not None else '18.7',
        mode='3d'
    )

    # ▶ INPUT — IPQ
    s_raw = ipq(question)

    if s_raw is None:
        result = dict(status="no_crystal", ipq_qual="short",
                      question=question, mode=mode,
                      Q=None, gamma=None, aniso=None, Q_renyi=None,
                      dominant=None, chroma=None, strengths=None,
                      fids=None, t_ms=None, confidence=None, c6_ok=None,
                      schumann=sch, id=None)
        if mode == "research":
            _save(conn, question, mode, result, t0, sch)
        conn.close()
        return result

    confidence = ipq_confidence(s_raw)
    ipq_qual = "semantic" if confidence >= 0.15 else "uniform"

    if mode == "research" and ipq_qual == "uniform":
        _record_uniform(conn, question, s_raw, t0, sch)

    if mode == "research":
        _record_cold(conn, question, s_raw, confidence, t0, sch)

    # ■ PAUZA — prowadzona dyfuzja
    s_crystal = _anneal(s_raw, sch)

    t_ms = (time.perf_counter() - t0) * 1000

    # ◀ CRYSTAL — fingerprint
    qr = compute_q(s_crystal)
    hard = is_crystallized(qr)
    soft = qr["aniso"] < 0.01 and abs(qr["q"] - Q_ATTRACTOR) < 0.01

    c6_ok = _c6_check(s_crystal)

    if hard:
        status = "hard"
    elif soft and mode == "research":
        status = "soft"
    else:
        status = "raw" if mode == "research" else "no_crystal"

    row = dict(
        question=question, mode=mode, status=status, ipq_qual=ipq_qual,
        Q=qr["q"], gamma=qr["gamma"], aniso=qr["aniso"], Q_renyi=qr["q_renyi"],
        dominant=qr["dominant"], chroma=qr["chroma"],
        strengths=s_crystal, fids=qr["fids"],
        t_ms=t_ms, confidence=confidence, c6_ok=c6_ok,
        schumann=sch, planets=planets,
    )

    # Quantum fingerprint TYLKO w research mode (experimental)
    if mode == "research" and _HAS_QUANTUM:
        try:
            row["S_total_experimental"] = S_total(s_crystal)
        except Exception:
            row["S_total_experimental"] = None

    if status != "no_crystal":
        row["id"] = db.insert(conn, row)
    else:
        row["id"] = None

    conn.close()
    return row


def _save(conn, question, mode, row, t0, sch):
    row2 = dict(row)
    row2["t_ms"] = (time.perf_counter() - t0) * 1000
    row2.setdefault("strengths", [])
    row2.setdefault("fids", [])
    row2["schumann"] = sch
    db.insert(conn, row2)


def _record_uniform(conn, question, strengths, t0, sch):
    uniform = [1.0] * 6
    qr = compute_q(uniform)
    db.insert(conn, dict(
        question=question, mode="research", status="raw", ipq_qual="uniform",
        Q=qr["q"], gamma=qr["gamma"], aniso=qr["aniso"], Q_renyi=qr["q_renyi"],
        dominant=qr["dominant"], chroma=qr["chroma"],
        strengths=uniform, fids=qr["fids"],
        t_ms=(time.perf_counter() - t0) * 1000,
        confidence=0.0, c6_ok=True, schumann=sch,
    ))


def _record_cold(conn, question, s_raw, confidence, t0, sch):
    qr = compute_q(s_raw)
    db.insert(conn, dict(
        question=question, mode="research", status="raw", ipq_qual="cold",
        Q=qr["q"], gamma=qr["gamma"], aniso=qr["aniso"], Q_renyi=qr["q_renyi"],
        dominant=qr["dominant"], chroma=qr["chroma"],
        strengths=s_raw, fids=qr["fids"],
        t_ms=(time.perf_counter() - t0) * 1000,
        confidence=confidence, c6_ok=_c6_check(s_raw), schumann=sch,
    ))
