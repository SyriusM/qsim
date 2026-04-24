"""
q_correlations — Q jako zmienna zależna, badanie co ją tłumaczy.

Hipoteza Mateusza: "Q jest zmienną, tylko jeszcze nie wiemy z czym.
Trzeba te kropki połączyć. Być może związane ze stanem przejściowych stanów 0-9-Q."

Dla każdej cyfry n∈[0..9] zbieramy cechy:
  statyczne:   γ°, aniso, dominant_idx, n (pozycja)
  przejścia:   L2(n-1,n), cos(n-1,n), ΔQ, Δγ°
  kumulatywne: cum_γ°, cum_L2, max|γ|_so_far
  strengths:   per-virtue strength
  geometryczne: has_square, has_crossing, has_infinity_arm, grid

Cel:
  1. Pearson + Spearman korelacje Q vs każda cecha
  2. top-5 silnie powiązanych cech
  3. prosta regresja multilinear Q ~ top-3 cechy (R²)
  4. hipoteza: jeśli R² > 0.9 — Q jest funkcją tych cech
                jeśli R² < 0.5 — Q ma ukrytą zmienną (semantyka/planety)
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase_integration import DIGIT_SIGS, digit_to_virtues
from phase_sequence import analyze_sequence
from hexagon import HEXAGON


def pearson(x, y):
    x, y = np.array(x, float), np.array(y, float)
    if len(x) < 2 or np.std(x) == 0 or np.std(y) == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def spearman(x, y):
    return pearson(_rank(x), _rank(y))


def _rank(x):
    return np.argsort(np.argsort(x))


def build_feature_matrix():
    r = analyze_sequence()
    stages = r["stages"]
    trans  = r["transitions"]

    # lookup transition do cyfry n (z poprzednika)
    trans_in = {t["to"]: t for t in trans}

    rows = []
    cum_gamma = 0.0
    cum_L2    = 0.0

    for n, s in enumerate(stages):
        t = trans_in.get(n)  # None dla n=0
        dominant_idx = HEXAGON.index(s["dominant"])
        sig = DIGIT_SIGS[n]
        strengths = s["strengths"]

        row = {
            "n":           n,
            "Q":           s["Q"],
            "gamma_abs":   abs(s["gamma_deg"]),
            "aniso":       s["aniso"],
            "gamma_signed": s["gamma_deg"],
            "dominant_idx": dominant_idx,

            # statyczne strengths
            "s_odwaga":       strengths[0],
            "s_pokora":       strengths[1],
            "s_przebaczenie": strengths[2],
            "s_wspolczucie":  strengths[3],
            "s_wdzięczność":  strengths[4],
            "s_rozumienie":   strengths[5],

            "max_strength":  max(strengths),
            "min_strength":  min(strengths),
            "n_active":      sum(1 for x in strengths if x > 0.01),
            "variance_s":    float(np.var(strengths)),
            "sum_s":         float(sum(strengths)),

            # geometryczne
            "has_square":       int(sig.has_square),
            "has_crossing":     int(sig.has_crossing),
            "has_infinity_arm": int(sig.has_infinity_arm),
            "grid_is_pi":       int(sig.grid == "pi"),
            "angles":           sig.angles,
            "inward":           sig.inward,
            "outward":          sig.outward,
        }

        # przejściowe
        if t is not None:
            row["L2_prev"] = t["l2_distance"]
            row["cos_prev"] = t["cosine_similarity"]
            row["delta_Q"]  = t["delta_Q"]
            row["delta_gamma_abs"] = abs(t["delta_gamma_deg"])
            cum_gamma += abs(t["delta_gamma_deg"])
            cum_L2    += t["l2_distance"]
        else:
            row["L2_prev"] = np.nan
            row["cos_prev"] = np.nan
            row["delta_Q"] = np.nan
            row["delta_gamma_abs"] = np.nan

        row["cum_gamma"] = cum_gamma
        row["cum_L2"]    = cum_L2

        rows.append(row)

    return rows


def correlate_all(rows, target="Q"):
    """Pearson + Spearman dla każdej cechy vs target."""
    keys = [k for k in rows[0].keys() if k != target]
    ys = [r[target] for r in rows]

    results = []
    for k in keys:
        xs = [r[k] for r in rows]
        # skip jeśli są NaN
        valid = [(x, y) for x, y in zip(xs, ys) if not (isinstance(x, float) and np.isnan(x))]
        if len(valid) < 3:
            continue
        xs_v, ys_v = zip(*valid)
        p = pearson(xs_v, ys_v)
        s = spearman(xs_v, ys_v)
        results.append({
            "feature": k,
            "pearson":  p,
            "spearman": s,
            "max_abs":  max(abs(p), abs(s)),
            "n":        len(valid),
        })

    return sorted(results, key=lambda x: -x["max_abs"])


def multilinear_fit(rows, features, target="Q"):
    """Prosta regresja Q = β0 + Σ βi*xi, zwraca R², współczynniki."""
    ys = np.array([r[target] for r in rows])
    # weź tylko wiersze z pełnymi danymi
    valid_idx = []
    X_rows = []
    for i, r in enumerate(rows):
        vals = [r[f] for f in features]
        if not any(isinstance(v, float) and np.isnan(v) for v in vals):
            valid_idx.append(i)
            X_rows.append(vals)
    X = np.array(X_rows)
    y = ys[valid_idx]

    # Dodaj intercept
    X_aug = np.column_stack([np.ones(len(X)), X])
    # Least squares
    beta, *_ = np.linalg.lstsq(X_aug, y, rcond=None)
    y_pred = X_aug @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return {
        "features":  features,
        "n":         len(X),
        "intercept": float(beta[0]),
        "coeffs":    {f: float(b) for f, b in zip(features, beta[1:])},
        "r2":        float(r2),
        "y_pred":    y_pred.tolist(),
        "residuals": (y - y_pred).tolist(),
    }


def main():
    rows = build_feature_matrix()
    correlations = correlate_all(rows)

    print("═" * 76)
    print("  Q jako zmienna zależna — badanie korelacji (n=10 cyfr)")
    print("═" * 76)
    print(f"\n  {'feature':<22} {'Pearson':>10} {'Spearman':>10} {'max_abs':>10}")
    print(f"  {'─' * 54}")
    for c in correlations:
        mark = "★" if c["max_abs"] > 0.7 else "·" if c["max_abs"] > 0.4 else " "
        print(f"  {c['feature']:<22} {c['pearson']:>+10.3f} "
              f"{c['spearman']:>+10.3f} {c['max_abs']:>10.3f}  {mark}")

    print("\n" + "─" * 76)
    print("  TOP-3 cechy (|korelacja| największe):")
    top3 = [c["feature"] for c in correlations[:3]]
    for i, c in enumerate(correlations[:3], 1):
        print(f"    {i}. {c['feature']:<22} |r|={c['max_abs']:.3f}")

    print(f"\n  TOP-5 cechy:")
    top5 = [c["feature"] for c in correlations[:5]]
    print(f"    {', '.join(top5)}")

    # Regresja liniowa z top-3 i top-5
    for name, feats in [("TOP-3", top3), ("TOP-5", top5)]:
        fit = multilinear_fit(rows, feats)
        print(f"\n  Regresja {name} (Q ~ {' + '.join(feats)}):")
        print(f"    R² = {fit['r2']:.4f}  (n={fit['n']})")
        print(f"    intercept = {fit['intercept']:+.4f}")
        for f, b in fit["coeffs"].items():
            print(f"      β[{f:<20}] = {b:+.5f}")

    # Rezyduja dla każdej cyfry (top-5)
    fit = multilinear_fit(rows, top5)
    print(f"\n  Rezyduja (Q_true - Q_pred) per cyfra (top-5 model):")
    # mapa indeks→n uwzględniając NaN cyfry 0
    # budujemy mapę valid_idx
    valid_idx = []
    for i, r in enumerate(rows):
        vals = [r[f] for f in top5]
        if not any(isinstance(v, float) and np.isnan(v) for v in vals):
            valid_idx.append(i)
    for idx, res in zip(valid_idx, fit["residuals"]):
        r = rows[idx]
        print(f"    n={r['n']}  Q_true={r['Q']:.4f}  "
              f"Q_pred={r['Q']-res:.4f}  residual={res:+.5f}")

    # Interpretacja
    print("\n" + "═" * 76)
    print("  WNIOSKI:")
    r2_top5 = multilinear_fit(rows, top5)["r2"]
    if r2_top5 > 0.95:
        print(f"  ★ R²={r2_top5:.3f} — Q jest PRAWIE DETERMINISTYCZNĄ funkcją "
              f"top-5 cech.")
        print("    To znaczy: geometria + przejście już tłumaczą Q.")
        print("    Ukryte zmienne (semantyka/planety) nie są potrzebne.")
    elif r2_top5 > 0.75:
        print(f"  · R²={r2_top5:.3f} — top-5 cech tłumaczą większość Q.")
        print("    Pozostałe ~20% wariancji może siedzieć w ukrytych "
              "zmiennych.")
    else:
        print(f"  ! R²={r2_top5:.3f} — top-5 cech NIE tłumaczą Q.")
        print("    Ukryta zmienna jest istotna. Kandydaci: semantyka, "
              "planety, kumulatywny γ, topologia.")
    print("═" * 76 + "\n")


if __name__ == "__main__":
    main()
