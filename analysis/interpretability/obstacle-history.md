# Are old interpretability obstacles being retired?

Evidence review completed 11 November 2026. Research question: does the historical
record support a trajectory toward timely, decisive catastrophe prevention, or
mainly increasingly capable demonstrations with unresolved safety requirements?

**Result:** the selected histories show real local repairs and one useful
same-benchmark improvement, alongside recurring problems of coverage, faithfulness
and robustness. They undermine extrapolation from attractive demonstrations to
dependable prevention. They do not establish that the entire field is too slow,
or that unforeseen discoveries cannot help. The public observations assembled
here do not identify a completion-time distribution.

## Method and limits

I selected four histories covering representation recovery, auditing, internal
supervision and interpretable construction. Selection was purposive, seeking
strong positive results with follow-up scrutiny, not a random sample. For each,
I sought the original motivation, concrete advance, challenge, and strongest
identified repair. The underlying goals predate recent benchmarks; their broad
wording was not a commitment to a fixed numerical target or delivery date.

The [event ledger](obstacles.json) supplies dated sources, locators, findings and
scope restrictions; the [CSV](obstacles.csv) makes the chronology independently
inspectable. It includes positive evidence and unresolved cases. It is not a
2019–2026 comparable performance series. An omitted year is not zero progress.
No experiments were rerun. Source transcription can be checked with:

```sh
python3 analysis/interpretability/build_obstacles.py --check-sources
```

I distinguish four outcomes: a narrower obstacle is mitigated; a claimed extension
is challenged; a requirement remains untested; or a result is replicated within
scope. “No verified retirement found” is not equivalent to “no solution exists.”
Likewise, a study with different access, models or metrics cannot overturn an
earlier finding merely because its headline number is worse.

## 1. Recovering features: extraction advances, coverage remains uncertain

