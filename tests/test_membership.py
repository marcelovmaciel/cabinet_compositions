"""Membership invariants, accepted inputs, and finite-alternative operations."""
import csv, json, tempfile, unittest
from pathlib import Path
from fixtures import ROOT, INPUTS, SOURCE, b, sv, af, reconstruction
import export as exporter

class HistoricalTests(unittest.TestCase):
 def test_literal_pr_and_party_union(self):
  result=b.aggregate([sv(),sv(sid='s2')],[af()],'2020-01-02',[])
  self.assertEqual(result[0],{'PR'})
 def test_switch_to_represented_party_and_multiple_portfolios(self):
  result=b.aggregate([sv(),sv('q','q'),sv('q','q2')],[af(party='A'),af('q',party='A')],'2020-01-02',[])
  self.assertEqual(result[0],{'A'})
 def test_unknown_never_unaffiliated(self):
  self.assertEqual(b.aggregate([sv()],[af(state='UNKNOWN',party='')],'2020-01-02',[])[2],{'p'})
  self.assertFalse(b.aggregate([sv()],[af(state='UNAFFILIATED',party='')],'2020-01-02',[])[2])
 def test_exhaustive_unknown_masked_only_by_existing_witnesses(self):
  active=[sv(),sv('q','q')];aa=[af(party='A'),af('q','UNKNOWN','',['A','UNAFFILIATED'])]
  core,poss,unknown,_,_,masked=b.aggregate(active,aa,'2020-01-02',[])
  self.assertEqual(core,{'A'});self.assertFalse(unknown);self.assertEqual(masked,['q'])
  aa[-1]['alternatives']='[]';self.assertEqual(b.aggregate(active,aa,'2020-01-02',[])[2],{'q'})
 def test_same_day_exclusive_succession(self):
  services=[sv(end='2020-01-10'),sv('q','q',start='2020-01-10')];active=[s for s in services if s['start_inclusive']<='2020-01-10'<s['end_exclusive']]
  self.assertEqual([x['person_id'] for x in active],['q'])
 def test_witness_coverage_requires_all_days(self):
  self.assertTrue(b.coverage([('2020-01-01','2020-01-10'),('2020-01-10','2020-01-20')],'2020-01-01','2020-01-20'))
  self.assertFalse(b.coverage([('2020-01-01','2020-01-10'),('2020-01-11','2020-01-20')],'2020-01-01','2020-01-20'))
 def test_rename_identity_and_merger_date(self):
  ev=[dict(predecessor_party_id='DEM',successor_party_id='UNIAO',effective_date='2022-02-08')]
  self.assertEqual(b.organizational_identity('DEM','2022-02-07',ev),'DEM');self.assertEqual(b.organizational_identity('DEM','2022-02-08',ev),'UNIAO')
  self.assertEqual(b.organizational_identity('PR','2022-02-08',ev),'PR')
 def test_atlas_duplicate_headers_and_provenance(self):
  with open(SOURCE/'research/inherited/atlas__7010-261partidogabineteministerio.csv',encoding='utf-8-sig') as f:raw=list(csv.reader(f,delimiter=';'))
  self.assertEqual(raw[0][1],raw[0][7]);row=raw[503];self.assertEqual(row[6],'Cid Gomes');self.assertEqual(row[7],'01/01/2015');self.assertEqual(row[8],'18/03/2015');self.assertNotEqual(row[8],row[2])
  matched=next(r for r in b.read(INPUTS/'atlas_reconciliation.csv') if r['atlas_line']=='504');self.assertEqual(matched['minister_end_raw'],'18/03/2015')
 def test_documentary_nonentry_scope_and_service_interruptions(self):
  ss=b.read(INPUTS/'services.csv');deco=[s for s in ss if s['person_name']=='Carlos Decotelli'];self.assertEqual(deco[0]['included'],'false')
  onyx=[s for s in ss if s['person_name']=='Onyx Lorenzoni' and s['administration_id']=='temer'];self.assertTrue(all(s['included']=='false' for s in onyx))
  campos=[s for s in ss if s['person_name']=='Roberto Campos Neto'];self.assertEqual(campos[0]['end_exclusive'],'2021-02-25')
  coelho=[s for s in ss if s['person_name']=='Fernando Bezerra Coelho Filho'];self.assertFalse(any(s['start_inclusive']<='2016-10-10'<s['end_exclusive'] for s in coelho));self.assertTrue(any(s['start_inclusive']=='2016-10-11' for s in coelho))
 def test_documentary_affiliation_changes(self):
  pp={p['person_name']:p['person_id'] for p in b.read(INPUTS/'people.csv')};aa=b.read(INPUTS/'affiliations.csv')
  def state(n,t):return next((a['state'],a['party_id']) for a in aa if a['person_id']==pp[n] and a['start_inclusive']<=t<a['end_exclusive'])
  self.assertEqual(state('George Hilton','2016-03-19'),('PARTY','PROS'));self.assertEqual(state('Ronaldo Fonseca','2018-06-01'),('UNAFFILIATED',''));self.assertEqual(state('Celso Sabino','2025-12-09'),('UNAFFILIATED',''))
 def test_bounded_date_convention_all_admissible_dates(self):
  cs=b.read(INPUTS/'sensitivity_constraints.csv');d=next(x for x in cs if x['before_party_id']=='PP');self.assertEqual(d['earliest_effective_date'],'2020-09-04');self.assertEqual(d['baseline_effective_date'],'2020-09-19');self.assertEqual(len(d['candidate_dates'].split(';')),16)
  m=next(x for x in cs if x['before_party_id']=='PSDB');self.assertEqual(m['earliest_effective_date'],'2020-06-16');self.assertEqual(m['candidate_dates'],'2020-06-16;2020-06-17;2020-06-18')
 def test_provenance_foreign_keys(self):
  e={r['evidence_id'] for r in b.read(INPUTS/'evidence.csv')};d={r['decision_id'] for r in b.read(INPUTS/'decisions.csv')}
  for name in ('services','affiliations'):
   for r in b.read(INPUTS/(name+'.csv')):
    self.assertTrue(b.tokens(r['evidence_ids'])<=e,(name,r['evidence_ids']))
    self.assertTrue(b.tokens(r['decision_ids'])<=d,(name,r['decision_ids']))
  cases={r['decision_id'] for r in b.read(INPUTS/'decisions.csv') if r['decision_id'].startswith('R')};self.assertEqual(cases,{f'R{i:02}' for i in range(1,31)})
 def test_full_build_deterministic_and_input_reordering(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);a=reconstruction()/'historical';reordered=root/'inputs';reordered.mkdir()
   for p in (INPUTS).glob('*.csv'):
    with open(p,encoding='utf8') as f:rr=list(csv.reader(f))
    with open(reordered/p.name,'w',newline='',encoding='utf8') as f:csv.writer(f).writerows([rr[0]]+rr[:0:-1])
   q=root/'q';b.build(reordered,q)
   self.assertEqual({p.name:p.read_bytes() for p in a.iterdir()},{p.name:p.read_bytes() for p in q.iterdir()})
   m=json.loads((a/'metadata.json').read_text());self.assertEqual(m['calendar_days'],4096);self.assertEqual(m['identified_days']+m['unidentified_days'],4096)

