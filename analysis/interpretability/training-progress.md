# Can internal signals make safety training durable?

Review: 11 November 2026. This is the second route-specific investigation, after
[auditing](audit-progress.md). The public presentation is
[Training safer models with internal signals](../../interpretability_training.html).
The [ledger](training-progress.json) records exact paper versions, experimental
protocols, numerical observations and limitations. No experiments were rerun.

## Why investigate this route next?

My prioritization judgment is that training is the most promising next route to
investigate, not that it has the highest established probability of success.
It has an observable intervention, relatively direct baseline comparisons and
multiple ways to succeed. It could prevent failures without requiring an
explanation of the whole model or a runtime monitor with near-perfect coverage.
These make it particularly suitable for the user's optimistic falsification test.

The causal claim is: information or interventions obtained from model internals
improve the training process; the resulting policy avoids dangerous behavior in
deployment; this additional improvement changes a consequential outcome. Each
link needs evidence. A reduction in a training loss is not the second link, and
a benchmark improvement alone is not the third.

I include probe-assisted preference labeling, direct internal losses, and latent
adversarial training. The last is adjacent to interpretability: it can exploit
internal structure without a human-readable explanation. This generous scope
avoids prematurely dismissing a useful descendant of interpretability research.
It also prevents attributing every representation-level result to mechanistic
understanding. Count a research contribution only when its incremental value is
established against a competitive alternative.

## Selection and verification

This purposive review starts from the previously selected probe-training paper,
then follows its references to latent adversarial training and lie-detector
supervision, and searches for follow-up scaling and evasion studies. It is not a
systematic search or an estimate of how frequently methods succeed. The ledger
contains six primary sources: the 2019 proposal, the 2024 targeted LAT study, the
2025 SOLiD study, and three 2026 follow-ups. Version dates are distinguished from
first submission dates. Missing years are not scored as zero progress.

The numerical extraction covers all rows of the probe paper's Table 1 and Table
9, plus explicitly stated endpoint numbers in the scaling paper. Table 1 and
Table 9 use different judges and interventions; their numbers must not be joined
into a trajectory. The scaling results are a within-study model-size comparison,
not successive years of research progress. Its spontaneous-lie analysis is a
different subset and metric from its headline training result.

Run `python3 analysis/interpretability/build_training_progress.py --check-sources`
to compare those transcriptions with the versioned primary HTML, export the CSV,
and render the page's evidence tables from the ledger. The network check is a
transcription check, not an experimental replication, significance test, or
verification of the authors' causal interpretation. Reported dispersion is
preserved without converting it into confidence intervals. Repeated prompts or
training seeds are not independent evidence about new hazard families.

## What changes the judgment?

The key new negative finding is about **durability**, while the strongest new
positive finding is that model scale can help a specified supervision protocol.
Neither supports a monotonic story in which larger models inevitably become
harder or easier to align. The webpage gives the exact comparisons and their
primary-source links.

The appropriate optimistic response is to split the proposed uses:

1. **Final training before a frozen deployment.** Later weight-update failures
   do not directly falsify this use. It still needs generalization to unseen
   opportunities for harm, independently evaluated useful performance, and
   comparison with the best behavioral training. In-context adaptation and
   strategic behavior remain possible even with fixed weights.
2. **Safety maintained through continued training.** A one-time intervention
   must survive the intended continuation, or be reapplied effectively. If it
   is reapplied, account for data collection, retraining, validation and the
   interval during which the model is inadequately protected. Revalidating
   before deployment can eliminate that exposure, but adds time and cost.
3. **Safety retained after an untrusted party changes weights.** This is a
   stronger, separately evaluated requirement. Failing it cannot by itself
   reject the controlled-training or frozen-deployment routes.

The best next experiment is therefore a **repair-and-retention experiment**:
apply the best combined behavioral and internal method to a capable target;
continue training on a realistic benign capability task or an independently
constructed reward-hacking environment; reapply the intervention if that is the
proposed operational protocol; evaluate both utility and harmful outcomes using
fresh evaluators. Give the behavioral-only baseline the same total budget,
including any saved internal-tool expense. Optimize attacks separately against
both systems under the same declared access and search budget.

Do not equate three different tests: updating a probe during safety training,
retraining a probe for evaluation, and rerunning a complete safety intervention
after capability training. Success at one does not establish the others.

## A compact metric and a progress test

At fixed total defense cost and minimum useful task performance, measure the
fraction of independently evaluated harmful episodes prevented by adding an
internal training signal to the best behavioral training pipeline. Repeat after
declared amounts and kinds of continued training, and against separately
optimized attacks. Compare old and new method vintages on both frozen and fresh,
more capable targets. Publish absolute failure rates as well as the proportional
reduction, `1 - p_internal / p_behavioral`, with uncertainty by target and hazard
family. It is undefined when the behavioral baseline has zero observed failures;
report uncertainty bounds instead. Negative values mean worse outcomes.

This is a proposed measurement, not a re-expression of StrongREJECT scores or
undetected-deception fractions as catastrophe probabilities. Training budget
means actual compute, data and human effort, not just the number of examples.
Useful performance must include the task being improved by continued training:
holding a model close to its starting policy can preserve safety by preventing
useful learning. A fixed regularization coefficient does not fix that tradeoff.

For pace, maintain three panels: new methods on old targets (method progress),
old methods on new targets (new difficulty), and new methods on new targets
(whether the intervention keeps up). Register the task and hazard inclusion
rules in advance; report the frozen panel separately from additions. Model
parameter count is a covariate, not a sufficient measure of dangerous capability.
Measure relevant autonomy, opportunity to evade supervision and useful learning.

A useful supplementary measure is the largest **tested** continuation budget
for which the full protocol meets a chosen failure and utility threshold. Report
it separately for benign learning, reward hacking and adversarial weight changes.
It is a bound on the evaluated conditions, not a universal robustness radius.
No such comparable historical series is established by this review.

## Decision rule

Advance this route if independent replications show a persistent additional
benefit on fresh hazard families, through operationally relevant training and
repair cycles, without giving up the capability gains that motivate deployment.
Deprioritize a specific program if the strongest affordable repairs repeatedly
fail these tests, including under favorable controlled-provenance assumptions.
Rejecting all future interpretability research would require a much broader
argument, including the scientific-discovery and warning routes.

To answer "fast enough," specify a deployment scenario, a tolerated residual
failure rate, and a deadline range. Then ask whether the measured capability and
continuation envelope covers that scenario before the deadline. A publication
timeline alone supplies none of these. The present evidence supports a focused
durability test; it does not justify a readiness date or abandoning the route.
