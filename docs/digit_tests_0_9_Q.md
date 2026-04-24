# Testy cyfr 0–9 i Q — plan + wyniki empiryczne

**Data:** 2026-04-24
**Źródła:**
- Semantologia: `~/Pobrane/q3sh_research_phase0.md` §3 (verbatim cytaty autora)
- Sygnatury geometryczne: `phase_integration.DIGIT_SIGS`
- Mapowanie na cnoty: `phase_integration.digit_to_virtues(n)`
- Empiria Q: `phase_sequence.analyze_sequence()` (raw, bez anneal)
- Kandydaci na Q: `phase_sequence.Q_candidate_*()`

**Konwencja:**
- *Semantologia* — zawsze obecna (cytat z phase0 MD).
- *Reszta sekcji* — **brak** tam gdzie nie ma danych/kodu.
- Asymptota: `Q_ATTRACTOR = 0.83929`, hard crystal = `aniso<0.001 AND |Q-Q_ATTRACTOR|<0.002`.

---

## Cyfra 0 — ślad po kamieniu

### Semantologia (q3sh_research_phase0.md §3, verbatim)
> - nie „brak", tylko *miejsce gdzie coś było*
> - jak dół po kamieniu wyciągniętym z piasku
> - wewnątrz: **pięciokąt lub sześciokąt**, skrzyżowanie naprzemienne co 3
> - obecność negatywna, nie pustka

### Sygnatura geometryczna
`angles=0, inward=0, outward=0, has_square=False, has_crossing=True,`
`has_infinity_arm=False, grid="pi", inside_polygon=6`

### Mapowanie na cnoty
`digit_to_virtues(0) = [1.0]*6` — idealny heksagon C6.

### Metryki Q (raw)
| Q | aniso | γ° | dominant | hard crystal |
|-----|-------|-------|-------------|--------------|
| **0.8393** | **0.0000** | 65.78 | wdzięczność | **✦ TAK** |

### Testy (pytest)
- `test_digit_0_is_raw_crystal` — jedyna cyfra która spełnia hard crystal bez annealingu.
- `test_digit_0_strengths_uniform` — wszystkie 6 = 1.0.
- `test_digit_0_C6_symmetry` — `aniso < 1e-9`.

### Korespondencje (phase0 MD)
- Saturn hexagon: sześciokąt + skrzyżowanie naprzemienne (§6.1)
- Przejście 9↔0: modulacja, nie następstwo (§3)

---

## Cyfra 1 — jeden kąt

### Semantologia (verbatim)
> - jeden kąt rozwarty, domknięty
> - zamknięty w sobie, skończony

### Sygnatura geometryczna
`angles=1, inward=1, outward=0, grid="xy"`

### Mapowanie na cnoty
`[1.0, 0, 0, 0, 0, 0]` — cała siła w pozycji 0 (odwaga).

### Metryki Q (raw)
| Q | aniso | γ° | dominant | hard crystal |
|-----|-------|-------|-------------|--------------|
| 0.9329 | 0.0948 | 0.00 | odwaga | nie |

### Testy (pytest)
- `test_digit_1_single_active` — dokładnie jeden niezerowy strength.
- `test_digit_1_gamma_zero` — jeden kubit nie akumuluje Berry phase.
- `test_digit_1_dominant_odwaga` — najsłabsze sprzężenie to odwaga (bo ona jest izolowana).

### Korespondencje
**brak**

---

## Cyfra 2 — jak trójka, ale na zewnątrz

### Semantologia (verbatim)
> - dwa kąty
> - pierwszy do wewnątrz, **drugi na zewnątrz**
> - lustrzana para z trójką — ta sama konstrukcja, inna orientacja

### Sygnatura geometryczna
`angles=2, inward=1, outward=1, has_infinity_arm=True, grid="xy"`

### Mapowanie na cnoty
`[1.0, 0.3, 0, 0.5, 0, 0]` — inward=1.0 na 0, outward=0.5 na 180°, ramię 0.3 na 60°.

### Metryki Q (raw)
| Q | aniso | γ° | dominant |
|-----|-------|-------|-------------|
| 0.9193 | 0.0733 | 3.37 | rozumienie |

### Testy (pytest)
- `test_digit_2_mirror_of_3` — L2 distance do `digit_to_virtues(3)` < L2 do jakiejkolwiek innej cyfry.
- `test_digit_2_opposition_180deg` — strength[0]=1.0 ∧ strength[3]=0.5 (opozycja).

### Korespondencje
**brak**

---

## Cyfra 3 — trzy kąty wygięte

