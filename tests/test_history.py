"""Accepted historical cases, identity evidence, and bounded/unbounded uncertainty."""
import json, unittest
from pathlib import Path
from fixtures import ROOT, INPUTS, SOURCE, b, reconstruction

class OnyxMarch2022Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.services=b.read(INPUTS/'services.csv')
        cls.affs=b.read(INPUTS/'affiliations.csv')
        cls.events=b.read(INPUTS/'organizational_events.csv')

    def witnesses(self,day):
        active=[s for s in self.services if s['included']=='true' and s['start_inclusive']<=day<s['end_exclusive']]
        result=b.aggregate(active,self.affs,day,self.events)
        return {(p,s['person_name']) for p,s,a in result[3]}

    def test_accepted_membership_precedes_cabinet_departure(self):
        self.assertIn(('UNIAO','Onyx Lorenzoni'),self.witnesses('2022-03-09'))
        self.assertIn(('PL','Onyx Lorenzoni'),self.witnesses('2022-03-10'))
        self.assertIn(('PL','Onyx Lorenzoni'),self.witnesses('2022-03-30'))
        self.assertFalse(any(n=='Onyx Lorenzoni' for p,n in self.witnesses('2022-03-31')))

    def test_pontes_masks_union_until_his_own_switch(self):
        self.assertEqual({n for p,n in self.witnesses('2022-03-10') if p=='UNIAO'},{'Marcos Pontes'})
        self.assertEqual({n for p,n in self.witnesses('2022-03-26') if p=='UNIAO'},{'Marcos Pontes'})
        self.assertFalse(any(p=='UNIAO' for p,n in self.witnesses('2022-03-27')))
        self.assertEqual({p for p,n in self.witnesses('2022-03-27')},{'PL','PP','PSC'})

    def test_both_predecessors_follow_merger_but_departure_stops_route(self):
        for predecessor in ('DEM','PSL'):
            self.assertEqual(b.organizational_identity(predecessor,'2022-02-08',self.events),'UNIAO')
        self.assertEqual(b.organizational_identity('PL','2022-03-10',self.events),'PL')
        evidence={e['evidence_id'] for e in b.read(INPUTS/'evidence.csv')}
        self.assertIn('AFF-027',evidence)
        self.assertIn('ONYX-E03',evidence)


