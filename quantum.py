"""
Experimental 6-qubit quantum simulation dla qsim.
Pełny Hilbert space (64 amplitudy), Ry + CNOT gates, partial trace.

UWAGA: EKSPERYMENTALNE. Zwalidowane tylko na anegdotycznych przykładach.
Nie używaj jako produkcyjny klasyfikator. Używaj jako pomiar splątania.

Main export: S_total(strengths) → float (von Neumann entropy sumaryczna)
"""

import numpy as np
from math import cos, sin
from hexagon import THETA_IDEAL

_I2 = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_P0 = np.array([[1, 0], [0, 0]], dtype=complex)
_P1 = np.array([[0, 0], [0, 1]], dtype=complex)


def _Ry(theta: float) -> np.ndarray:
    c, s = cos(theta / 2), sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def _kron_n(*ops):
    r = ops[0]
    for op in ops[1:]:
        r = np.kron(r, op)
    return r


def _single(gate, target, n=6):
    ops = [_I2] * n
    ops[target] = gate
    return _kron_n(*ops)


def _CNOT(control, target, n=6):
    a = [_I2] * n; a[control] = _P0
    b = [_I2] * n; b[control] = _P1; b[target] = _X
    return _kron_n(*a) + _kron_n(*b)


def _partial_trace(psi, keep, n=6):
    """Ślad częściowy. keep — lista indeksów kubitów do zachowania."""
    rho = np.outer(psi, psi.conj()).reshape([2] * (2 * n))
    trace_out = sorted([i for i in range(n) if i not in keep], reverse=True)
    n_cur = n
    for ti in trace_out:
        rho = np.trace(rho, axis1=ti, axis2=n_cur + ti)
        n_cur -= 1
    k = len(keep)
    return rho.reshape(2 ** k, 2 ** k)


def _vN(rho: np.ndarray) -> float:
    e = np.linalg.eigvalsh(rho).real
    e = e[e > 1e-12]
    return float(-np.sum(e * np.log2(e)))


def _concurrence(rho2: np.ndarray) -> float:
    Y = np.array([[0, -1j], [1j, 0]])
    YY = np.kron(Y, Y)
    rt = YY @ rho2.conj() @ YY
    M = rho2 @ rt
    e = np.sort(np.sqrt(np.maximum(np.linalg.eigvals(M).real, 0)))[::-1]
    return float(max(0.0, e[0] - e[1] - e[2] - e[3]))


def build_state(strengths: list[float], entangle_pairs: bool = True) -> np.ndarray:
    """6-qubit state z strengths, opcjonalnie ze splątaniem par opozycji."""
    n = 6
    psi = np.zeros(2 ** n, dtype=complex)
    psi[0] = 1.0
    for i, s in enumerate(strengths):
        psi = _single(_Ry(THETA_IDEAL * float(s)), i) @ psi
    if entangle_pairs:
        for i in range(3):
            psi = _CNOT(i, i + 3) @ psi
    return psi


def S_total(strengths: list[float]) -> float:
    """
    von Neumann entropy sumaryczna całego heksagonu.
    Interpretacja eksperymentalna: "kompleksność polarna" pytania.
    Pytania o dualizm → wyższe S_total (2.0+).
    Pytania o jedną jakość → niższe S_total (<1.0).

    UWAGA: Zwalidowane tylko na ~10 przykładach. Wymaga dalszych badań.
    """
    psi = build_state(strengths, entangle_pairs=True)
    return sum(_vN(_partial_trace(psi, [i])) for i in range(6))


def quantum_fingerprint(strengths: list[float]) -> dict:
    """
    Pełny quantum fingerprint (experimental).
    Returns: S_total, S_per_virtue, concurrences (3 pary opozycji).
    """
    psi = build_state(strengths, entangle_pairs=True)
    S_per = [_vN(_partial_trace(psi, [i])) for i in range(6)]
    Cs = [_concurrence(_partial_trace(psi, list(p))) for p in [(0, 3), (1, 4), (2, 5)]]
    return dict(
        S_total=float(sum(S_per)),
        S_per_virtue=S_per,
        concurrences=Cs,
        experimental=True,
    )


if __name__ == '__main__':
    # Test
    tests = {
        'C6_full':  [1.0] * 6,
        'C6_half':  [0.5] * 6,
        'single':   [1, 0, 0, 0, 0, 0],
        'gradient': [1, 0.8, 0.6, 0.4, 0.2, 0.1],
    }
    print(f"{'config':<12} {'S_total':>8}  concurrences")
    for lab, s in tests.items():
        fp = quantum_fingerprint(s)
        cs_str = ' '.join(f'{c:.3f}' for c in fp['concurrences'])
        print(f'{lab:<12} {fp["S_total"]:>8.4f}  [{cs_str}]')
