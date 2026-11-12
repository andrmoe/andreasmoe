# Capability frontier for alignment through understood construction

Review date: 12 November 2026. [Public page](../../interpretability_construction.html).
[Canonical ledger](construction-frontier.json). [CSV](construction-frontier.csv).

## Question and result

The prioritisation question is whether alignment through understood construction
is a promising way to obtain aligned general superhuman AI in time. The proposed
measurement is the capability of the strongest complete system whose alignment
is substantiated by understanding its construction. A necessary ingredient of
that measurement is an explicit, inspectable qualification judgment.

This review identifies bounded construction certificates and partial technical
advances, but no qualifying general-purpose system in the selected evidence.
It does **not** establish that none exists anywhere, that narrower systems cannot
qualify within their own scope, that the field has made no progress, or that the
route cannot succeed. It does not yield a common capability time series or a
probability of readiness. Missing observations and probabilities are null.

Two questions must remain separate:

1. Can construction establish a meaningful property of an implemented system
   within a bounded operating scope? The neural-controller examples supply
   positive evidence, subject to the recorded verification qualifications.
2. How capable is a general-purpose system whose alignment has been established
   this way? No reviewed system supplies this observation.

We do not require a system already to be superhuman before it can enter the
general-purpose series. A smaller, broadly capable agent with a substantiated
alignment argument could be the first entry. Conversely, a narrow superhuman
solver is not automatically evidence of general alignment. Capabilities and
operating scope are both needed; parameter count and state dimension are not
substitutes for competence.

## Operational qualification rule

A candidate needs an implemented system, a useful capability evaluation, a
specified alignment requirement and operating scope, an auditable argument
linking its construction to that requirement, and evidence that the actual
implementation satisfies the argument's premises. The safety claim must concern
meaningful behavior or choices, not just incapacity to cause harm. Any unexplained
components, external tools, online adaptation and permitted weight updates must
be addressed within the declared scope.

Formal proof is allowed but not required. Empirical validation of an explanatory
account can contribute if its scope, alternatives and residual uncertainties are
explicit. We do not impose a numerical confidence threshold that these studies
did not measure. Each admission decision therefore remains a natural-language
judgment with reasons and a source locator; it is not an automated score.

Construction includes modifying learned systems, compiling known algorithms,
learning with an interpretable architecture, and using compact invariants to
reason about a controller. It is not restricted to neural networks or semantic
descriptions of individual weights. A certificate can establish a bounded
property without exposing the full algorithm. This broad interpretation is
deliberately favorable to the route; under a stricter semantic-understanding
definition, some controller examples would instead be adjacent evidence.

Separate external enforcement remains part of the already assessed control
route. Do not credit an opaque base model with alignment because a wrapper limits
its actions. A constructed system using a predictor and scaffold could qualify,
but its complete alignment argument must cover both. This does not require
repair of every component, merely a justified argument for the complete system.

## Search and selection

This is a purposive candidate review, not a systematic review or literature
census. It started from previously collected mechanistic-interpretability and
sparse-construction sources, then searched primary publications for the strongest
counterexamples in formal construction and learned-controller certification.
Searches were performed on 12 November 2026; evidence predating 2019 was not
inventoried, so 2019 is the selected historical baseline, not the invention date
of understood construction or verified software.

Search families included:

- Mechanistic explanation to a complete behavioral guarantee: compact proofs,
  circuit tracing and mechanistic estimation.
- Construction with known internal computation: Tracr, weight-sparse models and
  descriptions that predict held-out weight-ablation effects.
- Conditional safety designs: Guaranteed Safe AI and Scientist AI.
- Agent-level incentive construction: AssistanceZero and corrigibility
  transformations, including their learned/prompted implementation gaps.
- Working bounded certificates: neural Lyapunov controllers, discrete-time
  extensions and output-feedback verification.
- Counterexamples and boundaries: later verification corrections, larger neural
  barrier certificates, and executable proof-constrained agent guardrails.

Representative search terms included “Scientist AI formal safety argument”,
“alignment mechanistic proof construction neural networks”, “Neural Lyapunov
Control 2019 verified controller”, “2026 certified neural controllers dimensions”,
and “2025 2026 alignment by construction safety”. Search results were used to find
primary sources, not as evidence for their strongest claims.

The ledger includes 14 candidates. Original publication and reviewed-version
dates are separate. Findings in a later version are dated to that version.
Judgments incorporate later criticism and are explicitly as of this review;
they are not reconstructed historical expert beliefs. No observations were
selected for 2020–2022. That gap is not a claim about research activity.

## Strongest challenges to the conclusion

### Explicit incentive construction already reaches agents

