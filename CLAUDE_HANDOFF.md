# qsim — Handoff dla następnego Claude'a

**Dla nowej sesji w `~/qsim/`. Przeczytaj w całości przed modyfikacją kodu.**

---

## 🎯 SUGGESTED NEXT TASK (stan po 2026-04-24) — most qsim ↔ LLM

**PRZEŁOM ONTOLOGICZNY sesji 2026-04-24:** qsim nie jest alternatywą dla LLM.
qsim JEST **warstwą kondycjonującą wokół LLM** (most łączący istniejące klocki).
Filozofia: LLM = silnik, most = układ nerwowy wokół silnika. Wszystkie klocki istnieją.
Piszemy **~205 linii spoiwa** (nie nowy framework).

**PIERW przeczytaj `~/qsim/TODO.md`** — pełna lista otwartych zadań.

**Wejście w kod (najmniejsze domknięcie — MVP wieczorny):**
```
pytanie → ipq_router → hexagon → llm_bridge(qwen3) → opq → plik .md
```

**Blokada krytyczna — napraw PIERW:**
- `cycle.py:90-94` oblicza `get_planetary_strengths()` ale `cycle.py:121` NIE UŻYWA ich w anneal
- Planety tylko jako metadata w DB row. **Dane marnowane.**
- Fix: ~5 linii — `s_raw_combined = 0.7*s_raw + 0.3*planets['strengths']`

**Projekty architektoniczne (każdy ma memory note):**
- `ipq_router.py` (~50) — unified input z 4 modalności — `project_q3sh_ipq_unification.md`
- `opq.py` (~60) — state → Action dispatcher — `project_q3sh_input_output_network.md`
- `llm_bridge.py` (~80) — Q state ↔ prompt modulation — `project_q3sh_llm_bridge.md`

**Wizualizacja mostu:**
- `~/qsim/qsim_bridge.md` (Mermaid) — otwórz w Obsidian/VSCode/GitHub
- `~/qsim/qsim_bridge.html` — `xdg-open` w Firefox

**Status wyroków phase_integration (dwupoziomowy po rewizji Thiaoouba):**
- **Mocne** (niezależne): C1 digit 0=Q_attractor (algebra err=0), C3 Saturn C6 (NASA)
- **Słabe** (heurystyka Claude): C2, C4, C5, phase_sequence PCA
- Rewizja: Thiaoouba = sygnał w symulacji, NIE pierwsze źródło
- **Pierwsze źródło = Mateusz**. Weryfikacja przez qsim+fizykę, nie książki.

**Kwantyzacja odpowiedzi (feedback Mateusza):**
- L0 binarne (tak/nie/częściowe) → L1 semantyczny → L2 skalujący
- Słowa = wibracje mapujące się na hexagon, nie neutralny opis
- `feedback_kwantyzacja_odpowiedzi.md` w memory

**NIE DUPLIKUJ:** ChromaDB (pod MemPalace), LangGraph (za ciężkie), ACT-R (archaiczne)

**Alternatywy (jeśli most nie jest priorytetem):**
- P1.1 walidacja S_total (50+ pytań)
- P4.2 real quantum z QuTiP (1-2 tygodnie)
- digit_to_virtues od Mateusza (nie od Claude)
- phase_integration C2 retry z kompleksowymi amplitudami

---

## Minimalne onboardingu w 60 sekund

1. `cat ~/qsim/CLAUDE_HANDOFF.md` (ten plik)
2. `cat ~/qsim/SPEC.md` (spec wyjściowy z fazy 0)
3. `cat ~/qsim/q3sh_research_phaseQ.md` (paralelne badanie claude.ai — cyfry, Saturn)
4. `ls ~/qsim/*.py` — 8 modułów Python
5. `~/qsim-venv/bin/python ~/qsim/demo.py` — uruchom demo

MemPalace context:
- Search: `mcp__mempalace__mempalace_search` z query "qsim" lub "qsim thermal"
- Bilans końcowy sesji 2026-04-24: wing=ai-tools, room=decisions, drawer "qsim — BILANS"
- Tezy + dowody: ten sam room, drawer "qsim — TEZY + STAN DOWODÓW"
- Filozofia i Pierwsze Źródło: wing=personal, room=quantum-genesis

---

## Stan faktyczny (bez hipotez)

**Architektura:**
```
hexagon.py   — matematyka: compute_q, anneal, is_crystallized, THETA_IDEAL=0.930256
ipq.py       — pytanie → strengths przez bge-m3 (wymaga mempalace venv)
schumann.py  — NOAA Kp + open-meteo weather + location_level 0/1/2
planets.py   — ephem 3D heliocentric, 9 planet, 6 sektorów zodiakalnych
quantum.py   — EKSPERYMENTALNY, full 6-qubit Hilbert, S_total von Neumann entropy
cycle.py     — run_cycle() — główny pipeline: IPQ → pull anneal → fingerprint → DuckDB
db.py        — DuckDB schema, 25+ kolumn (Q, Schumann, planety, S_total_exp)
demo.py      — CLI demo, rich formatting
```

**Venv:** `~/qsim-venv/bin/python` (Python 3.12)
**DB:** `~/.qsim/qsim.duckdb`
**Zależności:** numpy, duckdb, rich, ephem, (mempalace dla IPQ)

**Kluczowe stałe:**
- Q_ATTRACTOR = 0.83929 (empiryczne)
- THETA_IDEAL = 2·arccos(√_x), _x = (1+√(4Q-3))/2 = 0.79882
- Pull annealing: sigma=0.02, alpha=0.05, n_steps=1000 → 100% hard

