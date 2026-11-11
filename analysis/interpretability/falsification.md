# Trying to falsify interpretability as catastrophe prevention

Research pass: 11 November 2026. This is an adversarial review of selected primary
sources, not a systematic review, experimental replication, or probability estimate.
The numerical monitoring archive retains its separate 10 November cutoff.

## What is the hypothesis?

“Interpretability research will prevent an existential catastrophe” is a claim
about a future counterfactual. Present benchmark results cannot directly falsify
it. The useful research question is whether any plausible route can deliver a
large **additional** reduction in catastrophic risk, soon enough and at a cost
that permits adoption. We should specify a target reduction, resource budget,
deployment setting and deadline before declaring a route adequate or infeasible.
Those are decision inputs; the literature does not supply universal thresholds.

There are at least three materially different claims:

1. Current internal tools justify relying on a model's safety. The reviewed
   evidence does not establish this; some proposed assumptions have concrete
   counterexamples.
2. Further interpretability research could become a decisive safety contribution.
   This survives the present falsification attempts.
3. Interpretability will actually prevent catastrophe. This also requires the
   right threat to occur, timely adoption, and an effective response to findings.
   Technical promise alone cannot establish it.

An optimistic screen should give each route its strongest plausible use case.
An audit need not find every bad behavior: one credible discovery might stop a
dangerous deployment. A monitor can be valuable as one part of a stack. Conversely,
neither outcome shows that interpreting every model, or catching every action,
is feasible. Failure of one route is not failure of the disjunction of routes.

## Falsification attempts and surviving explanations

### 1. Runtime monitoring: an attacker can select the blind spot

**Assumption challenged:** high average detection, cheap checks and repeated
opportunities imply reliable interruption of dangerous episodes.