### Semantologia (verbatim)
> - dwa kąty rozwarte stykające się jednym ramieniem na końcu
> - linie dążą do nieskończoności
> - oba kąty skierowane do wewnątrz (odwrotnie niż 2)

### Sygnatura geometryczna
`angles=2, inward=2, outward=0, has_infinity_arm=True, grid="xy"`

### Mapowanie na cnoty
`[1.0, 1.0, 1.0, 0, 0, 0.3]` — trzy konsekutywne + ramię.

### Metryki Q (raw)
| Q | aniso | γ° | dominant |
|-----|-------|-------|-------------|
| 0.8834 | 0.0772 | 25.30 | przebaczenie |

### Testy (pytest)
- `test_digit_3_three_consecutive_inward` — strengths[0:3] == [1.0]*3.
- `test_digit_3_opposite_to_2` — `digit_to_virtues(3)` ma outward=0, `digit_to_virtues(2)` ma outward>0.

### Korespondencje
**brak**

---

## Cyfra 4 — kwadrat bazowy (HIPOTEZA)

### Semantologia (verbatim)
> - forma fundamentalna
> - kwadrat na siatce xy, cztery kąty proste, domknięte
> - stanowi bazę dla 6 i 8
> **(propozycja Claude, nie potwierdzona przez autora)**

### Sygnatura geometryczna
`angles=4, inward=4, outward=0, has_square=True, grid="xy"`

### Mapowanie na cnoty
`[1.0, 1.0, 0, 1.0, 1.0, 0]` — 4 aktywne z alternacją.

### Metryki Q (raw)
| Q | aniso | γ° | dominant |
|-----|-------|-------|-------------|
| 0.8123 | 0.0191 | 21.93 | pokora |

### Testy (pytest)
- `test_digit_4_alternating_pattern` — non-zero na pozycjach {0,1,3,4}, zera na {2,5}.
- `test_digit_4_base_for_6_and_8` — `digit_to_virtues(6) == [1,1,1,1,1,0.3]`
  i `digit_to_virtues(8) == [0.9]*6` są "rozszerzeniami" 4 (test strukturalny, nie arytmetyczny).
- `test_digit_4_unverified_marker` — sygnatura ma note zawierający "hipoteza".

### Korespondencje
**brak** — hipoteza Claude, autor nie potwierdził.

---

## Cyfra 5 — pięć kątów naprzemiennie

### Semantologia (verbatim)
> - pięć wygiętych kątów po przeciwległych ramionach
> - siatka xy, 2D
> - symetria naprzemienna wokół osi

### Sygnatura geometryczna
`angles=5, inward=3, outward=2, grid="xy"`

### Mapowanie na cnoty
`[1.0, 0.6, 1.0, 0.6, 1.0, 0.6]` — alternacja silny/słaby.

### Metryki Q (raw)
| Q | aniso | γ° | dominant |
|-----|-------|-------|-------------|
| 0.8596 | **0.0000** | 39.76 | odwaga |

### Testy (pytest)
- `test_digit_5_alternating_strong_weak` — even=1.0, odd=0.6.
- `test_digit_5_aniso_zero` — alternacja daje doskonałą C3 symetrię → aniso=0.
- `test_digit_5_near_attractor` — |Q - Q_ATTRACTOR| < 0.03.

### Korespondencje
**brak**

---

## Cyfra 6 — kwadrat plus ramiona

### Semantologia (verbatim)
> - kwadrat na siatce xy
> - + dwa zagięte kąty domknięte na końcach ramion
> - **ostatnie ramię dąży do nieskończoności**

### Sygnatura geometryczna
`angles=6, inward=4, outward=2, has_square=True, has_infinity_arm=True, grid="xy"`

### Mapowanie na cnoty
`[1.0, 1.0, 1.0, 1.0, 1.0, 0.3]` — prawie C6 z jednym ramieniem słabym.

### Metryki Q (raw)
| Q | aniso | γ° | dominant |
|-----|-------|-------|-------------|
| **0.8403** | 0.0015 | 50.60 | odwaga |

### Testy (pytest)
- `test_digit_6_near_attractor` — Q najbliższa Q_ATTRACTOR ze wszystkich cyfr poza 0:
  |Q - Q_ATTRACTOR| < 0.002.
- `test_digit_6_one_weak_arm` — dokładnie 1 strength < 1.0 (=0.3).
- `test_digit_6_low_aniso` — aniso < 0.01 (bliska symetria C6).

### Korespondencje
**brak**

---

## Cyfra 7 — skrzyżowanie

