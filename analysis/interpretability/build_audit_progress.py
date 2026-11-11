"""Export audit comparisons and check selected source transcriptions, not experiments."""
import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path
from urllib.request import urlopen

from check_sources import TableParser

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-sources', action='store_true')
    args = parser.parse_args()
    data = json.loads((HERE / 'audit-progress.json').read_text())
    sources = data['sources']
    protocols = data['protocols']
    ids = set()
    for row in data['observations']:
        assert row['id'] not in ids
        ids.add(row['id'])
        assert row['source'] in sources and row['protocol'] in protocols
        assert 0 <= row['success'] <= 1 and row['status']
    for source in sources.values():
        assert source['url'].startswith('https://')
        assert source['locator'] and source['verification']
        if source['publication_date']:
            assert date.fromisoformat(source['publication_date']) <= date.fromisoformat(data['retrieved'])
    fields = ['id', 'method', 'protocol', 'success', 'source', 'status']
    with (HERE / 'audit-progress.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(data['observations'])
    rows = {row['id']: row for row in data['observations']}
    a, b = (rows[key]['success'] for key in ['ia', 'loracles'])
    print(f'Reported IA to provisional LoRAcles: {(b-a)*100:.1f} pp; {(b-a)/(1-a)*100:.1f}% fewer misses')
    print(f"Validated {len(rows)} observations in {len(protocols)} separate protocols; generated CSV")
    print('PENDING MANUAL VERIFICATION: LoRAcles headline and exact publication date; not a dated trend point.')
    if not args.check_sources:
        return
    fetched = {}
    for key in ['ia', 'rl', 'loracles_code']:
        with urlopen(sources[key]['url'], timeout=45) as response:
            fetched[key] = response.read().decode('utf-8')
    for value in ['53%', '59%']:
        assert value in fetched['ia'], value
    parsed = TableParser()
    parsed.feed(fetched['rl'])
    tables = [rows for key, rows in parsed.tables.items() if key.startswith('A7.T10')]
    assert len(tables) == 1, 'Expected Appendix G Table 10'
    table = {row[0]: row for row in tables[0] if len(row) == 3}
    for label, keys in [
        ('Haiku 4.5 (base)', ['base_stc', 'base_chat']),
        ('MT IG PW 4/8 FP, 3 ep', ['rl_stc', 'rl_chat']),
    ]:
        for cell, key in zip(table[label][1:], keys):
            reported = float(re.match(r'[\d.]+', cell).group())
            assert abs(reported / 100 - rows[key]['success']) < 1e-10, (label, key, cell)
    for flag in ['--max-tokens 25000', '--n-runs 16', '--max-final-quirks 10', '--loracle-n-rollouts 8']:
        assert flag in fetched['loracles_code'], flag
    print('PASS: selected IA numbers, paired RL table rows and pinned code settings located.')
    print('LoRAcles 71% was NOT automatically verified; no experiments were replicated.')


if __name__ == '__main__':
    main()