[AssistanceZero](https://arxiv.org/html/2504.07091v2) is a stronger agent-level
near-match than a low-level controller. It uses a known assistance-game structure
and learned predictions to plan under uncertainty about the user's goal. Its
Minecraft human study measures useful cooperation. The theoretical appeal of an
ideal assistance game does not certify the learned human model or approximate
planner. Full RLHF is not a tested baseline. Broader alignment would require
checking those implementation obligations and extending the operating scope.

[Corrigibility Transformation](https://arxiv.org/html/2510.15395v2) constructs
goals with conditional incentive properties and tests them in gridworlds. Its
2026 revision also tests prompts on Kimi-K2.5, GPT-OSS-120B and GLM-5-Turbo, using
64 ImpossibleBench tasks per model/prompt combination. The raw Table 1 outcomes
are retained alongside the favorable monitor-disable result: reward hacking
remains high because accepting correction and pursuing the right goal are
different properties. Prompting an opaque model is not a demonstration that its
implemented objective obeys the theorem. The LLM results are dated to v2 in
August 2026, not the October 2025 first submission.

These examples make an overly broad negative conclusion less credible: there
is work on constructing agent incentives, not just interpreting classifiers.
They still do not supply the missing general-purpose construction guarantee.
Their usefulness is partly a judgment about implemented approximations, not
merely a question of increasing model size. Corrigibility also leaves the
ability to identify and perform the needed corrections as remaining work.

### Bounded guarantees are already real

Neural Lyapunov work is an important positive control against the claim that
learned systems cannot be constructed with justified behavioral properties.
The 2024 output-feedback example covers an observer together with the controller.
Its 8-dimensional augmented state/error domain is not a general-intelligence
measurement. Stability under modeled dynamics is not a guarantee about arbitrary
goals, perception or deployment conditions. This is a valid achievement with a
narrower scope, not a failed attempt at general alignment.

The same primary follow-up reports problems in earlier demonstrations, including
the PVTOL verification region in the 2023 implementation. The ledger records the
original report and the later challenge. It does not draw a monotonic capability
curve through the disputed claims.

### A safety theorem may precede a capable implementation

Scientist AI is a particularly relevant conditional construction proposal.
Its v2 Section 1.2 explicitly limits the argument to the Predictor's implicit-goal
misalignment, distinguishes posterior-relative safety from hazard adequacy, and
leaves agentic-scaffold safety and finite-resource issues open. Section 4.2
identifies an implementation requirement not empirically verified there.
These are reasons not to assign an implemented capability score, rather than a
refutation of the proposed route.

### A more capable model can have less comprehensive understanding

The Claude 3.5 Haiku application of circuit tracing concerns selected mechanisms.
It does not establish the proposed full-system alignment property. Conversely,
Max-of-K proofs support a comprehensive statement about a narrower task, not
agent alignment. Pooling those observations would silently change the property
being measured. The seed and proof-strategy counts are method-validation
descriptors; they are not alignment success rates.

### An apparent new aligned system may actually be a control result

The ePCA primary abstract proposes a separate action-verification mechanism and
states that its foundation is conditional on system assumptions. It was screened
as a boundary case, not deeply re-reviewed here. Its reported attack outcomes
are not copied into an alignment capability score. The relevant system-level
obligations belong in the control assessment.

### Could larger certificates change the answer?

The [2026 revision of scalable neural barrier verification](https://arxiv.org/abs/2511.06341v2)
reports verification of larger certificate networks. This extends an enabling
method; network size alone does not measure the competence of an aligned agent.
It was screened through its primary abstract, not ranked as a new complete-system
record. A later update should follow the strongest complete controller examples,
not simply the largest verifier or certificate network.

## Reading the measurement correctly

- There is no defensible single “strongest system” across these incompatible
  properties and domains. The 2024 controller is a concrete bounded near-match,
  not a claim to the world's most capable certified system.
- No common independent general-capability evaluation is available for a
  qualifying system here. The ledger leaves that field null instead of assigning
  an ordinal intelligence score or treating model size as capability.
- A family-specific series could eventually track capability at a fixed scope
  and evidence standard. Such a series would not become a general-alignment
  series merely by reaching a high score in its narrow domain.
- Costs are documented qualitatively when incompatible or unreported. Verifier
  runtime, proof FLOPs, and explanation-generation cost are not total research
  cost and cannot be pooled.
- A best-achievement frontier is deliberately optimistic. It says little about
  typical success rates, reproducibility, affordability or widespread adoption.
- The public record cannot resolve unpublished capability. A negative search
  conclusion must be bounded to the reviewed evidence.

## Implication for prioritisation

The route survives an optimistic falsification screen. There are implemented
construction certificates and mechanistic routes to behavioral guarantees.
That is insufficient to infer convergence on general alignment before general
superhuman capability. In this record the hard missing connection is between
understanding a computation and establishing aligned choices for a broadly
capable complete system.

The next useful candidate is a capable agent with explicit requirements and a
construction-based alignment account covering its declared environment. Test
independent predicted failure modes, novel opportunities to violate requirements,
composition with other components and any permitted learning. Report useful
competence and resources alongside the guarantee. Do not require arbitrary
malicious weight-edit robustness if the proposed deployment excludes it.

For a readiness forecast, compare progress within compatible task families,
check whether expansion of scope adds new unresolved difficulties, and condition
on joint scenarios for capability development and safety research. No calendar
extrapolation or probability is fitted here. Future AI research assistance may
change both the available time and the rate of progress and is not credited
without specifying and validating the assistance mechanism.

## Reproduction and limits

```sh
python3 analysis/interpretability/build_construction_frontier.py
python3 analysis/interpretability/build_construction_frontier.py --check --check-sources
```

The first command validates the ledger and generates CSV and the page's table.
The second checks those artifacts without editing them, and fetches the primary
sources to check selected identity/text markers. These checks do not reproduce
experiments, verify mathematical proofs, establish independent capability
measurements or adjudicate the qualification judgments. Exact paper versions and
section locators permit independent inspection. Author-hosted live pages can
change; their retrieval date is recorded.
