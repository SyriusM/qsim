"""
IPQ — pytanie → virtue strengths [s0..s5] w kolejności HEXAGON.

NETWORK SURFACE: none. Fully local (bge-m3 via MemPalace).
SPDX-License-Identifier: LicenseRef-Sovereign-MIT-1.0
See LICENSE for terms.
"""

import os
import sys
from pathlib import Path

_MEMPALACE = os.environ.get("MEMPALACE_PATH", str(Path.home() / "mempalace"))
sys.path.insert(0, _MEMPALACE)

from mempalace.q3sh_embed import virtue_map
from hexagon import HEXAGON


def ipq(question: str) -> list[float] | None:
    """
    Zwraca None gdy < 5 słów (za krótkie — brak crystallizacji).
    Kalibracja: dzieli przez max, najsilniejsza cnota = 1.0.
    NIE generuje uniform fallback — fałszywe kryształy bez semantyki.
    """
    if len(question.split()) < 5:
        return None
    scores = virtue_map(question)
    vals = [scores.get(v, 0.0) for v in HEXAGON]
    mx = max(vals) if max(vals) > 0 else 1.0
    return [v / mx for v in vals]


def ipq_confidence(strengths: list[float]) -> float:
    """
    Spread virtue_map scores. < 0.15 = podejrzane (płaski rozkład).
    """
    import statistics
    return statistics.stdev(strengths) if len(strengths) > 1 else 0.0
