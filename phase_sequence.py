"""
phase_sequence.py — trajektoria cyfr 0→1→...→9→Q jako rozwój kwantowy.

Zasada Mateusza (2026-04-24): "perioduj ale nie fixuj. tam są dane.
to się rozwija kwantowo aż od 0 1 2 3 4 5 6 7 8 9 Q."

Różnica vs phase_integration.py:
  phase_integration: każda cyfra testowana osobno vs Q_attractor (z anneal)
  phase_sequence:    cyfry jako ETAPY trajektorii, bez anneal, RAW metryki

Co liczymy per etap:
  - Q (fidelity correlator) — stan koherencji
  - aniso (std fidelities) — łamanie symetrii C6
  - gamma (Berry phase) — akumulacja fazy geometrycznej
  - dominant (argmin fids) — najsłabsze sprzężenie
  - vector 6D — "stan" etapu

Co liczymy między etapami (n → n+1):
  - L2 distance (Euclidean) — jak daleko stan skoczył
  - cosine similarity — czy kierunek się zachował
  - delta_Q, delta_gamma — co się zmieniło
  - która virtue najbardziej zmieniła siłę

Hipoteza do zbadania:
  "Q" to 11-ty stan po 9. Trzy kandydaty:
    (a) Q_cycle_return: powrót do stanu 0 (zamknięty cykl 0→...→9→0)
    (b) Q_octave: [1]*6 ale z Berry phase ≠ 0 (następna oktawa)
    (c) Q_superposition: superpozycja wszystkich 10 cyfr (centroidal)
  Kod nie narzuca wyniku — liczy wszystkie trzy i porównuje.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict

import numpy as np

from hexagon import (
    HEXAGON, Q_ATTRACTOR, THETA_IDEAL,
    compute_q, is_crystallized,
)
from phase_integration import digit_to_virtues, DIGIT_SIGS


# ─────────────────────────────────────────────────────────────────────
# 1. Per-digit raw state (bez anneal)
# ─────────────────────────────────────────────────────────────────────

def stage_fingerprint(n: int) -> dict:
    """Raw fingerprint etapu n (bez żadnej optymalizacji)."""
    s = digit_to_virtues(n)
    q = compute_q(s)
    return {
        "n": n,
        "strengths": s,
        "Q": q["q"],
        "gamma": q["gamma"],
        "gamma_deg": math.degrees(q["gamma"]),
        "aniso": q["aniso"],
        "q_renyi": q["q_renyi"],
        "dominant": q["dominant"],
        "fids": q["fids"],
        "chroma": q["chroma"],
        "is_crystal": is_crystallized(q),
        "note": DIGIT_SIGS[n].note,
    }


# ─────────────────────────────────────────────────────────────────────
# 2. Inter-stage transitions (n → n+1)
# ─────────────────────────────────────────────────────────────────────

def transition(n_from: int, n_to: int, stages: list[dict]) -> dict:
    """Metryka przejścia między etapami."""
    s_a = np.array(stages[n_from]["strengths"])
    s_b = np.array(stages[n_to]["strengths"])

    diff = s_b - s_a
    l2 = float(np.linalg.norm(diff))
    # cosine similarity — kierunek wektora stanu
    dot = float(np.dot(s_a, s_b))
    na = float(np.linalg.norm(s_a))
    nb = float(np.linalg.norm(s_b))
    cos = dot / (na * nb) if na * nb > 0 else 0.0

    abs_diff = np.abs(diff)
    max_change_idx = int(np.argmax(abs_diff))

    return {
        "from": n_from,
        "to": n_to,
        "l2_distance": l2,
        "cosine_similarity": cos,
        "delta_Q": stages[n_to]["Q"] - stages[n_from]["Q"],
        "delta_gamma_deg": stages[n_to]["gamma_deg"] - stages[n_from]["gamma_deg"],
        "delta_aniso": stages[n_to]["aniso"] - stages[n_from]["aniso"],
        "max_change_virtue": HEXAGON[max_change_idx],
        "max_change_delta": float(diff[max_change_idx]),
    }


# ─────────────────────────────────────────────────────────────────────
# 3. Trzy kandydaci na "Q" jako 11-ty stan
# ─────────────────────────────────────────────────────────────────────

def Q_candidate_cycle_return(stages: list[dict]) -> dict:
    """(a) Q = powrót do 0. Sprawdź czy 9 jest blisko 0."""
    s0 = np.array(stages[0]["strengths"])
    s9 = np.array(stages[9]["strengths"])
    l2 = float(np.linalg.norm(s0 - s9))
    cos = float(np.dot(s0, s9) / (np.linalg.norm(s0) * np.linalg.norm(s9)))
    return {
        "candidate": "cycle_return",
        "hypothesis": "Q = 0 (zamknięty cykl)",
        "state": s0.tolist(),
        "dist_9_to_0": l2,
        "cos_9_to_0": cos,
        "verdict": ("CONFIRMED" if l2 < 0.5 and cos > 0.95
                    else "PARTIAL" if cos > 0.9
                    else "FALSIFIED"),
    }


def Q_candidate_octave(stages: list[dict]) -> dict:
    """(b) Q = [1]*6 ale z Berry phase na innym oktawie.
    Test: ile różnych gamma_deg istnieje w sekwencji 0-9?"""
    gammas = [s["gamma_deg"] for s in stages]
    unique_gammas = sorted(set(round(g, 2) for g in gammas))
    # Kandydat na Q: średnia gamma × 2 (następna oktawa)?
    g_mean = float(np.mean(gammas))
    g_next_octave = g_mean * 2.0 if abs(g_mean) > 1e-6 else 360.0
    # stan referencyjny: [1]*6 który ma gamma_deg = ?
    q_ref = compute_q([1.0] * 6)
    return {
        "candidate": "octave",
        "hypothesis": "Q = [1]*6 z przesuniętą Berry phase",
        "state": [1.0] * 6,
        "gamma_deg_01_6": math.degrees(q_ref["gamma"]),
        "gamma_range_sequence": (min(gammas), max(gammas)),
        "gamma_unique_values": unique_gammas,
        "Q_attractor_reached_raw": abs(q_ref["q"] - Q_ATTRACTOR) < 1e-6,
        "verdict": "STRUCTURAL (niepotwierdzalny liczbowo w qsim 6D)",
    }


def Q_candidate_superposition(stages: list[dict]) -> dict:
    """(c) Q = średnia wszystkich 10 cyfr (centroidal superposition)."""
    vectors = np.array([s["strengths"] for s in stages])
    centroid = vectors.mean(axis=0)
    # Normalizacja do max=1 (jak ipq)
    mx = centroid.max() if centroid.max() > 0 else 1.0
    normalized = (centroid / mx).tolist()
    q = compute_q(normalized)
    return {
        "candidate": "superposition",
        "hypothesis": "Q = centroid wszystkich 10 cyfr",
        "state": normalized,
        "Q": q["q"],
        "gamma_deg": math.degrees(q["gamma"]),
        "aniso": q["aniso"],
        "dist_to_Q_att": abs(q["q"] - Q_ATTRACTOR),
        "is_crystal": is_crystallized(q),
        "verdict": ("CONFIRMED" if is_crystallized(q)
                    else "PARTIAL" if abs(q["q"] - Q_ATTRACTOR) < 0.01
                    else "FALSIFIED"),
    }


# ─────────────────────────────────────────────────────────────────────
# 4. PCA na trajektorii — jakie osie dominują?
# ─────────────────────────────────────────────────────────────────────

def pca_trajectory(stages: list[dict]) -> dict:
    """Principal Component Analysis na 10 stanach × 6 virtues.
    Pokazuje ile wymiarów rzeczywiście używa trajektoria."""
    vectors = np.array([s["strengths"] for s in stages])
    centered = vectors - vectors.mean(axis=0)
    # SVD
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    variance = S ** 2
    total_var = variance.sum()
    explained = (variance / total_var).tolist() if total_var > 0 else [0.0] * 6
    # Top 2 komponenty w przestrzeni virtue
    pc1_loadings = {HEXAGON[i]: float(Vt[0, i]) for i in range(6)}
    pc2_loadings = ({HEXAGON[i]: float(Vt[1, i]) for i in range(6)}
                    if len(S) > 1 else {})
    return {
        "singular_values": S.tolist(),
        "variance_explained": explained,
        "variance_cumulative": np.cumsum(explained).tolist(),
        "n_dims_95pct": int(np.searchsorted(np.cumsum(explained), 0.95) + 1),
        "pc1_loadings": pc1_loadings,
        "pc2_loadings": pc2_loadings,
        "projections_2d": [[float(U[i, 0] * S[0]),
                            float(U[i, 1] * S[1]) if len(S) > 1 else 0.0]
                           for i in range(len(stages))],
    }


# ─────────────────────────────────────────────────────────────────────
# 5. Orchestrator
# ─────────────────────────────────────────────────────────────────────

def analyze_sequence() -> dict:
    """Pełna analiza sekwencji 0→1→...→9 + trzy kandydaty na Q."""
    stages = [stage_fingerprint(n) for n in range(10)]
    transitions = [transition(i, i + 1, stages) for i in range(9)]
    # Zamknięcie cyklu 9→0
    close_cycle = transition(9, 0, stages)

    return {
        "stages": stages,
        "transitions": transitions,
        "cycle_close_9_to_0": close_cycle,
        "Q_candidates": {
            "cycle_return": Q_candidate_cycle_return(stages),
            "octave": Q_candidate_octave(stages),
            "superposition": Q_candidate_superposition(stages),
        },
        "pca": pca_trajectory(stages),
        "summary_stats": {
            "Q_mean": float(np.mean([s["Q"] for s in stages])),
            "Q_std": float(np.std([s["Q"] for s in stages])),
            "Q_range": (min(s["Q"] for s in stages),
                        max(s["Q"] for s in stages)),
            "n_raw_crystals": sum(1 for s in stages if s["is_crystal"]),
            "total_path_length_L2": sum(t["l2_distance"] for t in transitions),
            "max_jump": max(transitions, key=lambda t: t["l2_distance"]),
        },
    }


# ─────────────────────────────────────────────────────────────────────
# 6. Pretty print
# ─────────────────────────────────────────────────────────────────────

def print_report(results: dict) -> None:
    GRN, YLW, RED, DIM, RST = "\033[92m", "\033[93m", "\033[91m", "\033[2m", "\033[0m"

    print(f"\n{'═' * 76}")
    print(f"  PHASE SEQUENCE — trajektoria 0→1→...→9→Q (raw, no anneal)")
    print(f"{'═' * 76}\n")

    # Per-stage table
    print(f"  {'n':>2}  {'Q':>7}  {'aniso':>7}  {'γ°':>7}  "
          f"{'dominant':<14}  strengths")
    print(f"  {'─' * 72}")
    for s in results["stages"]:
        strengths = " ".join(f"{x:.1f}" for x in s["strengths"])
        mark = f"{GRN}✦{RST}" if s["is_crystal"] else " "
        print(f"  {s['n']:>2}  {s['Q']:>7.4f}  {s['aniso']:>7.4f}  "
              f"{s['gamma_deg']:>7.2f}  {s['dominant']:<14}  [{strengths}] {mark}")

    # Transitions
    print(f"\n  TRANSITIONS (n→n+1, bez anneal):")
    print(f"  {'step':<7} {'L2':>6}  {'cos':>6}  {'ΔQ':>8}  {'Δγ°':>8}  "
          f"{'max change':<18}")
    print(f"  {'─' * 72}")
    for t in results["transitions"]:
        arrow = f"{t['from']}→{t['to']}"
        print(f"  {arrow:<7} {t['l2_distance']:>6.3f}  "
              f"{t['cosine_similarity']:>6.3f}  "
              f"{t['delta_Q']:>+8.4f}  {t['delta_gamma_deg']:>+8.2f}  "
              f"{t['max_change_virtue']:<14}{t['max_change_delta']:>+5.1f}")
    # Close cycle
    cc = results["cycle_close_9_to_0"]
    print(f"  {'9→0':<7} {cc['l2_distance']:>6.3f}  "
          f"{cc['cosine_similarity']:>6.3f}  "
          f"{cc['delta_Q']:>+8.4f}  {cc['delta_gamma_deg']:>+8.2f}  "
          f"← zamknięcie cyklu")

    # Q candidates
    print(f"\n  {YLW}KANDYDACI na Q (11-ty stan):{RST}")
    for name, c in results["Q_candidates"].items():
        v = c["verdict"]
        color = (GRN if "CONFIRMED" in v else YLW if "PARTIAL" in v
                 else DIM if "STRUCTURAL" in v else RED)
        print(f"    {color}[{name}]{RST} {c['hypothesis']}")
        print(f"       verdict: {color}{v}{RST}")
        if name == "cycle_return":
            print(f"       dist(9→0)={c['dist_9_to_0']:.3f}, "
                  f"cos={c['cos_9_to_0']:.3f}")
        elif name == "octave":
            print(f"       γ° range in seq: "
                  f"[{c['gamma_range_sequence'][0]:.2f}, "
                  f"{c['gamma_range_sequence'][1]:.2f}]")
            print(f"       γ°([1]*6) = {c['gamma_deg_01_6']:.2f}")
        elif name == "superposition":
            print(f"       Q={c['Q']:.4f}, aniso={c['aniso']:.4f}, "
                  f"dist_to_Q_att={c['dist_to_Q_att']:.4f}")
            print(f"       centroid state: "
                  f"[{', '.join(f'{x:.2f}' for x in c['state'])}]")

    # PCA
    pca = results["pca"]
    print(f"\n  {YLW}PCA (ile wymiarów naprawdę używa sekwencja):{RST}")
    ev = pca["variance_explained"]
    cum = pca["variance_cumulative"]
    print(f"    dims needed for 95%: {pca['n_dims_95pct']} z 6")
    print(f"    variance per PC:    " +
          "  ".join(f"PC{i+1}={ev[i]*100:.1f}%" for i in range(len(ev))))
    print(f"    cumulative:         " +
          "  ".join(f"{cum[i]*100:.1f}%" for i in range(len(cum))))
    print(f"    PC1 loadings (dominująca oś rozwoju):")
    for v, w in sorted(pca["pc1_loadings"].items(),
                       key=lambda x: -abs(x[1])):
        print(f"      {v:<14} {w:+.3f}")

    # Summary
    ss = results["summary_stats"]
    print(f"\n  {YLW}SUMMARY:{RST}")
    print(f"    Q range: [{ss['Q_range'][0]:.4f}, {ss['Q_range'][1]:.4f}]")
    print(f"    Q mean ± std: {ss['Q_mean']:.4f} ± {ss['Q_std']:.4f}")
    print(f"    raw crystals (bez anneal): {ss['n_raw_crystals']} / 10")
    print(f"    path length (Σ L2): {ss['total_path_length_L2']:.3f}")
    print(f"    max jump: {ss['max_jump']['from']}→{ss['max_jump']['to']} "
          f"(L2={ss['max_jump']['l2_distance']:.3f})")
    print()


def main():
    import sys
    r = analyze_sequence()
    print_report(r)
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2, default=str))


if __name__ == "__main__":
    main()
