#!/usr/bin/env python3
"""Offline validation, with separate historical-completeness and primary-coverage checks."""
import argparse,csv,json,hashlib,sys
from pathlib import Path
from datetime import date,timedelta
from build import coverage,organizational_identity,tokens
from paths import SOURCE, INPUTS, safe_path

def read(p):
 with p.open(encoding='utf8') as f:return list(csv.DictReader(f))
def validate(root,require_complete=False,require_primary_coverage=False):
 meta=json.loads((root/'metadata.json').read_text());ps=read(root/'periods.csv');daily=read(root/'daily_coverage.csv');members=read(root/'membership.csv');ww=read(root/'witnesses.csv')
 services={s['service_id']:s for s in read(root/'services.csv')};affs={a['affiliation_id']:a for a in read(root/'affiliations.csv')};events=read(root/'organizational_events.csv');names=read(root/'party_names.csv')
 evidence_ids={e['evidence_id'] for e in read(root/'evidence.csv')};decision_ids={d['decision_id'] for d in read(root/'decisions.csv')}
 assumptions=read(root/'primary_assumptions.csv') if (root/'primary_assumptions.csv').is_file() else []
 assumption_by_id={a['assumption_id']:a for a in assumptions};assert len(assumption_by_id)==len(assumptions),'duplicate assumption IDs'
 for a in assumptions:
  assert a['assumed_state']=='UNAFFILIATED' and not a['assumed_party_id'] and a['historical_state']=='UNKNOWN'
  af=affs[a['affiliation_id']];assert af['state']=='UNKNOWN' and af['person_id']==a['person_id']
  assert max('2015-01-01',af['start_inclusive'])<=a['start_inclusive']<a['end_exclusive']<=min('2026-03-20',af['end_exclusive'])
  assert a['authorization'] and a['rationale'] and a['decision_ids']
  assert tokens(a['evidence_ids'])<=evidence_ids and tokens(a['decision_ids'])<=decision_ids
 expected=[(date(2015,1,1)+timedelta(days=i)).isoformat() for i in range(4096)]
 assert [r['date'] for r in daily]==expected
 assert len({p['period_id'] for p in ps})==len(ps)
 assert ps[0]['start_inclusive']=='2015-01-01' and ps[-1]['end_exclusive']=='2026-03-20'
 assert all(a['end_exclusive']==b['start_inclusive'] for a,b in zip(ps,ps[1:]))
 assert all(p['start_inclusive']<p['end_exclusive'] and int(p['days'])==(date.fromisoformat(p['end_exclusive'])-date.fromisoformat(p['start_inclusive'])).days for p in ps)
 def labels(parties,t):return tuple(sorted(next(n['label'] for n in names if n['party_id']==x and n['start_inclusive']<=t<n['end_exclusive']) for x in tokens(parties)))
 for a,b in zip(ps,ps[1:]):
  if a['administration_id']==b['administration_id'] and a['composition_status']!='unidentified' and b['composition_status']!='unidentified':assert (a['party_ids'],labels(a['party_ids'],a['start_inclusive']))!=(b['party_ids'],labels(b['party_ids'],b['start_inclusive']))
 used_assumptions=set()
 for r in daily:
  matches=[p for p in ps if p['start_inclusive']<=r['date']<p['end_exclusive']];assert len(matches)==1 and matches[0]['period_id']==r['period_id']
  assert r['party_ids']==matches[0]['party_ids'] and r['administration_id']==matches[0]['administration_id']
  selected=[a for a in assumptions if a['start_inclusive']<=r['date']<a['end_exclusive']]
  selected_ids={a['assumption_id'] for a in selected};selected_people={a['person_id'] for a in selected}
  assert len(selected_people)==len(selected),'overlapping person assumptions'
  assert tokens(r.get('primary_assumption_ids',''))==selected_ids
  historical=tokens(r['unresolved_dependencies']);assert selected_people<=historical
  remaining=historical-selected_people;used_assumptions|=selected_ids
  assert tokens(r.get('unfilled_primary_dependencies',r['unresolved_dependencies']))==remaining
  assert r['composition_status']==('unidentified' if remaining else 'primary_provisional' if historical else 'primary_adjudicated')
  if 'historical_status' in r:assert r['historical_status']==('unidentified' if historical else 'established')
 assert used_assumptions==set(assumption_by_id),'unused assumptions'
 historical_missing=sum(bool(r['unresolved_dependencies']) for r in daily);primary_missing=sum(r['composition_status']=='unidentified' for r in daily);provisional=sum(r['composition_status']=='primary_provisional' for r in daily)
 assert meta['identified_days']==4096-historical_missing and meta['unidentified_days']==historical_missing
 assert meta['complete']==(historical_missing==0)
 if 'primary_complete' in meta:
  assert meta['primary_complete']==(primary_missing==0) and meta['primary_covered_days']==4096-primary_missing and meta['primary_uncovered_days']==primary_missing and meta['provisional_days']==provisional
 for w in ww:
  sv=services[w['service_id']];af=affs[w['affiliation_id']]
  assert sv['included']=='true' and sv['person_id']==af['person_id']==w['person_id']
  assert max(sv['start_inclusive'],af['start_inclusive'])<=w['start_inclusive']<w['end_exclusive']<=min(sv['end_exclusive'],af['end_exclusive'])
  assert af['state']=='PARTY' and organizational_identity(af['party_id'],w['start_inclusive'],events)==w['party_id']
 for p in ps:
  mm={m['party_id'] for m in members if m['period_id']==p['period_id']};assert mm==tokens(p['party_ids'])
  if p['composition_status']=='unidentified':assert not mm
  if 'provisional_days' in p:
   count=sum(r['composition_status']=='primary_provisional' for r in daily if p['start_inclusive']<=r['date']<p['end_exclusive'])
   assert int(p['provisional_days'])==count
   if p['composition_status']!='unidentified':assert p['composition_status']==('primary_provisional' if count else 'primary_adjudicated')
  for party in mm:assert coverage([(w['start_inclusive'],w['end_exclusive']) for w in ww if w['period_id']==p['period_id'] and w['party_id']==party],p['start_inclusive'],p['end_exclusive'])
 accounting=read(root/'office_accounting.csv')
 for o in read(root/'offices.csv'):
  spans=sorted((r['start_inclusive'],r['end_exclusive']) for r in accounting if r['office_id']==o['office_id'])
  assert coverage(spans,o['start_inclusive'],o['end_exclusive']) and all(a[1]==b[0] for a,b in zip(spans,spans[1:]))
 for r in list(services.values())+list(affs.values()):
  assert {x.strip() for x in tokens(r['evidence_ids'])}<=evidence_ids
  assert {x.strip() for x in tokens(r['decision_ids'])}<=decision_ids
 manifest=json.loads((root/'manifest.json').read_text())
 for f,h in manifest['generated_file_sha256'].items():assert hashlib.sha256((root/f).read_bytes()).hexdigest()==h,f
 evidence_root=SOURCE
 for f,h in manifest['source_snapshot_sha256'].items():
  source=safe_path(evidence_root/f);assert source.is_file(),f
  assert hashlib.sha256(source.read_bytes()).hexdigest()==h,f
 blockers=read(root/'completion_blockers.csv');assert all(r['research_record_id'] and r['source_review_finding'] for r in blockers)
 result=dict(structural_checks='passed',calendar_days=len(daily),primary_covered_days=4096-primary_missing,primary_uncovered_days=primary_missing,provisional_days=provisional,primary_complete=primary_missing==0,identified_days=meta['identified_days'],unidentified_days=meta['unidentified_days'],complete=meta['complete'],remaining_dependencies=len({r['dependency_id'] for r in blockers}))
 if require_complete and not meta['complete']:raise ValueError('Historical completeness failed: '+str(meta['unidentified_days'])+' unidentified days remain')
 if require_primary_coverage and primary_missing:raise ValueError('Primary coverage failed: '+str(primary_missing)+' unfilled days remain')
 return result


