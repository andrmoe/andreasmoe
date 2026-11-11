"""Validate the historical ledger and export CSV; optionally check key source facts.

This checks transcription, not experimental replication or the review's judgments.
"""
import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

from check_sources import TableParser

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-sources', action='store_true')
    args = parser.parse_args()
    data = json.loads((HERE / 'obstacles.json').read_text())
    cutoff = date.fromisoformat(data['cutoff'])
    cases = {c['id'] for c in data['cases']}
    events = {}
    for event in data['events']:
        assert event['id'] not in events, event['id']
        assert set(event['cases']) <= cases and event['cases']
        assert date.fromisoformat(event['date']) <= cutoff
        assert event['url'].startswith('https://')
        assert all(event[key] for key in ['date_basis', 'locator', 'finding', 'scope'])
        events[event['id']] = event
    fields = ['id', 'cases', 'date', 'date_basis', 'kind', 'url', 'locator', 'finding', 'scope']
    with (HERE / 'obstacles.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields, lineterminator='\n')
        writer.writeheader()
        for event in sorted(events.values(), key=lambda e: (e['date'], e['id'])):
            writer.writerow({**event, 'cases': ';'.join(event['cases'])})
    for comparison in data['comparisons']:
        start, end = (events[comparison[key]] for key in ['from', 'to'])
        days = (date.fromisoformat(end['date']) - date.fromisoformat(start['date'])).days
        assert days > 0
        print(f"{comparison['id']}: {days} days between cited publications")
    numbers = data['numbers']
    prior, current = (numbers[key] for key in ['auditbench_prior_success', 'auditbench_ia_success'])
    assert 0 <= prior < current < 1
    print(f"AuditBench: {(current-prior)*100:.1f} percentage points; "
          f"{(current-prior)/(1-prior)*100:.1f}% relative reduction in reported misses")
    print(f"Validated {len(events)} events across {len(cases)} cases; generated obstacles.csv")
    if not args.check_sources:
        return
    fetched = {}
    for key in ['ia2026', 'symmetry2026', 'cbattack2024', 'matryoshka2025',
                'weightdescriptions2026', 'storage2026']:
        request = Request(events[key]['url'], headers={'User-Agent': 'InterpretabilityEvidenceCheck/1.0'})
        with urlopen(request, timeout=45) as response:
            raw = response.read().decode('utf-8')
        parsed = TableParser()
        parsed.feed(raw)
        fetched[key] = parsed
    normalized = {key: ' '.join(' '.join(p.text).split()) for key, p in fetched.items()}
    for token in ['59%', '53%', '44%']:
        assert token in normalized['ia2026'], token
    table_rows = [row for table in fetched['symmetry2026'].tables.values()
                  for row in table if len(row) >= 6 and row[0].startswith(
                      ('backdoor_', 'heuristic_', 'quirk_', 'rare_'))]
    assert len(table_rows) == 7, 'Symmetry Table 1: expected seven fine-tunes'
    for index, row in enumerate(table_rows):
        assert float(row[-2].rstrip('%')) == numbers['symmetry_pre_percent'][index], row
        assert float(row[-1].rstrip('%')) == numbers['symmetry_post_percent'][index], row
    assert re.search(r'100\s*%', normalized['cbattack2024'])
    assert '50%' in normalized['matryoshka2025']
    assert '12 to 31%' in normalized['weightdescriptions2026']
    assert '64' in normalized['storage2026'] and 'activation storage' in normalized['storage2026']
    print('PASS: IA comparison, seven symmetry rows and four supporting numeric statements located.')
    print('This is a transcription check. Scope, causal attribution and timing judgments require reading the sources.')


if __name__ == '__main__':
    main()
