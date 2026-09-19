#!/usr/bin/env python3
"""Build read-only cabinet history documentation from accepted local tables.

No scientific construction or research is performed. Historical output must
already exist; normalized copies are checked semantically before use.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
START, END = '2015-01-01', '2026-03-20'
ADMINS = {'dilma_2': 'Dilma II', 'temer': 'Temer', 'bolsonaro': 'Bolsonaro', 'lula_3': 'Lula III'}
EXCLUDED = {'non_entry', 'incoming_transition', 'incoming_transition_CETG', 'temporary_delegation', 'outside_cutoff'}


def read(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle))


def split(value):
    return {item.strip() for item in (value or '').split(';') if item.strip()}


def joined(values):
    return ';'.join(sorted(set(filter(None, values))))


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def previous(day):
    return (date.fromisoformat(day) - timedelta(days=1)).isoformat()


def stable_id(*values):
    return hashlib.sha256('|'.join(values).encode()).hexdigest()[:12]


def clean(value):
    return str(value or '').replace('|', '&#124;').replace('\n', ' ').replace('\r', ' ')


def anchor(kind, value):
    return kind + '-' + value.lower()


def ref(kind, value):
    return f'[{value}](#{anchor(kind, value)})'


def refs(kind, values):
    return ', '.join(ref(kind, value) for value in sorted(set(values))) or 'None recorded'


def local_link(path, label=None):
    return f'[{label or path}](<{quote("../" + str(path), safe="/._-#") }>)'


def write_csv(path, rows, fields=None, delimiter=','):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fields or list(rows[0]), delimiter=delimiter, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


class History:
    def __init__(self, historical):
        self.historical = historical
        self.data = {path.stem: read(path) for path in sorted((ROOT / 'data/normalized').glob('*.csv'))}
        self.generated = {name: read(historical / f'{name}.csv') for name in ('transitions', 'periods', 'daily_coverage', 'witnesses', 'residual_person_uncertainty', 'date_sensitivity')}
        for name, rows in self.data.items():
            copied = historical / f'{name}.csv'
            if copied.exists():
                assert sorted(map(dumps, rows)) == sorted(map(dumps, read(copied))), f'Stale historical input: {name}'
        self.people = {r['person_id']: r['person_name'] for r in self.data['people']}
        self.services = [r for r in self.data['services'] if r['included'] == 'true' and r['capacity'] not in EXCLUDED and r['start_inclusive'] < r['end_exclusive']]
        self.service = {r['service_id']: r for r in self.services}
        self.affiliation = {r['affiliation_id']: r for r in self.data['affiliations']}
        self.office = {r['office_id']: r for r in self.data['offices']}
        self.evidence = {r['evidence_id']: r for r in self.data['evidence']}
        self.decision = {r['decision_id']: r for r in self.data['decisions']}
        self.assumption = {r['assumption_id']: r for r in self.data['primary_assumptions']}
        self.daily = {r['date']: r for r in self.generated['daily_coverage']}
        self.transition = {r['date']: r for r in self.generated['transitions']}
        self.period = {r['period_id']: r for r in self.generated['periods']}
        self.constraints = self.data['sensitivity_constraints'] + self.data['service_sensitivity_constraints']
        self.constraint = {r['uncertainty_id']: r for r in self.constraints}
        self.residual = {r['uncertainty_id']: r for r in self.generated['residual_person_uncertainty']}
        self.snapshots = defaultdict(list)
        for r in self.data['evidence_snapshot_links']:
            self.snapshots[r['evidence_id']].append(r)
        self.rows = []
        self.issues = []
        self.sources_used = set()
        self.decisions_used = set()
        self.witnesses = self.generated['witnesses']
        self.service_by_person = defaultdict(list)
        self.aff_by_person = defaultdict(list)
        for r in self.services:
            self.service_by_person[r['person_id']].append(r)
        for r in self.data['affiliations']:
            self.aff_by_person[r['person_id']].append(r)

    def issue(self, event, issue, ids, why, paths):
        self.issues.append(dict(event=event, issue=issue, affected_ids=ids, why_suspicious=why, source_paths_to_review=paths))

    def admin(self, day):
        if day == END:
            return 'lula_3'
        return self.daily[day]['administration_id']

    def label(self, party, day):
        return next((r['label'] for r in self.data['party_names'] if r['party_id'] == party and r['start_inclusive'] <= day < r['end_exclusive']), party)

    def identity(self, party, day):
        seen = set()
        while party and party not in seen:
            seen.add(party)
            candidates = [r for r in self.data['organizational_events'] if r['predecessor_party_id'] == party and r['successor_party_id'] != party and r['effective_date'] <= day]
            if not candidates:
                return party
            party = max(candidates, key=lambda r: r['effective_date'])['successor_party_id']
        return party

    def active(self, person, day):
        return [r for r in self.service_by_person[person] if r['start_inclusive'] <= day < r['end_exclusive']]

    def aff(self, person, day):
        return [r for r in self.aff_by_person[person] if r['start_inclusive'] <= day < r['end_exclusive']]

    def aff_state(self, rows, day, active):
        if not active:
            return 'OUTSIDE_QUALIFYING_SERVICE'
        return joined(self.label(self.identity(r['party_id'], day), day) if r['state'] == 'PARTY' else r['state'] for r in rows)

    def contribution(self, rows, day, active):
        if not active:
            return set()
        return {self.identity(r['party_id'], day) for r in rows if r['state'] == 'PARTY'}

    def enrich(self, row, records=(), evidence=(), decisions=()):
        direct = set(evidence)
        dids = set(decisions)
        for r in records:
            direct |= split(r.get('evidence_ids', ''))
            dids |= split(r.get('decision_ids', ''))
        # Some office/vacancy/organization rows cite a same-ID evidence/decision
        # pair through evidence_ids only. Expose the associated accepted decision.
        dids |= direct & self.decision.keys()
        indirect = set()
        for did in dids:
            assert did in self.decision, ('missing decision', row['event_id'], did)
            indirect |= split(self.decision[did]['evidence_ids']) & self.evidence.keys()
        all_evidence = direct | indirect
        assert all(eid in self.evidence for eid in all_evidence), ('missing evidence', row['event_id'], all_evidence - self.evidence.keys())
        self.sources_used |= all_evidence
        self.decisions_used |= dids
        row['evidence_ids'] = joined(all_evidence)
        row['direct_evidence_ids'] = joined(direct)
        row['decision_evidence_ids'] = joined(indirect)
        row['decision_ids'] = joined(dids)
        row['stored_assertions_json'] = dumps({eid: {'description': self.evidence[eid]['asserted_fact'], 'publisher': self.evidence[eid]['publisher'], 'publication_date': self.evidence[eid]['publication_date'], 'source_type_or_access_status': self.evidence[eid]['access_status'], 'source_locator': self.evidence[eid]['source_locator']} for eid in sorted(direct)})
        row['decision_rationales_json'] = dumps({did: self.decision[did] for did in sorted(dids)})
        row['snapshot_paths'] = joined('data/source/' + s['snapshot_path'] for eid in all_evidence for s in self.snapshots[eid])
        row['source_catalog'] = 'source_catalog.json'
        self.rows.append(row)
        return row

    def base(self, eid, day, layer, types, notes='', person='', office=''):
        before = self.daily.get(previous(day), {})
        after = self.daily[day]
        return dict(event_id=eid, event_date=day, date_end_or_bound='', administration_id=self.admin(day), administration=ADMINS[self.admin(day)], event_layer=layer, event_type=types, person=person, office=office, previous_service_state='', new_service_state='', previous_affiliation='', new_affiliation='', party_entering='', party_leaving='', cabinet_set_before=before.get('party_ids', ''), cabinet_set_after=after['party_ids'], cabinet_labels_before=before.get('party_labels', ''), cabinet_labels_after=after['party_labels'], changes_aggregate_party_set='false', aggregate_transition_id=self.transition.get(day, {}).get('transition_id', ''), relationship_to_aggregate='no_aggregate_transition', composition_status_before=before.get('composition_status', 'outside_observation'), composition_status=after['composition_status'], date_status='', uncertainty_status='', person_ids='', office_ids='', service_ids='', affiliation_ids='', primary_assumption_ids='', uncertainty_ids='', related_event_ids='', evidence_ids='', direct_evidence_ids='', decision_evidence_ids='', decision_ids='', stored_assertions_json='', decision_rationales_json='', snapshot_paths='', source_catalog='', notes=notes)

    def matching_constraints(self, persons, day):
        return [r for r in self.constraints if persons & {r.get('person_id'), r.get('outgoing_person_id'), r.get('incoming_person_id')} and r['earliest_effective_date'] <= day <= r['latest_effective_date']]

    def personals(self):
        boundaries = defaultdict(set)
        for r in self.services:
            for key in ('start_inclusive', 'end_exclusive'):
                if START <= r[key] < END:
                    boundaries[r[key]].add(r['person_id'])
        for r in self.data['affiliations']:
            for key in ('start_inclusive', 'end_exclusive'):
                day = r[key]
                if START <= day < END:
                    prior_affs = self.aff(r['person_id'], previous(day))
                    next_affs = self.aff(r['person_id'], day)
                    adjacent_personal_change = prior_affs and next_affs and {(a['state'], a['party_id']) for a in prior_affs} != {(a['state'], a['party_id']) for a in next_affs}
                    if self.active(r['person_id'], day) or self.active(r['person_id'], previous(day)) or adjacent_personal_change:
                        boundaries[day].add(r['person_id'])
        for organization in self.data['organizational_events']:
            day = organization['effective_date']
            if organization['predecessor_party_id'] != organization['successor_party_id']:
                for person in self.service_by_person:
                    if self.active(person, day) and any(a['party_id'] == organization['predecessor_party_id'] for a in self.aff(person, previous(day))):
                        boundaries[day].add(person)
        for day in sorted(boundaries):
            for pid in sorted(boundaries[day], key=lambda p: self.people[p]):
                before_day = previous(day)
                sb, sa = self.active(pid, before_day), self.active(pid, day)
                ab, aa = self.aff(pid, before_day), self.aff(pid, day)
                ended = [r for r in sb if r['end_exclusive'] == day]
                started = [r for r in sa if r['start_inclusive'] == day]
                old_state = self.aff_state(ab, before_day, sb)
                new_state = self.aff_state(aa, day, sa)
                types, notes = [], []
                outside_personal_change = not sb and not sa and ab and aa and {(a['state'], a['party_id']) for a in ab} != {(a['state'], a['party_id']) for a in aa}
                context_services = []
                if outside_personal_change:
                    old_state = self.aff_state(ab, before_day, True)
                    new_state = self.aff_state(aa, day, True)
                    types.append('personal_affiliation_change_outside_qualifying_service')
                    notes.append('Personal affiliation changes while the person is outside qualifying service; neither state contributes to the cabinet union on this date.')
                    prior_services = [r for r in self.service_by_person[pid] if r['end_exclusive'] <= day]
                    next_services = [r for r in self.service_by_person[pid] if r['start_inclusive'] > day]
                    if prior_services:
                        last = max(r['end_exclusive'] for r in prior_services)
                        context_services += [r for r in prior_services if r['end_exclusive'] == last]
                        notes.append('Preceding qualifying service ended exclusively ' + last + '.')
                    if next_services:
                        next_day = min(r['start_inclusive'] for r in next_services)
                        upcoming = [r for r in next_services if r['start_inclusive'] == next_day]
                        context_services += upcoming
                        notes.append('Next recorded qualifying service begins ' + next_day + ' in ' + ', '.join(r['office_name'] for r in upcoming) + '.')
                # A clipped spell is not evidence of an affiliation joining/leaving date.
                if started and not sb:
                    types.append('opening_officeholder' if day == START else 'qualifying_service_begins')
                elif ended and not sa:
                    types.append('administration_service_ends' if any(r['end_exclusive'] == day for r in self.data['administrations']) else 'qualifying_service_ends')
                elif started or ended:
                    types.append('officeholder_service_transition')
                if sb and sa and old_state != new_state:
                    organization = [r for r in self.data['organizational_events'] if r['effective_date'] == day and any(a['party_id'] == r['predecessor_party_id'] for a in ab)]
                    if organization:
                        types.append('organizational_affiliation_effect')
                    elif 'UNKNOWN' in (old_state, new_state):
                        types.append('unresolved_affiliation_state_boundary')
                    elif 'UNAFFILIATED' in (old_state, new_state):
                        types.append('transition_to_or_from_unaffiliated')
                    else:
                        types.append('personal_party_switch')
                if not types:
                    continue
                for s in ended:
                    successors = [x for x in self.services if x['office_id'] == s['office_id'] and x['start_inclusive'] == day and x['person_id'] != pid]
                    if successors:
                        notes.append('Office succession: ' + s['person_name'] + ' → ' + ', '.join(x['person_name'] for x in successors) + ' (' + s['office_name'] + ').')
                for s in started:
                    predecessors = [x for x in self.services if x['office_id'] == s['office_id'] and x['end_exclusive'] == day and x['person_id'] != pid]
                    if predecessors:
                        notes.append('Preceded by ' + ', '.join(x['person_name'] for x in predecessors) + ' in ' + s['office_name'] + '.')
                if any('vacancy' in r['capacity'] for r in started + ended):
                    types.append('vacancy_officeholder_transition')
                if day == START:
                    notes.append('Observation opening; the clipped start does not claim that all original appointments or affiliations occurred on this date.')
                if day in {r['start_inclusive'] for r in self.data['administrations']} and day != START:
                    notes.append('Administration boundary; compare complete outgoing and incoming cabinets, including continuing persons.')
                row = self.base('person-' + day + '-' + stable_id(pid), day, 'individual', joined(types), ' '.join(notes), self.people[pid], joined(r['office_name'] for r in sb + sa))
                records = list({r['service_id']: r for r in sb + sa + context_services}.values()) + list({r['affiliation_id']: r for r in ab + aa}.values())
                row.update(person_ids=pid, office_ids=joined(r['office_id'] for r in sb + sa), service_ids=joined(r['service_id'] for r in sb + sa + context_services), affiliation_ids=joined(r['affiliation_id'] for r in ab + aa), previous_service_state=joined(r['office_name'] + ' (' + r['capacity'] + ')' for r in sb) or 'NO_QUALIFYING_SERVICE', new_service_state=joined(r['office_name'] + ' (' + r['capacity'] + ')' for r in sa) or 'NO_QUALIFYING_SERVICE', previous_affiliation=old_state, new_affiliation=new_state)
                # Date status describes the actual boundary records, not unrelated dates in a continuing spell.
                row['date_status'] = joined(r['date_status'] for r in started + ended + [r for r in ab + aa if r['start_inclusive'] == day or r['end_exclusive'] == day])
                if 'organizational_affiliation_effect' in types:
                    row['date_status'] = 'organizational_event_effective_date'
                cs = self.matching_constraints({pid}, day)
                residuals = [r for r in self.residual.values() if r['person_id'] == pid and r['start_inclusive'] <= day <= r['end_exclusive']]
                assumptions = [r for r in self.assumption.values() if r['person_id'] == pid and r['start_inclusive'] <= day <= r['end_exclusive']]
                row['uncertainty_ids'] = joined(r['uncertainty_id'] for r in cs + residuals)
                row['primary_assumption_ids'] = joined(r['assumption_id'] for r in assumptions)
                flags = []
                if cs:
                    flags.append('bounded_date')
                    row['date_end_or_bound'] = joined(r['earliest_effective_date'] + '..' + r['latest_effective_date'] for r in cs)
                if any(r['state'] == 'UNKNOWN' for r in ab + aa):
                    flags.append('UNKNOWN')
                if assumptions:
                    flags.append('PROVISIONAL_MODEL_ASSUMPTION')
                flags += [r['aggregate_effect'] for r in residuals]
                row['uncertainty_status'] = joined(flags) or 'no_linked_residual_uncertainty'
                before_contribution = self.contribution(ab, before_day, sb)
                after_contribution = self.contribution(aa, day, sa)
                tr = self.transition.get(day)
                if tr:
                    entering = split(tr['entering_party_ids']) & (after_contribution - before_contribution)
                    leaving = split(tr['leaving_party_ids']) & (before_contribution - after_contribution)
                    row['party_entering'], row['party_leaving'] = joined(entering), joined(leaving)
                    row['changes_aggregate_party_set'] = str(bool(entering or leaving)).lower()
                    row['relationship_to_aggregate'] = 'changed_party_witness' if entering or leaving else 'coincident_event_without_changed_party_contribution'
                elif day == START:
                    row['relationship_to_aggregate'] = 'opening_observation_no_pre_window_comparison'
                else:
                    changed = before_contribution ^ after_contribution
                    if changed:
                        independent = sorted({self.people[w['person_id']] + ' (' + self.label(w['party_id'], day) + ')' for w in self.witnesses if w['person_id'] != pid and w['party_id'] in changed and w['start_inclusive'] <= day < w['end_exclusive']})
                        row['notes'] += ' Party representation continues through other witnesses: ' + ', '.join(independent) + '.'
                self.enrich(row, records + cs + residuals + assumptions)

    def structural(self):
        groups = defaultdict(list)
        for r in self.data['organizational_events']:
            groups[(r['effective_date'], r['event_type'], r['successor_party_id'])].append(r)
        for (day, kind, successor), records in sorted(groups.items()):
            predecessors = joined(r['predecessor_party_id'] for r in records)
            old = joined(self.label(r['predecessor_party_id'], previous(day)) for r in records)
            new = self.label(successor, day)
            notes = f'Organizational record: {old} → {new}; stable identities {predecessors} → {successor}. '
            if kind == 'rename':
                notes += 'Stable party identity is unchanged. ' + ('Displayed acronym is also unchanged.' if old == new else 'Dated display label changes.')
            else:
                notes += 'The builder transfers only continuing predecessor affiliations; former members are not transferred.'
            row = self.base('organization-' + day + '-' + stable_id(kind, predecessors, successor), day, 'organization', 'party_' + kind, notes)
            row.update(previous_affiliation=old, new_affiliation=new, date_status='organizational_event_effective_date')
            tr = self.transition.get(day)
            if tr:
                row['party_entering'], row['party_leaving'] = tr['entering_party_ids'], tr['leaving_party_ids']
                row['changes_aggregate_party_set'] = str(bool(row['party_entering'] or row['party_leaving'])).lower()
                row['relationship_to_aggregate'] = 'organizational_membership_effect' if row['changes_aggregate_party_set'] == 'true' else 'historical_display_label_change'
            self.enrich(row, records)
        for office in self.data['offices']:
            admin = next(r for r in self.data['administrations'] if r['administration_id'] == office['administration_id'])
            for key, kind in [('start_inclusive', 'qualifying_office_scope_begins'), ('end_exclusive', 'qualifying_office_scope_ends')]:
                day = office[key]
                if day in {admin['start_inclusive'], admin['end_exclusive']} or not START <= day < END:
                    continue
                row = self.base('office-' + day + '-' + stable_id(office['office_id'], kind), day, 'office_scope', kind, 'Dated qualifying-office scope boundary; creation, abolition, or reorganization is not inferred beyond the stored scope basis: ' + office['scope_basis'], office=office['office_name'])
                row.update(office_ids=office['office_id'], date_status=office['date_status'])
                self.enrich(row, [office])
        for gap in self.data['office_coverage_gaps']:
            for key, kind in [('start_inclusive', 'explicit_vacancy_begins'), ('end_exclusive', 'explicit_vacancy_ends')]:
                day = gap[key]
                if not START <= day < END:
                    continue
                row = self.base('vacancy-' + day + '-' + gap['gap_id'] + '-' + kind, day, 'office_scope', kind, gap['rationale'], office=self.office[gap['office_id']]['office_name'])
                row.update(office_ids=gap['office_id'], date_end_or_bound=gap['end_exclusive'], previous_service_state=gap['state'] if key == 'end_exclusive' else '', new_service_state=gap['state'] if key == 'start_inclusive' else '', date_status='adjudicated_vacancy_interval')
                self.enrich(row, [gap])

    def uncertainty_events(self):
        for uid, record in self.residual.items():
            for key, action in [('start_inclusive', 'begins'), ('end_exclusive', 'ends')]:
                day = record[key]
                if not START <= day < END:
                    continue
                row = self.base('uncertainty-' + day + '-' + stable_id(uid, action), day, 'uncertainty', 'personal_uncertainty_interval_' + action, record['evidentiary_basis'] + ' Aggregate effect: ' + record['aggregate_effect'] + '. Alternatives: ' + record['alternatives'] + '. Interval boundaries describe the retained uncertainty scope; they are not additional observed affiliation events.', self.people[record['person_id']], self.office[self.service[record['service_id']]['office_id']]['office_name'])
                row.update(person_ids=record['person_id'], service_ids=record['service_id'], affiliation_ids=record['affiliation_id'], uncertainty_ids=uid, date_end_or_bound=record['end_exclusive'], date_status='retained_uncertainty_scope_boundary', uncertainty_status=record['primary_state'] + ';' + record['aggregate_effect'], previous_affiliation=record['primary_state'] + (':' + record['primary_party_id'] if record['primary_party_id'] else ''))
                self.enrich(row, [record, self.affiliation[record['affiliation_id']], self.service[record['service_id']]])
        for uid, record in self.constraint.items():
            persons = {record.get('person_id'), record.get('outgoing_person_id'), record.get('incoming_person_id')} - {None, ''}
            for key, action in [('earliest_effective_date', 'begins'), ('latest_effective_date', 'ends')]:
                day = record[key]
                row = self.base('bounded-' + day + '-' + stable_id(uid, action), day, 'uncertainty', 'bounded_date_window_' + action, record['constraints'] + ' Primary effective date: ' + record['baseline_effective_date'] + '. Admissible candidate dates: ' + record['candidate_dates'] + '.', joined(self.people[p] for p in persons), self.office.get(record.get('office_id', ''), {}).get('office_name', ''))
                row.update(person_ids=joined(persons), uncertainty_ids=uid, date_end_or_bound=record['latest_effective_date'], date_status='bounded_date_window', uncertainty_status='bounded_date', service_ids=record.get('linked_service_ids', ''), affiliation_ids=record.get('linked_affiliation_ids', ''))
                self.enrich(row, [record])
        for aid, record in self.assumption.items():
            for key, action in [('start_inclusive', 'begins'), ('end_exclusive', 'ends')]:
                day = record[key]
                if not START <= day < END:
                    continue
                row = self.base('assumption-' + day + '-' + aid + '-' + action, day, 'primary_assumption', 'primary_provisional_assumption_' + action, record['rationale'] + ' Historical affiliation remains UNKNOWN; the primary model assumes no additional party contribution only on [' + record['start_inclusive'] + ', ' + record['end_exclusive'] + ').', record['person_name'])
                row.update(person_ids=record['person_id'], affiliation_ids=record['affiliation_id'], service_ids=record['service_ids'], primary_assumption_ids=aid, date_end_or_bound=record['end_exclusive'], date_status='documented_assumption_scope_boundary', uncertainty_status='UNKNOWN;PROVISIONAL_MODEL_ASSUMPTION', previous_affiliation='UNKNOWN', new_affiliation='UNKNOWN')
                self.enrich(row, [record])

    def aggregates(self):
        for admin in sorted(self.data['administrations'], key=lambda r: r['start_inclusive']):
            day = admin['start_inclusive']
            active = [r for r in self.services if r['start_inclusive'] <= day < r['end_exclusive']]
            affs = [a for r in active for a in self.aff(r['person_id'], day)]
            row = self.base('opening-' + admin['administration_id'], day, 'opening', 'administration_opening_state', 'Opening cabinet-party set for this administration. The separate aggregate boundary compares administrations when a preceding observation exists.')
            row.update(date_status='administration_boundary', service_ids=joined(r['service_id'] for r in active), affiliation_ids=joined(a['affiliation_id'] for a in affs))
            self.enrich(row, active + affs)
        for transition in self.generated['transitions']:
            day, tid = transition['date'], transition['transition_id']
            before_day = previous(day)
            changed = split(transition['entering_party_ids']) | split(transition['leaving_party_ids'])
            ws = [w for w in self.witnesses if w['party_id'] in changed and (w['start_inclusive'] <= day < w['end_exclusive'] or w['start_inclusive'] <= before_day < w['end_exclusive'])]
            records = [self.service[w['service_id']] for w in ws] + [self.affiliation[w['affiliation_id']] for w in ws]
            related = [r for r in self.rows if r['event_date'] == day and r['event_layer'] in {'individual', 'organization', 'office_scope'}]
            causes = [r for r in related if r['relationship_to_aggregate'] in {'changed_party_witness', 'organizational_membership_effect', 'historical_display_label_change'}]
            persons = split(joined(r['person_ids'] for r in causes))
            cs = self.matching_constraints(persons, day)
            assumptions = [self.assumption[aid] for aid in split(transition['primary_assumption_ids'])]
            residuals = [r for r in self.residual.values() if r['person_id'] in persons and r['start_inclusive'] <= day <= r['end_exclusive']]
            types = [transition['transition_type']]
            if transition['entering_party_ids']:
                types.append('aggregate_party_entry')
            if transition['leaving_party_ids']:
                types.append('aggregate_party_exit')
            row = self.base(tid, day, 'aggregate', joined(types), 'Generated historical transition, with complete before/after union and changed-party witnesses. Supporting service/affiliation closure supplements the raw transition evidence list; same-date events are not automatically causes.', joined(r['person'] for r in causes), joined(r['office'] for r in causes))
            row.update(person_ids=joined(persons), party_entering=transition['entering_party_ids'], party_leaving=transition['leaving_party_ids'], changes_aggregate_party_set=str(bool(changed)).lower(), relationship_to_aggregate=transition['comparison_status'], cabinet_labels_before=transition['before_labels'], cabinet_labels_after=transition['after_labels'], service_ids=joined(w['service_id'] for w in ws), affiliation_ids=joined(w['affiliation_id'] for w in ws), related_event_ids=joined(r['event_id'] for r in related), primary_assumption_ids=transition['primary_assumption_ids'], uncertainty_ids=joined(r['uncertainty_id'] for r in cs + residuals), date_status=joined(r['date_status'] for r in causes) or transition['transition_type'])
            flags = []
            if cs:
                flags.append('bounded_date')
                row['date_end_or_bound'] = joined(r['earliest_effective_date'] + '..' + r['latest_effective_date'] for r in cs)
            if assumptions:
                flags.append('PROVISIONAL_MODEL_ASSUMPTION')
            if any(r['primary_state'] == 'UNKNOWN' for r in residuals):
                flags.append('UNKNOWN')
            flags += [r['aggregate_effect'] for r in residuals]
            row['uncertainty_status'] = joined(flags) or 'no_linked_residual_uncertainty'
            self.enrich(row, [transition] + records + cs + residuals + assumptions)

    def known_issues(self):
        self.issue('organization-2023-02-14', 'Organizational evidence target differs from coded event', 'PROS;SOLIDARIEDADE;AFF-050', 'The coded PROS→SOLIDARIEDADE incorporation on 2023-02-14 cites AFF-050, whose retained assertion and locator describe PHS incorporation into Podemos on 2019-09-19. Retain the current organizational coding; neither predecessor is represented at this cabinet boundary, so the primary chronology is unchanged.', 'data/normalized/organizational_events.csv;data/normalized/evidence.csv')
        self.issue('mdic-2018-succession;environment-2018-succession', 'General bounded-date rule and specific neutral succession baselines differ', 'R07;R08;service-eabeba688ae4;service-3e4783281846;service-michel_temer-0-38;service-c8d1b1f769cc', 'CODEBOOK says bounded changes use the latest admissible date, but the MDIC constraint selects 2018-01-04 within January 3–5 and Environment selects 2018-04-06 within April 6–7. Current service rows follow those explicit constraint baselines. Both successions preserve the party union; the audit preserves the specific baselines without adjudicating the general-rule discrepancy.', 'CODEBOOK.md;data/normalized/service_sensitivity_constraints.csv;data/normalized/services.csv;data/normalized/decisions.csv')
        for eid in sorted(self.sources_used):
            for snapshot in self.snapshots[eid]:
                path = ROOT / 'data/source' / snapshot['snapshot_path']
                if not path.exists():
                    self.issue(eid, 'Missing expected retained snapshot', eid, 'The evidence_snapshot_links entry does not resolve locally.', str(path.relative_to(ROOT)))
                elif path.is_file():
                    with path.open('rb') as handle:
                        if handle.read(60).startswith(b'version https://git-lfs.github.com/spec/v1'):
                            self.issue(eid, 'Retained path is an LFS pointer', eid, 'The locator exists but contains an LFS pointer rather than the described source content.', str(path.relative_to(ROOT)))

    def generate(self, output):
        self.personals()
        self.structural()
        self.uncertainty_events()
        self.aggregates()
        self.rows.sort(key=lambda r: (r['event_date'], r['event_layer'], r['person'], r['event_id']))
        self.known_issues()
        output.mkdir(parents=True, exist_ok=True)
        # The machine-readable event view is written before any prose document.
        write_csv(output / 'cabinet_history_events.csv', self.rows)
        write_csv(output / 'issues.tsv', self.issues, ['event', 'issue', 'affected_ids', 'why_suspicious', 'source_paths_to_review'], '\t')
        catalog = {eid: dict(self.evidence[eid], snapshots=[dict(s, local_path='data/source/' + s['snapshot_path']) for s in self.snapshots[eid]], assertion_ledger='data/normalized/evidence.csv') for eid in sorted(self.sources_used)}
        (output / 'source_catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        summary = dict(event_rows=len(self.rows), aggregate_transitions=len(self.generated['transitions']), aggregate_identity_set_changes=sum(bool(r['entering_party_ids'] or r['leaving_party_ids']) for r in self.generated['transitions']), aggregate_transition_types=dict(Counter(r['transition_type'] for r in self.generated['transitions'])), individual_events=sum(r['event_layer'] == 'individual' for r in self.rows), events_with_bounded_provisional_unknown=sum(any(flag in r['uncertainty_status'] for flag in ('bounded_date', 'PROVISIONAL_MODEL_ASSUMPTION', 'UNKNOWN')) for r in self.rows), individual_events_with_bounded_provisional_unknown=sum(r['event_layer'] == 'individual' and any(flag in r['uncertainty_status'] for flag in ('bounded_date', 'PROVISIONAL_MODEL_ASSUMPTION', 'UNKNOWN')) for r in self.rows), evidence_records=len(self.sources_used), decision_records=len(self.decisions_used), evidence_without_dedicated_snapshot=sum(not self.snapshots[eid] for eid in self.sources_used), primary_assumption_records=len(self.assumption), residual_uncertainty_records=len(self.residual), bounded_date_constraints=len(self.constraint), issue_count=len(self.issues), historical_input=str(self.historical.relative_to(ROOT)), layer_counts=dict(Counter(r['event_layer'] for r in self.rows)))
        (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(summary, indent=2), flush=True)
        return summary

    def citation(self, row):
        # Generic continuity/population decision evidence is discoverable through its
        # catalog once, rather than repeated as if each source established this event.
        return 'Evidence: ' + refs('evidence', split(row['direct_evidence_ids'])) + '. Decisions: ' + refs('decision', split(row['decision_ids'])) + '.'

    def event_line(self, row):
        state = ''
        if row['event_layer'] == 'individual':
            state = f"{row['previous_affiliation']} → {row['new_affiliation']}; {row['previous_service_state']} → {row['new_service_state']}. "
        return state + row['notes']

    def audit(self, target, summary):
        lines = ['# Cabinet history and evidence audit', '', 'This reference documents the **current frozen coding** from 1 January 2015 through 19 March 2026 (exclusive cutoff: 20 March). It reads accepted normalized records and the deterministic historical chronology; it does not reproduce research investigations or revise their decisions. The companion [narrative](CABINET_HISTORY_NARRATIVE.md) explains the consequential episodes in prose.', '', '**Navigate:** [Dilma II](#audit-dilma_2) · [Temer](#audit-temer) · [Bolsonaro](#audit-bolsonaro) · [Lula III](#audit-lula_3) · [Uncertainty](#audit-uncertainty) · [Issues](#audit-issues) · [Evidence](#audit-evidence) · [Decisions](#audit-decisions).', '', '## Reading the audit', '', 'Service and formal personal affiliation are separate. The cabinet set is the union of represented stable party identities among qualifying officeholders, displayed with the label in effect on each date. Intervals are half-open and dates follow the project’s daily closing-state convention. `UNKNOWN` is never a synonym for `UNAFFILIATED`. `primary_adjudicated` and `primary_provisional` are the builder’s actual composition statuses; a provisional set assumes no additional party contribution on explicitly documented dates while the historical affiliation remains UNKNOWN.', '', 'A period can contain both adjudicated and provisional days. Entries below use the daily status at the boundary, with assumptions linked separately. `adjudicated_source_boundary`, `adjudicated_continuity`, and similar stored statuses are shown verbatim; they must not be read as a blanket claim of exact registry dates. A bounded-date entry gives the inclusive earliest/latest admissible event dates and the selected primary date. The uncertainty interval itself ends exclusively at the latest date, when the after-state is fixed. The cutoff is observation clipping, never a dismissal. A stored date status can characterize an entire service or affiliation record; the linked constraints, rather than that label alone, define its exact bounded window.', '', 'The aggregate entries are exhaustive for the existing historical `transitions.csv`: **' + str(summary['aggregate_transitions']) + ' boundaries**, comprising ' + str(summary['aggregate_identity_set_changes']) + ' identity-set changes (including three administration boundaries) and one displayed-label change. The subordinate individual register contains **' + str(summary['individual_events']) + ' person/date events**. These combine coincident service and affiliation records without treating every clipped affiliation spell as a new joining or leaving event. A single party-set transition may have several changed-party witnesses. A coincident personnel event is not necessarily a cause.', '', '### Event typology', '', '| Layer | Event types and interpretation |', '|---|---|', '| Individual | Qualifying service begins/ends; continuing person changes office/service record; vacancy officeholder transition; actual personal party switch or transition to/from UNAFFILIATED; unresolved affiliation boundary; adjacent personal affiliation changes outside service (with no party contribution). Opening/admin endpoints are identified separately. Service entry/exit does not itself date personal affiliation entry/exit. |', '| Organization | Dated rename, merger, or incorporation. A rename preserves identity; only continuing predecessor affiliations transfer in a merger/incorporation. |', '| Office scope | Dated qualifying-office scope begins/ends; explicit vacancy begins/ends. Legal creation/abolition/reorganization is asserted only to the extent of the stored scope evidence. |', '| Uncertainty | Start/end of a residual personal uncertainty interval or bounded date window; these are scope markers, not additional observed historical acts. |', '| Primary assumption | Start/end of a documented PROVISIONAL_MODEL_ASSUMPTION, with historical UNKNOWN preserved. |', '| Aggregate | Party entry/exit, administration boundary, or historical displayed-label change in the complete union. Four administration opening states are separately retained. |', '', 'Each evidence link opens a catalog record with a recognizable source description, stored assertion, access status, original locator and retained local paths where available. The catalog distinguishes a retained assertion ledger from an archived original. Decisions expose their stored rationale and alternatives. Broad continuity/scope decisions link their wider evidence once; that evidence is not automatically independent support for every individual claim. Machine detail is generated at `build/history_audit/cabinet_history_events.csv`, with source descriptions, source/decision closure and uncertainty IDs.', '']
        for admin in sorted(self.data['administrations'], key=lambda r: r['start_inclusive']):
            aid = admin['administration_id']
            lines += ['<a id="audit-' + aid + '"></a>', '## ' + ADMINS[aid], '']
            opening = next(r for r in self.rows if r['event_id'] == 'opening-' + aid)
            lines += [f'<a id="{anchor("event", opening["event_id"])}"></a>', f"**Opening, {admin['start_inclusive']}:** {opening['cabinet_labels_after'].replace(';', ', ')}. Daily coding status: `{opening['composition_status']}`. Opening roster and evidence are in the individual register and machine event `{opening['event_id']}`.", '']
            for row in [r for r in self.rows if r['administration_id'] == aid and r['event_layer'] == 'aggregate']:
                causes = [r for r in self.rows if r['event_id'] in split(row['related_event_ids']) and r['relationship_to_aggregate'] in {'changed_party_witness', 'organizational_membership_effect', 'historical_display_label_change'}]
                lines += [f'<a id="{anchor("event", row["event_id"])}"></a>', f"### {row['event_date']}", '', '**Change:** ' + ('Historical displayed label changes; stable membership identities do not change.' if 'historical_label_change' in row['event_type'] else ('Administration changes. ' if 'administration_boundary' in row['event_type'] else '') + 'Enters: ' + (', '.join(self.label(p, row['event_date']) + (' [identity ' + p + ']' if self.label(p, row['event_date']) != p else '') for p in sorted(split(row['party_entering']))) or 'none') + '; leaves: ' + (', '.join(self.label(p, previous(row['event_date'])) + (' [identity ' + p + ']' if self.label(p, previous(row['event_date'])) != p else '') for p in sorted(split(row['party_leaving']))) or 'none') + '.'), '', '**Before:** ' + row['cabinet_labels_before'].replace(';', ', ') + '.\n\n**After:** ' + row['cabinet_labels_after'].replace(';', ', ') + '.', '']
                if causes:
                    lines += ['**Mechanism and changed-party witnesses:**', '']
                    for cause in causes:
                        label = cause['person'] or 'Party organization'
                        desc = cause['previous_affiliation'] + ' → ' + cause['new_affiliation'] if cause['previous_affiliation'] or cause['new_affiliation'] else cause['notes']
                        service = ''
                        if cause['event_layer'] == 'individual':
                            service = ' Service: ' + cause['previous_service_state'] + ' → ' + cause['new_service_state'] + '.'
                            succession_notes = [note for note in cause['notes'].split('. ') if note.startswith(('Office succession:', 'Preceded by '))]
                            if succession_notes:
                                service += ' ' + '. '.join(succession_notes).rstrip('.') + '.'
                        lines.append('- ' + label + ': ' + desc + '.' + service + ' ' + ref('event', cause['event_id']))
                    lines.append('')
                lines += [f"**Date status:** `{row['date_status']}`." + (' **Linked bounded event(s):** ' + '; '.join(ref('uncertainty', uid) + ': ' + self.constraint[uid]['earliest_effective_date'] + ' through ' + self.constraint[uid]['latest_effective_date'] + ' inclusive; selected primary boundary ' + self.constraint[uid]['baseline_effective_date'] for uid in sorted(split(row['uncertainty_ids']) & self.constraint.keys())) + '. The constraint specifies which service or affiliation boundary moves; a linked window does not make every event in that window the uncertain handoff.' if row['date_end_or_bound'] else ' The heading is the current coded boundary under the interval convention.'), '', f"**Composition:** `{row['composition_status_before']}` → `{row['composition_status']}`; comparison `{row['relationship_to_aggregate']}`. **Retained uncertainty:** `{row['uncertainty_status']}`.", '']
                if row['primary_assumption_ids']:
                    lines += ['**Primary assumptions:** ' + refs('assumption', split(row['primary_assumption_ids'])) + '. Historical UNKNOWN is preserved; no additional party is assumed only for primary coverage.', '']
                if row['uncertainty_ids']:
                    lines += ['**Bounds and alternatives:** ' + refs('uncertainty', split(row['uncertainty_ids'])) + '.', '']
                focus = sorted({eid for cause in causes for eid in split(cause['direct_evidence_ids'])}, key=lambda eid: (not (eid.startswith('C') or eid.startswith('V5') or eid.startswith('AFF') or eid.startswith('BOL')), eid))
                if focus:
                    lines += ['**Selected stored assertions (including any retained conflicting accounts):** ' + '; '.join(ref('evidence', eid) + ' — ' + self.evidence[eid]['publisher'] + ': ' + self.evidence[eid]['asserted_fact'] for eid in focus[:4]) + '.', '']
                cause_decisions = {did for cause in causes for did in split(cause['decision_ids'])} - {'PERSON-CONTINUITY-REVIEW', 'POPULATION-REVIEW', 'OFFICE-ADJUDICATION'}
                ordered_decisions = sorted(cause_decisions, key=lambda did: (0 if did.startswith(('V5', 'ONYX')) else 1 if did.startswith('C') else 2, did))
                for did in ordered_decisions[:2]:
                    rationale = self.decision[did]['rationale']
                    highlight = rationale if len(rationale) <= 650 else 'Disposition: `' + self.decision[did]['disposition'] + '`.'
                    lines += ['**Decision orientation:** ' + ref('decision', did) + ' — ' + highlight + ' The linked record preserves the full rationale and alternatives; current normalized records determine the coded state.', '']
                lines += [self.citation(row), '']
                if row['event_date'] in {'2025-12-19', '2025-12-23'}:
                    lines += ['**Inspection note:** R27 retains an earlier December 23 endpoint description. Current service records and C073 code Sabino’s final departure on December 19 and Ana Carla’s intervening service; this is documented precedence of the later service-specific decision over the earlier summary, not a newly unresolved affiliation case.', '']
            lines += ['### Individual personnel and affiliation register', '', 'Rows below retain all grouped individual events, including those already cited above. “Changed-party witness” identifies a contribution to that day’s aggregate difference; “coincident” means the cabinet changes for another recorded reason. When no aggregate transition occurs, the individual movement leaves the union unchanged. Service entry/exit does not itself date personal affiliation entry/exit. An explicitly labeled personal change outside qualifying service shows the actual personal states with no cabinet contribution.', '', '| Date / event | Person and mechanism | Service and affiliation / retained notes | Cabinet consequence and status | Evidence and decisions |', '|---|---|---|---|---|']
            for row in [r for r in self.rows if r['administration_id'] == aid and r['event_layer'] == 'individual']:
                consequence = row['relationship_to_aggregate'].replace('_', ' ')
                if row['aggregate_transition_id']:
                    consequence += ': ' + ref('event', row['aggregate_transition_id'])
                uncertainty = refs('uncertainty', split(row['uncertainty_ids'])) if row['uncertainty_ids'] else ''
                lines.append('| <a id="' + anchor('event', row['event_id']) + '"></a>' + row['event_date'] + ' | ' + clean(row['person']) + '; ' + clean(row['event_type'].replace('_', ' ')) + ' | ' + clean(self.event_line(row)) + ' | ' + clean(consequence) + '. Date: ' + clean(row['date_status']) + '. Uncertainty: ' + clean(row['uncertainty_status']) + '. ' + uncertainty + ' | ' + self.citation(row) + ' |')
            lines += ['', '### Organization, office scope and uncertainty markers', '', 'The following register preserves organizational events without cabinet consequences, office/vacancy changes, and the exact starts/ends of uncertainty or assumption scopes. These scope markers are not additional ministerial appointments or new personal affiliations.', '', '| Date / type | Person or office | Interpretation | Status and evidence |', '|---|---|---|---|']
            for row in [r for r in self.rows if r['administration_id'] == aid and r['event_layer'] not in {'individual', 'aggregate', 'opening'}]:
                links = refs('uncertainty', split(row['uncertainty_ids'])) if row['uncertainty_ids'] else ''
                links += ' ' + (refs('assumption', split(row['primary_assumption_ids'])) if row['primary_assumption_ids'] else '')
                lines.append('| <a id="' + anchor('event', row['event_id']) + '"></a>' + row['event_date'] + '; ' + row['event_type'].replace('_', ' ') + ' | ' + clean(row['person'] or row['office'] or 'Party organization') + ' | ' + clean(row['notes']) + ' | ' + clean(row['uncertainty_status'] or row['date_status']) + '. ' + links + ' ' + self.citation(row) + ' |')
            lines.append('')
        lines += ['<a id="audit-uncertainty"></a>', '## Retained uncertainty and assumption catalog', '', 'These descriptions reproduce the accepted scope and alternatives. `composition_neutral` means supported alternatives leave the union unchanged; it does not establish the person’s affiliation. `completion_blocker` remains an unresolved historical dependency even when a primary assumption supplies export coverage.', '']
        for uid, r in sorted(self.constraint.items()):
            effect = next(x for x in self.generated['date_sensitivity'] if x['uncertainty_id'] == uid)
            lines += [f'<a id="{anchor("uncertainty", uid)}"></a>', '### ' + uid, '', '**Bounded event:** ' + r['earliest_effective_date'] + ' through ' + r['latest_effective_date'] + ' inclusive; primary ' + r['baseline_effective_date'] + '. Aggregate effect: `' + effect['aggregate_effect'] + '`; potentially set-changing days ' + effect['potentially_set_changing_days'] + '; composition-neutral days ' + effect['composition_neutral_days'] + '.', '', r['constraints'], '', 'Evidence: ' + refs('evidence', split(r['evidence_ids'])) + '.', '']
        for uid, r in sorted(self.residual.items()):
            lines += [f'<a id="{anchor("uncertainty", uid)}"></a>', '### ' + r['person_name'] + ': ' + r['start_inclusive'] + '–' + r['end_exclusive'] + ' exclusive', '', f"**Record:** `{uid}`. **Primary personal state:** `{r['primary_state']}`" + (' (' + r['primary_party_id'] + ')' if r['primary_party_id'] else '') + '. **Alternatives:** `' + r['alternatives'] + '`. **Scope:** `' + r['alternative_scope'] + '`. **Aggregate effect:** `' + r['aggregate_effect'] + '`.', '', r['evidentiary_basis'], '', 'Potentially set-changing days: ' + r['potentially_set_changing_days'] + '; composition-neutral days: ' + (r['composition_neutral_days'] or 'not enumerated') + '; historical unidentified days caused: ' + r['unidentified_days_caused'] + '.', '', 'Evidence: ' + refs('evidence', split(r['evidence_ids'])) + '. Decisions: ' + refs('decision', split(r['decision_ids'])) + '.', '']
        for aid, r in sorted(self.assumption.items()):
            lines += [f'<a id="{anchor("assumption", aid)}"></a>', '### ' + aid + ': ' + r['person_name'], '', '[' + r['start_inclusive'] + ', ' + r['end_exclusive'] + '). `PROVISIONAL_MODEL_ASSUMPTION`; historical `UNKNOWN`; primary assumes **no additional party contribution**. Alternatives remain `UNBOUNDED`.', '', r['rationale'], '', 'Evidence: ' + refs('evidence', split(r['evidence_ids'])) + '. Decisions: ' + refs('decision', split(r['decision_ids'])) + '.', '']
        lines += ['<a id="audit-issues"></a>', '## Inspection issues', '', 'No scientific record was changed to address these findings. The generated machine issue register is `build/history_audit/issues.tsv`.', '', '| Event | Issue | Affected records and interpretation | Review paths |', '|---|---|---|---|']
        for issue in self.issues:
            lines.append('| ' + clean(issue['event']) + ' | ' + clean(issue['issue']) + ' | ' + clean(issue['affected_ids'] + ': ' + issue['why_suspicious']) + ' | ' + '; '.join(local_link(p) for p in issue['source_paths_to_review'].split(';')) + ' |')
        lines += ['', '<a id="audit-evidence"></a>', '## Evidence catalog', '', 'Descriptions and assertions below come from the stored evidence ledger. Source type is exposed through publisher, access status and snapshot kind because the schema has no independent source-title or source-type column. Publication and retrieval dates are distinct. An original locator is a retained reference, not a claim that the original was retrieved. Search extracts, cross-references and assertion-only records keep those limitations. The absence of a dedicated snapshot link is stated explicitly. No source passage is newly extracted or silently interpreted.', '']
        for eid in sorted(self.sources_used):
            r = self.evidence[eid]
            lines += [f'<a id="{anchor("evidence", eid)}"></a>', '### ' + eid + ' — ' + (r['publisher'] or 'Stored source assertion'), '', '**Stored assertion:** ' + r['asserted_fact'], '', '**Source/access:** `' + r['access_status'] + '`. **Publication:** ' + (r['publication_date'] or 'not recorded') + '. **Retrieval:** ' + (r['retrieval_date'] or 'not recorded') + '.', '']
            if r['rationale']:
                lines += ['**Stored evidence rationale:** ' + r['rationale'], '']
            if r['source_locator']:
                lines += ['**Original/stored locator:** `' + r['source_locator'].replace('`', '\\`') + '`.', '']
            if self.snapshots[eid]:
                lines += ['**Retained local sources:**', '']
                unique = {(s['snapshot_path'], s['source_locator'], s['snapshot_kind']) for s in self.snapshots[eid]}
                for path, locator, kind in sorted(unique):
                    lines.append('- ' + local_link('data/source/' + path) + ' — `' + kind + '`' + ('. Snapshot locator: `' + locator.replace('`', '\\`') + '`.' if locator else '.'))
                lines.append('')
            else:
                lines += ['**Retained local record:** ' + local_link('data/normalized/evidence.csv', 'evidence assertion ledger') + f' (row `{eid}`). No dedicated snapshot link is recorded; this is not presented as an archived original.', '']
        lines += ['<a id="audit-decisions"></a>', '## Decision catalog', '', 'Rationales and alternatives are reproduced from the accepted decision records. Earlier descriptions can coexist with more specific later decisions and current normalized rows; the audit flags identified interpretive conflicts without rewriting any record. No decision is described as human adjudication unless its provenance explicitly says so.', '']
        for did in sorted(self.decisions_used):
            r = self.decision[did]
            lines += [f'<a id="{anchor("decision", did)}"></a>', '### ' + did, '', '**Disposition:** `' + r['disposition'] + '`.', '', '**Stored rationale:** ' + r['rationale'], '', '**Stored alternatives:** ' + (r['alternatives'] or 'None recorded.') , '', '**Evidence:** ' + refs('evidence', split(r['evidence_ids']) & self.evidence.keys()) + '. Other stored references: ' + '; '.join(sorted(split(r['evidence_ids']) - self.evidence.keys())) + '.', '']
        lines += ['## Reproduction and scope', '', 'Run `python3 -B scripts/build_history_audit.py --historical build/stage10-final/historical` from the producer root after a current deterministic historical build exists. The script checks normalized copies semantically, writes the machine event view before this reference document, and leaves ignored outputs under `build/history_audit/`. It neither invokes research nor changes construction inputs. The narrative remains separately edited prose. `--check` checks the saved event/aggregate correspondence and citation/link references without rewriting documents. See [CODEBOOK.md](../CODEBOOK.md) and [CONTRACT.md](../CONTRACT.md) for authoritative semantics.', '']
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('\n'.join(lines), encoding='utf-8')

    def check(self, output, audit):
        import re
        rows = read(output / 'cabinet_history_events.csv')
        text = audit.read_text(encoding='utf-8')
        present_anchors = set(re.findall(r'id="([^"]+)"', text))
        aggregates = {r['event_id']: r for r in rows if r['event_layer'] == 'aggregate'}
        assert set(aggregates) == {r['transition_id'] for r in self.generated['transitions']}
        for t in self.generated['transitions']:
            r = aggregates[t['transition_id']]
            assert anchor('event', t['transition_id']) in text
            assert r['event_date'] == t['date']
            assert r['party_entering'] == t['entering_party_ids'] and r['party_leaving'] == t['leaving_party_ids']
            assert r['cabinet_set_before'] == self.period[t['from_period_id']]['party_ids']
            assert r['cabinet_set_after'] == self.period[t['to_period_id']]['party_ids']
        individuals = [r for r in rows if r['event_layer'] == 'individual']
        for service in self.services:
            for field in ('start_inclusive', 'end_exclusive'):
                day = service[field]
                if START <= day < END:
                    assert any(r['event_date'] == day and service['service_id'] in split(r['service_ids']) for r in individuals), ('missing service boundary', service['service_id'], day)
        for aggregate in aggregates.values():
            causes = [r for r in rows if r['event_date'] == aggregate['event_date'] and r['event_layer'] in {'individual', 'organization'} and r['changes_aggregate_party_set'] == 'true']
            assert {p for cause in causes for p in split(cause['party_entering'])} == split(aggregate['party_entering']), ('missing entering witness', aggregate['event_id'])
            assert {p for cause in causes for p in split(cause['party_leaving'])} == split(aggregate['party_leaving']), ('missing leaving witness', aggregate['event_id'])
        for r in rows:
            assert split(r['evidence_ids']) <= self.evidence.keys()
            assert split(r['decision_ids']) <= self.decision.keys()
            if r['event_layer'] == 'primary_assumption':
                assert r['previous_affiliation'] == r['new_affiliation'] == 'UNKNOWN'
            assert r['event_date'] < END
        for snapshot in self.data['evidence_snapshot_links']:
            assert (ROOT / 'data/source' / snapshot['snapshot_path']).exists(), snapshot['snapshot_path']
        docs = [audit, ROOT / 'docs/CABINET_HISTORY_NARRATIVE.md']
        links = 0
        for doc in docs:
            if not doc.exists():
                continue
            content = doc.read_text(encoding='utf-8')
            for kind, identifier in re.findall(r'\[([^\]]+)\]\([^)]*#((?:evidence|decision)-[^)]+)\)', content):
                target_kind, key = identifier.split('-', 1)
                valid = self.evidence if target_kind == 'evidence' else self.decision
                assert key in {item.lower() for item in valid}, (doc.name, identifier)
                assert identifier in present_anchors, (doc.name, 'missing catalog anchor', identifier)
                links += 1
            for target_path in re.findall(r'\]\(<([^>]+)>\)', content):
                from urllib.parse import unquote
                assert (doc.parent / unquote(target_path.split('#', 1)[0])).exists(), (doc.name, target_path)
        print(json.dumps(dict(validation='passed', aggregate_transitions=len(aggregates), event_rows=len(rows), evidence_decision_links_checked=links), indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historical', default='build/stage10-final/historical')
    parser.add_argument('--check', action='store_true', help='Validate saved documentation without rewriting it.')
    args = parser.parse_args()
    historical = (ROOT / args.historical).resolve()
    assert historical.is_relative_to(ROOT / 'build'), 'Historical inputs must be inside cabinet_compositions/build/'
    history = History(historical)
    output = ROOT / 'build/history_audit'
    audit = ROOT / 'docs/CABINET_HISTORY_AUDIT.md'
    if args.check:
        history.check(output, audit)
    else:
        summary = history.generate(output)
        history.audit(audit, summary)
        history.check(output, audit)


if __name__ == '__main__':
    main()