def validate_sources():
    """Check current foreign keys, local snapshots, reviewed originals and search records.

    Human-readable source locators preserve original spelling; snapshot_path is
    the canonical local locator. Cross-reference labels are resolved via the
    original retained ledgers, not misrepresented as retrieved source documents.
    """
    evidence = read(INPUTS / 'evidence.csv')
    decisions = read(INPUTS / 'decisions.csv')
    evidence_ids = {row['evidence_id'] for row in evidence}
    decision_ids = {row['decision_id'] for row in decisions}
    assert len(evidence_ids) == len(evidence), 'Duplicate evidence IDs'
    assert len(decision_ids) == len(decisions), 'Duplicate decision IDs'
    for table in INPUTS.glob('*.csv'):
        for row in read(table):
            for field, known in [('evidence_ids', evidence_ids), ('decision_ids', decision_ids)]:
                references = {v.strip() for v in row.get(field, '').split(';') if v.strip()}
                assert references <= known, (table.name, field, references - known)
    snapshots = {}
    links = read(INPUTS / 'evidence_snapshot_links.csv')
    for row in links:
        assert row['evidence_id'] in evidence_ids, row['evidence_id']
        name, digest = row['snapshot_path'], row['sha256']
        assert name not in snapshots or snapshots[name] == digest, name
        snapshots[name] = digest
    for name, digest in snapshots.items():
        path = safe_path(SOURCE / name)
        assert path.is_file(), name
        with path.open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == digest, name
    saved = set()
    for row in read(INPUTS / 'completion_research_register.csv'):
        saved.update(filter(None, row['saved_result_files'].split(';')))
    for name in saved:
        assert safe_path(SOURCE / name).is_file(), name
    diary = SOURCE / 'research/refinement_v5/worker_7_lula_dates/sources'
    reviewed = json.loads((diary / 'diary_review_manifest.json').read_text())
    for row in reviewed:
        path = safe_path(diary / row['file'])
        with path.open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['sha256_original_pdf'], row['file']
    inherited = SOURCE / 'research/inherited'
    aliases = {
        'CODE-04': ('audit__code_dependency_audit.md', 'CODE-04'),
        'LEG record for Quintella': ('audit__prior_evidence_assertions.csv', 'Quintella'),
        'MAIN_AUDIT_REPORT.md sections 3,6': ('audit__MAIN_AUDIT_REPORT.md', 'Quintella'),
        'OCC-005': ('audit__office_audit__occupancy_discrepancies.csv', 'OCC-005'),
        'OFF-031–OFF-034': ('audit__office_audit__evidence_assertions.csv', 'OFF-031'),
        'office_audit/occupancy_discrepancies.csv': ('audit__office_audit__occupancy_discrepancies.csv', ''),
        'office_audit/pinned_source_rows.csv': ('audit__office_audit__pinned_source_rows.csv', ''),
        'prior_evidence_assertions.csv': ('audit__prior_evidence_assertions.csv', ''),
    }
    for identifier, (filename, marker) in aliases.items():
        assert identifier in evidence_ids
        assert marker in safe_path(inherited / filename).read_text(), identifier
    return dict(evidence_records=len(evidence_ids), accepted_decisions=len(decision_ids),
                evidence_links=len(links), verified_snapshots=len(snapshots),
                reviewed_original_diaries=len(reviewed), saved_research_files=len(saved),
                resolved_legacy_cross_references=len(aliases))


def compare_public(release, reference):
    """Exact reproduction includes metadata and every finite sensitivity calendar."""
    release, reference = safe_path(release), safe_path(reference)
    expected = {'cabinet_periods.csv', 'cabinet_sensitivity_periods.csv',
                'cabinet_coverage.csv', 'metadata.json'}
    assert {p.name for p in release.iterdir()} == expected
    assert {p.name for p in reference.iterdir()} == expected
    for name in sorted(expected):
        assert safe_path(release / name).read_bytes() == safe_path(reference / name).read_bytes(), name
    return dict(public_files_byte_identical=4, sensitivity_calendars=52,
                primary_days=4096, scenario_dates=212992)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--release',type=Path,required=True);parser.add_argument('--require-complete',action='store_true');parser.add_argument('--require-primary-coverage',action='store_true');args=parser.parse_args()
 try:print(json.dumps(validate(args.release,args.require_complete,args.require_primary_coverage),indent=2))
 except (ValueError,AssertionError) as e:print(str(e),file=sys.stderr);sys.exit(1)