class RegistryEvidenceTests(unittest.TestCase):
 def test_homonymous_registry_record_is_not_the_officeholder(self):
  research=SOURCE/'research/followup_root'
  verified=json.loads((research/'wallace_identity_verification.json').read_text())
  selected=json.loads((research/verified['registry_path']).read_text())['matches'][0]
  homonym=json.loads((research/'tse_RJ_7043_47.json').read_text())['matches'][0]
  self.assertEqual(selected['nmEleitor'],homonym['nmEleitor'])
  self.assertNotEqual(selected['public_registry_identity_sha256'],homonym['public_registry_identity_sha256'])
  self.assertTrue(verified['official_partial_identifier_matches'])
  self.assertEqual(verified['registry_identity_sha256'],selected['public_registry_identity_sha256'])
  links=[r for r in b.read(INPUTS/'evidence_snapshot_links.csv') if r['evidence_id']=='C070']
  self.assertTrue(any(r['snapshot_path'].endswith(verified['registry_path']) for r in links))
 def test_pending_departure_preserves_conflicting_raw_fields_and_alternative(self):
  r=json.loads((SOURCE/'research/followup_bolsonaro_affiliations/tse_df_58.json').read_text())['matches'][0]
  self.assertTrue(r['dtDesfiliacao']);self.assertEqual(r['stRegistroFiliacao'],1);self.assertEqual(r['indPendencia'],1)
  a=next(a for a in b.read(INPUTS/'affiliations.csv') if 'C071' in b.tokens(a['decision_ids']))
  self.assertEqual(set(json.loads(a['alternatives'])),{r['sgPartido'],'UNAFFILIATED'})
  self.assertIn('adjudicated',a['date_status'])
 def test_documented_vacancies_interrupt_officeholding_not_affiliation(self):
  ss=b.read(INPUTS/'services.csv')
  vac=b.read(SOURCE/'research/followup_succession_justice_foreign/sabino_vacancy_successions.csv')
  titular=[r for r in ss if r['person_name']=='Celso Sabino' and r['included']=='true']
  for r in vac:
   holders=[v for v in ss if v['source_record_ids']==r['case_id'] and v['capacity']=='vacancy_acting']
   self.assertEqual(len(holders),1)
   self.assertEqual((holders[0]['person_name'],holders[0]['start_inclusive'],holders[0]['end_exclusive']),(r['person_name'],r['start_inclusive'],r['end_exclusive']))
   self.assertFalse(any(t['start_inclusive']<r['end_exclusive'] and r['start_inclusive']<t['end_exclusive'] for t in titular))
  aa=[r for r in b.read(INPUTS/'affiliations.csv') if r['person_id']==titular[0]['person_id']]
  self.assertFalse(any('C073' in b.tokens(a['decision_ids']) for a in aa))
 def test_later_personal_party_label_is_not_backprojected(self):
  aa=[a for a in b.read(INPUTS/'affiliations.csv') if a['person_id']=='person-carlos-henrique-menezes-sobral']
  earlier=next(a for a in aa if a['start_inclusive']<='2018-12-31'<a['end_exclusive'])
  later=next(a for a in aa if 'C074' in b.tokens(a['decision_ids']))
  self.assertEqual(earlier['state'],'UNKNOWN')
  self.assertGreaterEqual(later['start_inclusive'],'2023-01-25')
  self.assertIn('UNAFFILIATED',json.loads(later['alternatives']))
 def test_unknown_succession_affiliation_is_not_neutral_non_affiliation(self):
  rows=b.read(reconstruction()/'historical/date_sensitivity.csv')
  item=next(r for r in rows if r['uncertainty_id']=='mre-2021-effective-entry')
  self.assertEqual(item['aggregate_effect'],'unbounded_personal_alternative')
  self.assertEqual(int(item['composition_neutral_days']),0)
  self.assertGreater(int(item['potentially_set_changing_days']),0)


class UncertaintyTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.release=reconstruction()/'historical'
 def test_full_primary_coverage_keeps_historical_unknowns_explicit(self):
  from validate import validate
  result=validate(self.release,require_primary_coverage=True)
  self.assertEqual((result['primary_covered_days'],result['primary_uncovered_days'],result['provisional_days']),(4096,0,100))
  self.assertEqual((result['identified_days'],result['unidentified_days']),(3996,100))
  self.assertFalse(result['complete']);self.assertTrue(result['primary_complete'])
  with self.assertRaisesRegex(ValueError,'Historical completeness failed'):validate(self.release,require_complete=True)
  assumptions=b.read(self.release/'primary_assumptions.csv')
  self.assertEqual(len({a['person_id'] for a in assumptions}),9)
  affiliations={a['affiliation_id']:a for a in b.read(self.release/'affiliations.csv')}
  self.assertTrue(all(affiliations[a['affiliation_id']]['state']=='UNKNOWN' and a['historical_state']=='UNKNOWN' for a in assumptions))
  self.assertTrue(all(a['assumed_state']=='UNAFFILIATED' and not a['assumed_party_id'] for a in assumptions))
 def test_date_alternatives_do_not_escape_the_joint_event_window(self):
  residual=b.read(self.release/'residual_person_uncertainty.csv')
  constraints=b.read(INPUTS/'sensitivity_constraints.csv')
  for person in ['person-20d6d1c35408','person-87ad75f8d2f9']:
   bound=next(r for r in constraints if r['person_id']==person)
   rows=[r for r in residual if r['person_id']==person]
   self.assertEqual(len(rows),1)
   self.assertEqual((rows[0]['start_inclusive'],rows[0]['end_exclusive']),(bound['earliest_effective_date'],bound['latest_effective_date']))
   self.assertEqual(rows[0]['alternative_scope'],'linked_date_window')
   self.assertEqual(rows[0]['date_constraint_id'],bound['uncertainty_id'])
  helder=next(r for r in residual if r['person_id']=='person-helder-melillo-lopes-cunha-silva')
  self.assertEqual(helder['alternative_scope'],'service_affiliation_intersection')
  self.assertIn('UNAFFILIATED',json.loads(helder['alternatives']))
  self.assertEqual(int(helder['potentially_set_changing_days']),2)
 def test_sachsida_registry_identity_supports_successor_membership(self):
  source=SOURCE/'research/refinement_v5/worker_6_bolsonaro_affiliations/sources'
  identity=json.loads((source/'sachsida_identity_verification.json').read_text())
  record=json.loads((source/'tse_DF_72.json').read_text())['matches'][0]
  self.assertTrue(identity['exact_identity_match'])
  self.assertEqual(identity['public_registry_identity_sha256'],record['public_registry_identity_sha256'])
  self.assertEqual(record['dtFiliacao'],[2013,5,27]);self.assertIsNone(record['dtDesfiliacao'])
  self.assertEqual(record['indPendencia'],0)
  person=next(r['person_id'] for r in b.read(INPUTS/'people.csv') if r['person_name']=='Adolfo Sachsida')
  aff=next(r for r in b.read(INPUTS/'affiliations.csv') if r['person_id']==person and r['start_inclusive']<='2022-05-11'<r['end_exclusive'])
  self.assertEqual((aff['state'],aff['party_id']),('PARTY','UNIAO'))
  self.assertFalse(json.loads(aff['alternatives']))
  self.assertFalse(any(r['person_id']==person for r in b.read(self.release/'residual_person_uncertainty.csv')))
 def test_maria_vacancy_capacity_preserves_the_unresolved_affiliation(self):
  sv=next(r for r in b.read(INPUTS/'services.csv') if r['service_id']=='service-jair_bolsonaro-0-11')
  self.assertEqual((sv['capacity'],sv['included']),('vacancy_acting','true'))
  self.assertEqual((sv['start_inclusive'],sv['end_exclusive']),('2022-12-21','2023-01-01'))
  rows=[r for r in b.read(self.release/'daily_coverage.csv') if '2022-12-21'<=r['date']<'2023-01-01']
  self.assertEqual(len(rows),11)
  self.assertTrue(all(sv['person_id'] in b.tokens(r['unresolved_dependencies']) for r in rows))
 def test_remaining_ivani_blockers_retain_new_evidence_without_inventing_parties(self):
  rows=[r for r in b.read(self.release/'completion_blockers.csv') if r['dependency_id']=='person-ivani-dos-santos']
  self.assertTrue(rows)
  self.assertTrue(all('V5W1E001' in b.tokens(r['evidence_ids']) for r in rows))
  affs=[r for r in b.read(INPUTS/'affiliations.csv') if r['person_id']=='person-ivani-dos-santos']
  self.assertTrue(all(r['state']=='UNKNOWN' and not json.loads(r['alternatives']) for r in affs))

class AcceptedServiceRegression(unittest.TestCase):
    def test_gilson_switch_is_contemporaneous_not_appointment_frozen(self):
        services=b.read(INPUTS/'services.csv'); affiliations=b.read(INPUTS/'affiliations.csv')
        for day, expected in [('2022-03-29', {'PSC'}), ('2022-03-30', {'PL'}), ('2022-03-31', set())]:
            active=[s for s in services if s['person_name']=='Gilson Machado Neto'
                    and s['included']=='true' and s['start_inclusive']<=day<s['end_exclusive']]
            self.assertEqual(b.aggregate(active,affiliations,day,[])[0],expected)
