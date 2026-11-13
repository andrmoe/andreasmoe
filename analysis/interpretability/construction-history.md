# Historical test of progress indicators for understood construction

Review date: 12 November 2026. Research supplement to
[the current assessment](construction-frontier.md). No public page, page data,
or qualification decisions are changed by this note.

Follow-up: [what prevents qualification](construction-qualification.md),
13 November 2026, investigates the implementation and safety-claim gaps below.

## Finding

The historical evidence supports the possibility of reusable assurance for
powerful software. It also shows that increasing capability, explicit objectives,
and even reusable reasoning about plans are insufficient indicators of proximity
to general alignment. Those ingredients existed in much earlier work.

The more useful observation is a **capability improvement accompanied by evidence
that a relevant safety property survives the changes needed to obtain it**.
Record which assumptions change and how much new assurance work is required.
This is a way to examine a proposed route, not a universal necessary milestone,
a scalar progress score, or a validated forecast of general alignment.

The strongest positive historical evidence concerns preserving properties within
well-defined computational interfaces. Transferring that success to agents that
learn what the world and human preferences are remains an additional obligation.
This review does not establish that the latter obligation is impossible or that
no other architecture can avoid it.

## Method and scope

This is a purposive historical stress test, not a systematic review or a
statistical backtest of predictions. Cases were selected for contrasting roles:
early understood agency, theoretical error correction, practical verified
software, and a failure of a tempting composition argument. Contemporary
assistance games and neural controllers connect these comparisons to the
existing candidate review. There is no representative denominator of research
programs, so success frequencies cannot become probabilities of alignment.

For each comparison, ask:

1. What useful capability was demonstrated, and against which baseline?
2. What exact property was established, for which implemented components?
3. Did the extension preserve the same property, add a property, or merely
   demonstrate better behavior? These are different achievements.
4. Which assumptions were removed, retained, or newly trusted? Do not count
   assumptions: their consequences matter much more than their number.
5. What costs were actually reported? Distinguish runtime, proof effort and
   research time. Missing costs remain unmeasured.

The judgments below use primary papers and author reports. Numeric observations
are reported results, not replications. No proof assistants or historical
experiments were rerun. Judgments about implications for AI safety are ours.
Publication dates and exact reviewed versions are given where relevant; later
criticisms are not attributed to earlier researchers. Calendar gaps between
selected papers are not estimates of continuous research effort or acceleration.

## Historical evidence

### 1. Symbolic agency already supported some useful, understood learning