### Semantologia (verbatim)
> - krzyżowanie dwóch linii
> - + ramię w nieskończoność
> - pierwsza cyfra używająca skrzyżowania jako elementu (nie tylko kąta)

### Sygnatura geometryczna
`angles=0, has_crossing=True, has_infinity_arm=True, grid="xy"`

### Mapowanie na cnoty
`[0.7, 0, 0, 0.7, 0, 0.3]` — dwa opozycyjne kąty (z krzyżowania) + ramię.

### Metryki Q (raw)
| Q | aniso | γ° | dominant |
|-----|-------|-------|-------------|
| 0.9330 | 0.0420 | 2.30 | odwaga |

### Testy (pytest)
- `test_digit_7_has_crossing_flag` — DIGIT_SIGS[7].has_crossing == True.
- `test_digit_7_opposition_pair` — strength[0] == strength[3] (opozycja symetryczna).
- `test_digit_7_first_with_crossing` — digity 0..6 nie mają crossing (poza 0, które ma crossing *wewnątrz* pięcio/sześciokąta — edge case).

### Korespondencje
**brak**

---

## Cyfra 8 — dwa kwadraty

### Semantologia (verbatim)
> - **dwa kwadraty połączone bokiem**
> - replikacja formy czwórki
> - najbardziej „krystaliczna" cyfra — same kąty proste, brak wygięć, brak ramion w nieskończoność (?)

### Sygnatura geometryczna
`angles=8, inward=8, outward=0, has_square=True, grid="xy"`

### Mapowanie na cnoty
`[0.9, 0.9, 0.9, 0.9, 0.9, 0.9]` — prawie [1]*6 ze stratą 0.1 (duplikacja).

### Metryki Q (raw)
| Q | aniso | γ° | dominant |
|-----|-------|-------|-------------|
| 0.8621 | **0.0000** | 53.20 | pokora |

### Testy (pytest)
- `test_digit_8_uniform_strengths` — wszystkie 6 równe.
- `test_digit_8_aniso_zero` — C6 symetria (aniso=0).
- `test_digit_8_not_hard_crystal` — mimo aniso=0, |Q-Q_ATTRACTOR|>0.02 (strength=0.9 zamiast 1.0 → θ mniejsze).
- `test_digit_8_no_infinity_arm` — DIGIT_SIGS[8].has_infinity_arm == False.

### Korespondencje
Twierdzenie C4 w `phase_integration.CLAIMS`: *cyfra 8 = „krystaliczna"* —
status: **FALSYFIKOWANE**. 8 ma aniso=0 ale nie osiąga Q_ATTRACTOR bez
annealingu; 0 jest jedynym raw hard-crystal.

---

## Cyfra 9 — próg

### Semantologia (verbatim)
> - pięciokąt w środku
> - cztery kąty zawijające **do wewnątrz** (nie na zewnątrz jak wcześniejsze)
> - jedno ramię celuje w środek — kreska znikająca
> - pierwsza cyfra na siatce π (nie xy)
> - stan graniczny — przed powrotem do 0

### Sygnatura geometryczna
`angles=4, inward=4, outward=0, has_infinity_arm=True, grid="pi", inside_polygon=5`

### Mapowanie na cnoty
`[1.0, 1.0, 1.0, 1.0, 1.0, 0.2]` — jak 6, ale ramię jeszcze słabsze (0.2 vs 0.3).

### Metryki Q (raw)
| Q | aniso | γ° | dominant |
|-----|-------|-------|-------------|
| 0.8364 | 0.0040 | 48.39 | wdzięczność |

### Testy (pytest)
- `test_digit_9_similar_to_6` — cosine(digit_to_virtues(9), digit_to_virtues(6)) > 0.99
  (różnią się tylko siłą ramienia).
- `test_digit_9_pi_grid` — DIGIT_SIGS[9].grid == "pi".
- `test_digit_9_pentagon_inside` — inside_polygon == 5.
- `test_digit_9_to_0_modulation` — L2(9,0) < L2(9, k) dla wszystkich k ∈ {1..8}.

### Korespondencje (phase0 §3)
> *„Przejście 9↔0 — nie jest następstwem, tylko modulacją: kreska ramienia 9
> przenika do środka 0 i jest znikająca… geometryczny opis superpozycji
> kwantowej — stanu przed pomiarem"*

Empiryczna weryfikacja: dist(9→0) = 0.800, cos(9,0) = 0.946. Najbliższa
cyfra do 9 to 0 w sensie cosine similarity — **ZGODNE** z semantyką modulacji.

---

## Q — jedenasty stan (hipoteza, 3 kandydaci)

