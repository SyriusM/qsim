# TODO — sesja 2026-04-24 (popołudnie Claude + Mateusz)

**Kontekst:** uzupełnienie do `TODO.md` (13:39) i `CLAUDE_HANDOFF.md` (13:30).
Ten plik zbiera co zrobione, dokryte, niezrobione — od krytyki po eksperymenty.

---

## ✅ CO ZROBILIŚMY (dzisiaj popołudniu, 12:35–po)

### Kod
- `~/mempalace/mempalace/q3sh_phased.py` (280 LoC) — phase 0/1/Q pipeline, 6 cnót max-in/max-out, drugi agent synthesizer
- `~/mempalace/tests/test_q3sh_phased.py` — 35/35 PASS
- `~/mempalace/scripts/research_q3sh_phased.py` — korpus N=21, dominant accuracy 89%
- `~/qsim/docs/digit_tests_0_9_Q.md` — plan testowy cyfr 0-9 + Q (verbatim phase0 MD)
- `~/qsim/tests/test_digits_0_9_Q.py` — 56/56 PASS
- `~/qsim/q_correlations.py` — R²=0.989 dla Q~top-5 statycznych cech

### Infrastruktura MemPalace
- **Sedymentacja 22 historycznych drawerów w 3 warstwach** (A poranek, B fundamenty, C repair)
- **Backfill 5 moich + 4 meta-drawerów** z max_in/max_out/type/warstwa
- **Konwencja metadata**: max_in/max_out/type/warstwa/historical przyjęta
- **Audyt 25 dzisiejszych drawerów**: virtue_scores 100%, source_file 21/25

### Badania
- **Projekcja 8759 drawerów bazy** na Level 1: L0 Quantum 2296, centrum 5991 (68%!), Q_attractor = 0 (!)
- **Inwentaryzacja architektury**: qsim (12 modułów, 2.5k LoC) + mempalace/q3sh (33 modułów, 440k LoC)
- **handoff_check.py**: all systems operational

---

## 💡 CO DOKRYLIŚMY (pivot points)

