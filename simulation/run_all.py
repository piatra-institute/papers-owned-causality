"""Orchestrator: reproduces every numerical claim in the paper.

Run with:

    cd simulation
    uv run run_all.py

Writes output/results.json and the figure files under output/figures/. Every
numeric value cited in the paper is a key in the JSON file.
"""
from __future__ import annotations

import json
from pathlib import Path

from agency_ladder import run_ladder
from figures import plot_handover, plot_ladder
from scaffold import run_handover


OUT = Path(__file__).parent / "output"


def main() -> None:
    (OUT / "figures").mkdir(parents=True, exist_ok=True)

    # ------------------------ Agency ladder ------------------------
    ladder = run_ladder(n=8000, seed=7)
    ladder_d = {r.name: r.as_dict() for r in ladder}

    # ------------------------ Scaffold handover ------------------------
    handover = run_handover(
        n_steps=12000, window=600,
        scaffold_until=3000, scaffold_ramp_steps=3000,
        constraint_ramp_steps=2500,
        seed=42, ext_amplitude=1.0, sigma=0.9,
    )

    # ------------------------ Figures ------------------------
    plot_ladder(ladder, str(OUT / "figures" / "agency_ladder.png"))
    plot_handover(handover, str(OUT / "figures" / "scaffold_handover.png"))

    results = {
        "agency_ladder": ladder_d,
        "scaffold_handover": handover.as_dict(),
    }

    with (OUT / "results.json").open("w") as f:
        json.dump(results, f, indent=2, default=float)

    print("Agency ladder:")
    for r in ladder:
        print(f"  {r.name:>10s}  gamma={r.gamma:.3f}  DI_endo={r.di_endo:.3f}  "
              f"DI_ext={r.di_external:.3f}  dV={r.delta_v:.3f}  "
              f"reentry={r.reentry:.3f}  O_T={r.o_t:.3e}")
    print()
    print(f"Scaffold handover crossover at window: {handover.crossover_index} "
          f"of {len(handover.di_ext_to_q)}")
    print(f"  DI_ext peak:    {max(handover.di_ext_to_q):.3f}")
    print(f"  DI_omega peak:  {max(handover.di_omega_to_q):.3f}")
    print(f"  viability max:  {max(handover.viability_trace):.3f}")
    print(f"  viability min:  {min(handover.viability_trace):.3f}")
    print()
    print(f"Wrote: {OUT / 'results.json'}")


if __name__ == "__main__":
    main()