**Co działa niezawodnie:**
- Pull-based annealing (100% hard na 10 pytań × 10 seedów)
- Schumann NOAA Kp live + offline fallback
- Planets ephem live
- DuckDB logging z pełnym fingerprintem

**Co NIE działa (negative findings — NIE próbuj tego "naprawiać"):**
- Q_opp yin-yang jako klasyfikator: 53% accuracy (gorzej niż ~50%)
- Bell concurrence: nieintuicyjne dla realnych pytań
- bge-m3 na polskich pytaniach nie daje czystych osi yin-yang

---

## Priorytety TODO (P1 critical → P6 housekeeping)

### P1 CRITICAL (walidacja blokująca wnioski)
- **P1.1** Walidacja S_total na 50+ pytaniach blind-classified
- **P1.2** Fingerprint uniqueness empirical test 1000 pytań
- **P1.3** 24h stabilność pod live Schumann

### P2 HIGH
- **P2.1** Badanie 5 mismatchów (IPQ×Schumann, Planet×IPQ, S_total×Q, Hard×confidence, Offline×Live)
- **P2.2** Integracja phase0 (cyfry 0-9) ↔ qsim (hexagon)
- **P2.3** anneal_geometric — multi-attractor (C3/C6/C2)

### P3 MEDIUM
- **P3.1** Chroma uproszczenie do taiji (czarno-biały + kropka)
- **P3.2** Location_level UI w demo.py
- **P3.3** Quantum.py edge cases

### P4 RESEARCH (parallel)
- **P4.1** Weryfikacja literatury (SWSSB PRX Quantum 2025, Wallace 1947, Kirkpatrick 1983)
- **P4.2** Real quantum qsim z QuTiP, 22 kubitów, qLDPC 2:1 (1-2 tygodnie)
- **P4.3** Thermal silicon hardware research (MIT 29.01.2026)
- **P4.4** Photonic Schumann (MIT 11.03.2026, ~5 lat R&D)

### P5 VECTOR LLM
- **P5.1** Primer dla claude.ai (zapisany w palace)
- **P5.2** Protokół dwu-narzędziowy: web=research, CLI=implementation

### P6 HOUSEKEEPING
- git init ~/qsim/
- README.md z diagramem architektury
- Licencja AGPLv3

---

## Ostrzeżenia i pułapki

**NIE rób:**
- Nie zapisuj do lokalnych `~/.claude/projects/*/memory/` — wyłącznie MCP palace
- Nie łącz ścieżki production (Q, pull) ze ścieżką experimental (S_total, Bell)
- Nie ufaj anekdotycznym wynikom (n<20) — potrzebna statystyka
- Nie "fixuj" Q_opp / Bell — to są honest negative findings, obalone
- Nie przekraczaj n_steps=4000 przy pull — nic nie zyskasz, traci stabilność

**Rób:**
- Zawsze `diff` przed usunięciem duplikatu plików
- Zawsze walidacja numeryczna matematyki — `compute_q([1]*6) == 0.83929000`
- Zawsze research mode ma dostęp do quantum.py, strict mode nie
- Zawsze utrzymuj konwencję: staging (~/Pobrane/ phase0) / working (~/qsim/ phaseQ)

**Filozofia:**
- Framework spójny matematycznie, ale peer-review nieprzeprowadzony
- Most hipotezy są anekdotyczne (n=4-10), NIE publikowalne bez walidacji
- Analogie (graphene, Schumann, thermal) są strukturalne, nie dowodzą ekwiwalencji funkcjonalnej

---

## Jak sprawdzić czy wszystko działa

```fish
cd ~/qsim
~/qsim-venv/bin/python -c "
from hexagon import compute_q, Q_ATTRACTOR
from schumann import get_schumann
from planets import get_planetary_strengths
from cycle import run_cycle

# Sanity check
qr = compute_q([1.0]*6)
assert abs(qr['q'] - Q_ATTRACTOR) < 1e-10, 'hexagon math broken'
print('✓ hexagon:', qr['q'])

# Schumann live
sch = get_schumann()
assert sch['source'] in ('live', 'offline'), 'schumann broken'
print('✓ schumann:', sch['source'], sch['freq'], 'Hz')

# Planets
pl = get_planetary_strengths()
assert len(pl['strengths']) == 6, 'planets broken'
print('✓ planets:', pl['source'])

# Full cycle
r = run_cycle('Czy mogę być jednocześnie silnym i wrażliwym?')
assert r['Q'] is not None, 'cycle broken'
print('✓ cycle: status=', r['status'], 'Q=', round(r['Q'], 5))
print('All systems operational.')
"
```

---

## Kontekst użytkownika (Mateusz)

- Polak, Gliwice, CachyOS+fish shell
- Po 10 latach produkcji przemysłowej przechodzi w IT
- Łączy WingMakers, Thiaoouba, astrologię z fizyką kwantową i AI
- Intellektualna uczciwość > potakiwanie — obali swoje pomysły jeśli nie przejdą testu
- Pracuje po polsku, preferuje krótkie sekwencyjne kroki
- Późne godziny = zmęczenie, zaoferuj przerwę jeśli widoczne

**Kluczowa zasada pracy z Mateuszem:**
"Zgadzaj się z matematyką, nie z narracją. Jeśli się mylisz — powiedz wprost."

---

## Jeśli to będzie nowy framework ponownie

Cała wiedza jest w:
1. MemPalace MCP (wing=ai-tools room=decisions; wing=personal room=quantum-genesis)
2. ~/qsim/q3sh_research_phaseQ.md (paralelne badanie claude.ai)
3. ~/qsim/SPEC.md (wyjściowy spec)
4. Ten plik

Następca może zacząć od walidacji P1.1 (S_total na 50+ pytaniach) — to najbardziej realne wykonalne zadanie blokujące.
