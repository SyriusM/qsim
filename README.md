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

- Python 3.12
- [MemPalace](https://github.com/SyriusM/mempalace) z bge-m3 (ścieżka w `MEMPALACE_PATH`, domyślnie `~/mempalace`)
- DuckDB

## Uruchomienie

```bash
export MEMPALACE_PATH=$HOME/mempalace  # opcjonalne
python demo.py
```

## Licencja

Suwerenność danych: qsim nie wysyła żadnych danych użytkownika do zewnętrznych API. Cała logika działa lokalnie.
