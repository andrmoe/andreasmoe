# What prevents systems from qualifying as aligned through understood construction?

Review date: 13 November 2026. Follows the
[historical comparison](construction-history.md) and revisits the
[15-candidate ledger](construction-frontier.json). Research only: the public
page, generated data and original ledger classifications are unchanged.

## Main finding

The candidates are excluded for different reasons. The most informative missing
connection in the agent-level examples is between a useful implementation and
an alignment argument whose assumptions are justified for that implementation.
This is more specific than “we do not understand the network,” and more demanding
than knowing its training objective or observing helpful behavior.

There are also genuine bounded successes. Their exclusion from a general-purpose
frontier is partly a scope choice, not a technical failure. We should not describe
all 15 exclusions as failures to construct an aligned system, or infer that one
shared obstacle accounts for them all.

The historical test makes the distinction important: understood planning existed
long ago, and verified software shows reusable assurance is feasible. The
unresolved question is which safety-relevant properties can survive the learned
representations, approximations and autonomy needed by a capable AI.

## First fix the meaning of qualification

Three claims need separate answers:

1. **Scoped construction success:** a working system has a justified argument
   for a specified property in a declared operating domain.
2. **General-purpose alignment through construction:** a broadly useful system's
   choices satisfy an explicit alignment requirement, with its construction
   explaining why, including the consequential learned components and interfaces.
3. **A complete catastrophe-prevention route:** the requirement and deployment
   arrangements actually exclude the relevant catastrophic outcomes, at an
   acceptable residual risk, while delivering the needed capability.

The existing endpoint is primarily the second claim, motivated by the third.
Many entries contribute to the first. Calling all three simply “qualifying”
conceals the difference. A limited-domain system can be successful without
establishing a general-purpose route; a general-purpose system can satisfy a
particular property without preventing catastrophe.

Qualification does not require explaining every weight, certainty, zero errors,
or a formal proof. A probabilistic or empirically supported construction argument
can count if its extrapolation and residual uncertainty are justified. But no
numerical reliability threshold has been agreed for this assessment, so borderline
admission cannot honestly be presented as an objective binary fact. The cases
below have identifiable substantive gaps beyond that threshold ambiguity.

## Audit of the existing exclusions

This table accounts for every ledger entry. It is a diagnostic grouping, not a
ranking of distance to success. Entries not discussed in detail below retain the
earlier review's assessment; their experiments were not newly replicated.

| Ledger entries | What the evidence concerns | Main reason it does not establish the endpoint | Type of exclusion |
|---|---|---|---|
| Neural Lyapunov control, 2019 / 2023 / 2024 | Stability of controllers in modeled domains | General agent choices and broader deployment hazards are outside the property; some earlier demonstrations also face verification criticism | Scope, plus specific validation concerns |
| Utility-update agent, 2020 | Conditional properties of an explicitly constructed update mechanism | Update incentives do not establish correct payload goals, predictions or physical implementation | Partial safety property and implementation obligations |
| Tracr, 2023; compact Max-of-K proofs, 2024 | Known algorithms or bounds on task performance | The established property is not an alignment requirement for an agent | Enabling result; wrong property for this endpoint |
| Circuit tracing, 2025; sparse circuits, 2025; weight explanations, 2026 | Selected mechanisms and local explanatory coverage | No argument covering the consequential choices of the complete system | Missing system-level assurance |
| Mechanistic estimation, 2026 | Estimation for random networks | No implemented capable agent or relevant alignment property demonstrated | Enabling method |
| Guaranteed Safe AI, 2024 | A world-model/specification/verifier framework | A concrete capable system must instantiate and validate the components | Conditional design |
| ePCA guardrail, 2026 | External action enforcement | Assigned to control in our workflow; underlying model alignment is not established | Route boundary, with separate system-safety obligations |
| AssistanceZero, 2025 | Useful cooperation with a learned model of a human | Ideal cooperative structure is not a validated alignment argument for the approximate implementation | Missing assurance transfer |
| Corrigibility transformation, 2026 | Update-accepting goals and bounded behavioral demonstrations | Goal-level assumptions must hold in the agent; corrigibility also needs an effective correction process | Implementation and route completeness |
| Scientist AI, 2026 | A conditional predictor-safety argument | A useful trained system must satisfy the safety premises and connect posterior-relative safety to deployment hazards | Implementation, semantic adequacy and composition |

