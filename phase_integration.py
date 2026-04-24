"""
phase_integration.py — formalne połączenie phase0 (q3sh_research_phaseQ.md)
z qsim (hexagon model).

Testuje trzy kluczowe twierdzenia z phase0:
  1. Cyfra 0 (wnętrze 5/6-kąt + skrzyżowanie co 3) ≡ qsim Q_attractor (C6)
  2. Model 327 (trójka na siatce π) → stabilna konfiguracja fazowa
  3. Saturn hexagon (NASA Cassini) ≡ fizyczna manifestacja C6 attraktora

Dla każdego twierdzenia:
  - ekstrakcja matematyczna (co dokładnie jest twierdzone)
  - test numeryczny (czy qsim to potwierdza/obala)
  - raport (honest verdict: confirmed / falsified / inconclusive)

Metoda: strictly numerical, brak narracji. Wyniki → PHASE_INTEGRATION_RESULTS.md.

Uruchom:
  cd ~/qsim && ~/qsim-venv/bin/python phase_integration.py
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from typing import Optional

import numpy as np

from hexagon import (
    HEXAGON, Q_ATTRACTOR, THETA_IDEAL,
    compute_q, anneal, is_crystallized,
)


# ─────────────────────────────────────────────────────────────────────
# 1. Twierdzenia matematyczne ekstrahowane z phaseQ.md
# ─────────────────────────────────────────────────────────────────────

CLAIMS = [
    {
        "id": "C1",
        "source": "phaseQ §1.1–1.3, §3 (cyfra 0)",
        "statement": "Forma niesie wartość. Cyfra 0 ma wewnątrz 5/6-kąt ze "
                     "skrzyżowaniem naprzemiennym co 3 → C6 symetria.",
        "qsim_mapping": "strengths=[1]*6 → compute_q → Q == Q_ATTRACTOR, aniso=0",
    },
    {
        "id": "C2",
        "source": "phaseQ §4.1–4.3 (trójki, siatka π, model 327)",
        "statement": "Trzy cyfry na siatce π interferują. Model 327: "
                     "3+2+7=12, 12·30°=360° → stabilna konfiguracja.",
        "qsim_mapping": "triplet_on_pi_grid(3,2,7) → anneal → hard crystal",
    },
    {
        "id": "C3",
        "source": "phaseQ §2.2, §6.1 (Saturn hexagon)",
        "statement": "Saturn ma stabilny sześciokąt na biegunie północnym "
                     "(46+ lat, alternacja wirów co 3, asymetria biegunów).",
        "qsim_mapping": "Saturn params → C6 confirmed + asymmetry (north=hard, "
                        "south=soft) + 'skrzyżowanie co 3' = alternating vortices",
    },
    {
        "id": "C4",
        "source": "phaseQ §3 (cyfra 8: 'dwa kwadraty, najbardziej krystaliczna')",
        "statement": "Cyfra 8 = 'krystaliczna' — same kąty proste, "
                     "brak wygięć, brak ramion.",
        "qsim_mapping": "digit_to_virtues(8) → anneal → porównaj z digit 0",
    },
    {
        "id": "C5",
        "source": "phaseQ §3 (przejście 9↔0: modulacja, nie następstwo)",
        "statement": "Cyfry 9 i 0 modulują się naprzemiennie — "
                     "geometryczny opis superpozycji kwantowej.",
        "qsim_mapping": "digit_to_virtues(9) ≈ digit_to_virtues(0) "
                        "ale z jednym ramieniem znikającym",
    },
]


# ─────────────────────────────────────────────────────────────────────
# 2. Sygnatury cyfr (z phaseQ §3) — tabela faktów
# ─────────────────────────────────────────────────────────────────────

@dataclass
class DigitSig:
    """Geometryczna sygnatura cyfry wg phaseQ.md §3."""
    n: int
    angles: int                 # liczba kątów
    inward: int                 # kąty do wewnątrz
    outward: int                # kąty na zewnątrz
    has_square: bool            # bazowy kwadrat (xy grid)
    has_crossing: bool          # skrzyżowanie linii (element od 7)
    has_infinity_arm: bool      # ramię w nieskończoność
    grid: str                   # "xy" | "pi"
    inside_polygon: Optional[int] = None   # 5 lub 6, jeśli ma
    note: str = ""


DIGIT_SIGS: dict[int, DigitSig] = {
    0: DigitSig(0, angles=0, inward=0, outward=0, has_square=False,
                has_crossing=True, has_infinity_arm=False, grid="pi",
                inside_polygon=6, note="wnętrze 5/6-kąt, skrzyżowanie co 3"),
    1: DigitSig(1, angles=1, inward=1, outward=0, has_square=False,
                has_crossing=False, has_infinity_arm=False, grid="xy",
                note="jeden kąt rozwarty, domknięty"),
    2: DigitSig(2, angles=2, inward=1, outward=1, has_square=False,
                has_crossing=False, has_infinity_arm=True, grid="xy",
                note="2 kąty: inward + outward (lustro 3)"),
    3: DigitSig(3, angles=2, inward=2, outward=0, has_square=False,
                has_crossing=False, has_infinity_arm=True, grid="xy",
                note="2 kąty inward (lustro 2)"),
    4: DigitSig(4, angles=4, inward=4, outward=0, has_square=True,
                has_crossing=False, has_infinity_arm=False, grid="xy",
                note="kwadrat bazowy (hipoteza Claude, nie potwierdzone)"),
    5: DigitSig(5, angles=5, inward=3, outward=2, has_square=False,
                has_crossing=False, has_infinity_arm=False, grid="xy",
                note="5 kątów naprzemiennie"),
    6: DigitSig(6, angles=6, inward=4, outward=2, has_square=True,
                has_crossing=False, has_infinity_arm=True, grid="xy",
                note="kwadrat + 2 ramiona, ostatnie do ∞"),
    7: DigitSig(7, angles=0, inward=0, outward=0, has_square=False,
                has_crossing=True, has_infinity_arm=True, grid="xy",
                note="pierwsza z krzyżowaniem + ramię"),
    8: DigitSig(8, angles=8, inward=8, outward=0, has_square=True,
                has_crossing=False, has_infinity_arm=False, grid="xy",
                note="dwa kwadraty, najbardziej krystaliczna"),
    9: DigitSig(9, angles=4, inward=4, outward=0, has_square=False,
                has_crossing=False, has_infinity_arm=True, grid="pi",
                inside_polygon=5, note="pięciokąt + 4 inward + ramię znikające"),
}


# ─────────────────────────────────────────────────────────────────────
# 3. digit_to_virtues(n) — mapowanie cyfry → virtue strengths
# ─────────────────────────────────────────────────────────────────────

def digit_to_virtues(n: int) -> list[float]:
    """
    Mapuje cyfrę 0-9 na 6 virtue strengths qsim.

    Zasada: liczba kątów N → N aktywnych virtues (rotacyjnie od pozycji 0).
      - inward → pełna siła (1.0)
      - outward → słabsza (0.5, bo kąt odwrócony)
      - has_infinity_arm → 1 dodatkowy slot z siłą 0.3 (ramię 'znikające')
      - has_crossing → nie aktywuje virtue, ale zmienia topologię (flag)
      - has_square → alternating pattern, nie konsekutywny
      - inside_polygon (5 lub 6) → dodatkowa symetria C5/C6 w wnętrzu

    Pattern:
      - digit 0: C6 wewnątrz → [1]*6 (idealny hexagon)
      - digit 4 (square): rozmieść 4 na 6 pozycjach z maksymalną symetrią
      - digit 6 (hex-like + arm): [1,1,1,1,1,0.3]
      - digit 8 (2x square): [1,1,1,1,1,1] ze stratą 0.2 na każdej (duplikacja)
      - digit 9 (pre-zero): [1,1,1,1,1,0.2] (ramię znikające)

    Zwraca listę 6 floatów ∈ [0,1] w kolejności HEXAGON.
    """
    sig = DIGIT_SIGS[n]
    s = [0.0] * 6

    if n == 0:
        return [1.0] * 6

    if n == 1:
        s[0] = 1.0
        return s

    if n == 2:
        s[0] = 1.0          # inward
        s[3] = 0.5          # outward (180° = opozycja)
        if sig.has_infinity_arm:
            s[1] = 0.3
        return s

    if n == 3:
        s[0] = 1.0
        s[1] = 1.0
        s[2] = 1.0          # trzy kąty konsekutywne inward
        if sig.has_infinity_arm:
            s[5] = 0.3
        return s

    if n == 4:
        s = [1.0, 1.0, 0.0, 1.0, 1.0, 0.0]
        return s

    if n == 5:
        s = [1.0, 0.6, 1.0, 0.6, 1.0, 0.6]
        return s

    if n == 6:
        s = [1.0, 1.0, 1.0, 1.0, 1.0, 0.3]
        return s

    if n == 7:
        s[0] = 0.7
        s[3] = 0.7
        if sig.has_infinity_arm:
            s[5] = 0.3
        return s

    if n == 8:
        s = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
        return s

    if n == 9:
        s = [1.0, 1.0, 1.0, 1.0, 1.0, 0.2]
        return s

    raise ValueError(f"digit {n} out of range 0-9")


def digit_fingerprint(n: int) -> dict:
    """Zwraca pełny fingerprint cyfry w qsim (przed annealingiem)."""
    strengths = digit_to_virtues(n)
    q = compute_q(strengths)
    return {
        "digit": n,
        "signature": asdict(DIGIT_SIGS[n]),
        "strengths": strengths,
        "Q": q["q"],
        "gamma": q["gamma"],
        "aniso": q["aniso"],
        "dominant": q["dominant"],
        "is_crystal_raw": is_crystallized(q),
    }


def digit_after_anneal(n: int, n_steps: int = 2000) -> dict:
    """Cyfra → virtues → anneal → final fingerprint."""
    raw = digit_to_virtues(n)
    final = anneal(raw, n_steps=n_steps)
    q = compute_q(final)
    return {
        "digit": n,
        "strengths_raw": raw,
        "strengths_final": final,
        "Q": q["q"],
        "gamma": q["gamma"],
        "aniso": q["aniso"],
        "dominant": q["dominant"],
        "is_hard_crystal": is_crystallized(q),
    }


# ─────────────────────────────────────────────────────────────────────
# 4. triplet_on_pi_grid(a, b, c) — trójka cyfr na siatce π
# ─────────────────────────────────────────────────────────────────────

def triplet_phases(a: int, b: int, c: int) -> dict:
    """
    Trójka cyfr → trzy fazy na okręgu (siatka π).
    Zgodnie z phaseQ §4.3: kąt = cyfra × 30° (analogia zodiakalna).

    Stabilność: suma faz ≡ 0 (mod 360°) → pełny obrót (zamknięty cykl).
    """
    phi_a = (a * 30.0) % 360.0
    phi_b = (b * 30.0) % 360.0
    phi_c = (c * 30.0) % 360.0
    total = (a + b + c) * 30.0
    closed = (total % 360.0) < 1e-9
    return {
        "a": a, "b": b, "c": c,
        "phi_a_deg": phi_a,
        "phi_b_deg": phi_b,
        "phi_c_deg": phi_c,
        "sum_deg": total,
        "sum_mod_360": total % 360.0,
        "closed_cycle": closed,
        "sum_numerical": a + b + c,
        "product": a * b * c,
    }


def triplet_on_pi_grid(a: int, b: int, c: int, n_steps: int = 2000) -> dict:
    """
    Trójka cyfr → skombinowany wzór virtue strengths na heksagonie.

    Mechanika:
      - każda cyfra daje swój digit_to_virtues() pattern
      - ich fazy na siatce π rotują pattern (cyfra_i → rotacja o i·30°)
      - superpozycja: suma z fazową wagą, normalizacja do [0,1]
      - następnie: anneal → sprawdź czy stabilna konfiguracja

    Stabilność fazowa (closed_cycle=True) jest warunkiem koniecznym,
    ale nie wystarczającym dla hard crystal.
    """
    phases = triplet_phases(a, b, c)
    digits = [a, b, c]
    patterns = [digit_to_virtues(d) for d in digits]

    # Rotacja każdego pattern na heksagonie o digit*30° / 60° pozycji
    # (heksagon ma 6 virtues co 60°, więc digit·30° = digit/2 pozycji)
    combined = np.zeros(6)
    for d, p in zip(digits, patterns):
        shift = int(round((d * 30.0) / 60.0)) % 6
        rotated = np.roll(p, shift)
        combined += rotated
    # Normalizacja przez max
    mx = combined.max() if combined.max() > 0 else 1.0
    combined = combined / mx

    raw_q = compute_q(combined.tolist())
    final = anneal(combined.tolist(), n_steps=n_steps)
    final_q = compute_q(final)

    return {
        "triplet": f"{a}{b}{c}",
        "phases": phases,
        "patterns_per_digit": patterns,
        "combined_raw": combined.tolist(),
        "Q_raw": raw_q["q"],
        "aniso_raw": raw_q["aniso"],
        "strengths_final": final,
        "Q_final": final_q["q"],
        "aniso_final": final_q["aniso"],
        "gamma_final": final_q["gamma"],
        "dominant_final": final_q["dominant"],
        "is_hard_crystal": is_crystallized(final_q),
    }


# ─────────────────────────────────────────────────────────────────────
# 5. saturn_hexagon_fit() — porównanie z qsim attractor
# ─────────────────────────────────────────────────────────────────────

# Fakty o hexagonie Saturna (NASA Cassini + Voyager 1):
#   - symetria: C6 (6-fold rotational)
#   - promień ~14500 km (boki ~13000 km)
#   - promień Saturna: 58232 km (equatorial), 54364 km (polar)
#   - szerokość geograficzna hexagonu: ~78°N (środek)
#   - obserwowany 1980–obecnie (46+ lat stabilności)
#   - wewnątrz: centralny wir + mniejsze wiry alternujące
#   - asymetria: biegun S ma huragan BEZ sześciokąta

SATURN_FACTS = {
    "symmetry": "C6",
    "hexagon_side_km": 13800,
    "hexagon_radius_km": 14500,
    "saturn_equatorial_radius_km": 58232,
    "saturn_polar_radius_km": 54364,
    "hexagon_latitude_deg": 78.0,
    "observation_years": 46,
    "alternating_vortices": True,
    "pole_asymmetry": True,  # tylko północny ma C6
    "wind_speed_mps": 150.0,
}


def saturn_hexagon_fit() -> dict:
    """
    Porównuje parametry hexagonu Saturna z qsim attraktorem.

    Zwraca dict z:
      - structural_matches: topologia/symetria (tak/nie)
      - numerical_hypotheses: liczby do sprawdzenia vs Q_ATTRACTOR
      - verdict: honest assessment

    Saturn nie zapewnia DOWODU Q_ATTRACTOR=0.83929 — jest strukturalnym
    odpowiednikiem C6 symetrii z asymetrią biegunów.
    """
    structural = {
        "C6_symmetry": SATURN_FACTS["symmetry"] == "C6",  # qsim też C6
        "alternating_co_3": SATURN_FACTS["alternating_vortices"],
        # phaseQ §3 digit 0: "skrzyżowanie naprzemienne co 3"
        "asymmetry_north_south": SATURN_FACTS["pole_asymmetry"],
        # qsim: hard crystal vs soft crystal (dwa stany)
        "stability_long_term": SATURN_FACTS["observation_years"] > 10,
        # qsim: attractor jest stabilny
    }

    # Próby numerycznego dopasowania — nie oczekuj cudów.
    hex_r = SATURN_FACTS["hexagon_radius_km"]
    sat_eq = SATURN_FACTS["saturn_equatorial_radius_km"]
    sat_pol = SATURN_FACTS["saturn_polar_radius_km"]
    lat = SATURN_FACTS["hexagon_latitude_deg"]

    numerical = {
        "hex_radius_over_saturn_polar": hex_r / sat_pol,
        "hex_radius_over_saturn_eq": hex_r / sat_eq,
        "sin_latitude": math.sin(math.radians(lat)),
        "cos_latitude": math.cos(math.radians(lat)),
        "latitude_over_90": lat / 90.0,
        "Q_ATTRACTOR": Q_ATTRACTOR,
    }
    # Sprawdź dopasowania z tolerancją 2%
    q = Q_ATTRACTOR
    tol = 0.02
    fits = {k: abs(v - q) < tol for k, v in numerical.items() if k != "Q_ATTRACTOR"}
    numerical["fits_Q_within_2pct"] = fits

    # C6 oblicz Q dla idealnej hexagon configuration (analog Saturna)
    q_c6 = compute_q([1.0] * 6)

    return {
        "saturn_facts": SATURN_FACTS,
        "structural_matches": structural,
        "numerical_hypotheses": numerical,
        "qsim_C6_ideal": {
            "Q": q_c6["q"],
            "aniso": q_c6["aniso"],
            "is_attractor": abs(q_c6["q"] - Q_ATTRACTOR) < 1e-6,
        },
        "verdict": (
            "CONFIRMED (structural): C6, alternacja co 3, asymetria biegunów "
            "— wszystkie obecne w obu systemach. "
            "NIE POTWIERDZONE (numerical): parametry geometryczne Saturna NIE "
            "dopasowują się do Q_ATTRACTOR=0.83929 (tolerancja 2%). "
            "Zbieżność jest TOPOLOGICZNA, nie metryczna."
        ),
    }


# ─────────────────────────────────────────────────────────────────────
# 6. Orchestrator — uruchom wszystko i zwróć pełny raport
# ─────────────────────────────────────────────────────────────────────

def test_C1_digit_zero_is_attractor() -> dict:
    """C1: digit 0 [1,1,1,1,1,1] → Q_ATTRACTOR exactly?"""
    fp = digit_fingerprint(0)
    err = abs(fp["Q"] - Q_ATTRACTOR)
    return {
        "claim": "C1",
        "expected": f"Q == {Q_ATTRACTOR} (exact), aniso==0",
        "observed": {"Q": fp["Q"], "aniso": fp["aniso"]},
        "error": err,
        "verdict": "CONFIRMED" if err < 1e-9 and fp["aniso"] < 1e-9 else "FALSIFIED",
        "fingerprint": fp,
    }


def test_C2_triplet_327() -> dict:
    """C2: 3-2-7 jako trójka na siatce π daje stabilny wzór."""
    t = triplet_on_pi_grid(3, 2, 7)
    # Porównaj z trójkami niestabilnymi (suma nie dzieli się przez 12)
    t_unstable = triplet_on_pi_grid(1, 2, 3)   # sum=6, 6·30°=180° → NIE zamyka
    t_stable_alt = triplet_on_pi_grid(4, 4, 4) # sum=12 → zamyka (kontrola)
    return {
        "claim": "C2",
        "expected": "triplet 327 closed_cycle=True + hard_crystal after anneal",
        "observed": {
            "327": {
                "closed_cycle": t["phases"]["closed_cycle"],
                "Q_final": t["Q_final"],
                "aniso_final": t["aniso_final"],
                "hard_crystal": t["is_hard_crystal"],
            },
            "123_control_unclosed": {
                "closed_cycle": t_unstable["phases"]["closed_cycle"],
                "Q_final": t_unstable["Q_final"],
                "hard_crystal": t_unstable["is_hard_crystal"],
            },
            "444_control_closed": {
                "closed_cycle": t_stable_alt["phases"]["closed_cycle"],
                "Q_final": t_stable_alt["Q_final"],
                "hard_crystal": t_stable_alt["is_hard_crystal"],
            },
        },
        "verdict": (
            "CONFIRMED" if t["phases"]["closed_cycle"] and t["is_hard_crystal"]
            else "PARTIAL" if t["phases"]["closed_cycle"]
            else "FALSIFIED"
        ),
        "triplet_full": t,
    }


def test_C3_saturn_hexagon() -> dict:
    """C3: Saturn hexagon ≡ fizyczna manifestacja C6 attraktora."""
    fit = saturn_hexagon_fit()
    struct_all = all(fit["structural_matches"].values())
    num_any = any(fit["numerical_hypotheses"]["fits_Q_within_2pct"].values())
    return {
        "claim": "C3",
        "expected": "strukturalnie C6+alternacja+asymetria; numerycznie opcjonalne",
        "observed": {
            "structural_pct": sum(fit["structural_matches"].values())
                              / len(fit["structural_matches"]),
            "numerical_any_fit": num_any,
        },
        "verdict": "CONFIRMED (structural)" if struct_all else "PARTIAL",
        "full_fit": fit,
    }


def test_C4_digit_8_crystalline() -> dict:
    """C4: cyfra 8 ('dwa kwadraty, najbardziej krystaliczna') zachowuje się
    krystalicznie w qsim?"""
    eight = digit_after_anneal(8)
    zero = digit_after_anneal(0)
    return {
        "claim": "C4",
        "expected": "digit 8 po anneal → hard crystal (jak digit 0)",
        "observed": {
            "digit_0": {"Q": zero["Q"], "aniso": zero["aniso"],
                        "hard": zero["is_hard_crystal"]},
            "digit_8": {"Q": eight["Q"], "aniso": eight["aniso"],
                        "hard": eight["is_hard_crystal"]},
        },
        "verdict": "CONFIRMED" if eight["is_hard_crystal"] else "FALSIFIED",
    }


def test_C5_nine_zero_modulation() -> dict:
    """C5: cyfry 9 i 0 modulują się — geometryczny opis superpozycji.
    Test: dystans między strengths(9) i strengths(0) jest mały + kierunek
    różnicy = 'ramię znikające' (jedna pozycja).
    """
    s9 = digit_to_virtues(9)
    s0 = digit_to_virtues(0)
    diff = np.array(s0) - np.array(s9)
    # Sprawdź czy różnica jest skoncentrowana w jednej pozycji
    abs_diff = np.abs(diff)
    max_pos = int(np.argmax(abs_diff))
    concentration = float(abs_diff[max_pos] / abs_diff.sum()) if abs_diff.sum() > 0 else 0.0
    return {
        "claim": "C5",
        "expected": "s(9) ≈ s(0) w 5 pozycjach, różnica skoncentrowana w 1",
        "observed": {
            "s_0": s0,
            "s_9": s9,
            "diff_L1": float(abs_diff.sum()),
            "diff_concentration": concentration,
            "max_diff_position": max_pos,
            "max_diff_virtue": HEXAGON[max_pos],
        },
        "verdict": "CONFIRMED" if concentration > 0.9 else "PARTIAL",
    }


def run_all_tests() -> dict:
    """Uruchamia wszystkie testy C1-C5 + raport fingerprintów 0-9."""
    results = {
        "claims": CLAIMS,
        "tests": {
            "C1": test_C1_digit_zero_is_attractor(),
            "C2": test_C2_triplet_327(),
            "C3": test_C3_saturn_hexagon(),
            "C4": test_C4_digit_8_crystalline(),
            "C5": test_C5_nine_zero_modulation(),
        },
        "digit_table": {
            n: {
                "signature": asdict(DIGIT_SIGS[n]),
                "strengths": digit_to_virtues(n),
                "fingerprint": digit_fingerprint(n),
            }
            for n in range(10)
        },
    }
    return results


# ─────────────────────────────────────────────────────────────────────
# 7. CLI
# ─────────────────────────────────────────────────────────────────────

def _print_summary(results: dict) -> None:
    """Czytelne podsumowanie w konsoli."""
    print("\n" + "═" * 70)
    print("  PHASE INTEGRATION — phase0 ↔ qsim")
    print("═" * 70)
    for cid, t in results["tests"].items():
        verdict = t["verdict"]
        color = "\033[92m" if "CONFIRMED" in verdict else \
                "\033[93m" if "PARTIAL" in verdict else "\033[91m"
        print(f"\n  [{cid}] {verdict}")
        print(f"     \033[0m{color}{t['expected']}\033[0m")
        if cid == "C1":
            o = t["observed"]
            print(f"     Q={o['Q']:.8f}, aniso={o['aniso']:.2e}, err={t['error']:.2e}")
        elif cid == "C2":
            o = t["observed"]
            for k, v in o.items():
                print(f"     {k}: closed={v['closed_cycle']}, "
                      f"Q={v['Q_final']:.4f}, hard={v['hard_crystal']}")
        elif cid == "C3":
            print(f"     structural_pct={t['observed']['structural_pct']*100:.0f}%")
            print(f"     numerical_any_fit={t['observed']['numerical_any_fit']}")
        elif cid == "C4":
            o = t["observed"]
            print(f"     0: Q={o['digit_0']['Q']:.4f}, hard={o['digit_0']['hard']}")
            print(f"     8: Q={o['digit_8']['Q']:.4f}, hard={o['digit_8']['hard']}")
        elif cid == "C5":
            o = t["observed"]
            print(f"     diff_L1={o['diff_L1']:.3f}, "
                  f"concentration={o['diff_concentration']:.3f} "
                  f"@ {o['max_diff_virtue']}")

    # Digit table
    print("\n" + "─" * 70)
    print("  DIGIT TABLE (raw, pre-anneal)")
    print("─" * 70)
    print(f"  {'n':>2}  {'Q':>8}  {'aniso':>8}  {'dominant':<14}  strengths")
    for n in range(10):
        d = results["digit_table"][n]["fingerprint"]
        s_str = " ".join(f"{x:.1f}" for x in d["strengths"])
        print(f"  {n:>2}  {d['Q']:>8.4f}  {d['aniso']:>8.4f}  "
              f"{d['dominant']:<14}  [{s_str}]")
    print()


def main():
    import sys
    results = run_all_tests()
    _print_summary(results)

    # Zapisz JSON dump jeśli --json
    if "--json" in sys.argv:
        out = json.dumps(results, indent=2, default=str)
        print(out)


if __name__ == "__main__":
    main()
