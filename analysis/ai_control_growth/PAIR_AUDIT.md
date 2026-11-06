# Attacker–monitor pair audit

Reviewed the model rosters, model-swap experiments, tables and transfer ablations
in the fourteen linked arXiv papers and the OpenAI auto-review evaluation.
The pair census grows from 80 to 131 distinct `(source, attacker, monitor)`
combinations after canonicalizing names. No previously represented pair is lost.

| Source | Correction |
| --- | --- |
| [Remedios et al.](https://arxiv.org/html/2609.19587v2#A1.F9) | Extract all 49 cells in each of Figure 9's two grids. Rows are monitors; columns are attackers. This adds 47 model pairs beyond the existing Opus 5 results. |
| [Remedios et al., Appendix A.3](https://arxiv.org/html/2609.19587v2#A1.SS3) | Add Sonnet 4.6 → Opus 4.7, including the earlier-classifier baseline, brute-force retry and block-memory results at the reported 20-block budget. Do not count the repeated retry endpoint twice. |
| [EvasionBench, Figure 3](https://arxiv.org/html/2609.30217#S4.F3) | Extract all four attacker families at five reasoning efforts, including the omitted GPT-5.6 Terra → GPT-OSS-120B pair. Convert SVG coordinates with a 0.1 percentage-point readout allowance. Retain prevention upper bounds and exclude attacker-effort variants from defender leadership. |
| [MonitoringBench, Figure 12](https://arxiv.org/html/2605.09684#A9.F12) | Record Opus 4.7 paired with Opus 4.5, GPT-5 and GPT-5 Nano. These are suspiciousness-score distributions, without calibrated catch rates; expose the pairs in the census without safety likelihood terms. |
| [MonitoringBench, Tables 5–6](https://arxiv.org/html/2605.09684#A6.T5) | Re-extract full-trajectory averages under canonical identities, alongside stepwise averages. Replace old summaries rather than counting them twice. Table 5 has thirteen monitors; Table 6 has seven. |
| Retained base evidence | Canonicalize model names and look up the corresponding capability covariates, including GPT-4.1 Mini, GPT-4o Mini, Opus 4.5 and Sonnet aliases. |

Figure 9 in [Ctrl-Z](https://arxiv.org/html/2504.10374#A7.F9) has a misleading
caption: the surrounding text identifies GPT-4o mini as an attack-side predictor
of the trusted monitor's suspicion score. It is not an additional trusted-monitor
pair. Its selection ablation is explicitly indexed.

The other sources yielded no additional model pairs within this deployment
control synthesis. Human attacks, offline selectors, attack optimizers, judges,
untrusted helpers and unmonitored controls are not relabeled as model attackers
or trusted monitors. Oversight-game outcomes and conceptual constructions retain
their separate structural-evidence role. This census does not claim numerical
extraction of every repeated operating point or every diagnostic curve.

`data.json → evidence.tested_pairs` records pair locations and numerical
observation IDs; diagnostic-only pairs have empty observation lists. The page links to the complete census in the archive. Regression checks require both complete Remedios grids,
correct axis orientation, the Terra sweep, canonical names, the source table
rosters and the three diagnostic transfer pairs.

Reproduce with the dependencies in `requirements.txt`:

```sh
python ai_control.py refresh --cache /tmp/control-variant-sources
python ai_control.py expand --cache /tmp/control-variant-sources
OPENBLAS_NUM_THREADS=1 python ai_control.py test -v
OPENBLAS_NUM_THREADS=1 python simple_control.py
OPENBLAS_NUM_THREADS=1 python -m unittest test_simple_control -v
```

The current page uses the simple protocol-strength fit and its generated
`ai_control_simple_data.js` payload. It fits one shared capability-ratio slope
and one strength per protocol on a unified reported-failure proxy scale. The
archive retains the earlier complex-model results for provenance. The generated
`baseline_draws.npz` file belongs to that archived analysis and is not committed.
