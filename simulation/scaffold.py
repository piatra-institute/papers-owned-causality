"""Positive-scaffold handover protocol.

A bistable organisation begins in basin B with its constraint capacity
suppressed (analogue of threat or learned helplessness). An external scaffold
u_ext supplies most of the basin-steering for an initial window, after which
it is withdrawn linearly. Once the scaffold weakens, the organism's internal
constraint loop activates and takes over basin maintenance.

Handover is measured by computing per-step directed information

    DI(U_ext   -> Q)   and   DI(U_Omega -> Q)

on sliding windows. Under healthy bootstrapping, DI(U_ext -> Q) decreases and
DI(U_Omega -> Q) increases; their traces cross when endogenous control has
taken over. Viability tracks basin-A occupancy throughout.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from directed_info import directed_information_per_step


@dataclass
class ScaffoldResult:
    u_ext_schedule: list[float]
    di_ext_to_q: list[float]
    di_omega_to_q: list[float]
    viability_trace: list[float]
    crossover_index: int

    def as_dict(self) -> dict:
        return {
            "u_ext_schedule": list(self.u_ext_schedule),
            "di_ext_to_q":    list(self.di_ext_to_q),
            "di_omega_to_q":  list(self.di_omega_to_q),
            "viability_trace": list(self.viability_trace),
            "crossover_index": int(self.crossover_index),
        }


def _potential_grad(x: float) -> float:
    return x * (x ** 2 - 1.0)


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def run_handover(
    n_steps: int = 12000,
    window: int = 600,
    scaffold_until: int = 3000,
    scaffold_ramp_steps: int = 3000,
    constraint_ramp_steps: int = 2000,
    seed: int = 42,
    ext_amplitude: float = 1.0,
    sigma: float = 0.7,
    dt: float = 0.05,
) -> ScaffoldResult:
    rng = np.random.default_rng(seed)
    x = np.empty(n_steps + 1)
    c = np.empty(n_steps + 1)
    e = np.empty(n_steps)
    u_omega = np.empty(n_steps)
    x[0] = -0.95
    c[0] = 0.0

    def scaffold_amplitude(t: int) -> float:
        if t < scaffold_until:
            return ext_amplitude
        end = scaffold_until + scaffold_ramp_steps
        if t >= end:
            return 0.0
        return ext_amplitude * (1.0 - (t - scaffold_until) / scaffold_ramp_steps)

    def constraint_gate(t: int) -> float:
        # Gate the internal constraint loop: zero initially, rises linearly
        # to 1.0 over constraint_ramp_steps as the scaffold begins to withdraw.
        if t < scaffold_until:
            return 0.0
        end = scaffold_until + constraint_ramp_steps
        if t >= end:
            return 1.0
        return (t - scaffold_until) / constraint_ramp_steps

    for t in range(n_steps):
        e[t] = scaffold_amplitude(t) + 0.05 * rng.standard_normal()
        target = 1.0 * _sigmoid(3.5 * (0.6 - x[t]))
        gate = constraint_gate(t)
        c[t + 1] = c[t] + gate * 0.4 * (target - c[t])
        u_omega[t] = c[t + 1]
        drift = -_potential_grad(x[t]) + u_omega[t] + e[t]
        noise = sigma * np.sqrt(dt) * rng.standard_normal()
        x[t + 1] = x[t] + drift * dt + noise

    # Use the finer x values for the macrostate (binned by directed_info itself).
    x_next = x[1:]
    n_windows = n_steps // window
    di_ext = []
    di_omega = []
    viability_trace = []
    schedule_per_window = []
    for w in range(n_windows):
        s = w * window
        ee = e[s : s + window]
        uu = u_omega[s : s + window]
        xx = x_next[s : s + window]
        di_ext.append(directed_information_per_step(ee, xx))
        di_omega.append(directed_information_per_step(uu, xx))
        viability_trace.append(float((xx > 0).mean()))
        schedule_per_window.append(scaffold_amplitude(s))

    # Crossover: first window where DI(omega->Q) >= DI(ext->Q) AND scaffold
    # has begun to withdraw (so we don't trigger on the initial all-zero period).
    crossover_index = -1
    for i, (a, b) in enumerate(zip(di_ext, di_omega)):
        if b >= a and schedule_per_window[i] < ext_amplitude:
            crossover_index = i
            break

    return ScaffoldResult(
        u_ext_schedule=schedule_per_window,
        di_ext_to_q=di_ext,
        di_omega_to_q=di_omega,
        viability_trace=viability_trace,
        crossover_index=crossover_index,
    )
