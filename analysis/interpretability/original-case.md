# The original case for interpretability, and what would count as success

Historical assessment, 11 November 2026. This examines a prominent safety-motivated
research tradition, not every motivation or researcher in interpretability.
Statements about adequacy and priorities below are judgments, not measured
percentages of progress. See the [falsification review](falsification.md) for
route-specific evidence and proposed experiments.

## The original wager

The important wager was that internal understanding could distinguish systems
that behave similarly during testing but generalize very differently when the
stakes change. If successful, this could supply information that more behavioral
testing cannot easily provide. Producing explanations was an intermediate step.

In [Building Blocks of Interpretability (2018)](https://distill.pub/2018/building-blocks/),
Olah and colleagues proposed feedback on a model's decision process to address
problems that do not surface in training behavior. They explicitly warned that
optimizing what the interface shows could teach the model to fool it. Process
supervision and concerns about interpretability being gamed were present early;
neither is a new justification invented after circuit analysis became difficult.

[Hubinger's 2019 account of discussions with Olah](https://www.alignmentforum.org/posts/X2i9dQQK3gETCyqh2/chris-olah-s-views-on-agi-safety)
describes four routes: auditing before deployment, deliberate design, feedback on
internal processes, and microscope AI that extracts knowledge without deploying
an acting agent. This is Hubinger's reconstruction, not a verbatim Olah manifesto.
The auditing ambition was systematic discovery rather than lucky examples. The
account also describes a strong reverse-compilation aspiration, while discussing
deception, scaling and competitiveness as difficulties. These were hypotheses,
not promises of delivery by a specified year.

[Circuits (2020)](https://distill.pub/2020/circuits/zoom-in/) proposed that meaningful
features, their computational connections, and recurring structures across models
could support a natural science of networks. It explicitly described its central
claims as speculative. This scientific agenda is valuable independently of a
complete safety intervention, but that does not establish its safety impact.

By [2023, Anthropic's stated safety case](https://www.anthropic.com/news/core-views-on-ai-safety)
was particularly sharp: recognize deceptive alignment that survives difficult
behavioral tests, and eventually enable something like code review that finds
unsafe aspects or supports strong safety guarantees. The same document allowed
for changing research direction and for using discoveries to warn against unsafe
deployment. Thus, both ambitious assurance and the more modest early-warning
route were explicit before the recent wave of practical tools.

## Has progress been made?

Yes, with different evidential strength at different links in the argument.

| Original bet | Evidence of progress | What the evidence does not establish |
| --- | --- | --- |
| Networks contain understandable computations | Vision circuits developed into analyses of small transformers, including induction mechanisms. [Transformer Circuits, 2021](https://transformer-circuits.pub/2021/framework/index.html). | A faithful, comprehensive account of a frontier model. |
| Useful representations can be recovered at scale | Sparse dictionaries exposed many features in Claude 3 Sonnet. [Scaling Monosemanticity, 2024](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html). | Coverage of all safety-critical features, especially rare ones. The authors explicitly did not know the total feature count. |
| Understanding can explain and change behavior | Circuit tracing and persona-feature interventions supply causal evidence on selected computations and misalignment. [Tracing thoughts, 2025](https://www.anthropic.com/research/tracing-thoughts-language-model); [persona features](https://arxiv.org/abs/2506.19823). | Robust control of goals or generalization across deployment conditions. |
| Internal access adds practical safety information | Auditing methods now have task-level evaluations and reported pre-deployment use. [Introspection adapters, 2026](https://alignment.anthropic.com/2026/introspection-adapters/); [NLAs, 2026](https://www.anthropic.com/research/natural-language-autoencoders). | Reliable discovery of strategically hidden objectives, or measured catastrophe prevention. |

This is substantial progress in tools and experimental science. The remaining
assurance gap is nevertheless qualitative: unknown coverage, distribution shift,
strategic evasion, and validation of the interpretation itself. In 2025, the
circuit-tracing authors explicitly reported capturing only part of the computation
even for short prompts. More examples of understandable mechanisms do not by
themselves bound the importance of what remains unexplained.

Model scale has two effects. More capable models can have clearer, more useful
representations; they also introduce more consequential behaviors and stronger
potential adversaries. Studying a larger model is progress in absolute reach,
but not automatically progress toward the required safety standard. There is no
defensible percentage-complete or historical doubling-time estimate in this review.

## How much progress is needed?

The threshold belongs to the theory of change:

- **Early warning:** a credible, independently checked finding that changes a
  consequential decision in time. One finding can suffice; comprehensive coverage
  is unnecessary. Adoption and whether the finding was otherwise obtainable matter.
- **Auditing:** dangerous systems that pass strong behavioral tests must reliably
  trigger justified rejection, under unfamiliar failure mechanisms. An audit that
  diagnoses a known symptom is weaker evidence than this.
- **Training or editing:** internal intervention must durably improve safety at
  acceptable usefulness and cost, including after new optimization, rather than
  merely suppress the familiar signal.
- **Runtime control:** useful additional prevention against adaptive attacks,
  before irreversible harm, at tolerable cost and false-interruption rates.
- **Assurance by understanding:** faithful coverage of the safety-relevant
  computation, plus a defensible argument that the unexplained remainder cannot
  invalidate the conclusion. Full explanation of everything may be unnecessary;
  unbounded omissions are incompatible with strong assurance.

These are different finish lines. A field can cross the early-warning threshold
without approaching assurance. A single spectacular result cannot show how many
more years the latter requires. For allocation, specify the desired contribution
and deadline rather than asking whether the field is generically “working.”

## Have the goalposts shifted?

Three distinctions prevent an unfair or unfalsifiable assessment.

**Changing methods is legitimate.** Moving from neurons to feature directions,
from hand inspection to automated tools, or from explaining a whole model to
certifying a narrow component can preserve the original safety objective.

**Substituting an easier success criterion is a substantive retreat.** Useful
classifications do not discharge a claim about detecting hidden objectives;
selected causal circuits do not discharge a claim about adequate safety coverage.
If these are presented as progress, that is reasonable. If they are presented as
completion of the original assurance ambition, the standard has changed. This
review does not attribute that claim to the entire field.

**Changing an operational commitment is independently checkable.** Anthropic's
[archived 2026 roadmap](https://www.anthropic.com/responsible-scaling-policy/updates)
specified meaningful interpretability signal beyond behavioral methods and thorough
red-teaming of alignment arguments. On October 19 it retired that broader goal,
reported interpretability use in assessments, and acknowledged less red-teaming
than intended. A separate training-data oversight process was discontinued for
lack of additional findings; that was not a report that interpretability itself
had no value. This is a concrete revision worth tracking, not evidence that the
whole agenda has been abandoned.

Early-warning, process feedback and deliberate design were already present in
the early case. Invoking them today is not intrinsically moving the goalposts.
Switching among them without preserving separate success criteria would, however,
make the overall research program too easy to defend against any negative result.

## Is research generating new ways to prevent catastrophe?

Yes at the level of mechanisms and interventions. Evidence for entirely new,
validated catastrophe-prevention strategies is much weaker. Distinguish a new
implementation of an old route from a new route.

- [Circuit breakers (2024)](https://arxiv.org/abs/2406.04313) use representation
  engineering to redirect harmful computation. This is a concrete safety technique,
  not a full mechanistic explanation. [Follow-up attacks](https://arxiv.org/abs/2407.15902)
  challenge robustness under continuous embedding access, so success remains
  threat-model-dependent.
- [Refusal-direction research (2024)](https://arxiv.org/abs/2406.11717) found a
  manipulable internal mechanism across 13 chat models. It yielded an attack and
  evidence about brittle safeguards. Such discoveries can improve safety priorities
  even before they yield a defense; revealing a vulnerability is not preventing it.
- Persona-feature work makes model diffing and targeted interventions concrete.
  It supports investigating shared mechanisms of broad misalignment, without
  showing that an underlying dangerous objective has been permanently removed.
- [Updating probes during training (2026)](https://arxiv.org/html/2609.38645v3#S5)
  offers a tested response to the concern that internal supervision destroys its
  own signal. This is progress within the old process-feedback route.
- NLAs offer an interface for inspecting hidden representations, and
  [weight-sparse transformers](https://arxiv.org/abs/2511.13653) offer a concrete
  approach to interpretable construction. Both extend old strategies through new
  technical possibilities; neither yet establishes broad safety assurance.

A useful discovery ledger would record: previously unknown mechanism, proposed
intervention, independently tested safety improvement, and changed real decision.
Count each stage separately. Publication volume and number of proposed uses are
poor substitutes for conversion into preventive action.

## Revised assessment

The evidence supports a productive scientific program and emerging practical
tools. It does not establish that progress is fast enough relative to capability
growth to deliver the stronger original assurance ambition. That is the central
unresolved issue, not whether any useful interpretability result exists.

The runtime-monitoring page is one route-specific feasibility screen. It should
not stand in for an assessment of the original research wager. A more informative
next comparison would test whether internal access distinguishes dangerous and
benign models that strong behavioral evaluations cannot distinguish, and whether
that information enables an effective intervention. Where the claimed benefit is
scientific discovery instead, track the discovery-to-decision chain explicitly.
