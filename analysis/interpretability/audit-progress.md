# Is the strongest positive auditing result accumulating?

Research cutoff: 2026-11-11. Follow-up to the [obstacle histories](obstacle-history.md).
This is a targeted search for counterevidence to pessimism, not an exhaustive
leaderboard. No experiments were rerun. The [data](audit-progress.json) distinguish
source publication dates from retrieval dates; missing dates remain missing.

## What changed the assessment

The strongest positive observation is no longer just 53% → 59%.
[LoRAcles, §3.1 and Appendix F](https://openreview.net/pdf/5bfdac6526a2c1d8cf83e4fbb9e11a1a7a923540.pdf)
reports **71%** on the full AuditBench, compared with the published IA result of
59%. Its own four-run IA check reaches approximately 62%. The paper reports
uneven performance across training-data constructions. I verified these claims
through search-indexed passages of the primary PDF; direct retrieval returned
403. The exact date of this PDF version is unverified, so it is not a dated
trend point or independently reproduced result.

The [pinned author implementation](https://github.com/ceselder/loracles/blob/be71fa947a037f90d3d179a16cbd2ebc5d273a66/auditbench_paper_replication/README.md)
specifies 56 targets, Haiku 4.5, a 25,000-token investigator allowance, 16 runs
and ten final predictions. The new tool returns eight generated answers per
call. This supports protocol comparability; it does not reproduce the score or
establish equal total compute. The investigator allowance omits a complete
account of tool inference, training and preprocessing costs.

| Full-benchmark comparison | Reported success | Evidence status |
| --- | ---: | --- |
| Prior best, scaffolded text completion | 53% | Baseline reported in the IA paper |
| Introspection adapters | 59% | [Versioned paper, §3.1](https://arxiv.org/html/2604.16812v1#S3.SS1), 2026-04-18 |
| LoRAcles | 71% | Provisional source extraction; publication date unresolved |

Calculated from the rounded headlines, 59% → 71% means **29.3% fewer missed
investigations**: (0.71 − 0.59)/(1 − 0.59). This is a substantial local improvement.
It is not a reduction in catastrophic risk, nor the percentage of all problematic
behaviors discovered. A successful investigation identifies a planted behavior;
the benchmark does not sample the universe of future dangerous mechanisms.

## The behavioral alternative also moves

[Training Alignment Auditors via Reinforcement Learning, Appendix G](https://arxiv.org/html/2608.25460v1#A7)
tests only six TD+KTO behaviors, permits three predictions, and uses a Sonnet 4
judge. Table 10 reports base Haiku at 11.5% with scaffolded text completion and
33.3% with ordinary chat. The MT IG PW 4/8 FP, three-epoch auditor reaches 28.1%
and 33.3%, respectively. These are 96 audits per configuration. This particular
training gain depends on the interaction mode; ordinary chat shows no gain in
the aggregate. Other configurations differ. These are behavioral-auditing
results, not evidence of interpretability's incremental contribution.

The subset, prediction count and judge differ from the full-benchmark comparison.
Pooling the numbers would manufacture a misleading time series. A benchmark
name alone does not establish comparability. Neither study establishes a
fixed-cost, fixed-false-alarm improvement in deployment decisions.

## A better falsification target

My update is **against the claim that useful internal auditing is stagnant**.
The available result merits verification and a cost-matched replication. It
does not resolve whether the remaining difficult cases yield to further work,
or whether stronger targets replenish them faster than methods remove them.
Falsification must allow this positive evidence to count without treating
success on an easier prerequisite as completion of the safety case.

For this route, I would track the following short metric:

> **At a fixed total audit cost and false-alarm allowance, what fraction of
> concealed hazards does the best internally assisted audit catch, compared
> with the best audit without internal access? Evaluate successive method
> vintages both on frozen targets and on fresh, more capable targets. Report
> the two absolute detection rates and the fraction of baseline misses removed.**

This is a proposed measurement, not a new estimate. Use hazard families and
independently constructed targets as the sampling units; repeated runs mostly
measure investigator randomness. Include benign controls and publish predictions,
adjudications, prompts, target provenance, tool costs and method versions. Count
setup costs separately and show their amortization. Fix the allowed number of
claims so indiscriminate guessing cannot masquerade as discovery. A finding
should support a correct intervention, even if it does not explain the entire
dangerous objective.

Crossing old/new methods with old/new targets separates three questions:

| Comparison | Question answered |
| --- | --- |
| New versus old methods, frozen targets | Are we overcoming already observed obstacles? |
| Frozen methods, fresh targets | How much difficulty do new targets introduce? |
| New methods, fresh targets | Is achieved coverage keeping up at the specified budget? |

“More capable” needs a declared, independently measured capability relevant to
the threat, such as strategic concealment or autonomous task completion. Model
parameter count alone is unsuitable. Hold the hazard construction and attack
budget fixed for one comparison; separately test held-out constructions and
stronger attackers. Otherwise a difficulty increase has several possible causes.
Report stratified results rather than subtracting scores on arbitrary mixtures.

## What would actually change a safety priority?

- **Toward deprioritizing this route:** across several preregistered target
  cohorts, an optimistic internally assisted audit shows no material advantage
  at equal cost, or its gains consistently disappear on held-out concealment
  processes. One failed method is insufficient to reject the route.
- **Toward investing further:** meaningful absolute coverage gains persist
  across fresh targets and stronger attacks, costs remain tolerable, and the
  resulting interventions prevent failures in held-out end-to-end tasks.
- **Still undecided:** a rising frozen-benchmark score with unmeasured transfer,
  cost or false alarms. That is where the current comparison leaves us.

“Fast enough” also requires an external deadline and a route-specific coverage
threshold: a warning sufficient to pause deployment needs less coverage than a
safety guarantee. Neither is inferred from AuditBench. Evaluate plausible
deadline/threshold scenarios explicitly; do not present a fitted arrival date
until comparable observations support it. The same caution applies to an
unforeseen discovery: these results can test the auditing route, not rule out
every way interpretability might prevent catastrophe.

## Verification

```sh
python3 analysis/interpretability/build_audit_progress.py
python3 analysis/interpretability/build_audit_progress.py --check-sources
```

The script validates the ledger, exports CSV, checks arithmetic, and optionally
checks IA numbers, the paired RL table rows and pinned tool settings online.
It explicitly leaves the LoRAcles headline pending manual PDF verification.
It does not certify that the source experiments or judgments are correct.