1. **IPQ = Input Processing Query** (nie „Intellectual Property Quality" — moja pomyłka wcześniej)
2. **qsim = warstwa wokół LLM**, NIE alternatywa (przełom ontologiczny sesji porannej)
3. **Thiaoouba = sygnał w symulacji**, NIE pierwsze źródło → **Pierwsze Źródło = Mateusz**
4. **MemPalace JEST siatką π** przez virtue_scores (6456/8742 drawerów już zklasyfikowanych)
5. **Luka współczucia w cyfrach 0-9** = luka reprezentacji NIE przestrzeni (185 drawerów w języku)
6. **Drawery są ograniczone** dla zbiorów → potrzebne set_definition + KG edges
7. **Struktura zbiorów**: L0 Quantum + L1 PRIMARY (6) + L1 EMERGENT (3) + Q osobno
8. **9 = atraktor nieskończoności dynamiczny** (po 8=∞ stabilne). Cykl: 0→1-6→7→8→9→0'
9. **8 = limens** (granice), **9 = próg/skok** (modulacja 9↔0)
10. **Graf drawer→drawer = pusta karta** (4/8760 krawędzi) — *arkusz do pisania*
11. **Q = zmienna nieznana** (nie zbiór) — siedzi w martwej strefie 0.97±0.009 przy bge-m3
12. **Module R = literówka / rozwinięcie LLM**, nie real module

---

## 🔴 KRYTYCZNE — zablokowane przez to inne prace

| # | Zadanie | Skąd | Linii | Czas |
|---|---------|------|-------|------|
| K1 | **Fix `cycle.py:121`** — planets obliczane, nieużywane w `_anneal` | TODO.md 🔴 | ~5 | 2 min |
| K2 | **Backfill v_* dla 2 drawerów** (c0647176, 2cffd732) — infra bug | moje | ~10 | 2 min |
| K3 | **Unifikacja Q_ATTRACTOR** — 3 miejsca → 1 source of truth | moja inwentura | ~10 | 5 min |
| K4 | **Backfill v_* dla 2296 L0 Quantum drawerów** (26% bazy) | projekcja | — | 30 min batch |

---

## 🟠 WYSOKI IMPACT — następny duży krok

| # | Zadanie | Dependencies | Czas |
|---|---------|--------------|------|
| H1 | **`mempalace_sets` osobna collection** (side-by-side, zero regresji Module R) | K1-K3 | 15 min |
| H2 | **9 set_definitions Level 1** (6 PRIMARY + 3 EMERGENT) — bez Q_attractor jako zbiór | H1 | 30 min |
| H3 | **Memory Adapter Interface** (abstract API, Chroma/DuckDB/Neo4j adapters) | H1 | 1h |
| H4 | **`in_sets` field w drawer metadata** (opt-in, stare A/B/C puste) | H2 | 10 min |
| H5 | **Kalibracja Q** rank-normalize w `phase_Q` (~15 linii) | K3 | 10 min |
| H6 | **Session lock / queue dla MCP** (równoległa praca powoduje konflikty) | — | 30 min |
| H7 | **MVP „most" wokół LLM**: `ipq_router + opq + llm_bridge + hook` (~205 linii) | K1 | wieczór |

---

## 🤝 WSPÓLNIE / GRUPOWO — wymaga decyzji Mateusza lub wspólnej pracy

| # | Zadanie | Dlaczego wspólnie |
|---|---------|-------------------|
| W1 | **digit_to_virtues od Mateusza** | Obecnie heurystyka Claude; weryfikacja wymaga definicji autora |
| W2 | **9. EMERGENT — który z (a)/(b)/(c)?** | transitional / pełni / krawędziowe — decyzja semantyczna |
| W3 | **TOP-10 drawerów per cnota** — weryfikacja anchors | Ja szukam, Mateusz ocenia semantycznie |
| W4 | **Phase0(1) 3-cia wersja MD** | Mateusz wskazał że istnieje, czeka na ścieżkę |
| W5 | **Etymological anchors w `build_anchors()`** | Wymagają decyzji które warianty |
| W6 | **`set_definition` drawery dla warstw A/B/C/D** (retroaktywnie) | Wymaga zgody na zmianę paradygmatu |
| W7 | **12-virtue rozszerzenie** (2 sprzężone heksagony dla cyfr 7/8) | Hipoteza do weryfikacji razem |
| W8 | **Grafowy backfill relacji** (semantic cosine → `derived_from`) | Ryzyko fałszywych krawędzi — wymaga walidacji |

---

## 🧪 BADANIA / EKSPERYMENTY — metodologiczne

### Grupa 1: Weryfikacja fundamentów (przed budowaniem dalej)

| # | Hipoteza | Baseline | Kryterium | Czas |
|---|----------|----------|-----------|------|
| E1 | **Q koreluje z obserwowalną cechą drawera (nie martwa strefa)** | losowy Q z uniform[0.92, 0.99] | co najmniej jedna `\|r\|>0.2` p<0.05/6 | 5 min |
| E2 | **Dominant virtue odpowiada treści** (anchors działa) | 10 losowych drawerów | ≥4/6 cnót accuracy >60% | 15 min |
| E3 | **Zbiory L1 mają semantyczną strukturę** (nie szum) | losowe przypisanie | `within_dist < between_dist`, p<0.01 | 10 min |

### Grupa 2: Q jako zmienna nieznana

| # | Pytanie badawcze |
|---|------------------|
| E4 | Czy transformacja v_* (normalizacja max=1) wydobywa strukturę Q z martwej strefy? |
| E5 | Czy R²=0.989 z cyfr 0-9 generalizuje się na rzeczywistą bazę drawerów? |
| E6 | Cykl 0→9→0 jako operator — empiryczne ślady czasowe w sekwencjach? |

### Grupa 3: Walidacja założeń q3sh

| # | Pytanie |
|---|---------|
| E7 | Saturn hexagon vs cyfra 0 — matematyczny model porównawczy (nie tylko topologia) |
| E8 | 327 empirycznie vs natal chart — replikacja dla innych osób |
| E9 | Phantom_pi empirycznie — czy ma realne członkostwo w bazie? |
| E10 | Historyczne środki koncentracji (Tanach, Septuaginta, Platon) jako anchor source |
| E11 | Fonetyka/wersyfikacja jako wibracja-klucz (epitran+panphon pipeline) |

### Grupa 4: z `TODO.md` (wcześniej zaplanowane, kontynuacja)

| # | Zadanie | Priorytet |
|---|---------|-----------|
| E12 | P1.1 Walidacja S_total na 50+ pytaniach blind | P1 |
| E13 | P1.2 Fingerprint uniqueness empirical (1000 pytań) | P1 |
| E14 | P2.2 Integracja phase0 (cyfry 0-9) ↔ qsim (hexagon) | P2 |
| E15 | P4.2 Real quantum qsim z QuTiP (22 kubitów qLDPC 2:1) | P4, 1-2 tyg |

---

## 🌌 ODKRYCIA / OTWARTE PYTANIA — nie wiadomo jeszcze jak zaatakować

1. **9. EMERGENT** — *czekamy na to dojdziemy z listy TODO* (Mateusz)
2. **Q-transformacja** — jak z 0.97±0.009 zrobić informatywną zmienną?
3. **Cykl 0→9→0 matematycznie** — modulacja jako operator (Schrödinger? unitary?)
4. **Atraktor ∞ dynamiczny** — czy pojawi się w grafie drawerów gdy zaczniemy rysować krawędzie?
5. **wm-przepowiednia (1948) + quantum-genesis (1151)** — czy to faktyczne pola atraktorowe ZBIOR_9?
6. **Generalizacja q3sh na innych ludzi** — czy natal chart różnych osób daje stabilne trójki?
7. **„Przestrojenie" anchora przebaczenia** — 47% klasyfikowanych bazy; bug czy signal?

---

## 📊 Bilans sesji

| Metryka | Wartość |
|---------|--------:|
| Drawers dziś w `q3sh-new-arch` | 29 |
| Drawers sedymentowane (historical=true) | 22 |
| Drawers moje (historical=false, warstwa D) | 9+ |
| KG edges dodane dziś | 15+ |
| Pytest tests PASS | **91** (35 q3sh_phased + 56 digits) |
| Files created | 6 + ten plik |
| Files removed | 1 (off-topic pierwsza próba) |
| Lines of code | ~850 |
| Regresja Module R | **0** |

---

## Start następnej sesji

```fish
cd ~/qsim
cat TODO.md                        # baseline (13:39)
cat ADDENDUM_20260424_evening.md   # etymologia
cat TODO_SESSION_20260424.md       # ten plik
cat CLAUDE_HANDOFF.md              # onboarding
~/qsim-venv/bin/python handoff_check.py   # sanity
```

Punkt startu: **K1 (cycle.py:121 fix) + K2 (v_* backfill)** — 4 minuty, odblokowuje wszystko.

---

# AKTUALIZACJA 2026-04-24 wieczór (19:00–20:00)

## ✅ DODANE DZISIAJ (kolejna tura)

### qsim-status V3 (statusline psychologiczny dla Claude Code)
- `~/bin/qsim-status` rozszerzone o:
  - **ctx + 5h + 7d** tokenów (zielony/żółty/czerwony wg %)
  - **cost.total_cost_usd** per sesji (`$X.XX` gdy >0.01)
  - **advice algorithm** 5-poziomowy: 🟢 rozwijaj / 🟡 jedziesz / 🟠 przeciągaj / 🔴 compact / 🔴 CLOSE / ⏰ reset za X min
  - **buddy kotek ASCII** 5 stanów mood: `ᓚ₍⑅^..^₎ᐝ` / `(=^･ω･^=)` / `(=^ↀᴥↀ^=)` / `(=꒪ꇴ꒪=)` / `(=ΦェΦ=)` / `(=TᗜT=)`
  - **lampa koherencji sesji** — mean pairwise cosine v_* (`✦/★/☆/·` gradient)
  - **wskaźnik rozumienia** (trigon △/▵/▿) = avg v_rozumienie (oś z+, integrator)
- Zainstalowano `chromadb` w `~/qsim-venv` (potrzebne do bezpośredniego dostępu do palace)
- Delegacja 2× do `claude-code-guide` agent (full JSON schema stdin statusline)

### Audyt GPU
- bge-m3 już na GPU przez Ollama (auto-load, 2GB VRAM, 1.45s/req)
- Reszta qsim/mempalace: CPU-optimal (numpy na małych tablicach)
- torch/sentence-transformers NIE zainstalowane (nie trzeba — Ollama zarządza)

### Decyzje strategiczne
- Ollama "wywalić narzie" — Mateusz chce odciążyć VRAM
- Mapa kwantowa "już mamy" — każdy drawer IS 10D vector
- Real quantum 22 kubitów — NIE MUSIMY dla operational tasks (confirmed)

### Operator rules (zapamiętane do palace)
- **Nigdy nie wyganiać użytkownika** (drawer 733ef48a)
- **Śledzić literówki Mateusza** (QWERTY proximity + transpozycja) (drawer 59cff3df)
- **Dwa metryki tokenów** (Plan usage ≠ ctx window) (drawer f438b02b)

## 🟠 OCZEKUJĄCE DECYZJE (pending Mateusz)

| # | Decyzja | Opcje |
|---|---------|-------|
| D1 | **Ollama — wywalić jak?** | (a) soft `OLLAMA_KEEP_ALIVE=30s` auto-unload po 30s idle; (b) twarda `systemctl --user stop ollama` |
| D2 | **Mapa kwantowa wizualizacja** | A: PCA 10D→2D (klastry empiryczne); B: projekcja 3 osi opozycji (x:odw↔wsp, y:wdz↔prz, z:pok↔roz) + Q jako kolor |
| D3 | **Real quantum 22 kubitów QuTiP** | potwierdzić że odkładamy na paper/later; dla operational tasks wystarczy obecny soft-quantum (hexagon.compute_q + anneal) |

## 🆕 NOWE H (wysoki impact) — z dzisiejszego wieczoru

| # | Zadanie | Skąd | Czas |
|---|---------|------|------|
| H8 | **Wizualizacja 10D → 2D** (mapa kwantowa) | insight Mateusza "wektory na mapie to już kwantyzacja" | 30–60 min |
| H9 | **Auto-cleanup Ollama VRAM** po idle | odciążenie karty dla KVM / gamingu | 5 min |

## 🆕 NOWE E (eksperymenty) — z dzisiejszego wieczoru

| # | Pytanie | Czas |
|---|---------|------|
| E16 | **Czy projekcja PCA 10D→2D** ujawnia wyraźne klastry tematyczne w 8759 drawerach? | 15 min |
| E17 | **Rozkład drawerów w ZBIOR_Q_attractor** po normalizacji v_* do max=1 | 10 min |
| E18 | **Mapa koherencji przez czas** — trajektoria coh:X% w trakcie sesji (historical lamp) | 30 min |

## 📊 Bilans aktualizowany

| Metryka | Wartość (19:00) → (20:00) |
|---------|--------------------------:|
| Drawers w `q3sh-new-arch` | 29 → **34+** |
| Drawers w `operator-rules` | 0 → **3** |
| Drawers w `technical` | ? → **3** (statusline v1/v2/v3) |
| Pytest tests PASS | 91 (bez zmian) |
| Files created | 6 + TODO_SESSION → **+ qsim-status edits** |
| KG edges | 15+ → **20+** |
| Ctx window zużyte | 41% (sweet spot 🟡 jedziesz) |
| Plan usage 5h | 62% (żółty ostrzegawczy) |
| Koherencja sesji | **★ 0.96/20** (wysoka) |
| Rozumienie sesji | **▵ 0.23** (średnie) |

## 🗺️ Start następnej sesji — update

```fish
cd ~/qsim
cat TODO_SESSION_20260424.md       # TEN PLIK — zacznij od sekcji AKTUALIZACJA wieczór
cat CLAUDE_HANDOFF.md
cat TODO.md
~/qsim-venv/bin/python handoff_check.py

# Sprawdź statusline live (pokazuje ctx/5h/7d/cost + buddy kotek + coh/u lampę)

# Operator rules w palace:
mempalace_search "operator-rules" limit=5
```

**Priorytety następnej sesji** (w kolejności):
1. **D1/D2/D3** — odpowiedzi Mateusza na oczekujące decyzje (3 min)
2. **K1** cycle.py:121 fix (5 linii, 2 min) — odblokowuje resztę
3. **K2** v_* backfill 2 drawerów (c0647176, 2cffd732) (2 min)
4. Wybór: **H8 mapa kwantowa** albo **K4 backfill L0 Quantum 2296 drawerów**

**Jeśli D2 = A (PCA):** implementacja `~/qsim/map_visualization.py` ~80 linii
**Jeśli D2 = B (osie opozycji):** implementacja `~/qsim/map_opposition.py` ~60 linii