The [2020 circuits program](https://distill.pub/2020/circuits/zoom-in/) already
allowed features to be directions rather than individual neurons. Thus, moving
to dictionaries was a methodological development within the program, not a
retreat from a promise that every neuron would have one meaning.

[Dictionary learning in 2023](https://www.anthropic.com/research/towards-monosemanticity-decomposing-language-models-with-dictionary-learning)
made features accessible in a small transformer.
[Scaling to Sonnet in 2024](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html)
was an important extension, but the authors explicitly lacked a completeness
denominator. These are genuine advances in extraction, not evidence that the
unexplained remainder is safe to ignore.

The [September 2024 absorption study](https://arxiv.org/abs/2409.14507v1) found
that apparently clean features could miss cases they should cover. Simple size
or sparsity changes did not remove that issue in its first-letter task. This is
relevant to using a missing feature activation as evidence of absence.

The repair matters. [Matryoshka SAEs, March 2025](https://arxiv.org/html/2503.17547v1)
avoid absorption in a toy example and reduce it in tested language models. Nested
objectives introduce a reported training-time tradeoff. This is evidence against
the claim that each newly found obstacle is necessarily fundamental.

But evaluation also became more demanding. [SAEBench](https://arxiv.org/html/2503.09532v1)
extends absorption measurement and shows why reconstruction proxies cannot stand
in for practical performance. [MIB](https://arxiv.org/abs/2504.13151v1) finds no SAE
advantage over neurons for its causal-variable localization tasks. Neither result
erases feature discovery or directly refutes the Matryoshka result. A
[2026 visual-hierarchy study](https://arxiv.org/abs/2606.22994v1) finds related
absorption problems, but changes modality and evaluation; it is not a matched
failed replication either.

There are operational improvements too: a recent
[activation-storage study](https://arxiv.org/abs/2611.07756v1) reports 8–64× less
storage with little loss on its quality measures. That does not imply equivalent
improvement in total analysis cost or safety assurance.

**Assessment:** a previously limiting way of finding features has improved, and
a specific pathology has been partly repaired. No reviewed result turns feature
counts or reconstruction quality into a bound on missed safety-relevant concepts.
Local progress survives; broad coverage is not retired as an obstacle.

## 2. Auditing hidden objectives: measurable improvement, conditional reliability

The [2019 account of Olah's agenda](https://www.alignmentforum.org/posts/X2i9dQQK3gETCyqh2/chris-olah-s-views-on-agi-safety)
described audits that systematically find problems instead of relying on lucky
discoveries. It was an ambition, not a quantified deadline.

The [2025 hidden-objective auditing game](https://arxiv.org/html/2503.10965v2)
demonstrated successful discovery, but all successful teams could search training
data, and one succeeded without SAE tools. This is a useful proof of possibility;
it does not isolate the added value of internal access.

[AuditBench, February 2026](https://arxiv.org/abs/2602.22755v1) supplies a standard
testbed and finds that good standalone tool evidence need not improve an auditing
agent. [Introspection adapters, April 2026](https://arxiv.org/html/2604.16812v1#S3.SS1)
then improve reported investigator success from 53% for the prior best method to
59% under the same benchmark protocol. That is six percentage points, or about
12.8% fewer misses relative to the prior 47% miss rate. The score permits any of
ten predictions to match; it is not a calibrated deployment rejection rate.
Costs are not held equal, and the rounded aggregates do not support a significance
claim or annualized improvement rate here.

A direct follow-up,
[Symmetry Defeats Auditing, May 2026](https://arxiv.org/html/2605.27836v1), applies
behavior-preserving weight transformations before attaching a published IA. On
seven fine-tunes, reported detection falls from 100% to 0–20%. This requires a
malicious supplier controlling weights. It uses a different subset, adapter and
metric from AuditBench: it does **not** show that 59% became zero on AuditBench,
or that an auditor controlling model provenance loses the original benefit.
The result is an author-reported attack, not independently reproduced here.

[Task-specific self-reports, July 2026](https://arxiv.org/html/2607.03640v2) provide
a repair for some transfer failures, but require target training data and
per-target training. They are not a verified defense against the symmetry attack.
This is a change in the available information and cost, not automatically a
changed success criterion; comparison must preserve those differences.

**Assessment:** the claim that internal access adds no auditing value is too
pessimistic. The claim that a successful transferable auditor has resolved
adversarial robustness is too optimistic. More capable tools and additional
requirements are appearing together. We cannot infer which trend will dominate.

## 3. Internal supervision: a long-standing concern gets concrete tests and repairs

The [2018 proposal](https://distill.pub/2018/building-blocks/) already warned that
training on an interpretability interface could optimize its appearance.
Recent work is testing an old concern, not discovering it from scratch.

[Circuit breakers, June 2024](https://arxiv.org/abs/2406.04313v1) make representation
control a concrete defense. A [July challenge](https://arxiv.org/html/2407.15902v1)
reports 100% attack success with revised continuous embedding attacks. This
challenges robustness in that access regime, not every practical benefit against
ordinary prompts. [Obfuscated Activations](https://arxiv.org/html/2412.09565v2)
adds tests of latent defenses and trained models; task difficulty can impose an
evasion cost. [Neural Chameleons](https://arxiv.org/html/2512.11949v1) demonstrates
transfer of learned evasion to unseen probes under a constructed trigger setup.

The strongest repair found in this pass is
[updating probes during training, October 2026 version](https://arxiv.org/html/2609.38645v3#S5).
Frozen objectives can be exploited, whereas updating probes improves tested
behavior and retains linear detectability. That counters the blanket proposition
that internal supervision must destroy monitoring. Its 7B–14B experiments do not
establish robustness under arbitrarily strong optimization or reproduce every
earlier attack setting.

**Assessment:** a plausible mechanism for improvement survives. The original
optimization concern remains active across generations of methods. A repair of
one exploit is not yet retirement of the general obstacle, but neither is each
new attack proof that repairs cannot accumulate.

## 4. Interpretable construction: simpler models do not automatically give faithful explanations

Deliberate design was part of the 2019 agenda. The
[2025 weight-sparse transformer study](https://arxiv.org/abs/2511.13653v1) supplies
a concrete approach, with smaller understandable circuits and a measured
capability–interpretability tradeoff. Its abstract identifies scaling beyond tens
of millions of nonzero parameters while preserving interpretability as a challenge.

A [February 2026 primary research post](https://www.lesswrong.com/posts/sHpZZnRDLg7ccX9aF/weight-sparse-circuits-may-be-interpretable-yet-unfaithful)
partly replicates the smaller-circuit result while finding that extracted circuits
can repurpose nodes and disagree with the original model under small input changes.
Most experiments use zero ablation instead of the original mean ablation. This
is evidence about the extraction strategy, not a clean refutation of every
original circuit or of sparse architectures themselves.

[July 2026 weight-level evaluation](https://arxiv.org/abs/2607.02964v1) strengthens
validation by testing descriptions on held-out text. It reports successful short
descriptions for 12–31% of tested sparse-model weights, with an advantage over
dense models. This percentage is not the fraction of model behavior explained,
and the remainder is not proven uninterpretable.

**Assessment:** the small-model interpretability advantage has supporting follow-up
evidence. Faithfulness of extracted explanations and adequate capability at an
acceptable cost remain separate requirements. The newer approach has not made
those old difficulties disappear.

## What can be said about speed?

These are observable publication intervals, not measured research effort or
durations for which the original findings were valid:

| Selected sequence | Days | What it establishes |
| --- | ---: | --- |
| AuditBench v1 → IA v1 | 51 | A same-benchmark improvement appeared soon after the benchmark's first paper. |
| IA v1 → symmetry attack v1 | 39 | An additional attacker capability rapidly exposed a vulnerability in a published configuration. |
| Circuit breakers v1 → embedding-attack critique v1 | 46 | A robustness challenge appeared quickly within a relevant tested attack class. |

These intervals are recomputed from the ledger, and earlier informal releases
can change a first-public-availability calculation. They do **not** show that
attack research is faster than defense research: the cases are selected, work
can overlap, and we lack effort and publication-lag data. No average obstacle
retirement time, failure rate or hazard of new obstacles is estimated.

The audit comparison is the clearest short fixed-task progress observation in
this review. It is still insufficient for a trend fit: two reported methods,
unequal development costs, a changing tool family, and no subsequent matched
trajectory. None of the four histories supplies a fixed safety criterion measured
across successive capability frontiers with a complete cost account.

The broad original ambitions consequently cannot be assigned a percentage
complete. Saying that none of these histories establishes broad retirement is
an evidentiary statement, not a measured zero-percent success rate. The ambitions
were broad enough that such a statistic would be misleading.

## Does this falsify timely prevention?

It weakens three shortcuts:

1. Better-looking explanations imply adequate coverage or faithfulness.
2. Better ordinary audit scores imply robustness to the relevant adversary.
3. A new internal defense permanently removes the problem of optimizing around
   the measured signal.

The reviewed counterexamples reject particular versions of those inferences.
They do not reject a field-wide possibility of decisive contribution. The
positive repairs also prevent a fair conclusion that apparent progress is merely
illusory. My assessment is **local progress with recurring safety-validation
obstacles**, rather than demonstrated convergence or demonstrated impossibility.

The recurring obstacle is often not new in principle: proxy optimization,
distribution shift, incomplete coverage and unfaithful explanations were already
concerns. Their reappearance in new techniques is evidence against assuming that
solving them in one setting retires them across the field. It does not estimate
how many comparably hard obstacles will arise in the future.

For a short deadline, a plan depending on broad assurance or robust adaptive
monitoring cannot treat these results as evidence that it is nearly complete.
For a longer deadline, the record is compatible both with accumulating repairs
and with continuing replacement of obstacles. There is no defensible numerical
arrival forecast from this sample. Early warning and an unforeseen discovery
remain possible without satisfying every assurance requirement.

## Most informative next test

Use the same target models, hidden behaviors, access and total audit budget to
compare successive auditing methods. Include known controls, a withheld behavior-
creation process, and two separate adversary regimes: controlled model provenance
and malicious weight supply. Report matched decision accuracy and false alarms,
then repeat at higher actor capability with the safety criterion fixed.

The historical review can be completed from public sources; that experiment
requires running models and is not performed here. It would distinguish
improvement on fixed problems from failure to keep pace with new capabilities.
Until such evidence exists, the justified update is against assuming that
benchmark gains establish readiness—not toward certainty that interpretability
will arrive too late.
