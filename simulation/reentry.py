"""Re-entry I(Q_{t+T} ; C_{t+T:t+2T}).

Mutual information between the achieved macrostate at the end of an episode and
the constraint configuration over the subsequent episode. A positive value
means the macrostate informs future constraint production; zero means the
system does not learn from outcomes.
"""
from __future__ import annotations

import numpy as np

from directed_info import mutual_information


def reentry(
    q_first_half_end: np.ndarray,
    c_second_half: np.ndarray,
    n_bins: int = 5,
) -> float:
    return mutual_information(q_first_half_end, c_second_half, n_bins=n_bins)
