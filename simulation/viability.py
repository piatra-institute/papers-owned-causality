"""Viability and the Delta-V_T contribution.

For the bistable system, viability is taken as fractional occupancy of basin A
(the X > 0 well), with V in [0, 1]. The Delta-V contribution from endogenous
control is the difference between the system's viability under its own
constraint deployment and its viability under a scrambled constraint sequence,
with identical noise:

    Delta_V_T  =  E[ V | do(U_Omega) ]  -  E[ V | do(scramble(U_Omega)) ].

Scrambling preserves the marginal distribution of constraint values but breaks
their time-directed coupling to the state. A non-zero Delta_V_T means the
constraint's identity over time, not its average level, is what changes
viability.
"""
from __future__ import annotations

import numpy as np


def viability(q: np.ndarray, target_sign: int = +1) -> float:
    """Fraction of time the macrostate sits in the viable basin."""
    q = np.asarray(q)
    if q.size == 0:
        return 0.0
    return float((np.sign(q) == target_sign).mean())


def delta_v(
    q_endogenous: np.ndarray,
    q_scrambled: np.ndarray,
    target_sign: int = +1,
) -> float:
    return viability(q_endogenous, target_sign) - viability(q_scrambled, target_sign)
