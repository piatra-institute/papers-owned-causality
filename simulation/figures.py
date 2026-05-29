"""Two figures for the paper.

(i) Bar plot of owned-causality O_T across the six-rung agency ladder.
(ii) Scaffold handover: DI(U_ext -> Q) and DI(U_Omega -> Q) traces, plus the
    scaffold withdrawal schedule and viability over time.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_ladder(rungs: list, savepath: str) -> None:
    names = [r.name for r in rungs]
    values = [r.o_t for r in rungs]
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.bar(names, values, color="#2c5282", edgecolor="#1a202c")
    ax.set_ylabel(r"$\mathfrak{O}_T(\Omega) = \Gamma \cdot DI(U^\Omega\!\to\!Q) \cdot \Delta V \cdot I(Q;C)$")
    ax.set_title("Owned-causality score across the agency ladder")
    for i, v in enumerate(values):
        ax.annotate(f"{v:.2e}", xy=(i, v), xytext=(0, 4),
                    textcoords="offset points", ha="center", fontsize=8)
    ax.grid(True, axis="y", linewidth=0.3, alpha=0.4)
    fig.tight_layout()
    fig.savefig(savepath, dpi=150)
    plt.close(fig)


def plot_handover(result, savepath: str) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(8.0, 6.0), sharex=True)
    windows = np.arange(len(result.di_ext_to_q))
    ax0 = axes[0]
    ax0.plot(windows, result.di_ext_to_q, "o-", color="#c53030",
             label=r"$DI(U^{\mathrm{ext}}\!\to Q)$")
    ax0.plot(windows, result.di_omega_to_q, "s-", color="#2b6cb0",
             label=r"$DI(U^{\Omega}\!\to Q)$")
    ax0.set_ylabel("directed information")
    ax0.set_title("Scaffold handover: external control yields to endogenous control")
    if result.crossover_index >= 0:
        ax0.axvline(result.crossover_index, color="#1a202c", linewidth=0.8,
                    linestyle="--", alpha=0.6)
        ax0.annotate("crossover",
                     xy=(result.crossover_index, max(max(result.di_ext_to_q),
                                                     max(result.di_omega_to_q))),
                     xytext=(6, -8), textcoords="offset points", fontsize=8)
    ax0.legend(loc="best", fontsize=8)
    ax0.grid(True, linewidth=0.3, alpha=0.4)

    ax1 = axes[1]
    ax1.plot(windows, result.u_ext_schedule, "-", color="#c53030",
             label="scaffold amplitude")
    ax1.plot(windows, result.viability_trace, "-", color="#2f855a",
             label="viability (basin A fraction)")
    ax1.set_xlabel("episode window")
    ax1.set_ylabel("value")
    ax1.legend(loc="best", fontsize=8)
    ax1.grid(True, linewidth=0.3, alpha=0.4)

    fig.tight_layout()
    fig.savefig(savepath, dpi=150)
    plt.close(fig)
