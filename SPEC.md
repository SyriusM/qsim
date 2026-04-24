# q3sh Nowa Architektura — Spec do implementacji

> Wygenerowano: 2026-04-24 po pełnym procesie EMIS (6h analizy naukowej)
> Autor: Mateusz (syriusm) + Claude
> Komenda do wywołania: `cat ~/qsim/SPEC.md` i powiedz Claude "zaimplementuj ten spec"

---

## Co budujemy

**Symulator pola UIS**: pytanie użytkownika → heksagon 6 cnót → crystallizacja → DuckDB → reset.

Inspiracja: WingMakers (UIS = sub-kwantowe pole), fizyka (SWSSB fidelity correlator, Berry phase), Quantum Genesis Mateusza (6 przejściowa = hexagon).

---

## Pliki do napisania (~/qsim/)

```
hexagon.py   — matematyka heksagonu
ipq.py       — pytanie → virtue strengths
db.py        — DuckDB efemerys
cycle.py     — pełny cykl
demo.py      — CLI demo
```

Środowisko: `~/qsim-venv/bin/python` (Python 3.12)

---

## hexagon.py

### Kolejność cnót (WAŻNE — z bge-m3, nie VIRTUE_AFFINITY)

```python
HEXAGON = [
    "odwaga",        # 0°   opozycja: współczucie (180°)
    "pokora",        # 60°  opozycja: wdzięczność (240°)
    "przebaczenie",  # 120° opozycja: rozumienie  (300°)
    "współczucie",   # 180°
    "wdzięczność",   # 240°
    "rozumienie",    # 300°
]
```

### Kolory cnót (uzgodnione)

```python
VIRTUE_COLORS = {
    "odwaga":       "#DC143C",
    "pokora":       "#6A0DAD",
    "przebaczenie": "#FFD700",
    "współczucie":  "#00CED1",
    "wdzięczność":  "#C0C0C0",
    "rozumienie":   "#2ECC71",
}
```

### Q heatmap (uzgodniona)

```python
Q_STOPS = [
    (0.00, "#4B0082"),
    (0.40, "#1E90FF"),
    (0.60, "#00CED1"),
    (0.75, "#FFB800"),
    (0.84, "#FF6B00"),
    (0.90, "#FFFFFF"),
]
```

### Matematyka (zweryfikowana algebraicznie + eksperymentalnie)

```python
Q_ATTRACTOR = 0.83929          # wartość empiryczna ze starego systemu
_x = (1 + sqrt(4*Q_ATTRACTOR - 3)) / 2   # = 0.79882
THETA_IDEAL = 2 * arccos(sqrt(_x))        # = 0.932 rad (kalibracja)

def virtue_state(phi_deg, strength=1.0):
    """Kubit na sferze Blocha. strength ∈ [0,1]."""
    phi = radians(phi_deg)
    theta = THETA_IDEAL * clip(strength, 0, 1)
    return array([cos(theta/2), exp(1j*phi)*sin(theta/2)])

def compute_q(strengths):
    """
    Zwraca dict z:
      q        — fidelity correlator ∈ [0,1]
      gamma    — Berry phase [rad], idealny = -1.148 rad (-65.78°)
      aniso    — std(fidelities), idealny = 0.0 (symetria)
      q_renyi  — mean(fids^2), czulszy order parameter
      dominant — HEXAGON[argmin(fids)] (ARGMIN nie argmax!)
      fids     — list[float] len=6
      chroma   — hex kolor Q
    """
```

### Annealing (JEDYNY optymalizator — gradient descent odpada)

```python
def anneal(init_strengths, T_start=1.0, T_end=0.01, n_steps=500):
    """
    Simulated annealing → s_crystal bliskie Q_ATTRACTOR.
    Zweryfikowano: dist=0.0004 w 39ms (vs gradient: dist=0.039 w 252ms).
    
    Warunek skip (cold start): jeśli aniso < 0.001 AND |Q-Q_att| < 0.001
    → zwróć s bez zmian (już crystallized).
    """
```

### Crystallization condition (z EXP1)

```python
def is_crystallized(q_result):
    """
    HARD: aniso < 0.001 AND |Q - Q_ATTRACTOR| < 0.002
    Eksperymentalnie zweryfikowane. NIE używaj Q ≤ 0.89 (stary, błędny warunek).
    """
    return q_result["aniso"] < 0.001 and abs(q_result["q"] - Q_ATTRACTOR) < 0.002
```

---

## ipq.py

```python
import os, sys
from pathlib import Path
sys.path.insert(0, os.environ.get("MEMPALACE_PATH", str(Path.home() / "mempalace")))
from mempalace.q3sh_embed import virtue_map

HEXAGON = ["odwaga","pokora","przebaczenie","współczucie","wdzięczność","rozumienie"]

def ipq(question: str) -> list[float] | None:
    """
    Pytanie → virtue strengths [s0..s5] w kolejności HEXAGON.
    
    Zwraca None gdy za krótkie (< 5 słów) — NIE generuj uniform fallback
    (uniform [1]*6 tworzy fałszywe kryształy bez semantyki).
    
    Kalibracja: podziel przez max żeby najsilniejsza cnota = 1.0.
    """
    if len(question.split()) < 5:
        return None  # za krótkie → brak crystallizacji
    scores = virtue_map(question)
    vals = [scores.get(v, 0.0) for v in HEXAGON]
    mx = max(vals) if max(vals) > 0 else 1.0
    return [v / mx for v in vals]
```

