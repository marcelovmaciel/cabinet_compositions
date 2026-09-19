"""Calendar, witnesses, uncertainty and source reconciliation for the standalone cabinet build."""
import csv,json,hashlib
from datetime import date,timedelta
from pathlib import Path

def read(p):
 with open(p,encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
 with open(p,'w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def tok(s):return set(filter(None,s.split(';')))
def dates(s,e):
 t=date.fromisoformat(s);end=date.fromisoformat(e)
 while t<end:yield t.isoformat();t+=timedelta(days=1)
def alternatives_neutral(options,other_parties):
 """Compare finite person alternatives using only other people's witnesses."""
 return bool(options) and len({frozenset(other_parties|set(o)) for o in options})==1

def emit(data,periods,atomic,witnesses,output,resolve_identity):
 services=sorted((s for s in data['services'] if s['included']=='true'),key=lambda s:s['service_id'])
 affs=data['affiliations'];people={p['person_id']:p['person_name'] for p in data['people']}
 def identity(p,t):return resolve_identity(p,t,data['organizational_events'])
 def label(p,t):return next((n['label'] for n in data['party_names'] if n['party_id']==p and n['start_inclusive']<=t<n['end_exclusive']),p)
 def labels(ps,t):return ';'.join(sorted(label(p,t) for p in tok(ps)))
 daily=[];per={p['period_id']:p for p in periods}
 for a in atomic:
  p=per[a['period_id']]
  for t in dates(a['start_inclusive'],a['end_exclusive']):
   daily.append(dict(date=t,administration_id=a['administration_id'],period_id=a['period_id'],event_interval_id=a['event_interval_id'],composition_status=a['composition_status'],party_ids=p['party_ids'],party_labels=labels(p['party_ids'],t),definite_party_ids=a['definite_party_ids'],possible_party_ids=a['possible_party_ids'],unresolved_dependencies=a['unknown_person_ids'],masked_person_ids=a['masked_person_ids'],historical_status='unidentified' if a['unknown_person_ids'] else 'established',provisional_person_ids=a.get('provisional_person_ids',''),primary_assumption_ids=a.get('primary_assumption_ids',''),unfilled_primary_dependencies=a.get('unresolved_primary_person_ids',a['unknown_person_ids'])))
 assert len(daily)==4096 and len({r['date'] for r in daily})==4096
 write(output/'daily_coverage.csv',daily,list(daily[0]))
 dd={r['date']:r for r in daily}
 # Keep office and affiliation events separate from party-set transitions.
 events=[]
 for table,idcol in [('services','service_id'),('affiliations','affiliation_id')]:
  for r in sorted(data[table],key=lambda r:r[idcol]):
   if table=='services' and r['included']!='true':continue
   for col,action in [('start_inclusive','start'),('end_exclusive','end')]:
    t=r[col]
    if '2015-01-01'<=t<'2026-03-20':
     events.append(dict(event_id=r[idcol]+'-'+action,date=t,event_type=table+'_'+action,record_id=r[idcol],person_id=r['person_id'],person_name=people[r['person_id']],office_id=r.get('office_id',''),party_id=r.get('party_id',''),state=r.get('state',''),date_status=r['date_status'],evidence_ids=r['evidence_ids'],decision_ids=r['decision_ids']))
 for n,r in enumerate(sorted(data['organizational_events'],key=lambda r:json.dumps(r,sort_keys=True))):
  events.append(dict(event_id='organization-'+str(n),date=r['effective_date'],event_type=r['event_type'],record_id=r['predecessor_party_id']+'>'+r['successor_party_id'],person_id='',person_name='',office_id='',party_id=r['successor_party_id'],state='',date_status='dated_organizational_event',evidence_ids=r['evidence_ids'],decision_ids=''))
 events.sort(key=lambda r:(r['date'],r['event_id']))
 write(output/'officeholder_events.csv',events,list(events[0]))
 transitions=[]
 for before,after in zip(periods,periods[1:]):
  t=after['start_inclusive'];known=before['composition_status']!='unidentified' and after['composition_status']!='unidentified'
  comparison_assumptions=tok(dd[t].get('primary_assumption_ids',''))|tok(dd[(date.fromisoformat(t)-timedelta(days=1)).isoformat()].get('primary_assumption_ids',''))
  entering=tok(after['party_ids'])-tok(before['party_ids']) if known else set();leaving=tok(before['party_ids'])-tok(after['party_ids']) if known else set()
  kind='administration_boundary' if before['administration_id']!=after['administration_id'] else 'unresolved_boundary' if not known else 'membership_change' if entering or leaving else 'historical_label_change'
  ee=[e for e in events if e['date']==t];ww=[w for w in witnesses if w['period_id'] in (before['period_id'],after['period_id']) and w['party_id'] in entering|leaving and (w['start_inclusive']==t or w['end_exclusive']==t)]
  transitions.append(dict(transition_id='transition-'+t,date=t,from_period_id=before['period_id'],to_period_id=after['period_id'],transition_type=kind,comparison_status=('primary_sets_comparable_provisional' if comparison_assumptions else 'primary_sets_comparable') if known else 'unidentified_boundary',entering_party_ids=';'.join(sorted(entering)),leaving_party_ids=';'.join(sorted(leaving)),before_labels=labels(before['party_ids'],before['start_inclusive']),after_labels=labels(after['party_ids'],t),event_ids=';'.join(e['event_id'] for e in ee),supporting_service_ids=';'.join(sorted({w['service_id'] for w in ww})),evidence_ids=';'.join(sorted(set().union(*(tok(e['evidence_ids']) for e in ee)))),decision_ids=';'.join(sorted(set().union(*(tok(e['decision_ids']) for e in ee)))),primary_assumption_ids=';'.join(sorted(comparison_assumptions))))
 write(output/'transitions.csv',transitions,list(transitions[0]))
 # Account for every legally qualifying office, including explicit unresolved occupancy.
 accounting=[]
 for o in sorted(data['offices'],key=lambda o:o['office_id']):
  ss=[s for s in services if s['office_id']==o['office_id']];gg=[g for g in data['office_coverage_gaps'] if g['office_id']==o['office_id']]
  bs=sorted({o['start_inclusive'],o['end_exclusive']}|{max(o['start_inclusive'],min(t,o['end_exclusive'])) for r in ss+gg for t in [r['start_inclusive'],r['end_exclusive']]})
  for s,e in zip(bs,bs[1:]):
   active=[r for r in ss if r['start_inclusive']<=s<r['end_exclusive']];gaps=[g for g in gg if g['start_inclusive']<=s<g['end_exclusive']]
   assert active or gaps,('unaccounted office',o['office_id'],s,e)
   assert not (active and gaps),('service overlaps occupancy gap',o['office_id'],s,e)
   assert len(active)<=1,('overlapping officeholders',o['office_id'],s,e)
   accounting.append(dict(office_id=o['office_id'],administration_id=o['administration_id'],start_inclusive=s,end_exclusive=e,accounting_state='OFFICEHOLDER' if active else ';'.join(g['state'] for g in gaps),service_ids=';'.join(r['service_id'] for r in active),capacities=';'.join(r['capacity'] for r in active),gap_ids=';'.join(g['gap_id'] for g in gaps),evidence_ids=';'.join(sorted(set().union(*(tok(r['evidence_ids']) for r in active+gaps))))))
 write(output/'office_accounting.csv',accounting,list(accounting[0]))
 # Preserve personal uncertainty; a minister must never mask their own alternative.
 witness_days={t:[] for t in dd}
 for w in witnesses:
  for t in dates(w['start_inclusive'],w['end_exclusive']):witness_days[t].append(w)
 def others(t,pids):return {w['party_id'] for w in witness_days[t] if w['person_id'] not in pids}
 def options(raw,t):
  result=[];unspecified=False
  for x in json.loads(raw or '[]'):
   if isinstance(x,str):result.append(set() if x in ('NONE','UNAFFILIATED') else {identity(x,t)})
   elif x.get('state')=='PARTY':result.append({identity(x['party_id'],t)})
   elif x.get('state')=='UNAFFILIATED':result.append(set())
   else:unspecified=True
  return result,unspecified
 residual=[]
 for a in sorted(affs,key=lambda a:a['affiliation_id']):
  if a['state']!='UNKNOWN' and not json.loads(a['alternatives'] or '[]') and 'C026' not in tok(a['decision_ids']):continue
  for sv in [sv for sv in services if sv['person_id']==a['person_id']]:
   left=max(sv['start_inclusive'],a['start_inclusive']);right=min(sv['end_exclusive'],a['end_exclusive'])
   linked_bounds=[c for c in data['sensitivity_constraints'] if a['affiliation_id'] in tok(c['linked_affiliation_ids'])] if a['date_status']=='bounded_date_convention' else []
   assert len(linked_bounds)<=1,('multiple alternative date constraints',a['affiliation_id'])
   alternative_scope='service_affiliation_intersection';date_constraint_id=''
   if linked_bounds:
    bound=linked_bounds[0];assert bound['person_id']==a['person_id']
    left=max(left,bound['earliest_effective_date']);right=min(right,bound['latest_effective_date'])
    alternative_scope='linked_date_window';date_constraint_id=bound['uncertainty_id']
   if left>=right:continue
   blocked=0;changes=[];affected=set();neutral_dates=[];unspecified=False
   for t in dates(left,right):
    blocked+=a['person_id'] in tok(dd[t]['unresolved_dependencies'])
    opts,unknown=options(a['alternatives'],t);unspecified|=unknown
    if a['state']!='UNKNOWN':opts.append({identity(a['party_id'],t)} if a['state']=='PARTY' else set())
    oo=others(t,{a['person_id']})
    if not unknown and alternatives_neutral(opts,oo):neutral_dates.append(t)
    elif opts and not unknown:
     changes.append(t);unions=[o|oo for o in opts];affected|=set.union(*unions)-set.intersection(*unions)
   has_alternatives=bool(json.loads(a['alternatives'] or '[]'))
   effect='completion_blocker' if blocked else 'source_notation_adjudication_no_specific_alternative' if not has_alternatives else 'primary_adjudication_with_set_changing_alternative' if changes else 'composition_neutral' if not unspecified else 'unspecified_alternative'
   residual.append(dict(uncertainty_id=a['affiliation_id']+'@'+sv['service_id'],person_id=a['person_id'],person_name=people[a['person_id']],service_id=sv['service_id'],affiliation_id=a['affiliation_id'],start_inclusive=left,end_exclusive=right,primary_state=a['state'],primary_party_id=a['party_id'],alternatives=a['alternatives'],evidentiary_basis=a['support'],aggregate_effect=effect,affected_party_ids=';'.join(sorted(affected)),potentially_set_changing_days=len(changes),composition_neutral_days=len(neutral_dates) if has_alternatives else '',unidentified_days_caused=blocked,evidence_ids=a['evidence_ids'],decision_ids=a['decision_ids'],alternative_scope=alternative_scope,date_constraint_id=date_constraint_id))
 write(output/'residual_person_uncertainty.csv',residual,list(residual[0]))
 # Joint before/after states for genuinely bounded event dates, evaluated against other witnesses.
 sensitivity=[]
 for r in sorted(data['sensitivity_constraints'],key=lambda r:r['uncertainty_id']):
  possible=[];affected=set();neutral=0;concurrent_unknown=0
  for t in dates(r['earliest_effective_date'],r['latest_effective_date']):
   if not any(sv['person_id']==r['person_id'] and sv['start_inclusive']<=t<sv['end_exclusive'] for sv in services):continue
   opts=[{identity(r[prefix+'_party_id'],t)} if r[prefix+'_state']=='PARTY' else set() for prefix in ['before','after']]
   oo=others(t,{r['person_id']});unions=[o|oo for o in opts]
   if alternatives_neutral(opts,oo):neutral+=1
   else:possible.append(t);affected|=set.union(*unions)-set.intersection(*unions)
   concurrent_unknown+=bool(tok(dd[t]['unresolved_dependencies'])-{r['person_id']})
  sensitivity.append(dict(uncertainty_id=r['uncertainty_id'],event_type='affiliation_change',person_ids=r['person_id'],start_inclusive=r['earliest_effective_date'],end_exclusive=r['latest_effective_date'],primary_effective_date=r['baseline_effective_date'],aggregate_effect='potential_set_change' if possible else 'composition_neutral',affected_party_ids=';'.join(sorted(affected)),potentially_set_changing_days=len(possible),composition_neutral_days=neutral,concurrent_unidentified_days=concurrent_unknown,constraints=r['constraints'],evidence_ids=r['evidence_ids']))
 for r in sorted(data['service_sensitivity_constraints'],key=lambda r:r['uncertainty_id']):
  possible=[];affected=set();neutral=0;unknown=0
  unbounded=any(r[prefix+'_state']=='UNKNOWN' for prefix in ['outgoing','incoming'])
  for t in dates(r['earliest_effective_date'],r['latest_effective_date']):
   opts=[{identity(r[prefix+'_party_id'],t)} if r[prefix+'_state']=='PARTY' else set() for prefix in ['outgoing','incoming']]
   oo=others(t,{r['outgoing_person_id'],r['incoming_person_id']});unions=[o|oo for o in opts]
   if unbounded:possible.append(t)
   elif alternatives_neutral(opts,oo):neutral+=1
   else:possible.append(t);affected|=set.union(*unions)-set.intersection(*unions)
   unknown+=bool(tok(dd[t]['unresolved_dependencies'])-{r['outgoing_person_id'],r['incoming_person_id']})
  sensitivity.append(dict(uncertainty_id=r['uncertainty_id'],event_type='office_succession',person_ids=r['outgoing_person_id']+';'+r['incoming_person_id'],start_inclusive=r['earliest_effective_date'],end_exclusive=r['latest_effective_date'],primary_effective_date=r['baseline_effective_date'],aggregate_effect='unbounded_personal_alternative' if unbounded else 'potential_set_change' if possible else 'composition_neutral',affected_party_ids=';'.join(sorted(affected)),potentially_set_changing_days=len(possible),composition_neutral_days=neutral,concurrent_unidentified_days=unknown,constraints=r['constraints'],evidence_ids=r['evidence_ids']))
 write(output/'date_sensitivity.csv',sensitivity,list(sensitivity[0]))
 # Reconcile the union of source-specific rosters without rewriting raw assertions.
 roster=[]
 def append_roster(source,rid,person,office,start,end,party,matched,mode):
  aas=[a for a in affs if a['person_id'] in {sv['person_id'] for sv in matched}]
  roster.append(dict(source_family=source,source_record_id=rid,person_raw=person,office_raw=office,start_raw=start,end_raw=end,party_raw=party,link_basis=mode,service_ids=';'.join(sorted(sv['service_id'] for sv in matched)),inclusion_states=';'.join(sorted({sv['included']+':'+sv['capacity'] for sv in matched})),affiliation_ids=';'.join(sorted(a['affiliation_id'] for a in aas)),decision_ids=';'.join(sorted(set().union(*(tok(x['decision_ids']) for x in matched+aas))))))
 for r in data['prior_service_assertions']:
  matched=[sv for sv in data['services'] if r['source_record_id'] in tok(sv['source_record_ids'])];mode='same_source_record_id'
  if not matched:
   pids={a['person_id'] for a in data['person_aliases'] if r['person'] in (a['alias'],a['person_name'])}
   matched=[sv for sv in data['services'] if sv['person_id'] in pids and sv['administration_id']==r['government_id']];mode='reviewed_exact_person_alias_and_administration_office_claim_retained'
  append_roster('prior_complete_roster',r['source_record_id'],r['person_raw'],r['ministry_raw'],r['start'],r['end'],r['party'],matched,mode if matched else 'unmatched_prior_claim_requires_review')
 for r in data['atlas_reconciliation']:
  matched=[sv for sv in data['services'] if sv['service_id'] in tok(r['service_ids'])]
  append_roster('atlas','atlas-line-'+r['atlas_line'],r['person_raw'],r['office_raw'],r['minister_start_raw'],r['minister_end_raw'],r['minister_party_raw'],matched,'reviewed_person_and_administration_links_raw_office_claim_retained')
 for r in data['candidate_dispositions']:
  cells=json.loads(r['source_cells_json']);matched=[sv for sv in data['services'] if sv['service_id'] in tok(r['service_ids'])]
  append_roster('pinned_cabinet_list',r['source_record_id'],json.dumps(cells,ensure_ascii=False),'','','','',matched,r['disposition'])
 write(output/'roster_reconciliation.csv',sorted(roster,key=lambda r:(r['source_family'],r['source_record_id'],json.dumps(r,sort_keys=True,ensure_ascii=False))),list(roster[0]))
 blockers=[]
 research_by_dep={r['dependency_id']:r for r in data['completion_research_register']}
 for a in atomic:
  if not a['unknown_person_ids']:continue
  for dep in sorted(tok(a['unknown_person_ids'])):
   rr=[s for s in services if s['person_id']==dep and s['start_inclusive']<=a['start_inclusive']<s['end_exclusive']]
   rr+=[g for g in data['office_coverage_gaps'] if 'office:'+g['gap_id']==dep]
   dependency_affiliations=[af for af in affs if af['person_id']==dep and af['start_inclusive']<=a['start_inclusive']<af['end_exclusive']]
   dependency_assumptions=[r['assumption_id'] for r in data.get('primary_assumptions',[]) if r['person_id']==dep and r['start_inclusive']<=a['start_inclusive']<r['end_exclusive']]
   blockers.append(dict(dependency_id=dep,person_name=people.get(dep,''),start_inclusive=a['start_inclusive'],end_exclusive=a['end_exclusive'],period_id=a['period_id'],office_ids=';'.join(sorted({r['office_id'] for r in rr})),research_record_id=research_by_dep.get(dep,{}).get('research_id',''),source_review_finding=research_by_dep.get(dep,{}).get('source_review_finding',''),saved_result_files=research_by_dep.get(dep,{}).get('saved_result_files',''),required_fact='Contemporaneous personal affiliation or evidence limiting alternatives' if not dep.startswith('office:') else 'Actual succession/effective service and personal affiliation of vacancy replacement',evidence_ids=';'.join(sorted(set().union(*(tok(r['evidence_ids']) for r in rr+dependency_affiliations)))),primary_treatment='provisional_no_additional_party' if dependency_assumptions else 'unfilled',primary_assumption_ids=';'.join(sorted(dependency_assumptions)),primary_set_filled=str(a['composition_status']!='unidentified').lower()))
 write(output/'completion_blockers.csv',blockers,['dependency_id','person_name','start_inclusive','end_exclusive','period_id','office_ids','research_record_id','source_review_finding','saved_result_files','required_fact','evidence_ids','primary_treatment','primary_assumption_ids','primary_set_filled'])
 return dict(daily_rows=len(daily),membership_transition_count=sum(t['transition_type']=='membership_change' for t in transitions),historical_label_transition_count=sum(t['transition_type']=='historical_label_change' for t in transitions),administration_boundary_count=sum(t['transition_type']=='administration_boundary' for t in transitions),unresolved_boundary_count=sum(t['transition_type']=='unresolved_boundary' for t in transitions),office_count=len(data['offices']))
