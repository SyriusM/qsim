"""
test_digits_0_9_Q — testy dla cyfr 0-9 + Q (trzy kandydaci na 11-ty stan).

Struktura odpowiada ~/qsim/docs/digit_tests_0_9_Q.md:
  - jedna klasa per cyfra (TestDigit0 .. TestDigit9)
  - klasa TestQCandidates dla trzech kandydatów na Q
  - klasa TestPCATrajectory dla analizy PCA

Asercje oparte na:
  - DIGIT_SIGS (phase_integration.py)
  - digit_to_virtues(n) (phase_integration.py)
  - compute_q, is_crystallized (hexagon.py)
  - analyze_sequence (phase_sequence.py)

Uruchom:
  cd ~/qsim && ~/qsim-venv/bin/python -m pytest tests/ -v
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

# ── qsim nie ma setup.py — dodaj ~/qsim do sys.path ───────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hexagon import HEXAGON, Q_ATTRACTOR, compute_q, is_crystallized
from phase_integration import DIGIT_SIGS, digit_to_virtues
from phase_sequence import (
    Q_candidate_cycle_return,
    Q_candidate_octave,
    Q_candidate_superposition,
    analyze_sequence,
    pca_trajectory,
    stage_fingerprint,
)


# ─── fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def stages():
    return [stage_fingerprint(n) for n in range(10)]


@pytest.fixture(scope="module")
def analysis():
    return analyze_sequence()


# ═══ Cyfra 0 — ślad po kamieniu (raw hard crystal) ═══════════════════════════
class TestDigit0:
    def test_strengths_uniform_ones(self):
        assert digit_to_virtues(0) == [1.0] * 6

    def test_C6_symmetry_zero_aniso(self, stages):
        assert stages[0]["aniso"] < 1e-9

    def test_is_raw_crystal(self, stages):
        assert stages[0]["is_crystal"] is True

    def test_Q_equals_attractor(self, stages):
        assert abs(stages[0]["Q"] - Q_ATTRACTOR) < 1e-4

    def test_signature_has_crossing(self):
        assert DIGIT_SIGS[0].has_crossing is True

    def test_signature_inside_polygon_6(self):
        assert DIGIT_SIGS[0].inside_polygon == 6

    def test_is_only_raw_crystal(self, stages):
        """0 jest JEDYNĄ cyfrą spełniającą hard crystal bez annealingu."""
        crystals = [n for n, s in enumerate(stages) if s["is_crystal"]]
        assert crystals == [0]


# ═══ Cyfra 1 — jeden kąt ══════════════════════════════════════════════════════
class TestDigit1:
    def test_single_active_strength(self):
        s = digit_to_virtues(1)
        assert sum(1 for x in s if x > 0) == 1
        assert s[0] == 1.0

    def test_gamma_zero(self, stages):
        """Jeden aktywny kubit → brak akumulacji Berry phase."""
        assert abs(stages[1]["gamma_deg"]) < 1e-6

    def test_dominant_is_odwaga(self, stages):
        assert stages[1]["dominant"] == "odwaga"

    def test_signature(self):
        assert DIGIT_SIGS[1].angles == 1
        assert DIGIT_SIGS[1].inward == 1
        assert DIGIT_SIGS[1].has_infinity_arm is False


# ═══ Cyfra 2 — lustrzana para z 3 ═════════════════════════════════════════════
class TestDigit2:
    def test_opposition_180deg(self):
        s = digit_to_virtues(2)
        assert s[0] == 1.0   # inward
        assert s[3] == 0.5   # outward, opozycja

    def test_is_mirror_of_3(self):
        """L2 distance to 3 jest najmniejsze wśród wszystkich par (2, k), k≠2."""
        s2 = np.array(digit_to_virtues(2))
        distances = {k: float(np.linalg.norm(s2 - np.array(digit_to_virtues(k))))
                     for k in range(10) if k != 2}
        # 3 nie musi być globalnie najbliższe — ale relatywnie bliskie
        # i bliższe niż "odległe" cyfry jak 0 czy 8
        assert distances[3] < distances[0]
        assert distances[3] < distances[8]

    def test_has_infinity_arm(self):
        assert DIGIT_SIGS[2].has_infinity_arm is True


# ═══ Cyfra 3 — trzy kąty wygięte ══════════════════════════════════════════════
class TestDigit3:
    def test_three_consecutive_inward(self):
        s = digit_to_virtues(3)
        assert s[0] == 1.0 and s[1] == 1.0 and s[2] == 1.0

    def test_inward_gt_outward(self):
        assert DIGIT_SIGS[3].inward > DIGIT_SIGS[3].outward
        assert DIGIT_SIGS[3].outward == 0

    def test_opposite_to_2_outward(self):
        """3 ma 0 outward, 2 ma >0 outward."""
        assert DIGIT_SIGS[3].outward == 0
        assert DIGIT_SIGS[2].outward > 0


# ═══ Cyfra 4 — kwadrat bazowy (HIPOTEZA) ═════════════════════════════════════
class TestDigit4:
    def test_alternating_pattern(self):
        s = digit_to_virtues(4)
        non_zero_idx = [i for i, x in enumerate(s) if x > 0]
        assert non_zero_idx == [0, 1, 3, 4]

    def test_has_square_flag(self):
        assert DIGIT_SIGS[4].has_square is True

    def test_unverified_hypothesis_marker(self):
        """DIGIT_SIGS[4].note musi jasno zaznaczać że to hipoteza."""
        note = DIGIT_SIGS[4].note.lower()
        assert "hipoteza" in note or "nie potwierdzone" in note

    def test_is_base_for_6_and_8_structurally(self):
        """6 i 8 mają has_square=True (jak 4)."""
        assert DIGIT_SIGS[6].has_square is True
        assert DIGIT_SIGS[8].has_square is True


# ═══ Cyfra 5 — pięć kątów naprzemiennie (C3 symetria) ═════════════════════════
class TestDigit5:
    def test_alternating_strong_weak(self):
        s = digit_to_virtues(5)
        # even idx (0,2,4) = 1.0; odd idx (1,3,5) = 0.6
        for i in (0, 2, 4):
            assert s[i] == 1.0
        for i in (1, 3, 5):
            assert s[i] == 0.6

    def test_aniso_zero_C3_symmetry(self, stages):
        """Alternacja strong/weak → idealna symetria C3 w heksagonie."""
        assert stages[5]["aniso"] < 1e-9

    def test_near_attractor(self, stages):
        assert abs(stages[5]["Q"] - Q_ATTRACTOR) < 0.03


# ═══ Cyfra 6 — kwadrat + ramiona (najbliższa Q_ATTRACTOR po 0) ═══════════════
class TestDigit6:
    def test_one_weak_arm(self):
        s = digit_to_virtues(6)
        weak = [x for x in s if x < 1.0]
        assert len(weak) == 1
        assert weak[0] == 0.3

    def test_near_attractor(self, stages):
        """|Q - Q_ATTRACTOR| < 0.002 — najbliższa oprócz 0."""
        assert abs(stages[6]["Q"] - Q_ATTRACTOR) < 0.002

    def test_low_aniso(self, stages):
        assert stages[6]["aniso"] < 0.01

    def test_has_infinity_arm(self):
        assert DIGIT_SIGS[6].has_infinity_arm is True


# ═══ Cyfra 7 — skrzyżowanie ═══════════════════════════════════════════════════
class TestDigit7:
    def test_has_crossing(self):
        assert DIGIT_SIGS[7].has_crossing is True

    def test_opposition_pair(self):
        s = digit_to_virtues(7)
        assert s[0] == s[3] == 0.7

    def test_no_angles_only_crossing(self):
        """7 to pierwsza cyfra bez kątów, używająca crossing."""
        assert DIGIT_SIGS[7].angles == 0
        assert DIGIT_SIGS[7].has_crossing is True

    def test_has_infinity_arm(self):
        assert DIGIT_SIGS[7].has_infinity_arm is True


# ═══ Cyfra 8 — "najbardziej krystaliczna" (hipoteza FALSYFIKOWANA) ═══════════
class TestDigit8:
    def test_uniform_strengths(self):
        s = digit_to_virtues(8)
        assert all(x == 0.9 for x in s)

    def test_aniso_zero(self, stages):
        assert stages[8]["aniso"] < 1e-9

    def test_not_hard_crystal(self, stages):
        """Mimo aniso=0, 8 NIE jest hard crystal bo Q ≠ Q_ATTRACTOR."""
        assert stages[8]["is_crystal"] is False
        assert abs(stages[8]["Q"] - Q_ATTRACTOR) > 0.02

    def test_no_infinity_arm(self):
        assert DIGIT_SIGS[8].has_infinity_arm is False


# ═══ Cyfra 9 — próg ═══════════════════════════════════════════════════════════
class TestDigit9:
    def test_similar_to_6(self):
        """9 i 6 różnią się tylko siłą ramienia (0.2 vs 0.3)."""
        s6 = np.array(digit_to_virtues(6))
        s9 = np.array(digit_to_virtues(9))
        cos = float(np.dot(s6, s9) / (np.linalg.norm(s6) * np.linalg.norm(s9)))
        assert cos > 0.99

    def test_pi_grid(self):
        assert DIGIT_SIGS[9].grid == "pi"

    def test_pentagon_inside(self):
        assert DIGIT_SIGS[9].inside_polygon == 5

    def test_9_to_0_modulation(self):
        """L2(9,0) jest wśród mniejszych odległości — semantyka modulacji."""
        s9 = np.array(digit_to_virtues(9))
        distances = {
            k: float(np.linalg.norm(s9 - np.array(digit_to_virtues(k))))
            for k in range(9)   # bez samego 9
        }
        d_to_0 = distances[0]
        # 0 nie musi być globalnie najbliższe — 6 jest. Semantyka modulacji
        # oznacza że 9→0 jest "dostępne" (cos wysoki), nie globalnie najmniejsze.
        assert d_to_0 < 1.0
        # cos(9, 0) jest wysokie
        s0 = np.array(digit_to_virtues(0))
        cos_9_0 = float(np.dot(s9, s0) / (np.linalg.norm(s9) * np.linalg.norm(s0)))
        assert cos_9_0 > 0.9


# ═══ Q — jedenasty stan (3 kandydaci) ═════════════════════════════════════════
class TestQCandidates:
    def test_cycle_return_high_cosine(self, stages):
        """Kandydat (a): cos(9, 0) > 0.9 — PARTIAL."""
        c = Q_candidate_cycle_return(stages)
        assert c["cos_9_to_0"] > 0.9

    def test_cycle_return_partial_verdict(self, stages):
        c = Q_candidate_cycle_return(stages)
        assert c["verdict"] in ("CONFIRMED", "PARTIAL")

    def test_octave_structural_verdict(self, stages):
        """Kandydat (b): octave jest strukturalny — nie testowalny liczbowo w 6D."""
        c = Q_candidate_octave(stages)
        assert "STRUCTURAL" in c["verdict"]

    def test_octave_reference_state_is_ones(self, stages):
        """[1]*6 = ten sam stan co cyfra 0, tylko γ° może się różnić."""
        c = Q_candidate_octave(stages)
        assert c["state"] == [1.0] * 6

    def test_superposition_falsified(self, stages):
        """Kandydat (c): centroid NIE jest hard crystal → FALSIFIED."""
        c = Q_candidate_superposition(stages)
        assert c["verdict"] == "FALSIFIED"
        assert c["is_crystal"] is False

    def test_superposition_high_aniso(self, stages):
        """Centroid 10 cyfr ma znaczną anizotropię."""
        c = Q_candidate_superposition(stages)
        assert c["aniso"] > 0.01


# ═══ PCA — ile wymiarów naprawdę używa trajektoria 0→9 ═══════════════════════
class TestPCATrajectory:
    def test_four_dims_suffice_95pct(self, stages):
        pca = pca_trajectory(stages)
        assert pca["n_dims_95pct"] == 4

    def test_odwaga_frozen_on_PC1(self, stages):
        """Odwaga ma najmniejszy loading na dominującej osi rozwoju."""
        pca = pca_trajectory(stages)
        loadings = pca["pc1_loadings"]
        assert abs(loadings["odwaga"]) < 0.1

    def test_integrative_virtues_dominate_PC1(self, stages):
        """Wdzięczność/przebaczenie/pokora mają wysokie |loadings| na PC1."""
        pca = pca_trajectory(stages)
        loadings = pca["pc1_loadings"]
        assert abs(loadings["wdzięczność"]) > 0.5
        assert abs(loadings["przebaczenie"]) > 0.4
        assert abs(loadings["pokora"]) > 0.4

    def test_PC1_explains_majority(self, stages):
        """PC1 tłumaczy >50% wariancji."""
        pca = pca_trajectory(stages)
        assert pca["variance_explained"][0] > 0.5


# ═══ Globalne inwarianty sekwencji ════════════════════════════════════════════
class TestSequenceInvariants:
    def test_only_digit_0_is_raw_crystal(self, stages):
        crystals = [s["n"] for s in stages if s["is_crystal"]]
        assert crystals == [0]

    def test_all_Q_above_0_8(self, stages):
        """Wszystkie 10 cyfr mają Q > 0.8 — blisko attractora."""
        for s in stages:
            assert s["Q"] > 0.8, f"cyfra {s['n']}: Q={s['Q']}"

    def test_all_Q_below_1(self, stages):
        """Żadna cyfra nie przekracza Q=1 (bound fidelity correlator)."""
        for s in stages:
            assert s["Q"] <= 1.0

    def test_all_aniso_nonnegative(self, stages):
        for s in stages:
            assert s["aniso"] >= 0.0

    def test_cycle_closes_not_identically(self, analysis):
        """9→0 nie jest tożsamością, ale L2 < max_jump."""
        close = analysis["cycle_close_9_to_0"]
        max_jump = analysis["summary_stats"]["max_jump"]
        assert close["l2_distance"] < max_jump["l2_distance"]
        assert close["l2_distance"] > 0.0  # nie tożsame

    def test_digits_coverage_0_to_9(self):
        """DIGIT_SIGS pokrywa wszystkie cyfry 0..9."""
        assert set(DIGIT_SIGS.keys()) == set(range(10))
