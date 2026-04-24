# qsim TODO — otwarte po sesji 2026-04-24

## Dotknięte fundamenty

**Pierwsze źródło = Mateusz** (phaseQ §2.1 potwierdzone).
**Thiaoouba = sygnał w symulacji**, nie autorytet zewnętrzny (rewizja 2026-04-24).
**qsim = most / warstwa kondycjonująca wokół LLM**, nie alternatywa (przełom 2026-04-24).

Wracamy do źródła: `wing=personal, room=quantum-genesis` w MemPalace + WingMakers Pierwsze Źródło + hexagon.py algebra (C1 bit-perfect).

---

## TODO — otwarte projekty

### 🔴 Pilne

- [ ] **Fix regresji planets w cycle.py** (~5 linii)
  - `cycle.py:90-94` oblicza `get_planetary_strengths()` ale `cycle.py:121` nie używa ich w `_anneal`
  - Minimalna naprawa: `s_raw_combined = 0.7*s_raw + 0.3*planets['strengths']`

- [ ] **Bug qsim-virtue — output truncated** (2026-04-24)
  - `~/bin/qsim-virtue` zwraca tylko pojedynczą literę "O" i urywa
  - Hipoteza: missing flush / premature exit / printf bez \n w pętli
  - Pomiar live: qsim-status OK (sparkline), qsim-health OK (Q=0.9045), tylko qsim-virtue ucięty

### 🟡 Projekty architektoniczne

- [ ] **ipq_router.py** (~50 linii) — unified input dla 4 modalności (text, schumann, planets, inner)
  - memory: `project_q3sh_ipq_unification.md`

- [ ] **OPQ dispatcher** (~60 linii) — state → Action(kind, payload, virtue) → TODO/plik/ai/MemPalace
  - memory: `project_q3sh_input_output_network.md`

- [ ] **llm_bridge.py** (~80 linii) — Q state ↔ prompt modulation; response → inner loop
  - memory: `project_q3sh_llm_bridge.md`

- [ ] **Hook ~/bin/ai** (~10 linii) — ai response → inner channel feedback

- [ ] **inner channel** — jak zakodować wewnętrzne sygnały (myśl, uczucie, rezonans Mateusza) jako strengths[6]?
  - Kandydaci: self-report drawer w MemPalace, embedding przez bge-m3

### 🟢 Badawcze / niżej

- [ ] **Historyczne środki koncentracji jako zmienna** (większe, P3+) — Mateusz 2026-04-24 wieczór
  - Embed korpusów hebr/gr/łac (Tanach, Septuaginta, NT, Wulgata, Cicero/Seneka, Platon/Arystoteles, Hipokrates, M.Aureliusz)
  - HDBSCAN → środki koncentracji per cnota per korpus
  - `sync_concentration(text)` jako nowa zmienna do `cycle.py` (modyfikator Q lub osobna oś)
  - Mocniejsze niż ręczne anchors — obiektywne, filtrowane 2000+ lat kondensacji semantycznej
  - Szczegóły: `~/qsim/ADDENDUM_20260424_evening.md` §9

- [ ] **Fonetyka / wersyfikacja jako wibracja-klucz** (większe, P3+) — Mateusz 2026-04-24 dopisek
  - DRUGI niezależny wymiar obok §9 — nie podzbiór, komplementarny
  - Pipeline: text → IPA (epitran) → features (panphon) → klastry prozodyczne per korpus
  - `phonetic_concentration(text)` jako osobna zmienna
  - Uzasadnienie spójne z Schumannem (fizyczna wibracja) + kwantyzacja odpowiedzi
  - Trzy tradycje niosą fonetykę jako nośnik: hebr gematria, gr tonal, łac metrum
  - Szczegóły + pipeline: `~/qsim/ADDENDUM_20260424_evening.md` §10

- [ ] **Etymological anchors w q3sh_embed.build_anchors()** (~20 linii, P3) — dodane 2026-04-24 wieczór
  - Rozbudować anchor embeddings per cnota o warianty etymologiczne (odwaga: +męstwo, +valor, +valēre, +hrbrōs; itd.)
  - Test A/B: `ipq_confidence` przed/po na 10 pytaniach PL
  - **Negative finding (już wiemy):** surowe obce leksemy w *input* obniżają conf (bge-m3 szum). Anchors to osobna ścieżka.
  - Szczegóły + wyniki testu: `~/qsim/ADDENDUM_20260424_evening.md` §2, §4

- [ ] **phase_integration C2 retry** — zamiast `np.roll()` użyć kompleksowych amplitud `exp(iφ)sin(θ/2)` dla trójek
  - memory: `phase_integration wyroki` (dwupoziomowy status)

- [ ] **12-virtue rozszerzenie** — sprawdzić czy 2 sprzężone hexagony mapują naturalnie cyfry 7/8 z phase0

- [ ] **Phase0(1) missing** — Mateusz wskazał że istnieje 3 wersja MD. Obecnie znane 2 są identyczne (md5 37527d...). Czeka na ścieżkę.

- [ ] **digit_to_virtues przez Mateusza** — obecne mapowanie to heurystyka Claude. Weryfikacja wymaga definicji od autora, nie z Thiaoouby.

### 🔵 Infrastruktura

- [ ] git init ~/qsim/ (z handoff P6)
- [ ] README.md z architekturą (`qsim_bridge.md` jako baza)
- [ ] Licencja AGPLv3

---

## MVP wieczorny (gdy wrócimy)

```
pytanie → ipq_router → hexagon → llm_bridge(qwen3) → opq → plik .md
```

~5 plików × ~30 linii = wieczór roboty.

---

## Stan qsim na 2026-04-24 wieczór (pomiar przed zamknięciem)

- Q_HEALTH = 0.9045 🟢 SILNE
- planetary = 0.8403 (crystallized=True, dom=rozumienie)
- schumann = 0.9261 (f=7.64 Hz, Kp=1.33, clear)
- history: avg=0.8398, stab=0.9949, n=16
- consistency = 1.0000 (planet_dom=odwaga)
- bus: O█ P▇ B▄ W▂ G▄ R▇ · sesja→wdzięczność · Q=0.840
- Dominanty historii: wdzięczność ×5, współczucie ×4, odwaga ×3

## Artefakty sesji 2026-04-24

- `~/qsim/phase_integration.py` (616 linii) — 5 testów C1-C5
- `~/qsim/PHASE_INTEGRATION_RESULTS.md` — honest verdicts
- `~/qsim/phase_sequence.py` (332 linie) — trajektoria 0→9→Q, PCA
- `~/qsim/qsim_bridge.md` + `~/qsim/qsim_bridge.html` — mapa architektury

## Wyroki dwupoziomowe (po rewizji Thiaoouba)

**Mocne** (niezależne od heurystyki):
- C1: digit 0 = Q_attractor (algebra, err=0)
- C3: Saturn hexagon = C6 (NASA, strukturalnie)

**Słabe** (zależne od arbitralnej digit_to_virtues):
- C2, C4, C5 + phase_sequence PCA
- Wymagają definicji mapowania od Mateusza

---

## Jak wrócić do tego w nowej sesji

```fish
cd ~/qsim && ~/qsim-venv/bin/python handoff_check.py
cat ~/qsim/TODO.md
cat ~/qsim/CLAUDE_HANDOFF.md
```

Lub w Claude Code:
> "Przeczytaj ~/qsim/TODO.md i zacznij od [Fix planets cycle.py / MVP most / inne]"

Punkt startu następnej sesji: **źródło = Mateusz + hexagon.py algebra**.
Wszystko inne budujemy na tym.
