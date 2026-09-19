#!/usr/bin/env python3
"""Export complete election-identity cabinet calendars, without electoral data.

Construct complete primary and finite alternative calendars from the accepted
curated history. Only standard-library and producer-local inputs are used.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from paths import PROJECT as ROOT, PROJECTION as APPLICATION, build_path
RELEASE_VERSION = '2026-03-19-v6-election-v1'
START, END = '2015-01-01', '2026-03-20'
WINDOWS = [(2014, START, '2019-01-01'), (2018, '2019-01-01', '2023-01-01'),
           (2022, '2023-01-01', END)]
PERIOD_FIELDS = ['period_id', 'election_year', 'start_inclusive', 'end_exclusive', 'party_set']
COVERAGE_FIELDS = ['start_inclusive', 'end_exclusive', 'administration', 'status']
FILES = {'cabinet_periods.csv': PERIOD_FIELDS,
         'cabinet_sensitivity_periods.csv': ['scenario_id'] + PERIOD_FIELDS,
         'cabinet_coverage.csv': COVERAGE_FIELDS}


def read(path):
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


def write(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def tokens(value):
    return set(filter(None, (item.strip() for item in value.split(';'))))


def joined(values):
    return ';'.join(sorted(set(values)))


def truth(value):
    return str(value).lower() in ('true', 'yes', '1')


def dates(start, end):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    return [(first + timedelta(days=i)).isoformat() for i in range((last-first).days)]


def tomorrow(day):
    return (date.fromisoformat(day) + timedelta(days=1)).isoformat()


def election(day):
    for year, start, end in WINDOWS:
        if start <= day < end:
            return year
    raise ValueError(f'Date outside pinned coverage: {day}')


def producer_path(path):
    """Reject redirected paths before opening any producer source or destination."""
    path = Path(path).absolute()
    if any(part.is_symlink() for part in [path, *path.parents]):
        raise ValueError(f'Symlink paths are not supported: {path}')
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f'Path must be inside independent producer {ROOT}: {path}')
    return resolved


def validate_inputs(source):
    source = producer_path(source)
    pin = json.loads((APPLICATION/'cabinet_release_pin.json').read_text())
    # This digest is historical provenance in the immutable public contract.
    # Current scientific inputs are checked individually below; current build
    # metadata truthfully records the refactored code and current artifact set.
    meta = json.loads((source/'metadata.json').read_text())
    assert meta['schema_version'] == pin['schema_version'] == 3
    assert meta['data_version'] == pin['data_version']
    assert meta['cutoff_exclusive'] == pin['cutoff_exclusive'] == END
    assert meta['primary_complete'] and meta['primary_covered_days'] == 4096
    assert meta['identified_days'] == 3996 and meta['provisional_days'] == 100
    for name, checksum in pin['file_hashes'].items():
        assert digest(producer_path(source/name)) == checksum, f'Frozen source changed: {name}'
    crosswalk = APPLICATION/'cabinet_release_election_crosswalk.csv'
    assert digest(crosswalk) == pin['crosswalk_sha256'], 'Projection pin mismatch'
    mapping, seen = defaultdict(set), set()
    for row in read(crosswalk):
        key = (int(row['election_year']), row['party_id'], row['election_party'])
        assert key not in seen and row['basis'] and row['mapping_type'] in {
            'explicit_identity', 'crosswalk_rename', 'crosswalk_fusion_expansion'}
        seen.add(key)
        mapping[key[:2]].add(key[2])
    return pin, mapping


def translate(historical, year, mapping):
    result = set()
    for party in historical:
        assert (year, party) in mapping and mapping[year, party], f'Unaudited identity: {year}/{party}'
        result.update(mapping[year, party])
    return joined(result)


def compress(daily):
    """Membership and election alone define maximal periods; status is separate."""
    result = []
    for row in daily:
        if (result and result[-1]['end_exclusive'] == row['date']
                and result[-1]['election_year'] == row['election_year']
                and result[-1]['party_set'] == row['party_set']):
            result[-1]['end_exclusive'] = tomorrow(row['date'])
        else:
            result.append(dict(period_id=f'CV5-{len(result)+1:03d}', election_year=row['election_year'],
                               start_inclusive=row['date'], end_exclusive=tomorrow(row['date']),
                               party_set=row['party_set']))
    return result


def compress_coverage(daily):
    result = []
    for row in daily:
        status = 'provisional' if row['provisional_day'] else 'established'
        if (result and result[-1]['end_exclusive'] == row['date']
                and result[-1]['administration'] == row['administration']
                and result[-1]['status'] == status):
            result[-1]['end_exclusive'] = tomorrow(row['date'])
        else:
            result.append(dict(start_inclusive=row['date'], end_exclusive=tomorrow(row['date']),
                               administration=row['administration'], status=status))
    return result


def primary_daily(source, mapping):
    daily = []
    for row in read(source/'daily_coverage.csv'):
        day = row['date']
        assert not row['unfilled_primary_dependencies']
        provisional = row['composition_status'] == 'primary_provisional'
        assert provisional == bool(row['primary_assumption_ids']) == bool(row['provisional_person_ids'])
        daily.append(dict(date=day, election_year=election(day),
                          party_set=translate(tokens(row['party_ids']), election(day), mapping),
                          administration=row['administration_id'], provisional_day=provisional,
                          provisional_person_ids=row['provisional_person_ids']))
    assert [row['date'] for row in daily] == dates(START, END), 'Gap, duplicate or disorder'
    return daily


def other_union(witnesses, day, excluded_person=None, excluded_services=()):
    """Remove the changed witness only; independently represented parties survive."""
    return {w['party_id'] for w in witnesses
            if w['start_inclusive'] <= day < w['end_exclusive']
            and w['person_id'] != excluded_person and w['service_id'] not in excluded_services}


def service_alternative(witnesses, day, constraint, candidate, outgoing, incoming, provisional_people):
    """Shift the outgoing end AND incoming start at the same candidate boundary."""
    result = other_union(witnesses, day, excluded_services={outgoing['service_id'], incoming['service_id']})
    side = 'outgoing' if day < candidate else 'incoming'
    if constraint[side+'_state'] == 'PARTY':
        result.add(constraint[side+'_party_id'])
    if constraint[side+'_state'] == 'UNKNOWN':
        assert constraint[side+'_person_id'] in provisional_people
    return result


def concrete_sensitivities(source, mapping, daily):
    """The accepted 52 one-at-a-time calendars; no invented joint alternatives."""
    bydate = {row['date']: row for row in daily}
    witnesses, services = read(source/'witnesses.csv'), read(source/'services.csv')
    scenario_periods, definitions = [], []

    def evaluate(sid, candidate, start, end, alter, kind, meaning, unbounded=False):
        scenario = sid+'/'+candidate
        changed = [dict(row) for row in daily]
        for day in dates(start, end):
            index = (date.fromisoformat(day)-date.fromisoformat(START)).days
            changed[index]['party_set'] = translate(alter(day), bydate[day]['election_year'], mapping)
        definitions.append(dict(scenario_id=scenario, sensitivity_id=sid, kind=kind, candidate=candidate,
                                start_inclusive=start, end_exclusive=end,
                                unbounded_personal_uncertainty=unbounded, meaning=meaning))
        scenario_periods.extend(dict(scenario_id=scenario, **period) for period in compress(changed))

    for constraint in read(source/'sensitivity_constraints.csv'):
        assert constraint['event_type'] == 'affiliation_change'
        for candidate in sorted(tokens(constraint['candidate_dates'])):
            if candidate == constraint['baseline_effective_date']:
                continue
            def alter(day, c=constraint, candidate=candidate):
                result = other_union(witnesses, day, excluded_person=c['person_id'])
                side = 'before' if day < candidate else 'after'
                active = any(s['person_id'] == c['person_id'] and truth(s['included'])
                             and s['start_inclusive'] <= day < s['end_exclusive'] for s in services)
                if active and c[side+'_state'] == 'PARTY':
                    result.add(c[side+'_party_id'])
                return result
            evaluate(constraint['uncertainty_id'], candidate, constraint['earliest_effective_date'],
                     constraint['latest_effective_date'], alter, 'joint_affiliation_date',
                     f"One affiliation transition effective {candidate} instead of {constraint['baseline_effective_date']}; "
                     'adjacent states move together; all other accepted facts retain primary values.')

    for constraint in read(source/'service_sensitivity_constraints.csv'):
        outgoing = [s for s in services if s['office_id'] == constraint['office_id']
                    and s['person_id'] == constraint['outgoing_person_id']
                    and s['end_exclusive'] == constraint['baseline_effective_date'] and truth(s['included'])]
        incoming = [s for s in services if s['office_id'] == constraint['office_id']
                    and s['person_id'] == constraint['incoming_person_id']
                    and s['start_inclusive'] == constraint['baseline_effective_date'] and truth(s['included'])]
        assert len(outgoing) == len(incoming) == 1, constraint['uncertainty_id']
        for candidate in sorted(tokens(constraint['candidate_dates'])):
            if candidate == constraint['baseline_effective_date']:
                continue
            def alter(day, c=constraint, candidate=candidate, outgoing=outgoing, incoming=incoming):
                return service_alternative(witnesses, day, c, candidate, outgoing[0], incoming[0],
                                           tokens(bydate[day]['provisional_person_ids']))
            evaluate(constraint['uncertainty_id'], candidate, constraint['earliest_effective_date'],
                     constraint['latest_effective_date'], alter, 'joint_service_date',
                     f"One succession effective {candidate} instead of {constraint['baseline_effective_date']}; "
                     'outgoing and incoming service boundaries move together; all other accepted facts retain primary values.',
                     unbounded='UNKNOWN' in (constraint['outgoing_state'], constraint['incoming_state']))

    for constraint in read(source/'residual_person_uncertainty.csv'):
        if constraint['alternative_scope'] == 'linked_date_window':
            continue  # Already covered by one coupled event, never free daily choices.
        primary = constraint['primary_party_id'] if constraint['primary_state'] == 'PARTY' else constraint['primary_state']
        for candidate in json.loads(constraint['alternatives']):
            if candidate == primary:
                continue
            assert candidate != 'UNKNOWN', 'Unbounded alternatives must not be fabricated'
            def alter(day, c=constraint, candidate=candidate):
                result = other_union(witnesses, day, excluded_person=c['person_id'])
                if candidate != 'UNAFFILIATED':
                    result.add(candidate)
                return result
            evaluate(constraint['uncertainty_id'], candidate, constraint['start_inclusive'],
                     constraint['end_exclusive'], alter, 'finite_affiliation',
                     f'One bounded affiliation alternative ({candidate}) on the stated interval; independent representation '
                     'and all other accepted facts retain primary values. Candidate is an opaque upstream label; '
                     'the complete published election-year memberships are authoritative.')
    definitions.sort(key=lambda row: row['scenario_id'])
    scenario_periods.sort(key=lambda row: (row['scenario_id'], row['start_inclusive']))
    assert len({row['scenario_id'] for row in definitions}) == len(definitions) == 52
    return definitions, scenario_periods


def aggregate_checksum(output):
    """One checksum: sorted UTF-8 filename, NUL, file bytes, NUL for each CSV."""
    checksum = hashlib.sha256()
    for name in sorted(FILES):
        checksum.update(name.encode('utf-8') + b'\0')
        checksum.update((output/name).read_bytes())
        checksum.update(b'\0')
    return checksum.hexdigest()


def export(source, output):
    source, output = producer_path(source), build_path(output)
    if output.exists():
        raise FileExistsError(f'Release output must be fresh: {output}')
    pin, mapping = validate_inputs(source)
    daily = primary_daily(source, mapping)
    primary, coverage = compress(daily), compress_coverage(daily)
    scenarios, alternatives = concrete_sensitivities(source, mapping, daily)
    assert len(primary) == 53 and len(alternatives) == 2753
    output.mkdir(parents=True)
    write(output/'cabinet_periods.csv', primary, PERIOD_FIELDS)
    write(output/'cabinet_sensitivity_periods.csv', alternatives, ['scenario_id'] + PERIOD_FIELDS)
    write(output/'cabinet_coverage.csv', coverage, COVERAGE_FIELDS)
    metadata = dict(
        schema='cabinet-election-periods', schema_version=1, release_version=RELEASE_VERSION,
        coverage=dict(start_inclusive=START, end_exclusive=END),
        election_windows=[dict(election_year=year, start_inclusive=start, end_exclusive=end)
                          for year, start, end in WINDOWS],
        files=FILES,
        date_convention='ISO 8601 civil dates; start inclusive, end exclusive; closing-state convention; days are calendar-date differences.',
        party_identity_convention='2014, 2018 and 2022 election labels under the accepted projection; one-to-many merger expansions are set unions before maximal compression.',
        party_set_encoding='Semicolon-separated, sorted unique UTF-8 party labels. Empty string is a complete empty set. Missing cells/rows are invalid; UNKNOWN is never a party label.',
        period_identifiers='CV5-NNN in chronological order, scoped to primary or scenario_id. Maximal membership and election periods; administration and status boundaries come from cabinet_coverage.csv.',
        coding_policy='Complete primary union of qualifying cabinet party witnesses under accepted V6 coding. A provisional date assumes no additional party contribution from an unresolved affiliation; it does not establish historical non-affiliation.',
        scenario_policy='Each scenario is a complete calendar changing one accepted uncertainty at a time. Candidates with the same sensitivity_id are mutually exclusive. No joint combinations or exhaustive joint uncertainty are asserted. Equal memberships are retained as distinct accepted scenarios. All calendars inherit the exact primary coverage/status mask; provisional comparisons remain conditional.',
        unresolved_status='unbounded_unknown',
        unresolved_scope='Exactly the provisional intervals in cabinet_coverage.csv. Membership outside the finite alternatives is not bounded; no extra party or claim of zero possible effect is supplied.',
        scenarios=scenarios,
        source=dict(release_version=pin['data_version'], schema_version=pin['schema_version'],
                    metadata_sha256=pin['metadata_sha256'],
                    provenance_location=pin['release_path'],
                    projection_location='applications/coalition_inversions/cabinet_release_election_crosswalk.csv',
                    projection_sha256=pin['crosswalk_sha256']),
        data_checksum=dict(algorithm='sha256', framing='For each CSV filename in lexical order: UTF-8 filename, NUL byte, exact file bytes, NUL byte.',
                           value=aggregate_checksum(output)))
    (output/'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Exported {len(primary)} primary periods, {len(coverage)} coverage intervals, '
          f'{len(scenarios)} scenarios / {len(alternatives)} scenario periods to {output}')
    return metadata


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Explicit pinned internal V6 release directory inside producer')
    parser.add_argument('--output', type=Path, required=True, help='Fresh public release directory inside producer; existing output is rejected')
    args = parser.parse_args()
    export(args.source, args.output)