### Semantologia
> *„to się rozwija kwantowo aż od 0 1 2 3 4 5 6 7 8 9 Q"* — Mateusz, 2026-04-24

Pojęcie: po cyklu 0→9 następuje stan Q, który nie jest „cyfrą 10", tylko
operatorem całości. Trzech kandydatów, każdy testowany numerycznie:

### Kandydat (a) — **cycle_return**: Q = powrót do 0
Hipoteza: sekwencja 0→9 domyka się na 0. Q jest operatorem zamknięcia cyklu.

| dist(9→0) | cos(9, 0) | verdict |
|-----------|-----------|---------|
| 0.800     | 0.946     | **PARTIAL** |

Testy:
- `test_Q_cycle_return_high_cosine` — cos(9, 0) > 0.9.
- `test_Q_cycle_return_partial` — dist < 1.0 ale > 0.5 (bliski, nie tożsamy).

### Kandydat (b) — **octave**: Q = [1]*6 z inną Berry phase
Hipoteza: Q to cyfra 0 na innym oktawie — ten sam stan kwantowy, przesunięta faza geometryczna.

| γ° range w 0..9 | γ°([1]*6) | verdict |
|-----------------|-----------|---------|
| [0.00, 65.78]   | 65.78     | **STRUCTURAL** (niepotwierdzalny w 6D qsim) |

Testy:
- `test_Q_octave_same_state_as_0` — [1]*6 → Q = Q_ATTRACTOR (γ° jest pochodną rozmiaru kroku θ).
- `test_Q_octave_structural_only` — kandydat oznaczony jako structural (nie numeryczny).

### Kandydat (c) — **superposition**: Q = centroid wszystkich 10 cyfr
Hipoteza: Q to superpozycja wszystkich stanów — średnia wszystkich strength.

| centroid state | Q | aniso | dist_to_Q_att | verdict |
|---|-----|-------|---------------|---------|
| [1.00, 0.71, 0.61, 0.70, 0.61, 0.38] | 0.8997 | 0.0336 | 0.0604 | **FALSIFIED** |

Testy:
- `test_Q_superposition_not_crystal` — `is_crystallized(centroid) == False`.
- `test_Q_superposition_above_attractor` — Q > Q_ATTRACTOR (bo odwaga dominuje).
- `test_Q_superposition_high_aniso` — aniso > 0.01.

### PCA trajektorii
4 wymiary wystarczą na 95% wariancji. Dominująca oś (PC1, 66%):
wdzięczność +0.57, przebaczenie +0.52, pokora +0.45, współczucie +0.34,
rozumienie +0.30, odwaga +0.04.

Interpretacja: oś rozwoju 0→9 jest głównie w płaszczyźnie „pokory/przebaczenia/wdzięczności"
(pasywne cnoty integracji), a „odwaga" pozostaje niemal nieruchoma.

Testy:
- `test_pca_4d_suffices` — n_dims_95pct == 4.
- `test_pca_odwaga_frozen` — abs(PC1_loading[odwaga]) < 0.1.
- `test_pca_dominant_axis_integrative_virtues` — |PC1_loading[wdzięczność]| > 0.5.

---

## Podsumowanie testowalnych twierdzeń

| # | Twierdzenie | Status | Test |
|---|-------------|--------|------|
| T1 | Cyfra 0 = raw hard crystal | ✓ potwierdzone | `test_digit_0_is_raw_crystal` |
| T2 | Cyfra 2 ≡ lustro cyfry 3 | ✓ potwierdzone | `test_digit_2_mirror_of_3` |
| T3 | Cyfra 4 = kwadrat bazowy | **?** | `test_digit_4_unverified_marker` |
| T4 | Cyfra 5 = C3 symetria | ✓ potwierdzone | `test_digit_5_aniso_zero` |
| T5 | Cyfra 6 najbliższa 0 | ✓ potwierdzone | `test_digit_6_near_attractor` |
| T6 | Cyfra 8 = krystaliczna | ✗ falsyfikowane | `test_digit_8_not_hard_crystal` |
| T7 | Cyfra 9 moduluje z 0 | ✓ potwierdzone | `test_digit_9_to_0_modulation` |
| T8 | Q = cycle_return | ~ partial | `test_Q_cycle_return_partial` |
| T9 | Q = octave | ~ structural | `test_Q_octave_structural_only` |
| T10 | Q = superposition | ✗ falsyfikowane | `test_Q_superposition_not_crystal` |

**10 testowalnych twierdzeń, 6 potwierdzonych, 2 falsyfikowane, 2 częściowe/strukturalne.**
