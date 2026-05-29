"""Closure score Gamma_T.

Two factors combine:

    Gamma_T = P(Omega persists across T) * (maintained_constraints / required_constraints)

For the bistable organisation, persistence is taken as the fraction of time the
trajectory remains within a bounded region (|X| < 3), interpreted as boundary
continuity. The maintained-constraint fraction is the fraction of internally
maintained constraints over all constraints required for the dynamics; this is
a per-system constant set in the agency_ladder module.
"""
from __future__ import annotations

import numpy as np


def persistence(x: np.ndarray, bound: float = 3.0) -> float:
    inside = (np.abs(x) <= bound).mean()
    return float(inside)


def gamma(
    x: np.ndarray,
    maintained_constraints: int,
    required_constraints: int,
    bound: float = 3.0,
) -> float:
    if required_constraints <= 0:
        return 0.0
    return persistence(x, bound=bound) * (maintained_constraints / required_constraints)