class CompletionRegressionTests(unittest.TestCase):
 def test_a_primary_affiliation_cannot_mask_its_own_alternative(self):
  from release_outputs import alternatives_neutral
  self.assertFalse(alternatives_neutral([{'P'},set()],set()))
  self.assertTrue(alternatives_neutral([{'P'},set()],{'P'}))
 def test_nonexhaustive_alternatives_remain_unidentified(self):
  x=af('q','UNKNOWN','',[{'state':'PARTY','party_id':'A'},{'state':'UNKNOWN'}])
  self.assertEqual(b.aggregate([sv(),sv('q','q')],[af(party='A'),x],'2020-01-02',[])[2],{'q'})
 def test_self_rename_never_cycles_or_transfers_departed_person(self):
  ev=[dict(predecessor_party_id='A',successor_party_id='A',effective_date='2020-01-01',event_type='rename'),dict(predecessor_party_id='A',successor_party_id='B',effective_date='2020-01-15',event_type='merger')]
  self.assertEqual(b.organizational_identity('A','2020-01-10',ev),'A')
  self.assertEqual(b.organizational_identity('A','2020-01-20',ev),'B')
  self.assertFalse(b.aggregate([sv()],[af(state='UNAFFILIATED',party='')],'2020-01-20',ev)[0])
 def test_only_documented_vacancy_adjudications_suppress_unknown_office(self):
  gap=dict(gap_id='g',state='UNKNOWN_OCCUPANCY')
  self.assertEqual(b.aggregate([],[],'2020-01-02',[],[gap])[2],{'office:g'})
  gap['state']='VACANT_PENDING_FIRST_MINISTER'
  self.assertFalse(b.aggregate([],[],'2020-01-02',[],[gap])[2])
 def test_repaired_vacancy_designation_and_cutoff(self):
  ss=b.read(INPUTS/'services.csv')
  x=next(s for s in ss if s['service_id']=='service-C054-welington-coimbra')
  self.assertEqual((x['person_name'],x['capacity'],x['start_inclusive'],x['end_exclusive']),('Welington Coimbra (Lelo Coimbra)','vacancy_acting','2020-02-14','2020-02-18'))
  x=next(s for s in ss if s['person_name']=='Dario Durigan')
  self.assertEqual(x['included'],'false')
  x=next(s for s in ss if s['person_name']=='Fernando Haddad')
  self.assertEqual(x['end_exclusive'],'2026-03-20')
 def test_selected_sets_maximal_and_all_witnesses_covered(self):
  from validate import validate
  p=reconstruction()/'historical';result=validate(p)
  self.assertEqual(result['calendar_days'],4096)
  rr=b.read(p/'date_sensitivity.csv')
  self.assertEqual(next(x for x in rr if x['uncertainty_id']=='justice-2026-entry')['aggregate_effect'],'composition_neutral')
  self.assertEqual(next(x for x in rr if x['uncertainty_id']=='mdic-2018-succession')['aggregate_effect'],'composition_neutral')
  for e in b.read(p/'officeholder_events.csv'):self.assertLess(e['date'],'2026-03-20')