Source identities, versions and locators for these 15 entries are in the
[existing ledger](construction-frontier.json). Grouping nearby entries does not
imply they solve the same problem or share a comparable capability measure.

## The strongest agent-level cases

### AssistanceZero: useful behavior does not validate the inferred objective

The reviewed implementation uses learned human/reward predictions and approximate
planning. Its human study establishes useful task assistance; it does not certify
the inferred preferences or a safety property under model misspecification.
[AssistanceZero v2](https://arxiv.org/html/2504.07091v2), §§4–6.

**Diagnosis:** The gap is not simply limited Minecraft capability. Knowing that
an algorithm optimizes its estimate of a human's reward leaves open whether that
estimate represents the intended goal and whether approximation preserves the
desired choices. Perfect human modeling is not required in principle; sufficiently
robust behavior under justified error bounds could be enough.

**What would change this judgment:** Pick a concrete requirement, such as obeying
a specified correction channel without manipulating its input. Establish why the
actual planner meets it under an explicit, empirically justified range of human-
model and planning errors, then test predicted failure boundaries independently.
That could establish a scoped construction success at current capability. Broad
qualification additionally needs coverage of the intended wider tasks, not just
more Minecraft performance.

### Utility updates and corrigibility: accepting repair is only part of the route

Holtman's 2020 construction already analyzes learning and finite-time planning.
In particular, §13.7 argues its S2 indifference property persists in its modeled
learning agent; rejecting it merely because learning invalidates every result
would be wrong. The paper also separates those properties from prediction errors,
physical implementation and residual manipulation incentives.
[Primary paper](https://arxiv.org/html/2007.05411v1), §§6, 13.7–13.8 and 14.

The 2026 corrigibility transformation similarly has goal-level results and an
actor–critic implementation proposal. It acknowledges uncertainty about what
neural training produces. Its LLM experiment operates at the prompt level,
explicitly asks for reward hacking, and measures willingness to disable a monitor.
The reported mean disabling rate falls from 73.4% to 1.0%; that is promising
behavioral evidence, not establishment of the formal goal inside the LLM.
[Primary paper, v2](https://arxiv.org/html/2510.15395v2), §§3–4, Table 1 and
Appendices B–C. Reward hacking in this protocol is not evidence against its
corrigibility theorem: the initial task objective deliberately requests it.

**Diagnosis:** These constructions deserve credit for the properties they do
establish. The remaining work includes evidence for the actual agent's goal,
critic and update semantics. Even a completely corrigible agent needs people or
another process to detect mistakes, supply good updates and intervene in time.
Those obligations belong in the complete route; they are not all demands for
better interpretability.

**What would change this judgment:** A useful implementation whose correction-
acceptance property survives its actual learning and deployment mechanisms,
plus a justified correction process for the hazards in scope. The first would
qualify as a stronger partial construction result even before the second is
solved. More prompt-compliance measurements alone would not close both gaps.

### Scientist AI: the missing premises carry substantive safety content

The paper explicitly leaves hazard adequacy of its posterior, finite-resource
accuracy and broader scaffold safety unresolved. Its bound needs dangerous
predictors to be sufficiently rare within comparable-loss bands and training
not to excessively concentrate on them. It also requires a trajectory-level
guardrail condition stronger than accepting each release locally. No qualifying
capable implementation is demonstrated.
[Primary paper, v2](https://arxiv.org/html/2606.29657v2), §§1.2, 4.2, 5.3–5.4.2.

**Diagnosis:** This is not only missing engineering around a finished guarantee.
A concrete system must substantiate those premises, including the link between
what it predicts and actual hazards. A predictor without harmful goals could
still make consequential mistakes. The same separation would matter even if
every inference operation were understood.

**What would change this judgment:** An implemented predictor and bounded
deployment protocol with supported estimates or structural arguments for the
relevant conditions, useful capability, and evidence that its hazard judgments
track the intended real events. A general agent also needs the scaffold's
actions and repeated use covered. This need not demand a complete theory of
human values, but it does demand the particular safety argument's premises.

## Evidence about whether the gaps are removable

### Human-model error is a real difficulty, but perfection is not necessary

Hong, Bhatia and Dragan show both an adverse case—small model perturbations can
produce arbitrarily large reward-inference errors—and a positive stability bound.
The positive result assumes identifiability and strong log-concavity of true and
modeled policies in reward parameters. It bounds expected squared parameter
error using weighted policy divergence; it is not a tail-risk bound on deployed
harm. Their gridworld, continuous-control and human-data experiments support the
stability relationship in studied settings. The paper also supplies a simple
navigation example violating log-concavity.
[Reviewed v2, 30 October 2023](https://arxiv.org/html/2212.04717v2), Assumptions
1–2, Theorems 2–3, §6 and Appendix B; first submitted December 2022.

**Judgment:** This is a constructive lead for qualification, not just another
warning. Test whether analogous robustness conditions hold for an implemented
assistant, and connect errors to consequential actions. The worst-case result
does not establish typical failure; the favorable result does not automatically
apply to arbitrary learned human models.

Armstrong and Mindermann show a different problem: behavior alone does not
uniquely identify both preferences and the process that imperfectly pursues them;
a simplicity prior alone does not resolve this. Additional normative assumptions
are needed. [Reviewed v6, January 2019](https://arxiv.org/abs/1712.05812v6),
abstract and main results; first submitted December 2017, NeurIPS 2018.

**Judgment:** “More accurate behavior prediction” cannot stand in for “knows what
the human wants.” This does not prove learning preferences impossible. It requires
making the additional assumptions explicit and testing their consequences.

### Some intuitive safety properties do not follow even in ideal assistance games

Emmons et al. show that partially observable assistance games can incentivize
interference with human observations. They distinguish action-level from
policy-level interference and prove conditions under which noninterfering optimal
policies exist. Communication can remove some incentives, under assumptions
including usable, costless channels; boundedly rational humans introduce others.
[Reviewed v2, August 2025](https://arxiv.org/html/2412.17797v2), §§4–7,
especially Theorem 4.7, Proposition 6.3 and the Impact Statement; first submitted
December 2024, ICML 2025.

**Judgment:** This challenges the inference that shared reward automatically
provides whatever transparency or deference property we want. It does not show
these agents have malicious objectives: the authors explicitly analyze
interference that benefits the human under the modeled utility. Whether such
interference is unacceptable must be part of the requirement, rather than an
unstated assumption. It is not a measured catastrophe risk for AssistanceZero.

### Open-ended goals are being addressed, with a new implementation burden

GOOD extends assistance games to evolving natural-language goals and uses
LLM-based goal generation and inference. A diagnostic experiment on 30 multiple-
choice questions reports 100% accuracy for its pairwise ranking when correct
options are supplied, versus 33.3% ± 2.7% when options must be generated; these
are different task conditions, with standard deviations across three runs.
[Reviewed v2, May 2026](https://arxiv.org/html/2508.15119v2), §§3–6 and Table 1;
first submitted August 2025 as *Open-Universe Assistance Games*, revised title
*Flexible Agent Alignment with Goal Inference from Open-Ended Dialog*.

**Judgment:** This is concrete work on removing a fixed, predefined goal-space
restriction. Its task results do not establish a construction-based alignment
guarantee. In particular, readable goal descriptions leave goal generation,
interpretation and execution dependent on learned components. The small ranking
experiment illustrates a dependence on candidate generation; it is not an
alignment failure rate or proof of general failure. This is an additional screened
candidate, not a silent change to the original 15-entry ledger.

## Why bounded controllers qualify more easily

A neural controller can have an opaque implementation while a certificate
establishes a bounded stability property. The 2024 output-feedback example brings
an observer inside the certificate rather than assuming direct state access.
[Primary paper](https://arxiv.org/html/2404.07956v1), §4.3 and Limitations.

This supports an important correction to the framing: mechanistic explanation of
every consequential internal detail is not required when an invariant covers it.
The difficulty in transferring the success to alignment is finding an adequate
behavioral property and model, and making the implementation satisfy them at the
desired scope. Stability alone does not imply collision avoidance or beneficial
goal selection. Excluding a controller from a general-purpose frontier should
not erase its narrower accomplishment.

## Boundary cases that should not be mistaken for technical failure

- **External enforcement:** ePCA places a verifier between proposed actions and
  execution. Its threat model and limitations identify operational-semantic fidelity and
  complete mediation as assumptions. Whether to label such a complete system
  “controlled” or “aligned by construction” is a workflow choice. It does not
  establish the underlying model's objectives, but can still be safety-relevant.
  [Primary paper](https://arxiv.org/html/2605.29251v1), §§3.2, 5.5 and 8.1.
- **A design family without a completed system:** Guaranteed Safe AI identifies
  the world model, safety specification and verifier as separate obligations.
  The framework is not a failed implementation; it does not itself provide a
  capability-frontier observation. [Primary paper](https://arxiv.org/html/2405.06624v1),
  §§3–4.
- **An enabling interpretability result:** local circuit or weight explanations
  should be assessed as progress toward the property they can eventually support.
  The absence of a complete alignment argument is not evidence their own stated
  experimental claim is false.

## What to prioritize and how to measure it

The smallest useful diagnostic is three questions, rather than three presumed
independent research milestones:

1. **Would the claimed property be enough for the specified safety role?**
   Corrigibility needs correction; stability does not establish beneficial goals;
   posterior-relative safety needs hazard adequacy.
2. **Does the actual system satisfy the argument's premises?**
   Include the learned model, optimizer, critic, goal interpretation, tools and
   updates wherever they matter. An unexplained component can remain if its
   possible behavior is already covered by a justified bound or interface.
3. **Does that evidence survive the changes required for useful capability?**
   Measure assumptions and assurance costs alongside capability, including
   failures. Do not presume every capability upgrade weakens safety, or that
   every obstacle needs a general solution before one viable route can work.

These questions expose related but separable work. Better interpretability might
help with the second. Better specification, human modeling or robust construction
might address the first or avoid needing detailed interpretation. There is no
evidence here for one universally necessary interpretability breakthrough.

My recommended next empirical focus is **safety under human-model and planner
error in an implemented assistance agent**. This connects a useful existing
system to an identified technical gap and a positive robustness literature.
For a fixed requirement and domain, report violations, useful task completion,
error conditions and evaluation exposure. Increase planning power or broaden
goals while retaining that reporting. Tests can refute a construction account or
validate its predicted limits; favorable tests alone do not establish rare-event
catastrophe prevention. Qualification would still need a justified argument for
the untested conditions that matter.

For prioritization, the main update is that missing qualifications are not
explained solely by model size or incomplete circuit inspection. Some are
definitional, some are unfinished implementations, and some concern the content
of the safety claim itself. Progress in neural capability need not automatically
solve the latter two. This investigation does not determine a readiness date,
an acceleration rate, or the probability that the route succeeds before general
superhuman AI.

## Audit limits

The strongest agent-level sources and the additional robustness/goal-inference
papers were revisited directly. The grouped enabling-method entries use the
earlier ledger. All numerical observations are author-reported, and theorem
conditions were inspected rather than independently proved. No training runs,
proof checks, or deployment trials were reproduced. New candidate searches were
targeted, not exhaustive. The page and ledger remain unchanged so these
qualification judgments can be reviewed before any presentation changes.