[Obfuscated Activations, v2](https://arxiv.org/html/2412.09565v2#S3.SS3)
reports harmfulness probes falling to 0% recall under optimized obfuscation
attacks. Attacker access and optimization matter: this is not an observation of
ordinary deployed models spontaneously concealing a plan.
[Neural Chameleons, v1](https://arxiv.org/html/2512.11949v1#S4)
goes further: training evasion on benign concepts transfers to unseen safety
monitors, including probes fitted after the model is frozen. It uses constructed
model organisms and an explicit concept-specific trigger. Ensembles and nonlinear
monitors help, but do not eliminate the demonstrated evasion.

These results defeat two shortcuts: assuming internal representations are
intrinsically hard to manipulate, and assuming a secret probe is sufficient
protection. They do not prove that all internal signals can be hidden at acceptable
capability cost. In the other direction,
[evaluation-awareness experiments, v2](https://arxiv.org/abs/2609.03035v2)
find that announcing the monitor, with or without score feedback, does not defeat
the best probes in two collusion games. Awareness alone and trained evasion are
different attacker capabilities.

**Decision:** do not extrapolate random-example recall to an adaptive adversary.
Prioritize capability-preserving evasion tests against the full intervention
protocol. The attacker may select a rare blind spot repeatedly; its deployment
weight need not equal its frequency in a benchmark.

### 2. Deployment audits: recognizable symptoms may hide the dangerous objective

**Assumption challenged:** discovering hidden behaviors reliably exposes the
underlying reason a model will act dangerously in unfamiliar situations.

[AuditBench](https://alignment.anthropic.com/2026/auditbench/) evaluates 56 models
across 14 implanted behaviors and four training configurations. Scaffolded
black-box tools perform best in its initial comparison. That challenges the
incremental value of the tested internal tools, not white-box access in general.

Later [introspection adapters](https://alignment.anthropic.com/2026/introspection-adapters/)
achieve 59% investigator success versus 53% for the previous best method. Success
allows any of ten predictions to match the hidden behavior, judged by an LLM;
it is not low-false-alarm deployment certification. In a separate reward-seeking
organism, the adapter surfaces 16 of 52 symptomatic behaviors without reporting
the core reward-maximizing objective. Nevertheless, discovering a symptom could
be sufficient to reject that model. The relevant failure would be a dangerous
model passing an audit that triggers appropriate action on credible findings.

[Natural language autoencoders](https://www.anthropic.com/research/natural-language-autoencoders)
also provide counterevidence to blanket pessimism: the authors report useful
pre-deployment investigations and improved discovery of implanted motivations.
These cases establish diagnostic usefulness, not a measured counterfactual
reduction in catastrophic risk.

**Decision:** evaluate correct deployment decisions, including safe controls and
follow-up confirmation, rather than requiring complete reconstruction of goals.
Hold out the process used to create dangerous models, not merely new prompts for
familiar implanted behaviors. Compare against equally resourced behavioral audits.

### 3. Training and editing: does the intervention remove danger or its signal?

**Assumption challenged:** suppressing an interpretable direction removes the
underlying unsafe propensity, including under future optimization.

[Probe-guided fine-tuning, v3](https://arxiv.org/html/2609.38645v3#S5)
provides both a failure and a surviving route. Frozen-probe loss can vanish while
harmful compliance persists. Continuously updating probes improves the tested
harmlessness and honesty outcomes while retaining linear detectability. Experiments
use Llama 3 8B, Mistral 7B and Qwen3 14B; the authors leave stronger optimization
and other settings open. Some responses become empty or disrupted, so safety must
be evaluated alongside useful performance. This rebuts the universal claim that
training against internal tools necessarily destroys monitorability.

[Persona Features Control Emergent Misalignment](https://arxiv.org/abs/2506.19823)
supplies a separate causal foothold: identified persona features control measured
misalignment. It also reports a simple benign fine-tuning mitigation. Thus, a
causal explanation need not itself be the cheapest effective remedy.

**Decision:** compare persistent safety at matched utility and budget against
ordinary fine-tuning. Use new behavioral evaluators, freshly trained monitors,
unseen tasks and subsequent optimization. Failure would be danger returning while
the original intervention's score stays reassuring. Test the best updating
defense, not only a knowingly exploitable frozen classifier.

### 4. Interpretable construction and verification: explanation may not scale to assurance

**Assumption challenged:** increasingly good local explanations compose into
tractable guarantees about capable systems.

[Weight-sparse transformers](https://arxiv.org/abs/2511.13653) demonstrate unusually
understandable circuits and a capability–interpretability tradeoff. The paper
identifies scaling beyond tens of millions of nonzero parameters while preserving
interpretability as a challenge. This is a demonstrated gap, not a scaling
impossibility result.
[Compact proofs](https://arxiv.org/abs/2406.11779) prove accuracy bounds for a small
Max-of-K transformer across many seeds, while identifying compounding unstructured
errors as an obstacle. A proof can also certify the wrong property for the
deployment environment; specification adequacy is a separate obligation.

**Decision:** test whether proof effort or capability cost becomes prohibitive
as the certified task grows. Report an explicit property, assumptions, bound and
cost, not just an attractive circuit. This route may instead work for a narrow
safety-critical component; failure to explain a whole frontier model would not
reject that use.

### 5. Scientific discovery and early warning: useful knowledge might not change a decision

**Assumption challenged:** better explanations automatically produce preventive
actions unavailable to behavioral research.

The persona-feature and NLA studies above establish useful causal and diagnostic
findings. The additional link is a decision: change training, constrain a model,
delay deployment, or redirect research. This route can succeed through a few
high-leverage discoveries and therefore does not require high detection coverage.
Publication counts and explained-feature counts do not test that link.

**Decision:** record discoveries that change a consequential safety decision,
their validation, and whether a comparable behavioral investigation would have
found the same problem within the relevant time and budget. The reviewed examples
do not identify the counterfactual catastrophe-prevention effect. Missing evidence
for that effect is not evidence of zero effect.

## A more decision-relevant metric

For runtime monitoring, compare the **fraction of adversarial episodes reaching
a specified harmful endpoint with and without internal tools, at equal total
defense cost and useful task performance**. Optimize the attack separately against
each stack under the same declared attack budget. Report the escape-rate ratio,
absolute rates, uncertainty, attacker access and intervention timing. A paired
fixed-trajectory evaluation additionally reveals which failures overlap, but
cannot alone estimate how attackers adapt to the changed defense.

Let e_B be the baseline escape probability and e_I that of the stack containing
internal tools. The incremental reduction factor is e_B / e_I. If either rate is
unresolved or zero in a finite sample, report bounds rather than an infinite
factor. With a common set of dangerous trajectories, the diagnostic quantity

    g = P(internal tool blocks before harm | baseline fails, dangerous episode)

measures coverage of baseline misses. In a simple additive stack with no adverse
interactions, its escape rate on that fixed distribution is e_B*(1-g). This
identity does not assume independent monitors. It also does not model adaptive
selection, behavior changes, displacement of existing controls or new attacks.
Good unconditional recall is compatible with g=0.

The existing page's 1,000× scenario is a demanding illustrative target, not a
necessary threshold for interpretability to matter. It also assumes risk lies
inside the monitored channel. In a deliberately simple risk accounting, let q
be the fraction of baseline catastrophic risk both addressed and reached by an
adopted intervention, and let R be its risk-reduction factor there. Holding other
risks fixed and assuming no induced harms:

    residual risk / baseline risk = (1-q) + q/R

Even R=1,000 only halves total risk if q=0.5. A total 1,000× reduction requires
q at least 0.999 even with perfect elimination inside the channel. These are
algebraic examples, not estimates of q or R. A global deployment decision may
affect a much wider channel than a runtime monitor; unintended changes in
deployment or capability invalidate the simple accounting.

## The next experiment most likely to change the decision

1. Pre-register a threat model, acceptable task performance, defense cost and
   target reduction. Include the strongest relevant baseline, including behavioral
   and reasoning monitors where available. Declare which weight access, feedback
   and optimization the attacker gets; separate realistic-access from stress tests.
2. Test baseline-only and internally assisted stacks, with independent attack
   search against each. Include naturally elicited failures and deliberately
   constructed evasive organisms, reporting them separately.
3. Score completed adversarial episodes and interventions before irreversible
   actions. Log joint misses on shared trajectories, false interruptions of benign
   work, actual costs, and capability retention. Cluster results by attack family
   and target model, rather than treating paraphrases as independent.
4. Repeat across actor capability and attack-search budgets. Larger actors may
   expose clearer signals while finding better evasions; parameter count alone
   cannot determine which effect wins. Keep a fixed task panel for comparability
   and a separately reported expanding panel for new capabilities.
5. Test the strongest repair for a discovered failure on fresh attacks. Persistent
   lack of marginal benefit within the declared budget would justify deprioritizing
   that monitoring program. It would not establish impossibility of future methods
   or reject the other routes above.

Even zero escapes in a test does not prove adequacy: under independent identically
distributed Bernoulli episodes, at least 2,995 zero-failure trials are needed for
a one-sided 95% upper bound below 0.1%, since 1-0.05**(1/n) < 0.001. Shared attack
families and adaptive search invalidate that simple sampling interpretation.
Such a bound would apply to the specified episode distribution, not existential
risk. Testing a reduction *relative to a baseline* also needs baseline uncertainty.

## Current prioritization judgment

The strongest negative evidence concerns adaptive evasion and the gap between
classification and prevention. It argues against relying on current probes as a
decisive barrier. The strongest surviving case is conditional: internal tools
could add information unavailable to behavioral checks, support a consequential
audit decision, or enable a durable training improvement. Newer positive results
make “the whole field is doomed” too strong a conclusion.

Fund tests of incremental prevention and decision value before treating better
interpretability benchmarks as evidence of catastrophe prevention. Whether these
tests deserve more funding than a different safety approach also requires that
approach's expected benefit and cost; this review alone does not settle portfolio
allocation.