class MembershipOperations(unittest.TestCase):
    def test_independent_witness_masks_person_removal(self):
        witnesses = [dict(person_id=person, service_id=service, party_id=party,
                          start_inclusive='2020-01-01', end_exclusive='2020-01-04')
                     for person, service, party in [('changed', 'a', 'P'), ('other', 'b', 'P'),
                                                   ('changed', 'c', 'Q'), ('third', 'd', 'R')]]
        self.assertEqual(exporter.other_union(witnesses, '2020-01-02', excluded_person='changed'), {'P', 'R'})

    def test_joint_succession_replaces_both_boundary_witnesses(self):
        witnesses = [dict(person_id=person, service_id=service, party_id=party,
                          start_inclusive=start, end_exclusive=end)
                     for person, service, party, start, end in [
                         ('out', 'out-service', 'P', '2020-01-01', '2020-01-03'),
                         ('in', 'in-service', 'Q', '2020-01-03', '2020-01-06'),
                         ('other', 'other-service', 'R', '2020-01-01', '2020-01-06')]]
        constraint = dict(outgoing_state='PARTY', outgoing_party_id='P',
                          incoming_state='PARTY', incoming_party_id='Q')
        outgoing, incoming = {'service_id':'out-service'}, {'service_id':'in-service'}
        for day in ['2020-01-02', '2020-01-03']:
            actual = exporter.service_alternative(witnesses, day, constraint, '2020-01-02', outgoing, incoming, set())
            self.assertEqual(actual, {'Q', 'R'})
        self.assertEqual(exporter.service_alternative(witnesses, '2020-01-03', constraint,
                                                     '2020-01-04', outgoing, incoming, set()), {'P', 'R'})

    def test_unknown_succession_requires_existing_provisional_assumption(self):
        constraint = dict(outgoing_state='UNKNOWN', outgoing_person_id='unknown', incoming_state='UNAFFILIATED')
        with self.assertRaises(AssertionError):
            exporter.service_alternative([], '2020-01-01', constraint, '2020-01-02',
                                         {'service_id':'a'}, {'service_id':'b'}, set())
        self.assertEqual(exporter.service_alternative([], '2020-01-01', constraint, '2020-01-02',
                                                     {'service_id':'a'}, {'service_id':'b'}, {'unknown'}), set())

    def test_merger_expansion_is_union_before_compression(self):
        mapping = {(2018,'DEM'):{'DEM'}, (2018,'PSL'):{'PSL'}, (2018,'UNIAO'):{'DEM','PSL'}}
        before = exporter.translate({'DEM','PSL'}, 2018, mapping)
        after = exporter.translate({'UNIAO','DEM'}, 2018, mapping)
        self.assertEqual(before, after)
        self.assertEqual(before, 'DEM;PSL')
        rows = [dict(date=day, election_year=2018, party_set=parties)
                for day, parties in [('2022-02-07',before), ('2022-02-08',after)]]
        self.assertEqual(len(exporter.compress(rows)), 1)
        with self.assertRaises(AssertionError):
            exporter.translate({'UNMAPPED'}, 2018, mapping)

    def test_status_and_administration_boundaries_survive_membership_compression(self):
        daily = [dict(date=day, election_year=2014, party_set='P', administration=admin,
                      provisional_day=provisional) for day,admin,provisional in [
                          ('2016-05-10','a',False), ('2016-05-11','a',True),
                          ('2016-05-12','b',True), ('2016-05-13','b',False)]]
        self.assertEqual(len(exporter.compress(daily)), 1)
        coverage = exporter.compress_coverage(daily)
        self.assertEqual([(r['administration'],r['status']) for r in coverage],
                         [('a','established'),('a','provisional'),('b','provisional'),('b','established')])
        self.assertEqual([r['start_inclusive'] for r in coverage], [r['date'] for r in daily])

    def test_external_output_rejected(self):
        with self.assertRaises(ValueError):
            exporter.producer_path('/tmp/not-a-producer-release')

class TemporalMembershipTests(unittest.TestCase):
    def test_in_tenure_switch_and_post_tenure_event_are_distinct(self):
            services = [sv(end='2020-01-20')]
            before = af(party='A')
            before['end_exclusive'] = '2020-01-10'
            during = dict(af(party='B'), start_inclusive='2020-01-10', end_exclusive='2020-01-20')
            after = dict(af(party='C'), start_inclusive='2020-01-20')
            for day, expected in [('2020-01-09', {'A'}), ('2020-01-10', {'B'}),
                                  ('2020-01-19', {'B'}), ('2020-01-20', set())]:
                active = [s for s in services if s['start_inclusive'] <= day < s['end_exclusive']]
                self.assertEqual(b.aggregate(active, [before, during, after], day, [])[0], expected)
