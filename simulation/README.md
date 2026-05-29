# Simulation

Computes the owned-causality formula

$\mathfrak{O}_T(\Omega) = \Gamma_T(\Omega) \cdot DI(U^\Omega \to Q) \cdot \Delta V_T \cdot I(Q; C)$

on a six-rung agency ladder running a common bistable Langevin dynamics under different constraint-production policies, and traces the scaffold-handover protocol over an episode in which an external scaffold withdraws linearly while the organism's own constraint loop activates.

```
uv run run_all.py
```

Produces `output/results.json` (every numeric claim cited in the paper is a key there) and two figures under `output/figures/`.

Modules:

- `organization.py` — bistable Langevin organisation with optional constraint closure.
- `agency_ladder.py` — six rungs (rock, thermostat, flame, RAF, chemoton, organism) running a common dynamics under different policies.
- `scaffold.py` — handover protocol; constraint loop gated off initially, activated as the scaffold withdraws.
- `closure_score.py`, `viability.py`, `reentry.py` — the four formula factors.
- `directed_info.py` — plug-in mutual-information and per-step directed-information estimators.
- `figures.py` — ladder bar chart, handover crossover plot.
- `run_all.py` — orchestrator.

Dependencies: `numpy>=1.26`, `scipy>=1.11`, `matplotlib>=3.8`. Python $\geq$ 3.10.
