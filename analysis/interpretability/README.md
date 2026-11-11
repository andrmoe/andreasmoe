# Internal activation monitoring: evidence and optimistic screen

This is a curated evidence review, not a systematic review or a fitted historical
growth model. Cutoff: 2026-11-10. `evidence.json` is the canonical source for the
page. `build.py` validates it and writes the browser bundle and downloadable CSV.

```sh
python3 analysis/interpretability/build.py
node --test analysis/interpretability/model.test.js
python3 analysis/interpretability/check_sources.py
```

The last command uses the network to check selected numerical extractions against
versioned primary-source HTML. It does not rerun the authors' experiments.

The separate [falsification review](falsification.md), dated 2026-11-11, stress-tests
the catastrophe-prevention claim across monitoring, auditing, training, verification
and scientific discovery. Its additional sources are linked inline; they are not
pooled into the monitoring dataset or fitted as a historical series.
The [historical assessment](original-case.md) compares progress with the original
safety arguments and distinguishes new techniques from changed success criteria.

## Inclusion rule

Include internal-state monitors with public safety-relevant detection results.
Keep ranking metrics (AUROC), threshold recall, poisoning identification,
high-stakes classification and deception/sabotage separate. Include contrary
evidence about adaptation. Earlier work gives context, not invented annual scores.
There is no common fixed benchmark covering 2019–2026 in this collection. An empty
year means no selected comparable observation, not zero capability or no research.

## Numerical provenance

- Apollo: version 1, section 4.1.1, AUROCs and approximately 96% roleplaying recall
  (the text says 4% missed). Its false-positive reference is unrelated Alpaca
  dialogue, not honest responses in the deception scenarios. Appendix E Table 3
  lists a conflicting 0.998 roleplaying recall. We retain the main-text 0.96 as
  approximate, flag the inconsistency, and do not average the two values.
- High-stakes: version 2, section 3 gives approximately 43% probe recall and 55%
  best LLM recall at 1% FPR. These are reported aggregates. Appendix A.3 Tables
  5–6 give theoretical inference cost formulas; they exclude training and assume
  the monitored model's activations already exist. The 40% routing example is
  an AUROC/cost comparison, not evidence of high recall at low FPR.
- FIBS: version 1, Appendix E Table 12 gives numerators and denominators for eight
  hidden-goal conditions. We use counts rather than rounded recalls. These are
  a stress test of hidden-state readout, not runtime sabotage measurements.
  Own-goal lies and off-goal honest denials are selected using a CoT monitor;
  labels and question clusters limit generalization and independent sample size.
- FAR.AI's live project page reports 73% sabotage-step recall at 1% FPR. Its
  author-reported best result is dated by retrieval (2026-11-10), not backdated to
  the paper's first publication. The page does not specify which model produces
  this particular number or supply its numerator, denominator or confidence
  interval. We do not infer them. The live page and paper abstract/main text also
  have different AUROC summaries; they are not silently merged.
- A zero recall under obfuscation is a reported experimental result for specified
  attacks, not a bound on all future monitors. No uncertainty interval is invented.
- No confidence intervals are constructed from repeated questions as if they
  were independent samples. Exact counts are extraction precision, not certainty.

## Scenario model (not an empirical fit)

For observed single-check recall r and assumed transfer t, m = 1 - r*t.
If fraction z of these misses persist at every checkpoint, b = z*m. For k >= 1:

    E(k) = b + (1-b) * ((m-b)/(1-b))**k

E(1)=m. z=0 is independent misses; z=1 makes every miss persistent. Re-reading
the same deterministic probe output is not an independent checkpoint. k requires
new, informative opportunities before irreversible harm and perfect intervention
when flagged. The curves are not estimates of catastrophic risk or of the joint
failure of a whole safety stack. A first irreversible action may allow only k=1.

Normalized benign-traffic monitoring cost, relative to one full reference
text-monitor pass, is:

    C(k) = A/N + k*(c + alpha*h)

A is setup cost in reference-pass units, N amortization volume, c checkpoint
cost, alpha the selected study's nominal FPR and h cost per false alarm. We
charge all k checks. True-positive handling is omitted for a rare-event,
optimistic screen. Token lengths, human review prices and latency need separate
measurement. No empirical dollar cost or calibrated cost-to-99.9%-coverage curve
is claimed. Input c is deliberately free because follow-up inference, activation
collection and engineering can dominate probe-head arithmetic. The cost example
from high-stakes detection is not transferred as a measurement to FIBS.

## Decision interpretation

The screening judgment is **investigate further**. Cheap internal readouts have
demonstrated signal, so current evidence does not establish that this route must
fail. It does not establish deployment adequacy. Low-FPR coverage under adaptive
attacks, transfer, correlated errors, preventive timing and end-to-end cost remain
open. A negative result here would not reject model editing, better training,
interpretable architectures or verification as theories of change.
