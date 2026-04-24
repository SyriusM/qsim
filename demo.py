"""
CLI demo qsim — pełny cykl Pauzy Kwantowej.
"""

import sys
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text

import db
from cycle import run_cycle
from hexagon import HEXAGON, VIRTUE_COLORS, Q_ATTRACTOR

console = Console()

QUESTIONS = [
    "Jak mogę lepiej rozumieć siebie i swoje emocje w trudnych chwilach?",
    "Czy odwaga wymaga braku strachu czy działania pomimo strachu?",
    "Jak wybaczyć komuś kto wyrządził mi głęboką krzywdę i ruszyć dalej?",
    "Co oznacza prawdziwa wdzięczność gdy życie jest pełne bólu i trudności?",
    "Jak zachować pokorę nie tracąc poczucia własnej wartości i siły?",
]


def render_strengths(strengths: list[float], fids: list[float]) -> Text:
    t = Text()
    for i, (v, s, f) in enumerate(zip(HEXAGON, strengths, fids)):
        color = VIRTUE_COLORS[v].lower()
        bar = "█" * int(s * 10) + "░" * (10 - int(s * 10))
        t.append(f"  {v:<15}", style=f"bold {color}")
        t.append(f" {bar} s={s:.3f} fid={f:.4f}\n")
    return t


def show_crystal(r: dict, idx: int):
    status_color = {
        "hard": "green bold",
        "soft": "yellow",
        "raw": "dim",
        "no_crystal": "red",
    }.get(r["status"], "white")

    header = (
        f"[{status_color}]{r['status'].upper()}[/] "
        f"  Q={r['Q']:.5f}  γ={r['gamma']:.4f}rad  "
        f"aniso={r['aniso']:.6f}  t={r['t_ms']:.1f}ms"
    )
    body = Text()
    body.append(f"dominant : {r['dominant']}\n", style=f"bold {VIRTUE_COLORS[r['dominant']].lower()}")
    body.append(f"chroma   : {r['chroma']}  ", style=r["chroma"])
    body.append("█████\n", style=r["chroma"])
    body.append(f"Q_rényi  : {r['Q_renyi']:.5f}\n")
    body.append(f"C6_ok    : {r['c6_ok']}\n")
    body.append(f"confidence: {r['confidence']:.3f}  ipq_qual: {r['ipq_qual']}\n\n")
    body.append(render_strengths(r["strengths"], r["fids"]))

    console.print(Panel(
        body,
        title=f"[dim]#{idx}[/] {header}",
        border_style="green" if r["status"] == "hard" else "yellow",
        expand=False,
    ))


def show_last_n(conn, n=5):
    rows = db.last_n(conn, n)
    t = Table(title=f"Ostatnie {n} crystallizacji", box=box.SIMPLE_HEAVY)
    t.add_column("id", style="dim")
    t.add_column("status")
    t.add_column("Q", justify="right")
    t.add_column("aniso", justify="right")
    t.add_column("t_ms", justify="right")
    t.add_column("dominant")
    t.add_column("pytanie", max_width=40)
    for r in rows:
        sc = "green" if r["status"] == "hard" else "yellow" if r["status"] == "soft" else "dim"
        t.add_row(
            str(r["id"]),
            f"[{sc}]{r['status']}[/]",
            f"{r['Q']:.5f}" if r["Q"] else "—",
            f"{r['aniso']:.6f}" if r["aniso"] else "—",
            f"{r['t_ms']:.1f}" if r["t_ms"] else "—",
            r["dominant"] or "—",
            (r["question"] or "")[:40],
        )
    console.print(t)


def show_stats(conn):
    s = db.stats(conn)
    avg_q = f"{s['avg_q']:.5f}" if s["avg_q"] is not None else "—"
    avg_a = f"{s['avg_aniso']:.6f}" if s["avg_aniso"] is not None else "—"
    console.print(
        f"\n[bold]Statystyki:[/] COUNT={s['count']}  "
        f"AVG_Q={avg_q}  AVG_aniso={avg_a}\n"
    )


def exp_b_demo(conn):
    """EXP_B: C6 symetria na ostatniej hard crystallizacji."""
    import json
    import numpy as np
    from hexagon import compute_q

    rows = db.last_n(conn, 20)
    hard = [r for r in rows if r["status"] == "hard"]
    if not hard:
        console.print("[dim]Brak hard crystallizacji do EXP_B.[/]")
        return

    r = hard[0]
    strengths = json.loads(r["strengths"])
    qs = []
    s = list(strengths)
    for _ in range(6):
        qs.append(compute_q(s)["q"])
        s = s[1:] + s[:1]

    t = Table(title="EXP_B — C6 symmetry check", box=box.SIMPLE)
    t.add_column("rotacja")
    t.add_column("Q", justify="right")
    for i, q in enumerate(qs):
        t.add_row(f"rot {i}", f"{q:.10f}")
    t.add_row("[bold]std[/]", f"[bold]{np.std(qs):.2e}[/]")
    console.print(t)


def main():
    console.print(Panel(
        f"[bold cyan]qsim — Symulator pola UIS[/]\n"
        f"Q_ATTRACTOR = {Q_ATTRACTOR}  |  heksagon 6 cnót  |  anneal → crystal",
        expand=False,
    ))

    conn = db.get_conn()

    console.print("\n[bold]▶ Crystallizacja pytań...[/]\n")
    for i, q in enumerate(QUESTIONS, 1):
        console.print(f"[dim]{i}.[/] {q}")
        r = run_cycle(q, mode="strict")
        if r["status"] == "no_crystal":
            console.print(f"  [red]no_crystal[/] ({r.get('ipq_qual','?')})\n")
        else:
            show_crystal(r, i)

    console.rule("Ostatnie 5 crystallizacji z bazy")
    show_last_n(conn, 5)
    show_stats(conn)

    console.rule("EXP_B — C6 symmetry")
    exp_b_demo(conn)

    conn.close()


if __name__ == "__main__":
    main()
