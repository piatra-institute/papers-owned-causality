"""A six-rung agency ladder, computed under a unified protocol.

Each rung is a Langevin simulation on a bistable potential

    V(x) = (x**2 - 1)**2 / 4

with a viable well at x > 0 (basin A) and a non-viable well at x < 0
(basin B). All rungs start at x0 = -0.9, run for the same number of steps
under the same noise schedule, and are gently scaffolded into the viable
basin during the first quarter of the episode. The four factors

    Gamma_T, DI(U_Omega -> Q), Delta_V_T, I(Q; C)

are computed identically across rungs over the post-scaffold window. Rungs
differ only in their constraint-production policy and in the fraction of
constraints they internally maintain.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from closure_score import gamma as gamma_score
from directed_info import (
    conditional_directed_information_per_step,
    mutual_information,
)
from viability import delta_v


@dataclass
class LadderResult:
    name: str
    gamma: float
    di_endo: float
    di_external: float
    delta_v: float
    reentry: float
    o_t: float

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "gamma": self.gamma,
            "di_endo": self.di_endo,
            "di_external": self.di_external,
            "delta_v": self.delta_v,
            "reentry": self.reentry,
            "o_t": self.o_t,
        }


def _potential_grad(x: float) -> float:
    return x * (x ** 2 - 1.0)


def _simulate(
    n: int,
    policy,
    rng: np.random.Generator,
    x0: float = -0.9,
    sigma: float = 0.75,
    dt: float = 0.05,
    scaffold_until: int = 0,
    scaffold_strength: float = 0.9,
    external_amp: float = 0.06,
):
    """Generic bistable Langevin simulation. The policy is c_{t+1} = policy(t, x_t, c_t).

    The per-step noise increments are recorded and returned so that the
    counterfactual (scrambled-constraint) run can be replayed under the *same*
    noise realisation (common random numbers). Without this, the viability
    difference would measure the gap between two independent noise draws rather
    than the effect of the constraint timing.
    """
    x = np.empty(n + 1)
    c = np.empty(n + 1)
    e = np.empty(n)
    u_omega = np.empty(n)
    noise = np.empty(n)
    x[0] = x0
    c[0] = 0.0
    for t in range(n):
        if t < scaffold_until:
            e_scaffold = scaffold_strength
        else:
            e_scaffold = 0.0
        e[t] = e_scaffold + external_amp * rng.standard_normal()
        c_next = policy(t, x[t], c[t])
        u_omega[t] = c_next
        drift = -_potential_grad(x[t]) + u_omega[t] + e[t]
        noise[t] = sigma * np.sqrt(dt) * rng.standard_normal()
        x[t + 1] = x[t] + drift * dt + noise[t]
        c[t + 1] = c_next
    return x, c, e, u_omega, noise


def _simulate_scrambled(
    n: int,
    c_recorded: np.ndarray,
    e_recorded: np.ndarray,
    noise_recorded: np.ndarray,
    perm_rng: np.random.Generator,
    x0: float = -0.9,
    dt: float = 0.05,
):
    """Counterfactual run: same external drive and the same recorded noise as
    the factual run (common random numbers), but with the constraint sequence
    time-shuffled. The only thing that changes between factual and counterfactual
    is the *timing* of the constraint, so the viability difference isolates the
    effect of the constraint deployment rather than a difference in noise draws.
    """
    perm = perm_rng.permutation(n)
    c_s = c_recorded[1:][perm]
    x2 = np.empty(n + 1)
    x2[0] = x0
    for t in range(n):
        drift = -_potential_grad(x2[t]) + c_s[t] + e_recorded[t]
        x2[t + 1] = x2[t] + drift * dt + noise_recorded[t]
    return x2


def _coarse_q(x: np.ndarray, n_bins: int = 4) -> np.ndarray:
    """Coarse-grained macrostate in [n_bins] levels by quantile bin of x."""
    if x.std() < 1e-12:
        return np.zeros_like(x, dtype=int)
    edges = np.quantile(x, np.linspace(0.0, 1.0, n_bins + 1))
    edges = np.unique(edges)
    if len(edges) < 2:
        return np.zeros_like(x, dtype=int)
    return np.searchsorted(edges[1:-1], x, side="right").astype(int)


def _compute_factors(
    n: int,
    name: str,
    policy,
    maintained_constraints: int,
    required_constraints: int,
    seed: int,
) -> LadderResult:
    rng = np.random.default_rng(seed)
    scaffold_steps = n // 4
    x, c, e, u_omega, noise = _simulate(
        n=n, policy=policy, rng=rng,
        scaffold_until=scaffold_steps,
        scaffold_strength=0.9,
    )
    # Common random numbers: the counterfactual reuses the exact noise stream
    # recorded above, so Delta_V isolates the effect of the constraint timing,
    # not a difference between independent noise draws.
    perm_rng = np.random.default_rng(seed + 31)
    x_scrambled = _simulate_scrambled(
        n=n, c_recorded=c, e_recorded=e, noise_recorded=noise, perm_rng=perm_rng,
    )

    # Measurement window: post-scaffold. x and c are length n+1; e and u_omega
    # are length n. Use x[start+1 : ] aligned with u_omega[start:].
    start = scaffold_steps
    x_w = x[start + 1 :]
    c_w = c[start + 1 :]
    e_w = e[start:]
    u_w = u_omega[start:]
    x_now_w = x[start:-1]
    xs_w = x_scrambled[start + 1 :]
    q_w = _coarse_q(x_w, n_bins=4)
    qs_w = _coarse_q(xs_w, n_bins=4)

    g = gamma_score(x_w, maintained_constraints=maintained_constraints,
                    required_constraints=required_constraints)
    # Conditional directed information DI(U_Omega -> Q | X_t, E): condition the
    # endogenous channel on the current state and the external drive, as the
    # owned-causality definition requires, so external and self-state causes are
    # factored out. The external channel DI(E -> Q | X_t) is conditioned on the
    # current state alone.
    cond_endo = np.column_stack([x_now_w, e_w])
    di_e = conditional_directed_information_per_step(u_w, q_w.astype(float), cond_endo)
    di_x = conditional_directed_information_per_step(e_w, q_w.astype(float), x_now_w)
    v_endo = float((x_w > 0).mean())
    v_scr = float((xs_w > 0).mean())
    dv = v_endo - v_scr
    half = len(q_w) // 2
    rv = mutual_information(q_w[:half].astype(float), c_w[half : 2 * half], n_bins=4)
    o = g * di_e * max(0.0, dv) * rv
    return LadderResult(name, g, di_e, di_x, dv, rv, o)


# ---------------- Constraint-production policies for each rung ----------------
#
# All non-trivial rungs respond to viability departures (i.e., x drifting toward
# basin B). They differ in response gain, response speed, and the degree to
# which the response is produced internally (Gamma) versus stipulated by an
# external rule.

def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def _policy_rock(t, x, c):
    return 0.0


def _policy_thermostat(t, x, c):
    # Fixed linear response specified by an external setpoint. Not produced
    # by the system.
    return 0.9 * _sigmoid(2.0 * (0.5 - x))


def _policy_flame(t, x, c):
    # Memory term added: response builds slowly. Process self-maintains
    # weakly but the constraint rule is still fixed.
    target = 0.6 * _sigmoid(1.5 * (0.5 - x))
    return c + 0.20 * (target - c)


def _policy_raf(t, x, c):
    # Autocatalytic gain: response amplified by current constraint level.
    target = 0.8 * _sigmoid(2.5 * (0.5 - x))
    return c + 0.30 * (target - c) + 0.05 * c


def _policy_chemoton(t, x, c):
    # Faster response, sharper gating: the boundary effectively keeps the
    # response coherent.
    target = 0.95 * _sigmoid(3.0 * (0.5 - x))
    return c + 0.40 * (target - c)


def _policy_organism(t, x, c):
    # Viability-gradient response with memory: persistent push toward the
    # viable basin tracked by an internal model of own state.
    target = 1.0 * _sigmoid(3.5 * (0.6 - x))
    return c + 0.50 * (target - c) + 0.05 * c


LADDER = [
    ("rock",       _policy_rock,        0,  1),
    ("thermostat", _policy_thermostat,  0,  2),
    ("flame",      _policy_flame,       1,  3),
    ("raf",        _policy_raf,         2,  3),
    ("chemoton",   _policy_chemoton,    3,  4),
    ("organism",   _policy_organism,    4,  4),
]


def run_ladder(n: int = 6000, seed: int = 7) -> list[LadderResult]:
    return [
        _compute_factors(
            n=n, name=name, policy=policy,
            maintained_constraints=m, required_constraints=r,
            seed=seed + i,
        )
        for i, (name, policy, m, r) in enumerate(LADDER)
    ]
