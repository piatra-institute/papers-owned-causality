# Audit

Dated log of editorial passes and verification runs. Newest first.

## 2026-06-13 — voice reform

Voice-reform editing pass to remove AI-writing tells (house voice.md).

Lexical density: before — carries/carry 5, the very 3, genuinely 2, exactly 1, load-bearing 1; tricolon proxy 35. After — carries/carry 5, the very 3, genuinely 2; tricolon proxy 35.

Changes:
- Fixed five inline-contrastive (", not Z") constructions into positive declaratives: §2 ("exhibit it on top of, not instead of" -> "exhibit the same structural property, with consciousness layered above it"); §3.3 ("chemistry in a soup, not yet an organisation" -> "still chemistry in a soup; it remains short of an organisation"); §3.4 ("constraint deployment, not direct material push" -> "rather than direct material push"); §4.1 ("arrives with the closure, not on top of it" -> "arrives with the closure itself, already present in the act of self-maintenance").
- Retitled §5 from the contrastive "Basin steering, not point control" to "Agency as basin steering". Paper title ("Basin Steering") and §5.1 cross-references unaffected; no internal references to the old heading.
- Removed pet-vocabulary "load-bearing" in §6.2 ("was load-bearing for survival" -> "was necessary for survival"); deleted filler "exactly" in §9 closing.
- Varied a repeated rhythmic device: §8.1 keeps "Same architecture, different attractor"; §9 closing changed from "Same architecture, different downstream phenomenology" to a plain declarative.
- §2 distinctive opener ("What 'owned' is not") kept. No numbers, citations, math, or tables touched. En-dashes in reference page ranges left intact (pandoc convention, not the banned em-dash).

Verify: voice 0 errors, 0 warns; refs 44 in-text keys unchanged, 0 missing, 1 unused (pre-existing); claims no-match values pre-existing (scientific-notation table values and the 10.9 ratio, untouched); build clean; check => PASS.

## 2026-05-29 — upgrade pass (Group A)

Scope contract:
1. Motivate the four factors before the formula: add an impostor-preview
   paragraph in §6.2 ahead of the Definition; replace the throat-clear transition.
2. Cut §6.3 "The right-hand side, audited" — redundant with the Definition's
   closing line and §9's opening.
3. Sharpen the Rosen vs Moreno-Mossio distinction in §3.4 (efficient causes vs
   the wider class of constraints).
4. Add Barbieri's code biology to §3.5 (semantic closure) + bibliography.
5. Voice tightenings: §3.1 "grammar" cadence; §5.1 bloated Lorenz sentence;
   §9 "The order of construction is the important point" throat-clear + the
   italic takeaway-label on the latent variable.

Verification: voice 0 errors; refs 0 missing (Barbieri added both sides); claims
trace to results.json (no new numbers); build clean; check => PASS.

## 2026-05-13 — reference expansion

Scope: a synthesis on agency was missing cornerstone authors; broaden and
integrate.

Changes:
- +12 references (Juarrero, Deacon, Kauffman 2000, Campbell, Thompson, Levin,
  Prigogine, Schrödinger, England, Ellis, Damasio, Dennett), each woven into the
  body section where it earns its place rather than appended to the bibliography.
  §3.1 Prigogine/Schrödinger; §3.4 Kauffman 2000 + Juarrero + Deacon; §4.1
  Thompson; §5.1 England + Levin; §5.2 Campbell + Ellis; §9 Damasio + Dennett.

Verification:
- voice: 0 errors, 0 em-dashes, 0 Pattern-2 negate-pivots, 0 numbered-observation lists.
- refs: 43 references → expanded; every in-text citation resolves both ways.
- build: clean, 17 pages (was 15), zero missing-character warnings.
- synced public/papers/owned-causality.pdf.

## 2026-05-13 — voice + reference-locator audit

Scope: voice pass + fix high-error citation locators.

Changes:
- Pattee (1982): corrected *Cognition and Brain Theory* 5(4) → vol 4 (verified
  against Pattee's official bibliography).
- Added Friston, Parr & de Vries (2017); §9 now cites it explicitly rather than a
  bare "Friston et al." with no co-authored entry.
- Voice fixes: dropped trailing ", not upstream" contrastive (§6.3); rewrote a
  "not a failure ... It is" negate-pivot as a positive declarative (§10.3); split
  a "Three implications follow" numbered list into standalone paragraphs (§9).
- §6.1 counting fix: "five variables ... all six" → "seven components ... all
  seven" (matches the seven-tuple Definition).

Verification:
- voice: 0 em-dashes, 0 Pattern-2, 0 numbered-observation lists.
- build: 15 pages, zero missing-character warnings.

---

## 2026-07-02 — reform pass (strip proof theater)

Corpus reform. The paper's synthesis and its honest disclosure of the non-monotonic within-group ordering (§7.1) were left intact; the target was the "\begin{proposition}...\square" theater the audit flagged, where elementary facts wore theorem clothing.

- paper/PAPER.md §7.1: Proposition [Closure boundary] ("if Γ=0 then 𝔒=0") and its one-line proof ("product of non-negative factors") converted to plain prose. The claim is arithmetic (a product with a zero factor is zero); it needed no proposition environment. Numbers preserved (Δν_T=0.090).
- paper/PAPER.md §8.2: Proposition [Scaffold handover] and its "Proof. Direct evaluation against results.json" removed; the added content (peak ratio 10.9, crossover values 0.059/0.016, min viability 0.885) folded into prose as readings from a single realisation, explicitly not a theorem. The `\begin{definition}` environments in §6 (Organisation, Owned causality) are legitimate and kept.
- Verify: no `\begin{proposition}`/`\square` remain; voice 0 errors; refs 0 missing/0 unused; claims unchanged from baseline (5 pre-existing sci-notation/parameter no-matches, none introduced); check => PASS; synced.