McCarthy and Hayes (1969) proposed selecting actions by reasoning that a strategy
achieves an assigned goal. Their discussion already separated solving problems
in a representation from obtaining an adequate representation of the world.
[Primary paper](https://www-formal.stanford.edu/jmc/mcchay69.html), Introduction
and “Why Artificial Intelligence Needs Philosophy.”

STRIPS (1971) implemented planning with explicit goal formulas, world models and
action operators. The paper expressly distinguished applying a model operator
from executing its corresponding physical routine.
[Primary paper](https://ai.stanford.edu/~nilsson/OnlinePubs-Nils/PublishedPapers/strips.pdf),
pp. 189–191 and §4.

The 1972 extension generalized previously constructed plans into reusable macro
operators and used them in planning and execution monitoring. The following
measurements come from Technical Note 70, Table 1; times include macro production.

| Task | Without stored macros | With stored macros | Interpretation |
|---|---:|---:|---|
| Problem 2 | 9 min 42 s | 3 min 54 s | Faster planning on this example |
| Problem 4 | 14 min 9 s | 4 min 37 s | Faster planning; resulting plans differ |
| Problem 5 | Not solved in the reported experiment | 9 min 13 s | Expanded demonstrated capability; no timeout threshold reported in the table |

The report also describes rerouting around a newly encountered blocked doorway.
These are selected demonstrations in a seven-room environment, not failure-rate
estimates or an end-to-end safety proof. Human-supplied operators and modeled
preconditions remain central.
[Technical Note 70, July 1972](https://stacks.stanford.edu/file/druid:cb684hc9514/cb684hc9514.pdf),
§VII, printed pp. 47–52 and 61; Table 1 is PDF page 57. The table was visually
checked against the scan. [Journal publication](https://doi.org/10.1016/0004-3702(72)90051-3).

**Judgment:** A criterion such as “learns reusable computations, becomes more
capable, and retains an understood structure” already admits this historical
case. That does not make the achievement trivial. It makes that criterion too
weak to establish proximity to general alignment. There was also genuine
interaction with the physical world; calling it merely a simulation would
misidentify the remaining difficulty.

### 2. Reliability amplification is a mechanism, not a readiness measurement

Von Neumann's 1956 paper, based on 1952 lectures, develops redundancy and
restoration constructions for computation with unreliable components. The
mechanism can stop errors accumulating unchecked under its probabilistic
assumptions. Section 11.3 explicitly identifies constant, history-independent
component failure probabilities as unrealistic and leaves a more general
analysis undone. [Primary paper](https://www.peliti.org/Notes/vonNeumannNew.pdf),
§§8–11, especially §§8.2, 10.7 and 11.3.

**Judgment:** This supplies a conceptual reason assurance might scale without
understanding every execution. It is not an empirical demonstration of deployed
reliability, and it does not establish a dated takeoff in engineering progress.
For AI, voting or redundancy would need justified assumptions about correlated
errors and strategic behavior. A theorem for a convenient failure model is an
early result, not evidence those assumptions hold in the target system.

### 3. Verified compilation: real capability and an observable implementation gap

The 1967 McCarthy–Painter proof covered expressions made from constants,
variables and a binary operation, translated to a four-instruction machine
without jumps. The stated ambition was usable, computer-checked compiler proofs.
[Primary paper](https://www-formal.stanford.edu/jmc/mcpain.pdf), §§1 and 4–5.

By the 2009 CompCert report, the verified chain covered a substantial C subset
through multiple intermediate languages to PowerPC assembly. On the authors'
small custom benchmark suite, generated code averaged **12% slower than GCC
4.0.1 at -O2**; this is a runtime comparison on supported programs, not coverage
of all C or a universal performance gap. The formalization and proof required
approximately **3 person-years**. The parser and other components remained
outside the verified portion.
[Leroy, 2009](https://xavierleroy.org/publi/compcert-CACM.pdf), §§3.3–3.5,
especially Figure 2. This is an author manuscript with an older copyright
placeholder; the bibliographic publication year is 2009.

**Judgment:** Practical capability and substantial assurance can coexist. A
compact, reusable argument can cover programs too numerous to inspect
individually. Semantic preservation, however, inherits the source program's
behavior; it does not establish that the program's purpose is beneficial.
The interval from 1967 is neither a forecast for AI nor evidence of stagnation
through all intervening years.

Independent Csmith testing in 2011 found **six wrong-code bugs in CompCert's
unverified front end**, prompting expansion of verification to tricky implicit
casts and integer promotions. The report found no middle-end bugs and says the
then-development version resisted wrong-code discovery despite roughly
**six CPU-years of testing**. It also reports crashes and a specification issue
affecting assembly generation. [Yang et al., 2011](https://web.stanford.edu/class/cs343/resources/finding-bugs-compilers.pdf),
§3.1, “Testing CompCert,” printed p. 6.

**Judgment:** This is especially informative: failures located an uncovered
implementation boundary, and assurance was extended to cover it. The test effort
is not a deployment failure rate or a proof of the whole toolchain's correctness.

### 4. Reuse reduces some costs; it can also move trust or encounter new obstacles

XCert (2010) extended CompCert with a verified optimization engine. The authors
ran its optimizations on about **10,000 lines of benchmark C code**. Additional
supported optimizations required no new manual correctness proofs. However,
the trusted base grew to include a roughly **100-line OCaml checker**, an SMT
solver, and a semantics encoding; simulation relations were manually translated
and their correctness axiomatized in Coq. Comparative optimization performance
and extension effort were left for future evaluation.
[Tatlock and Lerner, 2010](https://www.cs.cornell.edu/~lerner/papers/pldi10-xcert.pdf),
§§6.3–6.6 and §7.

**Judgment:** This qualifies the earlier suggestion that XCert simply made
extensions cheap while retaining identical assurance. The logical property was
retained conditionally, with additional trust. It demonstrates a reuse mechanism,
not an unqualified reduction in total assurance cost at fixed assumptions.

seL4's 2014 retrospective documents implementation-level correctness, verified
optimizations, security properties and binary verification. Its reported costs
are particularly useful:

| Change | Reported assurance effort |
|---|---:|
| Initial functional correctness proof, including frameworks/tools | About 20 person-years |
| Major IPC fastpath optimization | About 5 person-months |
| Small local optimizations taking about a day to implement | About 2–3 person-days |
| Adding reply capabilities, changing less than 5% of the code | About 1 person-year |

Binary verification removed reliance on compiler/linker correctness but retained
hardware and other assumptions and used additional proof infrastructure.
Confidentiality required changes beyond ordinary refinement, including a more
deterministic specification and a scheduler change.
[Klein et al., 2014](https://sel4.systems/Research/pdfs/comprehensive-formal-verification-os-microkernel.pdf),
§§4.7–4.8, 7.2.3–7.2.5 and 7.4. Costs are author estimates, not controlled
comparisons of equivalent tasks; some changes occurred during initial development.

**Judgment:** Reuse is real, but its value depends on whether a change preserves
the relevant invariants. Cheap local changes and costly conceptual changes can
coexist after a major assurance milestone. This does not establish a universal
post-milestone acceleration.

### 5. Understood components do not automatically compose into the desired property

Doyle's 1978 counterexample shows that full LQG regulators, incorporating a
state estimator, need not inherit the guaranteed gain/phase margins associated
with full-state LQ regulation. A two-state example has arbitrarily small gain
margin. [Primary paper](https://hasler.ece.gatech.edu/Courses/ECE6550/Doyle_1978_Margins_LDG_Regulators.pdf),
pp. 756–757, “Example” and concluding discussion.

**Judgment:** This refutes an unrestricted inference from understood component
design and nominal optimality to robustness of the combined system. It does not
say every LQG controller is fragile, refute its nominal optimality, or establish
the failure rate of deployed controllers. This is a theoretical boundary case,
not an empirical time-series point or a longitudinal experiment on one system.

## Applying the historical test to current candidates

### Assistance games, 2016–2025

CIRL formally connects an unknown human reward to a cooperative decision problem
and reduces optimal joint planning to a POMDP. The original work also includes
an approximate algorithm; tractability was not solved by the reduction.
[2016 paper, v3](https://arxiv.org/pdf/1606.03137v3), §3.2, Theorem 1 and following
discussion. Reviewed version: 12 November 2016, rather than the 2024 revision.

AssistanceZero's 2025 v2 implements learned human models and approximate planning
in Minecraft. Human-study helpfulness ratings were **3.1 ± 0.4** for
AssistanceZero, **1.7 ± 0.3** for supervised fine-tuning, and **4.0 ± 0.5** for
the human baseline, on a five-point scale with reported 90% confidence intervals.
It explicitly compares human-model alternatives and their mismatch with human
behavior. [Primary paper, v2](https://arxiv.org/html/2504.07091v2), §§4.3 and 5.2,
Table 2 and Figure 2. Reviewed version: 12 June 2025.

**Judgment:** Useful implementation and human interaction improved; this is
substantive progress. But helpfulness is a different property from reliable
deference or absence of harmful incentives. The reviewed work does not establish
that an alignment guarantee survives learned-model error and approximate search.
The historical test classifies this as capability evidence with an unresolved
assurance transfer, not a certified upgrade or proof the route fails.

The Off-Switch Game already made deference conditional: its theorem covers a
rational human policy, and its analysis of suboptimal humans allows bypassing
oversight. [2017 v3](https://arxiv.org/pdf/1611.08219v3), Theorem 1 and §4;
first submitted November 2016, reviewed revision June 2017.
Neth's 2025 analysis examines further limits involving information processing
and misleading signals. [Primary paper, v1](https://arxiv.org/html/2502.08864v1),
§§4–6. These are scope challenges, not a refutation of the original conditional
theorem or measured failure rates for AssistanceZero. Nor does the historical
record justify treating all such qualifications as newly discovered obstacles.

### Neural control, 2019–2024

The 2019 neural Lyapunov work learns a controller and certificate for modeled
dynamics. [Original paper](https://papers.neurips.cc/paper_files/paper/2019/hash/2647c1dba23bc0e0f9cdf75339e120d2-Abstract.html).

The 2024 output-feedback work certifies a controller and observer together,
including a simulated quadrotor with six truncated lidar rays. Its verified
state/error domain has eight dimensions; dimension is not intelligence. Unlike
assuming the true state is directly observed, the observer now lies inside the
certificate. The paper also reports reproducibility/correctness issues with
earlier methods, including the 2023 PVTOL validation region.
[Primary paper, v1](https://arxiv.org/html/2404.07956v1), §4.3, Limitations and
Appendix B.6; reviewed version: 11 April 2024.

**Judgment:** This is stronger evidence of assurance surviving added complexity
than a larger uncertified controller. It addresses the kind of composition issue
highlighted by the LQG comparison, without claiming to solve the same problem.
The certificate remains conditional on modeled dynamics/observations and its
region of attraction. It is not broad visual understanding, general alignment,
or a clean monotonic 2019–2024 capability series through disputed results.

## What survives the historical test?

| Proposed inference | Outcome of this review |
|---|---|
| Understood construction is confined to trivial computational artifacts. | Too pessimistic: verified software supplies practical counterexamples. This does not establish aligned agency. |
| Explicit goals plus improving understood agency indicate proximity to general alignment. | Too permissive: early symbolic planning already fits that description. No calibrated lead time follows. |
| A milestone in reusable assurance makes later upgrades uniformly cheap. | Unsupported: extensions can reuse prior reasoning, add trust, or require new cross-cutting invariants. |
| Guarantees for components automatically survive realistic composition. | False without additional conditions; the LQG example supplies a counterexample. |
| Historical examples establish that current alignment progress is accelerating or fast enough. | Not established: the selected observations lack a comparable longitudinal denominator and an alignment endpoint. |

The cases do not demonstrate the historical false-positive rate of a forecasting
rule: we did not freeze a rule before selecting cases, and no historical system
here is a completed general-alignment route. They expose what the rule fails to
distinguish. This is useful diagnostic evidence, with a weaker claim than
predictive validation.

## Revised measurement and next decision

**Short description:** Within a research lineage, track useful capability under
a fixed, explicit safety requirement, together with the evidence connecting that
requirement to the implemented system. For each upgrade, record which safety
assumptions became more realistic, which new assumptions were introduced, and
the additional assurance effort. Report transitions individually; do not merge
unrelated properties or environments into one score.

This supplements the strongest-qualifying-system metric. It does not replace a
missing qualifying system with a good benchmark score. Relaxing an assumption
counts only when the relevant property still has support in the expanded scope.
Conversely, an upgrade can be valuable while retaining the same assumptions:
the target deployment may already satisfy them. Not every assumption must vanish.

For the superhuman-AI decision, first determine whether the safety requirement
would exclude a specified catastrophic failure mechanism at the intended level
of agency. If it would not, the result is an enabling contribution requiring
another argument, regardless of how cheaply it scales. A compounding software
assurance mechanism can support construction or control; it should not be counted
as an independently complete alignment route merely because it is successful.

My update is positive about the feasibility of reusable assurance and cautious
about using recent bounded successes to infer readiness. This record does not
falsify alignment through understood construction. It also does not establish
that the field is overcoming the deployment-critical obstacles quickly enough.

The next focused investigation should be the **transfer from an ideal assistance
agent to an implemented approximate agent**. Compare results across human-model
error, planner approximation, and opportunities to manipulate or override human
feedback. Ask whether a specific harmful incentive stays excluded as useful
capability grows. Existing human-model ablations can establish sensitivity, but
cannot substitute helpfulness for that requirement. The decisive encouraging
observation would be a relevant property retaining justified support after a
previously idealized component is replaced by a workable one. An opposing
observation would be repeated capability gains while the same indispensable
assumption remains unvalidated. Neither pattern alone supplies a universal
deadline forecast.

## Audit and limitations

- Sources were retrieved on the review date; web indexing dates were not used
  as publication dates. The 1972 technical report and its later journal layout
  have different page numbering; the numeric table uses the technical report.
- Quantities were checked against the cited prose or table, including the scan
  of STRIPS Table 1. Person-years, CPU-years, program runtime and confidence
  intervals measure different things and are not combined.
- Search families included STRIPS plan learning/execution; early compiler
  correctness; CompCert performance, extensibility and independent testing;
  seL4 verification costs and maintenance; LQG robustness; fault-tolerant
  computation; CIRL, off-switch incentives and implemented assistance games.
- This is a small, intentionally contrasting sample. Hardware reliability,
  cryptography, aviation and other plausible analogues were not comprehensively
  reviewed. These cases cannot supply a base rate for safety research success.
- No model experiments, formal proofs, failure frequencies, or acceleration
  estimates were independently reproduced. The page and existing evidence ledger
  remain unchanged.
