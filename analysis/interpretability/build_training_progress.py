"""Check training evidence transcriptions; export CSV and render page tables.

Uses the standard library. This does not replicate any model experiment.
"""
import argparse
import csv
import hashlib
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
from urllib.request import urlopen

from check_sources import TableParser

HERE = Path(__file__).resolve().parent
PAGE = HERE.parent.parent / 'interpretability_training.html'


def first_number(cell):
    # arXiv MathML can repeat numbers in its accessible text / TeX annotation.
    # The pinned tables report exactly two decimal places; read the first copy.
    match = re.match(r'\s*([+-]?\d+\.\d{2})', cell)
    assert match, f'Expected a two-decimal table value: {cell!r}'
    return float(match.group(1))


def fetch(source):
    with urlopen(source['url'], timeout=45) as response:
        raw = response.read()
    parsed = TableParser()
    parsed.feed(raw.decode('utf-8'))
    return parsed, hashlib.sha256(raw).hexdigest()


def check_sources(data):
    keys = ['probes', 'scaling']
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(fetch, [data['sources'][k] for k in keys]))
    fetched = dict(zip(keys, results))
    for key, (_, digest) in fetched.items():
        status = 'unchanged' if digest == data['sources'][key]['retrieved_html_sha256'] else 'changed'
        print(f'{key}: retrieved HTML hash {status}; checking values against exact version')
    for row in data['observations']:
        protocol = data['protocols'][row['protocol']]
        if 'source_table' not in row:
            continue
        table = fetched[protocol['source']][0].tables[row['source_table']]
        columns = protocol['columns']
        cells = table[row['source_row']][-len(columns):]
        assert len(cells) == len(columns), row['id']
        for metric, cell in zip(columns, cells):
            assert first_number(cell) == row['values'][metric], (row['id'], metric, cell)
            if 'reported_dispersion' in row:
                after_plusminus = cell.split('±', 1)[1].replace('\\pm', '')
                assert first_number(after_plusminus) == row['reported_dispersion'][metric], (row['id'], metric)
    # Verify textual endpoint numbers in their own clauses, not anywhere in a paper.
    scaling = ' '.join(' '.join(fetched['scaling'][0].text).split())
    patterns = [
        (r'drops from (\d+)% at 1B to (\d+)% at 405B', ['scaling_1b', 'scaling_405b']),
        (r'\((\d+)% at 8B, (\d+)% at 70B\)', ['spontaneous_8b', 'spontaneous_70b']),
    ]
    rows = {row['id']: row for row in data['observations']}
    for pattern, ids in patterns:
        match = re.search(pattern, scaling)
        assert match, f'Primary-source clause not found: {pattern}'
        for value, key in zip(match.groups(), ids):
            assert int(value) / 100 == next(iter(rows[key]['values'].values())), key
    for text in ['single seed for 405B', '0.15', 'spontaneous']:
        assert text in scaling, text
    print('PASS: all selected Table 1 / Table 9 values and dispersions, and four textual endpoints.')
    print('This verifies transcription only; no experiments or statistical claims were replicated.')


def render(data):
    rows = {row['id']: row for row in data['observations']}
    blocks = {}
    chosen = ['mistral_dpo', 'mistral_poly_updated', 'llama_dpo', 'llama_poly_updated']
    lines = []
    for key in chosen:
        row = rows[key]
        values = ''.join(f'<td>{row["values"][metric]:.2f}</td>' for metric in data['protocols']['jailbreak']['columns'])
        label = html.escape(f'{row["model"]} / {row["method"]}')
        lines.append(f'<tr><th scope="row">{label}</th>{values}</tr>')
    blocks['jailbreak'] = '\n'.join(lines)
    lines = []
    for row in data['observations']:
        if row['protocol'] != 'continuation':
            continue
        label = html.escape(row['method'])
        values = ''.join(f'<td>{row["values"][metric]:.2f}</td>' for metric in ['start', 'harmful_0'])
        lines.append(f'<tr><th scope="row">{label}</th>{values}</tr>')
    blocks['continuation'] = '\n'.join(lines)
    page = PAGE.read_text()
    for key, body in blocks.items():
        pattern = rf'(<!-- training:{key}:start -->).*?(<!-- training:{key}:end -->)'
        page, count = re.subn(pattern, lambda m: m[1] + '\n' + body + '\n' + m[2], page, flags=re.S)
        assert count == 1, f'Missing or duplicate table marker: {key}'
    PAGE.write_text(page)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-sources', action='store_true')
    args = parser.parse_args()
    data = json.loads((HERE / 'training-progress.json').read_text())
    ids = set()
    for source in data['sources'].values():
        assert source['url'].startswith('https://')
        assert date.fromisoformat(source['first_published']) <= date.fromisoformat(source['version_date']) <= date.fromisoformat(data['reviewed'])
    for row in data['observations']:
        assert row['id'] not in ids
        ids.add(row['id'])
        protocol = data['protocols'][row['protocol']]
        assert protocol['source'] in data['sources']
        assert list(row['values']) == protocol['columns']
        assert all(0 <= value <= 1 for value in row['values'].values())
        if 'reported_dispersion' in row:
            assert list(row['reported_dispersion']) == protocol['columns']
            assert all(value >= 0 for value in row['reported_dispersion'].values())
    # Do not regenerate artifacts after a failed optional source check.
    if args.check_sources:
        check_sources(data)
    fields = ['id', 'protocol', 'model', 'method', 'metric', 'value', 'reported_dispersion', 'source_url', 'locator']
    count = 0
    with (HERE / 'training-progress.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields, lineterminator='\n')
        writer.writeheader()
        for row in data['observations']:
            protocol = data['protocols'][row['protocol']]
            for metric, value in row['values'].items():
                writer.writerow({
                    **{key: row[key] for key in fields[:4]}, 'metric': metric, 'value': value,
                    'reported_dispersion': row.get('reported_dispersion', {}).get(metric, ''),
                    'source_url': data['sources'][protocol['source']]['url'], 'locator': protocol['locator'],
                })
                count += 1
    render(data)
    print(f'Validated {len(ids)} rows / {count} values in {len(data["protocols"])} separate protocols; exported CSV and rendered tables.')


if __name__ == '__main__':
    main()
