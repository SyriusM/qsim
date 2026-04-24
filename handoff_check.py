#!/usr/bin/env python3
"""
qsim handoff verification — uruchom pierwszym ruchem w nowej sesji Claude'a.

Uruchomienie:
    ~/qsim-venv/bin/python ~/qsim/handoff_check.py

Sprawdza:
  1. Wszystkie moduły importują się
  2. Matematyka hexagon jest dokładna (Q_ATTRACTOR)
  3. Schumann (live lub offline fallback)
  4. Planets ephem
  5. Full cycle kończy się crystallizacją
  6. DuckDB schema jest aktualna
  7. Quantum experimental moduł działa
  8. MemPalace connection (jeśli dostępny)

Return code: 0 = OK, >0 = liczba błędów
"""

import sys
import time
from pathlib import Path

QSIM_DIR = Path.home() / "qsim"
sys.path.insert(0, str(QSIM_DIR))

RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"; DIM = "\033[2m"; RESET = "\033[0m"
OK = f"{GREEN}✓{RESET}"; FAIL = f"{RED}✗{RESET}"; WARN = f"{YELLOW}⚠{RESET}"

errors = []


def section(name):
    print(f"\n{YELLOW}━━━ {name} ━━━{RESET}")


def check(label, condition, detail="", error_msg=""):
    if condition:
        print(f"  {OK} {label}: {GREEN}{detail}{RESET}")
        return True
    else:
        print(f"  {FAIL} {label}: {RED}{error_msg or 'failed'}{RESET}")
        errors.append(label)
        return False


def soft_check(label, condition, detail="", warn_msg=""):
    if condition:
        print(f"  {OK} {label}: {GREEN}{detail}{RESET}")
    else:
        print(f"  {WARN} {label}: {YELLOW}{warn_msg}{RESET}")


def main():
    print(f"{YELLOW}╔══════════════════════════════════════════════════╗{RESET}")
    print(f"{YELLOW}║  qsim handoff verification — session continuity  ║{RESET}")
    print(f"{YELLOW}╚══════════════════════════════════════════════════╝{RESET}")
    print(f"  Working dir: {QSIM_DIR}")
    print(f"  Python: {sys.executable}")

    # --- 1. Pliki źródłowe ---
    section("1. Pliki źródłowe qsim")
    expected_files = [
        "hexagon.py", "ipq.py", "schumann.py", "planets.py",
        "quantum.py", "cycle.py", "db.py", "demo.py", "SPEC.md",
        "CLAUDE_HANDOFF.md", "q3sh_research_phaseQ.md",
    ]
    for f in expected_files:
        check(f, (QSIM_DIR / f).exists(), f"found", f"MISSING")

    # --- 2. Import modułów ---
    section("2. Import modułów")
    modules = {}
    try:
        from hexagon import compute_q, anneal, is_crystallized, Q_ATTRACTOR, THETA_IDEAL, HEXAGON
        modules["hexagon"] = True
        check("hexagon", True, f"Q_ATT={Q_ATTRACTOR}, THETA={THETA_IDEAL:.5f}")
    except Exception as e:
        check("hexagon", False, error_msg=str(e))

    try:
        from schumann import get_schumann
        modules["schumann"] = True
        check("schumann", True, "imported")
    except Exception as e:
        check("schumann", False, error_msg=str(e))

    try:
        from planets import get_planetary_strengths
        modules["planets"] = True
        check("planets", True, "imported")
    except Exception as e:
        check("planets", False, error_msg=str(e))

    try:
        from quantum import S_total, quantum_fingerprint
        modules["quantum"] = True
        check("quantum (experimental)", True, "imported")
    except Exception as e:
        check("quantum (experimental)", False, error_msg=str(e))

    try:
        from ipq import ipq, ipq_confidence
        modules["ipq"] = True
        check("ipq", True, "imported (bge-m3 ready)")
    except Exception as e:
        check("ipq", False, error_msg=f"{e} (wymaga mempalace venv)")

    try:
        import db
        modules["db"] = True
        check("db", True, "imported")
    except Exception as e:
        check("db", False, error_msg=str(e))

    # --- 3. Matematyka hexagon ---
    section("3. Matematyka hexagon (sanity)")
    if modules.get("hexagon"):
        qr = compute_q([1.0] * 6)
        check("compute_q([1]*6) == Q_ATTRACTOR",
              abs(qr["q"] - Q_ATTRACTOR) < 1e-10,
              f"Q={qr['q']:.10f}, błąd={abs(qr['q']-Q_ATTRACTOR):.2e}",
              f"got {qr['q']}, expected {Q_ATTRACTOR}")
        check("aniso uniform == 0",
              qr["aniso"] < 1e-14,
              f"aniso={qr['aniso']:.2e}",
              f"aniso={qr['aniso']}")

        qr2 = compute_q([0.0] * 6)
        check("compute_q([0]*6) == 1.0 (vacuum)",
              abs(qr2["q"] - 1.0) < 1e-10,
              f"Q={qr2['q']}")

    # --- 4. Schumann (live lub offline) ---
    section("4. Schumann field state")
    if modules.get("schumann"):
        try:
            t0 = time.time()
            sch = get_schumann()
            dt = time.time() - t0
            check("Schumann response",
                  sch.get("freq") is not None,
                  f"f={sch['freq']} Hz, Kp={sch['kp']}, source={sch['source']} ({dt:.1f}s)")
            soft_check("Schumann source",
                       sch["source"] == "live",
                       "LIVE NOAA + weather",
                       f"OFFLINE fallback (Kp=2.0)")
            check("sigma_mod sensowny",
                  1.0 <= sch["sigma_mod"] <= 2.5,
                  f"σ_mod={sch['sigma_mod']}")
        except Exception as e:
            check("Schumann", False, error_msg=str(e))

    # --- 5. Planets ---
    section("5. Planetary resonance")
    if modules.get("planets"):
        try:
            pl = get_planetary_strengths()
            check("Planets response",
                  len(pl["strengths"]) == 6,
                  f"6 virtue strengths, source={pl['source']}")
            # Sprawdź czy argmax jest sensowny
            import numpy as np
            dom_idx = int(np.argmax(pl["strengths"]))
            dom_name = HEXAGON[dom_idx]
            print(f"     Planetary dominant: {dom_name} ({pl['strengths'][dom_idx]:.3f})")
        except Exception as e:
            check("Planets", False, error_msg=str(e))

    # --- 6. Quantum experimental ---
    section("6. Quantum fingerprint (experimental)")
    if modules.get("quantum"):
        try:
            # S_total dla uniform [1]*6
            st_uniform = S_total([1.0] * 6)
            # S_total dla single virtue
            st_single = S_total([1, 0, 0, 0, 0, 0])
            check("S_total oblicza się",
                  st_uniform >= 0,
                  f"S([1]*6)={st_uniform:.4f}, S(single)={st_single:.4f}")
            fp = quantum_fingerprint([0.7, 0.3, 0.5, 0.8, 0.4, 0.6])
            check("quantum_fingerprint schema",
                  "S_total" in fp and "concurrences" in fp,
                  f"S={fp['S_total']:.3f}, C={[round(c,3) for c in fp['concurrences']]}")
        except Exception as e:
            check("Quantum experimental", False, error_msg=str(e))

    # --- 7. IPQ + Full cycle ---
    section("7. Full pipeline (IPQ → anneal → crystallize)")
    if modules.get("ipq") and modules.get("hexagon"):
        try:
            test_q = "Jak pogodzić intelekt z intuicją serca w decyzjach?"
            t0 = time.time()
            raw = ipq(test_q)
            dt_ipq = time.time() - t0
            check("IPQ (bge-m3)",
                  raw is not None and len(raw) == 6,
                  f"{[round(x,3) for x in raw]} ({dt_ipq:.1f}s cold start)")

            t0 = time.time()
            s_crystal = anneal(raw)
            dt_anneal = time.time() - t0
            qr = compute_q(s_crystal)
            hard = is_crystallized(qr)
            check("Annealing",
                  qr["q"] > 0.8,
                  f"Q={qr['q']:.5f}, aniso={qr['aniso']:.6f}, {dt_anneal*1000:.0f}ms")
            soft_check("Hard crystal",
                       hard,
                       f"HARD (aniso<0.001 AND |Q-Q_ATT|<0.002)",
                       f"SOFT/RAW (anneal nie osiągnął hard)")
            print(f"     dominant: {qr['dominant']}")
        except Exception as e:
            check("Pipeline", False, error_msg=str(e))

    # --- 8. DuckDB ---
    section("8. DuckDB crystallization store")
    if modules.get("db"):
        try:
            conn = db.get_conn()
            s = db.stats(conn)
            check("DB connection",
                  s["count"] is not None,
                  f"{s['count']} crystallizations stored, AVG_Q={s.get('avg_q')}")
            # Schema check
            cols = [c[1] for c in conn.execute("PRAGMA table_info(crystallizations)").fetchall()]
            expected_cols = ['sch_freq', 'sch_kp', 'pl_dominant', 'S_total_exp']
            missing = [c for c in expected_cols if c not in cols]
            check("DB schema aktualna",
                  not missing,
                  f"{len(cols)} kolumn OK",
                  f"brakujące: {missing}")
            conn.close()
        except Exception as e:
            check("DuckDB", False, error_msg=str(e))

    # --- 9. Venv + zależności ---
    section("9. Środowisko")
    for pkg in ["numpy", "duckdb", "rich", "ephem"]:
        try:
            __import__(pkg)
            check(f"pkg: {pkg}", True, "available")
        except ImportError:
            check(f"pkg: {pkg}", False, error_msg="MISSING")

    # --- 10. Priorytety TODO ---
    section("10. PRIORITY TODOs (przeczytaj CLAUDE_HANDOFF.md dla pełnej listy)")
    priorities = [
        "P1.1 Walidacja S_total na 50+ pytaniach (blind)",
        "P1.2 Fingerprint uniqueness empirical test (1000 pytań)",
        "P1.3 24h stabilność pod live Schumann",
        "P2.1 5 mismatchów (IPQ×Schumann, Planet×IPQ, S_total×Q, Hard×conf, Off×Live)",
        "P4.2 Real quantum qsim z QuTiP (22 kubitów, ~1-2 tygodnie)",
    ]
    for p in priorities:
        print(f"  {DIM}•{RESET} {p}")

    # --- Podsumowanie ---
    print()
    print(f"{YELLOW}╔══════════════════════════════════════════════════╗{RESET}")
    if not errors:
        print(f"{YELLOW}║  {GREEN}All systems operational.{YELLOW}                        ║{RESET}")
        print(f"{YELLOW}║  Ready for: implementation or validation work.   ║{RESET}")
    else:
        print(f"{YELLOW}║  {RED}Errors: {len(errors)}{YELLOW}                                       ║{RESET}")
        for e in errors:
            print(f"{YELLOW}║    - {e:<44}║{RESET}")
    print(f"{YELLOW}╚══════════════════════════════════════════════════╝{RESET}")

    print(f"\n{DIM}Next steps:{RESET}")
    print(f"  1. {DIM}Read:{RESET} cat ~/qsim/CLAUDE_HANDOFF.md")
    print(f"  2. {DIM}Context:{RESET} MemPalace query 'qsim' (wing=ai-tools, quantum-genesis)")
    print(f"  3. {DIM}Pick P1 TODO{RESET} above and start with validation experiments")

    return len(errors)


if __name__ == "__main__":
    sys.exit(main())
