"""A stylised bistable organisation.

The organisation Omega has:

    X      slow material state (a real number; basin coordinate)
    C      internal constraint (a real number; drift bias)
    B      boundary indicator (binary; persistence test)
    M      measurement of own state (a real number; here, X itself)
    Q      macrostate (categorical; sign of X = which basin)

Dynamics on a unit time grid:

    dX = ( -V'(X) + g(C, X) + e_t ) * dt + sigma * sqrt(dt) * eta_t
    dC = ( lambda * (rho * sign(X)  - C) ) * dt   when constraint_closure is True
    C  fixed at 0                                  when constraint_closure is False

with V(X) = (X**2 - 1)**2 / 4, a double-well potential. The constraint C drifts
toward rho * sign(X) under closure, but only insofar as the macrostate sign(X)
is itself biased by C. The endogenous active perturbation is

    U_Omega_t = g(C_t, X_t) = C_t * (1 - X_t**2)

shaped to act maximally near the barrier. The external perturbation is e_t.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np


@dataclass
class BistableOrganization:
    sigma: float = 0.45
    rho: float = 0.6
    lam: float = 0.25
    dt: float = 0.05
    constraint_closure: bool = True
    scramble_constraint: bool = False

    def potential_derivative(self, x: float) -> float:
        return x * (x ** 2 - 1.0)

    def g_constraint(self, c: float, x: float) -> float:
        # Acts maximally near the barrier (x ~ 0).
        return c * (1.0 - x ** 2)

    def simulate(
        self,
        n_steps: int,
        x0: float = -0.9,
        c0: float = 0.0,
        external: Callable[[int], float] | None = None,
        rng: np.random.Generator | None = None,
        scramble_seed: int | None = None,
    ) -> dict:
        rng = rng if rng is not None else np.random.default_rng(0)
        x = np.empty(n_steps + 1)
        c = np.empty(n_steps + 1)
        e = np.empty(n_steps)
        u_omega = np.empty(n_steps)
        x[0] = x0
        c[0] = c0

        for t in range(n_steps):
            e_t = external(t) if external is not None else 0.0
            e[t] = e_t
            u_omega[t] = self.g_constraint(c[t], x[t])
            drift = -self.potential_derivative(x[t]) + u_omega[t] + e_t
            noise = self.sigma * np.sqrt(self.dt) * rng.standard_normal()
            x[t + 1] = x[t] + drift * self.dt + noise
            if self.constraint_closure:
                target = self.rho * np.sign(x[t]) if abs(x[t]) > 1e-6 else 0.0
                c[t + 1] = c[t] + self.lam * (target - c[t]) * self.dt
            else:
                c[t + 1] = 0.0

        if self.scramble_constraint and scramble_seed is not None:
            rng2 = np.random.default_rng(scramble_seed)
            perm = rng2.permutation(n_steps)
            c_scrambled = c[:-1][perm]
            # Replay with scrambled c sequence and fresh noise from rng.
            x2 = np.empty(n_steps + 1)
            u2 = np.empty(n_steps)
            x2[0] = x0
            rng3 = np.random.default_rng(rng.integers(0, 2 ** 31 - 1))
            for t in range(n_steps):
                u2[t] = self.g_constraint(float(c_scrambled[t]), x2[t])
                drift = -self.potential_derivative(x2[t]) + u2[t] + e[t]
                noise = self.sigma * np.sqrt(self.dt) * rng3.standard_normal()
                x2[t + 1] = x2[t] + drift * self.dt + noise
            return {
                "x": x2,
                "c": np.concatenate([c_scrambled, c_scrambled[-1:]]),
                "e": e,
                "u_omega": u2,
                "q": np.sign(x2),
            }

        return {
            "x": x,
            "c": c,
            "e": e,
            "u_omega": u_omega,
            "q": np.sign(x),
        }
