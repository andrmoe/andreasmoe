"""Check published numeric extractions, without third-party dependencies.

This is a transcription check, not replication of any experiment. HTML files
are fetched from the exact versions in evidence.json; no private APIs are used.
"""
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = {}
        self.table = None
        self.row = None
        self.cell = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table':
            self.table = attrs.get('id', '')
            self.tables[self.table] = []
        if tag == 'tr' and self.table is not None:
            self.row = []
        if tag in ('td', 'th') and self.row is not None:
            self.cell = []

    def handle_data(self, value):
        self.text.append(value)
        if self.cell is not None:
            self.cell.append(value)

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.tables[self.table].append(self.row)
            self.row = None
        if tag == 'table':
            self.table = None


def main():
    data = json.loads(Path(__file__).with_name('evidence.json').read_text())
    source = {s['id']: s for s in data['sources']}
    parsed = {}
    for key in ['fibs2026', 'apollo2025', 'stakes2025', 'fibsweb2026']:
        request = Request(source[key]['url'], headers={'User-Agent': 'InterpretabilityEvidenceCheck/1.0'})
        with urlopen(request, timeout=60) as response:
            raw = response.read()
        p = TableParser()
        p.feed(raw.decode('utf-8'))
        parsed[key] = p
        expected_hash = source[key].get('retrieved_html_sha256')
        same_hash = hashlib.sha256(raw).hexdigest() == expected_hash
        print(key, 'HTML hash unchanged' if same_hash else 'HTML changed or unpinned; checking numeric facts')
    tables = parsed['fibs2026'].tables
    relevant = [rows for name, rows in tables.items() if name.startswith('A5.T12')]
    assert len(relevant) == 1, 'FIBS Table 12 not found'
    rows = {r[0]: r for r in relevant[0] if len(r) >= 5}
    method_column = {'Activation oracle': 2, 'Axial probe': 3, 'Self-report': 4}
    checked = 0
    for o in data['observations']:
        if o['scope'] != 'hidden-goal':
            continue
        row = rows[o['task']]
        count = int(re.search(r'\((\d+)\)', row[method_column[o['method']]]).group(1))
        assert int(row[1]) == o['n_positive'], o['id']
        assert count == o['caught'], o['id']
        assert abs(count/int(row[1])-o['value']) < 1e-12, o['id']
        checked += 1
    apollo = ' '.join(parsed['apollo2025'].text)
    for token in ['0.964', '0.999', '0.974', '0.983', 'misses 4%']:
        assert token in apollo, token
    stakes = ' '.join(parsed['stakes2025'].text)
    for token in ['43%', '55%', '40%']:
        assert token in stakes, token
    web = ' '.join(parsed['fibsweb2026'].text)
    assert '73%' in web and '1% false-positive rate' in web, 'Live FIBS headline changed'
    print(f'PASS: {checked} count-based observations, four Apollo AUROCs, and reported approximate anchors located.')
    print('Source consistency issue retained: Apollo main-text and Appendix E roleplaying recall differ.')


if __name__ == '__main__':
    main()
