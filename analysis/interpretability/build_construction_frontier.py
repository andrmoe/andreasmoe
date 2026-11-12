#!/usr/bin/env python3
"""Validate the candidate ledger and render its CSV and static HTML table.

--check checks generated artifacts without changing them.
--check-sources checks source identity/selected text, not experimental validity.
"""
import argparse
import csv
import io
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
PAGE = HERE.parent.parent / "interpretability.html"
LABELS = {
    "bounded_certificate": "Bounded construction certificate",
    "partial_result": "Partial result",
    "conditional_design": "Conditional design",
    "external_control": "External control",
}
BEGIN = "<!-- construction:ledger:start -->"
END = "<!-- construction:ledger:end -->"


class SourceText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def normalized(text):
    return " ".join(text.split()).casefold()


def source_check(record):
    request = Request(record["source_url"], headers={"User-Agent": "ConstructionFrontierSourceCheck/1.0"})
    with urlopen(request, timeout=45) as response:
        parser = SourceText()
        parser.feed(response.read().decode("utf-8"))
    text = normalized(" ".join(parser.parts))
    missing = [s for s in record["source_check_tokens"] if normalized(s) not in text]
    if missing:
        raise ValueError(f"{record['id']}: source text missing {missing}")
    return record["id"]


def validate(data):
    cutoff = date.fromisoformat(data["reviewed"])
    ids = set()
    for r in data["records"]:
        assert r["id"] not in ids, f"Duplicate ID: {r['id']}"
        ids.add(r["id"])
        assert r["category"] in LABELS
        for key in ("first_publication", "source_date"):
            assert re.fullmatch(r"\d{4}(-\d{2}-\d{2})?", r[key]), r[key]
            parsed = date.fromisoformat(r[key] if len(r[key]) == 10 else r[key] + "-01-01")
            assert parsed <= cutoff, f"Future evidence: {r['id']}"
        assert r["first_publication"] <= r["source_date"], r["id"]
        assert type(r["general_alignment_qualified"]) is bool
        if r["general_alignment_qualified"]:
            assert r["general_capability_score"] is not None, "Qualifying point needs a measured capability"
        for key in ("system", "capability", "property", "judgment", "remaining_work", "effort", "validation", "source_locator"):
            assert r[key], f"Missing {key}: {r['id']}"
        assert r["source_url"].startswith("https://")
        assert r["source_check_tokens"]
    return sorted(data["records"], key=lambda r: (r["source_date"], r["id"]))


def render(records):
    rows = []
    for r in records:
        first = f" First published {r['first_publication']}." if r["first_publication"] != r["source_date"] else ""
        link = f'<a href="{escape(r["source_url"], quote=True)}">{escape(r["title"])}</a>'
        details = f'<details><summary>Scope, cost and verification</summary><p>{escape(r["remaining_work"])}</p><p>{escape(r["effort"])}</p><p>{escape(r["validation"])}</p><p>Source: {escape(r["source_locator"])}</p>'
        if r["related_source_url"]:
            details += f'<p><a href="{escape(r["related_source_url"], quote=True)}">Related primary evidence</a></p>'
        details += "</details>"
        rows.append(
            f'<tr id="{escape(r["id"])}"><th scope="row">{escape(r["source_date"])}<br>{link}'
            f'<p class="note">{escape(r["source_version"] + first)}</p></th>'
            f'<td><b>{escape(r["system"])}</b><p>{escape(r["capability"])}</p></td>'
            f'<td>{escape(r["property"])}</td>'
            f'<td><b>{LABELS[r["category"]]}</b><p>{escape(r["judgment"])}</p>{details}</td></tr>'
        )
    return "\n".join(rows)


def csv_text(records):
    output = io.StringIO(newline="")
    fields = [key for key in records[0] if key != "source_check_tokens"]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for r in records:
        row = {key: r[key] for key in fields}
        row["measurements"] = json.dumps(row["measurements"], ensure_ascii=False)
        writer.writerow(row)
    return output.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--check-sources", action="store_true")
    args = parser.parse_args()
    data = json.loads((HERE / "construction-frontier.json").read_text())
    records = validate(data)
    if args.check_sources:
        with ThreadPoolExecutor(max_workers=4) as pool:
            for record_id in pool.map(source_check, records):
                print(f"Source text checked: {record_id}")
    page = PAGE.read_text()
    assert page.count(BEGIN) == page.count(END) == 1, "Expected exactly one generated table"
    before, remainder = page.split(BEGIN)
    _, after = remainder.split(END)
    expected = before + BEGIN + "\n" + render(records) + "\n" + END + after
    outputs = {PAGE: expected, HERE / "construction-frontier.csv": csv_text(records)}
    for path, value in outputs.items():
        if args.check:
            assert path.exists() and path.read_text() == value, f"Stale generated artifact: {path}"
        else:
            path.write_text(value)
    qualified = [r["id"] for r in records if r["general_alignment_qualified"]]
    print(f"Validated {len(records)} candidates; general-purpose qualifiers: {qualified or 'none identified in this review'}")
    print("No capability value is assigned to a missing observation.")


if __name__ == "__main__":
    main()
