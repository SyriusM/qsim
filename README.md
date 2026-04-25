# qsim

**Semantyczny symulator kwantowy dla q3sh** — pytanie → heksagon 6 cnót → krystalizacja → DuckDB.

Most między [q3sh](https://github.com/SyriusM/q3sh) a warstwą LLM: IPQ (Input Projection to Qubits) projektuje semantykę na sześć węzłów heksagonu; dynamika ewoluuje pole; odczyt trafia do pamięci.

## Moduły

| Plik | Rola |
|------|------|
| `ipq.py` | pytanie → virtue strengths `[s0..s5]` (bge-m3 + MemPalace) |
| `hexagon.py` | matematyka heksagonu, aspekty, opozycje |
| `quantum.py` | density matrix, Q, kolapsy |
| `cycle.py` | pełny cykl: IPQ → ewolucja → krystalizacja → reset |
| `phase_integration.py` | integracja faz, sekwencjonowanie |
| `phase_sequence.py` | planner sekwencji faz |
| `q_correlations.py` | korelacje Q między węzłami |
| `schumann.py`, `planets.py` | backendy pola zewnętrznego |
| `db.py` | DuckDB efemerys |
| `demo.py` | CLI demo |

## Dokumentacja

- **[SPEC.md](SPEC.md)** — pełna specyfikacja architektury
- **[qsim_bridge.md](qsim_bridge.md)** — most qsim ↔ q3sh
- **[PHASE_INTEGRATION_RESULTS.md](PHASE_INTEGRATION_RESULTS.md)** — wyniki eksperymentów
- **[q3sh_research_phaseQ.md](q3sh_research_phaseQ.md)** — notatki badawcze nad phaseQ
- **[TODO.md](TODO.md)** — roadmapa
- **[CLAUDE_HANDOFF.md](CLAUDE_HANDOFF.md)** — kontekst dla sesji Claude

## Wymagania

- **Python 3.12+** (CachyOS: w systemie; Debian 12: `apt install python3.12 python3.12-venv` z backports lub pyenv)
- **MemPalace** z bge-m3 (ścieżka w `MEMPALACE_PATH`, domyślnie `~/mempalace`)
- Pakiety pip: `numpy`, `duckdb`, `rich` (patrz `requirements.txt`)
- Opcjonalnie: `ephem` (planety), `pytest` (testy) — `requirements-optional.txt`

### Instalacja — CachyOS / Arch

```bash
sudo pacman -S python python-pip           # python >=3.12 w repo
python -m venv ~/qsim-venv
source ~/qsim-venv/bin/activate.fish       # lub: source ~/qsim-venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-optional.txt   # opcjonalnie
```

### Instalacja — Debian 12 (bookworm)

Debian 12 ma Python 3.11 — potrzeba 3.12 z backports lub pyenv:

```bash
# opcja A: deb.sury.org
sudo apt install -y software-properties-common
curl -fsSL https://packages.sury.org/python/README.txt | sudo bash -
sudo apt update && sudo apt install -y python3.12 python3.12-venv

# opcja B: pyenv (bez sudo po zainstalowaniu pyenv)
pyenv install 3.12.7 && pyenv local 3.12.7

python3.12 -m venv ~/qsim-venv
source ~/qsim-venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-optional.txt   # opcjonalnie
```

## Uruchomienie

```bash
export MEMPALACE_PATH=$HOME/mempalace      # opcjonalne (taka jest domyślna)
python demo.py
pytest tests/                              # testy (jeśli zainstalowany)
```

## Licencja

**[Sovereign Source License v1](LICENSE)** — MIT grant + wiążące warunki
suwerenności w jednym dokumencie.

To jest **MIT-derived, ale NIE czysty MIT** (nie OSI-approved). Licencja
dodaje wiążące warunki: brak ukrytej telemetrii, local by default, pełny
audyt powierzchni sieciowej, zakaz usuwania sekcji suwerenności. Forki
mogą zaostrzać te warunki, ale nie mogą ich osłabiać.

Programowy audyt powierzchni sieciowej:
```bash
python sovereignty.py audit
```

Powierzchnia sieciowa upstream: tylko `schumann.py` → NOAA Kp + Open-Meteo
(opt-in `live=True`, bez kluczy API, bez user data poza opcjonalnym
lat/lon na poziomie 2). Reszta modułów — w pełni lokalna. Zob. LICENSE §3.