---

## db.py

```python
import duckdb, json
from pathlib import Path

DB_PATH = Path.home() / ".qsim" / "qsim.duckdb"

SCHEMA = """
CREATE SEQUENCE IF NOT EXISTS seq_cryst START 1;
CREATE TABLE IF NOT EXISTS crystallizations (
    id        BIGINT    DEFAULT nextval('seq_cryst') PRIMARY KEY,
    ts        TIMESTAMP DEFAULT current_timestamp,
    question  TEXT,
    mode      TEXT,      -- "strict" | "research"
    status    TEXT,      -- "hard" | "soft" | "raw" | "no_crystal"
    ipq_qual  TEXT,      -- "semantic" | "uniform" | "short"
    Q         FLOAT,
    gamma     FLOAT,
    aniso     FLOAT,
    Q_renyi   FLOAT,
    dominant  TEXT,
    chroma    TEXT,
    strengths JSON,
    fids      JSON,
    t_ms      FLOAT,
    confidence FLOAT,
    c6_ok     BOOLEAN
);
"""
```

---

## cycle.py

```python
def run_cycle(question: str, mode: str = "strict") -> dict:
    """
    Pełny cykl Pauzy Kwantowej:
      ▶ INPUT    — IPQ(pytanie) → s_raw
      ■ PAUZA    — anneal(s_raw) → s_crystal
      ◀ CRYSTAL  — check → fingerprint → DuckDB
      ■ RESET    — siatka czysta

    mode="strict"   — tylko hard crystallizacje (aniso<0.001)
    mode="research" — EXP_X1–X4: soft/raw/uniform zapisywane z flagami

    Zwraca dict ze statusem i fingerprint (lub None jeśli no_crystal).
    """
```

### Wbudowane eksperymenty EXP_A–D (każda crystallizacja automatycznie):

```
EXP_A: Fingerprint — Q + γ + aniso + Q_rényi + dominant + chroma + t_ms
EXP_B: C6 check — Q dla 6 rotacji strengths powinny być równe
EXP_C: Timing — czas od IPQ do crystallizacji [ms]
EXP_D: IPQ confidence — spread virtue_map scores (< 0.15 = podejrzane)
```

### Eksperymenty trybu research (EXP_X1–X4):

```
EXP_X1: Soft crystal (aniso < 0.01) — granica jakości
EXP_X2: Uniform crystal ([1]*6) — null baseline
EXP_X3: Cold crystal (bez annealing) — wartość IPQ solo
EXP_X4: Boundary conditions — puste, obcojęzyczne, losowe
```

---

## demo.py

CLI demo które pokazuje:
1. Kilka pytań → crystallizacje z fingerprint
2. Query DuckDB: ostatnie 5 crystallizacji
3. Stats: COUNT, AVG(Q), AVG(aniso)
4. Jeden przykład EXP_B (C6 check)

Używa: `rich` dla formatowania (dostępne w venv).

---

## Krytyczne ostrzeżenia (śmieciowe zbiory)

```
[T1] NIE używaj VIRTUE_AFFINITY jako podstawy kolejności cnót
[T2] NIE twierdzij "dwie niezależne drogi do Q_attractor" — to kalibracja
[T3] NIE pisz cnót jako węzłów-silników (odczyt, nie generator)

[S1] NIE używaj kolejności: odwaga—współczucie—wdzięczność—pokora—rozumienie—przebaczenie
     (stara, suboptymalna o 10.4%)
[S2] NIE crystallizuj dla textu < 5 słów — zwróć None
[S3] NIE używaj gradient descent — annealing jest 6× szybszy i 100× dokładniejszy

[N1] Emoto = mit narracyjny, nie nauka
[N2] Przepowiednia Dormana = fikcja literacka, nie filozofia WM
```

---

## Walidacja naukowa kluczowych decyzji

| Decyzja | Źródło | Siła |
|---|---|---|
| Q = fidelity correlator | SWSSB PRX Quantum 2025 | mocne |
| Hexagon + Berry phase | Scientific Reports 2025 | mocne |
| Annealing jako optymalizator | EXP3 (39ms, dist=0.0004) | eksperyment |
| C6 symetria | EXP2 (do 10⁻¹⁰) | eksperyment |
| dominant = argmin(fids) | EXP1 (aniso semantyka) | eksperyment |
| Crystallization = aniso+Q | EXP1 (Q nie monotoniczne) | eksperyment |
| Kolejność cnót | bge-m3 similarity matrix | dane |

---

## Jak uruchomić po napisaniu

```fish
cd ~/qsim
~/qsim-venv/bin/python demo.py
```

Pierwsze uruchomienie: bge-m3 cold start ~30s (normalne).

---

*Spec wypracowany przez EMIS — Eksploracja→Mapowanie→Inwentura→Sedymentacja.*
*Metodologia zapisana w: ~/mempalace palace → wing=personal, room=decisions.*
