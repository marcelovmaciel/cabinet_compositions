"""Reconstruction boundary plus an independent four-file reader of its fresh export."""
import csv
from datetime import date, timedelta
import hashlib
import json
from pathlib import Path
import unittest

from fixtures import reconstruction

def release():
    return reconstruction()/'release'


def read(name):
    with (release()/name).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def expand(periods):
    result = {}
    for row in periods:
        start, end = date.fromisoformat(row['start_inclusive']), date.fromisoformat(row['end_exclusive'])
        assert start < end
        assert row['party_set'] is not None
        members = row['party_set'].split(';') if row['party_set'] else []
        assert members == sorted(set(members))
        for index in range((end-start).days):
            day = (start+timedelta(days=index)).isoformat()
            assert day not in result
            result[day] = (int(row['election_year']), tuple(members))
    return result


class DataOnlyContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta = json.loads((release()/'metadata.json').read_text())
        cls.primary = read('cabinet_periods.csv')
        cls.daily = expand(cls.primary)

    def test_primary_and_coverage_are_complete_exact_date_masks(self):
        start, end = date.fromisoformat(self.meta['coverage']['start_inclusive']), date.fromisoformat(self.meta['coverage']['end_exclusive'])
        expected = {(start+timedelta(days=i)).isoformat() for i in range((end-start).days)}
        self.assertEqual(set(self.daily), expected)
        covered, provisional = set(), 0
        for row in read('cabinet_coverage.csv'):
            self.assertIn(row['status'], ('established','provisional'))
            first, last = date.fromisoformat(row['start_inclusive']), date.fromisoformat(row['end_exclusive'])
            days = {(first+timedelta(days=i)).isoformat() for i in range((last-first).days)}
            self.assertFalse(days & covered)
            covered.update(days)
            if row['status'] == 'provisional': provisional += len(days)
        self.assertEqual(covered, expected)
        self.assertEqual((len(covered), provisional), (4096,100))
        self.assertEqual(self.meta['unresolved_status'], 'unbounded_unknown')
        for day, (year, _) in self.daily.items():
            self.assertEqual([w['election_year'] for w in self.meta['election_windows']
                              if w['start_inclusive'] <= day < w['end_exclusive']], [year])

    def test_all_scenarios_are_complete_with_changes_only_in_declared_scope(self):
        byscenario = {}
        for row in read('cabinet_sensitivity_periods.csv'):
            byscenario.setdefault(row['scenario_id'], []).append(row)
        definitions = {r['scenario_id']:r for r in self.meta['scenarios']}
        self.assertEqual(set(byscenario), set(definitions))
        self.assertEqual(len(byscenario),52)
        for sid, rows in byscenario.items():
            daily = expand(rows)
            self.assertEqual(set(daily),set(self.daily))
            definition = definitions[sid]
            for day, value in daily.items():
                if not definition['start_inclusive'] <= day < definition['end_exclusive']:
                    self.assertEqual(value,self.daily[day])
            self.assertEqual(len({r['period_id'] for r in rows}),len(rows))
            self.assertTrue(all((a['election_year'],a['party_set']) != (b['election_year'],b['party_set'])
                                for a,b in zip(rows,rows[1:])))
        flagged = [d['scenario_id'] for d in definitions.values() if d['unbounded_personal_uncertainty']]
        self.assertEqual(flagged,['mre-2021-effective-entry/2021-03-30'])

    def test_schema_and_single_content_checksum(self):
        self.assertEqual((self.meta['schema'], self.meta['schema_version']), ('cabinet-election-periods', 1))
        self.assertEqual(self.meta['release_version'], '2026-03-19-v6-election-v1')
        h = hashlib.sha256()
        self.assertEqual(set(self.meta['files']), {'cabinet_periods.csv','cabinet_sensitivity_periods.csv','cabinet_coverage.csv'})
        for name in sorted(self.meta['files']):
            h.update(name.encode()+b'\0')
            h.update((release()/name).read_bytes())
            h.update(b'\0')
            rows = read(name)
            self.assertEqual(list(rows[0]),self.meta['files'][name])
            self.assertTrue(all(None not in row and None not in row.values() for row in rows))
        self.assertEqual(h.hexdigest(), self.meta['data_checksum']['value'])



import shutil, tempfile
from unittest.mock import patch
from fixtures import ROOT, INPUTS, b, pipeline
from paths import PUBLISHED
from validate import compare_public

class ReconstructionTests(unittest.TestCase):
    def test_full_reconstruction_matches_all_four_published_files(self):
        output = reconstruction()
        compare_public(output / 'release', PUBLISHED)
        with self.assertRaises(FileExistsError):
            pipeline.reconstruct(output)
        with self.assertRaises(ValueError):
            pipeline.reconstruct(PUBLISHED)
        with self.assertRaises(ValueError):
            pipeline.reconstruct(INPUTS / 'output')

    def test_failed_construction_leaves_no_partial_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            inputs = root / 'inputs'
            shutil.copytree(INPUTS, inputs)
            rows = b.read(inputs / 'primary_assumptions.csv')
            rows[1]['assumption_id'] = rows[0]['assumption_id']
            b.write(inputs / 'primary_assumptions.csv', rows, list(rows[0]))
            with patch.object(pipeline, 'INPUTS', inputs):
                with self.assertRaisesRegex(AssertionError, 'duplicate assumption IDs'):
                    pipeline.reconstruct(root / 'failed')
            self.assertEqual({p.name for p in root.iterdir()}, {'inputs'})

    def test_overlapping_office_services_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            inputs = root / 'inputs'
            shutil.copytree(INPUTS, inputs)
            rows = b.read(inputs / 'services.csv')
            duplicate = next(r for r in rows if r['included'] == 'true').copy()
            duplicate['service_id'] += '-overlap'
            rows.append(duplicate)
            b.write(inputs / 'services.csv', rows, list(rows[0]))
            with self.assertRaisesRegex(AssertionError, 'overlapping officeholders'):
                b.build(inputs, root / 'historical')

