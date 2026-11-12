# Alignment through understood construction

The [interpretability page](../../interpretability.html) assesses the capability
of the strongest complete system whose alignment is substantiated by understanding
its construction. The [research note](construction-frontier.md) explains the
qualification rule, search scope, findings and limitations.

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
