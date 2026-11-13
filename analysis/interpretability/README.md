# Alignment through understood construction

The [interpretability page](../../interpretability.html) assesses the capability
of the strongest complete system whose alignment is substantiated by understanding
its construction. The [research note](construction-frontier.md) explains the
qualification rule, search scope, findings and limitations.

[Historical research supplement](construction-history.md): tests candidate
progress indicators against earlier systems and records assurance-preserving
extensions, assumption changes and costs. This supplement is not incorporated
into the public page or its evidence ledger.

[Qualification investigation](construction-qualification.md): distinguishes
scope exclusions, missing implementation evidence and incomplete safety claims,
with a deeper review of assistance games, corrigibility and Scientist AI.

- [JSON ledger](construction-frontier.json): canonical evidence and judgments.
- [CSV export](construction-frontier.csv): generated from the ledger.
- [Builder and checker](build_construction_frontier.py): validates the ledger,
  renders the public evidence table and exports CSV.

```sh
python3 analysis/interpretability/build_construction_frontier.py
python3 analysis/interpretability/build_construction_frontier.py --check --check-sources
```

Source checks locate selected text in the primary publications. They do not
reproduce experiments, verify proofs or adjudicate alignment. Missing capability
observations remain null, not zero.
