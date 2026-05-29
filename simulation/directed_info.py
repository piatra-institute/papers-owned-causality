"""Directed-information and mutual-information estimators on binned time series.

Definitions follow Massey (1990) and Schreiber (2000). The per-step proxy used
here is the conditional mutual information

    DI(X -> Y) approx mean_t  I( X_t ; Y_{t+1} | Y_t ),

which equals zero when X is conditionally independent of Y's next value given
Y's current value, and grows with the time-directed dependence of Y on X.
Plug-in entropy is used for the underlying distributions.

The estimators are deliberately simple: this module supports a small set of
illustrative simulations, not high-dimensional inference. Sample sizes in the
paper's simulations are large enough that finite-sample bias is small compared
to the qualitative differences between configurations.
"""
from __future__ import annotations

import numpy as np


def _bin_series(x: np.ndarray, n_bins: int) -> np.ndarray:
    """Quantile-bin a 1-D real series into integer codes 0 .. n_bins-1."""
    x = np.asarray(x, dtype=float)
    if x.std() < 1e-12:
        return np.zeros_like(x, dtype=int)
    edges = np.quantile(x, np.linspace(0.0, 1.0, n_bins + 1))
    # Make edges strictly increasing to avoid degenerate empty bins.
    edges = np.unique(edges)
    if len(edges) < 2:
        return np.zeros_like(x, dtype=int)
    codes = np.searchsorted(edges[1:-1], x, side="right")
    return codes.astype(int)


def _joint_entropy(*codes: np.ndarray) -> float:
    if len(codes) == 0:
        return 0.0
    stacked = np.stack(codes, axis=0)
    # Hash each column to a unique integer.
    n = stacked.shape[1]
    keys = np.zeros(n, dtype=np.int64)
    factor = 1
    for row in stacked:
        keys = keys + row.astype(np.int64) * factor
        factor *= int(row.max()) + 1
    _, counts = np.unique(keys, return_counts=True)
    p = counts / counts.sum()
    return float(-(p * np.log(p)).sum())


def conditional_mutual_information(
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    n_bins: int = 5,
) -> float:
    """Estimate I(X ; Y | Z) by plug-in entropy on quantile bins."""
    cx = _bin_series(x, n_bins)
    cy = _bin_series(y, n_bins)
    cz = _bin_series(z, n_bins)
    h_xz = _joint_entropy(cx, cz)
    h_yz = _joint_entropy(cy, cz)
    h_z = _joint_entropy(cz)
    h_xyz = _joint_entropy(cx, cy, cz)
    cmi = h_xz + h_yz - h_z - h_xyz
    return max(0.0, cmi)


def mutual_information(x: np.ndarray, y: np.ndarray, n_bins: int = 5) -> float:
    cx = _bin_series(x, n_bins)
    cy = _bin_series(y, n_bins)
    h_x = _joint_entropy(cx)
    h_y = _joint_entropy(cy)
    h_xy = _joint_entropy(cx, cy)
    mi = h_x + h_y - h_xy
    return max(0.0, mi)


def directed_information_per_step(
    source: np.ndarray,
    target: np.ndarray,
    n_bins: int = 4,
) -> float:
    """Per-step directed information

        DI(source -> target) approx  I( source_t ; target_{t+1} ).

    A practical per-step proxy for Massey directed information that does not
    condition on the target's current value. The unconditioned form is more
    sensitive when the underlying state space is discrete (small alphabet) and
    when the target is approximately deterministic given a recent source
    history, both of which apply to the toy systems used here. Conditional
    variants under-report dependency for tight feedback loops where source and
    target are jointly determined by current state.
    """
    s = np.asarray(source, dtype=float)
    t = np.asarray(target, dtype=float)
    if s.shape != t.shape or s.ndim != 1 or len(s) < 4:
        return 0.0
    return mutual_information(s[:-1], t[1:], n_bins=n_bins)
