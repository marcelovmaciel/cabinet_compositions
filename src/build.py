#!/usr/bin/env python3
"""Deterministic offline cabinet composition builder (stdlib only).
Internal construction; use scripts/build_release.py for offline reconstruction.
"""
import argparse,csv,hashlib,json,shutil,sys
from pathlib import Path
from datetime import date,timedelta
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from release_outputs import emit
from paths import PROJECT, INPUTS, SOURCE, build_path, safe_path
VERSION='2026-03-19-history-v6-onyx-candidate'; START='2015-01-01';END='2026-03-20'
ADJUDICATED_VACANCIES={'VACANT_FUNCTIONS_REASSIGNED','VACANT_PENDING_FIRST_MINISTER'}
def read(path):
 with open(path,encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def write(path,rows,columns):
 with open(path,'w',encoding='utf8',newline='') as f:
  w=csv.DictWriter(f,columns,lineterminator='\n');w.writeheader();w.writerows(rows)
def days(s,e):return (date.fromisoformat(e)-date.fromisoformat(s)).days
def tokens(s):return set(filter(None,s.split(';')))
def coverage(intervals,s,e):
 cursor=s
 for a,b in sorted(intervals):
  if a>cursor:return False
  if b>cursor:cursor=b
  if cursor>=e:return True
 return cursor>=e
def organizational_identity(p,t,events):
 seen=set()
 while p not in seen:
  seen.add(p);eligible=[x for x in events if x['predecessor_party_id']==p and x['successor_party_id']!=p and x['effective_date']<=t]
  if not eligible:return p
  p=max(eligible,key=lambda x:x['effective_date'])['successor_party_id']
 raise ValueError('Organizational identity cycle')
def aggregate(active,affiliations,t,events,active_gaps=()):
 core=set();unknown=set();possible=set();ww=[];bounded=set();masked=[]
 for s in active:
  aa=[a for a in affiliations if a['person_id']==s['person_id'] and a['start_inclusive']<=t<a['end_exclusive']]
  if len(aa)!=1:raise ValueError(('missing/overlapping affiliation',s['service_id'],t,aa))
  a=aa[0]
  if a['date_status']=='bounded_date_convention' and a.get('date_earliest','')<=t<a.get('date_latest',''):bounded.add(a['affiliation_id'])
  if a['state']=='PARTY':
   p=organizational_identity(a['party_id'],t,events);core.add(p);ww.append((p,s,a))
  elif a['state']=='UNKNOWN':
   alt=json.loads(a.get('alternatives','[]') or '[]')
   opts=set();unspecified=not alt
   for x in alt:
    if isinstance(x,str):
     if x not in ('UNAFFILIATED','NONE'):opts.add(organizational_identity(x,t,events))
    elif x.get('state')=='PARTY':opts.add(organizational_identity(x['party_id'],t,events))
    elif x.get('state')!='UNAFFILIATED':unspecified=True
   possible|=opts;unknown.add((s['person_id'],tuple(sorted(opts)),unspecified))
  elif a['state']!='UNAFFILIATED':raise ValueError(('invalid affiliation state',a))
 unresolved=set()
 for p,opts,unspecified in unknown:
  if unspecified or not set(opts)<=core:unresolved.add(p)
  else:masked.append(p)
 unresolved|={'office:'+g['gap_id'] for g in active_gaps if g['state'] not in ADJUDICATED_VACANCIES}
 return core,possible,unresolved,ww,bounded,masked

def build(inputs,output):
 inputs=safe_path(inputs);output=build_path(output)
 if output.exists():raise FileExistsError(f'Construction output must be fresh: {output}')
 output.mkdir(parents=True)
 data={p.stem:read(p) for p in sorted(inputs.glob('*.csv'))}
 services=sorted([s for s in data['services'] if s['included']=='true' and s['capacity'] not in ('non_entry','incoming_transition','incoming_transition_CETG','temporary_delegation','outside_cutoff') and s['start_inclusive']<s['end_exclusive']],key=lambda x:x['service_id'])
 affs=sorted(data['affiliations'],key=lambda x:x['affiliation_id']);events=data['organizational_events'];gaps=data['office_coverage_gaps'];assumptions=data.get('primary_assumptions',[])
 assert len({a['assumption_id'] for a in assumptions})==len(assumptions),'duplicate assumption IDs'
 people={p['person_id'] for p in data['people']};offices={o['office_id'] for o in data['offices']}
 assert len({s['service_id'] for s in services})==len(services)
 assert all(s['person_id'] in people and s['office_id'] in offices for s in services)
 for p in people:
  aa=sorted([a for a in affs if a['person_id']==p],key=lambda x:x['start_inclusive'])
  assert all(x['end_exclusive']<=y['start_inclusive'] for x,y in zip(aa,aa[1:])),p
 for a in affs:
  assert a['state'] in ('PARTY','UNAFFILIATED','UNKNOWN')
  assert bool(a['party_id'])==(a['state']=='PARTY'),a
 periods=[];atomic=[];membership=[];possibilities=[];witnesses=[];uncertainties=[]
 def party_labels(parties,t):
  return tuple(sorted(next((n['label'] for n in data['party_names'] if n['party_id']==p and n['start_inclusive']<=t<n['end_exclusive']),p) for p in parties))
 for admin in sorted(data['administrations'],key=lambda x:x['start_inclusive']):
  aid=admin['administration_id'];left=admin['start_inclusive'];right=admin['end_exclusive'];ss=[s for s in services if s['administration_id']==aid];gg=[g for g in gaps if g['administration_id']==aid]
  boundaries={left,right}
  for x in ss+affs+gg+assumptions:
   for col in ('start_inclusive','end_exclusive','date_earliest','date_latest'):
    t=x.get(col,'')
    if left<t<right:boundaries.add(t)
  for x in events:
   if left<x['effective_date']<right:boundaries.add(x['effective_date'])
  for x in data['party_names']:
   if left<x['start_inclusive']<right:boundaries.add(x['start_inclusive'])
  bs=sorted(boundaries)
  for s,e in zip(bs,bs[1:]):
   active=[x for x in ss if x['start_inclusive']<=s<x['end_exclusive']];active_gaps=[x for x in gg if x['start_inclusive']<=s<x['end_exclusive']]
   core,poss,unknown,ww,bounded,masked=aggregate(active,affs,s,events,active_gaps)
   service_bounded={r['service_id'] for r in ss if r.get('date_status')=='bounded_date_convention' and r.get('date_earliest','')<=s<r.get('date_latest','')}
   applied=[r for r in assumptions if r['start_inclusive']<=s<r['end_exclusive']]
   assert len({r['person_id'] for r in applied})==len(applied),'overlapping primary assumptions'
   for assumption in applied:
    assert assumption['person_id'] in unknown,('stale/nonblocking assumption',assumption['assumption_id'],s)
    assert assumption['assumed_state']=='UNAFFILIATED' and not assumption['assumed_party_id']
    aa=next(a for a in affs if a['affiliation_id']==assumption['affiliation_id'])
    assert aa['state']=='UNKNOWN' and aa['person_id']==assumption['person_id']
    assert aa['start_inclusive']<=assumption['start_inclusive']<assumption['end_exclusive']<=aa['end_exclusive']
    assert assumption['historical_state']=='UNKNOWN' and assumption['authorization']
   provisional={r['person_id'] for r in applied};assumption_ids={r['assumption_id'] for r in applied}
   unfilled=unknown-provisional
   status='unidentified' if unfilled else 'primary_provisional' if unknown else 'primary_adjudicated'
   # Set-equivalent periods may coalesce while witness/status changes remain in atomic_events.
   key=(aid,tuple(sorted(core)),party_labels(core,s),'unidentified' if unfilled else 'primary')
   if periods and periods[-1]['_key']==key and periods[-1]['end_exclusive']==s:
    p=periods[-1];p['end_exclusive']=e;p['days']+=days(s,e);p['_unknown']|=unknown;p['_bounded']|=bounded;p['_masked']|=set(masked);p['_provisional']|=provisional;p['_assumptions']|=assumption_ids;p['provisional_days']+=days(s,e) if status=='primary_provisional' else 0;p['composition_status']='primary_provisional' if p['_provisional'] and not unfilled else status;p['possible_party_ids']=';'.join(sorted(tokens(p['possible_party_ids'])|poss))
   else:
    p=dict(period_id=f'{aid}-{s}',administration_id=aid,start_inclusive=s,end_exclusive=e,days=days(s,e),composition_status=status,party_ids=';'.join(sorted(core)) if not unfilled else '',definite_party_ids=';'.join(sorted(core)),possible_party_ids=';'.join(sorted(poss)),_key=key,_unknown=set(unknown),_bounded=set(bounded),_masked=set(masked),_provisional=set(provisional),_assumptions=set(assumption_ids),provisional_days=days(s,e) if status=='primary_provisional' else 0,_decisions=set());periods.append(p)
   for assumption in applied:p['_decisions']|=tokens(assumption['decision_ids'])
   for _,sv,af in ww:p['_decisions']|=tokens(sv['decision_ids'])|tokens(af['decision_ids'])
   atomic.append(dict(event_interval_id=f'{aid}-{s}',period_id=p['period_id'],administration_id=aid,start_inclusive=s,end_exclusive=e,days=days(s,e),composition_status=status,definite_party_ids=';'.join(sorted(core)),possible_party_ids=';'.join(sorted(poss)),unknown_person_ids=';'.join(sorted(unknown)),bounded_affiliation_ids=';'.join(sorted(bounded)),bounded_service_ids=';'.join(sorted(service_bounded)),masked_person_ids=';'.join(sorted(masked)),provisional_person_ids=';'.join(sorted(provisional)),primary_assumption_ids=';'.join(sorted(assumption_ids)),unresolved_primary_person_ids=';'.join(sorted(unfilled))))
   for party,sv,af in ww:
    witnesses.append(dict(witness_id=hashlib.sha256((sv['service_id']+af['affiliation_id']+s+e+party).encode()).hexdigest()[:20],period_id=p['period_id'],party_id=party,person_id=sv['person_id'],service_id=sv['service_id'],affiliation_id=af['affiliation_id'],start_inclusive=s,end_exclusive=e,evidence_ids=';'.join(sorted(tokens(sv['evidence_ids'])|tokens(af['evidence_ids']))),decision_ids=';'.join(sorted(tokens(sv['decision_ids'])|tokens(af['decision_ids'])))))
   if unknown or bounded or service_bounded or masked:
    uncertainties.append(dict(period_id=p['period_id'],start_inclusive=s,end_exclusive=e,unknown_person_ids=';'.join(sorted(unknown)),bounded_affiliation_ids=';'.join(sorted(bounded)),bounded_service_ids=';'.join(sorted(service_bounded)),masked_person_ids=';'.join(sorted(masked)),treatment='unidentified_gap' if unfilled else 'provisional_primary_assumption' if provisional else ('aggregate_masked' if masked else 'bounded_date_primary_convention'),possible_party_ids=';'.join(sorted(poss))))
 for p in periods:
  if p['composition_status']!='unidentified':membership += [dict(period_id=p['period_id'],party_id=x) for x in p['party_ids'].split(';') if x]
  possibilities += [dict(period_id=p['period_id'],party_id=x,membership_status='definitely_represented_core',exhaustive_primary=str(p['composition_status']!='unidentified').lower()) for x in p['definite_party_ids'].split(';') if x]
  possibilities += [dict(period_id=p['period_id'],party_id=x,membership_status='possibly_represented',exhaustive_primary='false') for x in p['possible_party_ids'].split(';') if x and x not in p['definite_party_ids'].split(';')]
  p['provisional_person_ids']=';'.join(sorted(p.pop('_provisional')));p['primary_assumption_ids']=';'.join(sorted(p.pop('_assumptions')));p['unknown_person_ids']=';'.join(sorted(p.pop('_unknown')));p['bounded_affiliation_ids']=';'.join(sorted(p.pop('_bounded')));p['masked_person_ids']=';'.join(sorted(p.pop('_masked')));p['decision_ids']=';'.join(sorted(p.pop('_decisions')));p.pop('_key')
 for m in membership:
  p=next(p for p in periods if p['period_id']==m['period_id']);ww=[(w['start_inclusive'],w['end_exclusive']) for w in witnesses if w['period_id']==m['period_id'] and w['party_id']==m['party_id']]
  assert coverage(ww,p['start_inclusive'],p['end_exclusive']),(m,p)
 assert sum(p['days'] for p in periods)==4096
 assert periods[0]['start_inclusive']==START and periods[-1]['end_exclusive']==END
 assert all(x['end_exclusive']==y['start_inclusive'] for x,y in zip(periods,periods[1:]))
 write(output/'periods.csv',periods,list(periods[0]));write(output/'membership.csv',membership,['period_id','party_id']);write(output/'possible_membership.csv',possibilities,['period_id','party_id','membership_status','exhaustive_primary']);write(output/'witnesses.csv',witnesses,['witness_id','period_id','party_id','person_id','service_id','affiliation_id','start_inclusive','end_exclusive','evidence_ids','decision_ids']);write(output/'atomic_events.csv',atomic,list(atomic[0]));write(output/'uncertainties.csv',uncertainties,['period_id','start_inclusive','end_exclusive','unknown_person_ids','bounded_affiliation_ids','bounded_service_ids','masked_person_ids','treatment','possible_party_ids'])
 extras=emit(data,periods,atomic,witnesses,output,organizational_identity)
 # Canonical sorted copies make input row order immaterial, with semantic and raw hashes separate.
 for name,rows in data.items():
  fields=list(rows[0]) if rows else next(csv.reader(open(inputs/(name+'.csv'),encoding='utf8')))
  write(output/(name+'.csv'),sorted(rows,key=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)),fields)
 shutil.copyfile(PROJECT/'CODEBOOK.md',output/'CODEBOOK.md')
 labelrows=data['party_names']
 def labels(parties,t):return ', '.join(next((n['label'] for n in labelrows if n['party_id']==p and n['start_inclusive']<=t<n['end_exclusive']),p) for p in parties)
 lines=['# Cabinet chronology: '+VERSION,'','Observation calendar: [2015-01-01, 2026-03-20), 4,096 days.','', 'Primary sets may be historically adjudicated or explicitly provisional. A provisional set fills its unknown contributions using primary_assumptions.csv; it does not establish those affiliations. Historical completeness remains separate. Dated witnesses and individual uncertainty remain available even if composition does not change.','', '| Period | Start inclusive | End exclusive | Days | Status | Party membership |','|---|---|---|---:|---|---|']
 for p in periods:lines.append('| '+ ' | '.join(str(x) for x in [p['period_id'],p['start_inclusive'],p['end_exclusive'],p['days'],p['composition_status'],labels(p['party_ids'].split(';'),p['start_inclusive']) if p['party_ids'] else 'UNIDENTIFIED; known core: '+labels(p['definite_party_ids'].split(';'),p['start_inclusive'])])+' |')
 (output/'chronology.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
 semantic={n+'.csv':hashlib.sha256(json.dumps(sorted(rr,key=lambda x:json.dumps(x,sort_keys=True)),sort_keys=True,ensure_ascii=False).encode()).hexdigest() for n,rr in data.items()}
 metadata=dict(schema_version=1,data_version=VERSION,release_status='incomplete_candidate' if any(a['unknown_person_ids'] for a in atomic) else 'completed_standalone',coverage_start=START,cutoff_exclusive=END,cutoff_inclusive='2026-03-19',calendar_days=4096,historical_period_count=len(periods),identified_days=sum(a['days'] for a in atomic if not a['unknown_person_ids']),unidentified_days=sum(a['days'] for a in atomic if a['unknown_person_ids']),primary_covered_days=sum(a['days'] for a in atomic if a['composition_status']!='unidentified'),primary_uncovered_days=sum(a['days'] for a in atomic if a['composition_status']=='unidentified'),provisional_days=sum(a['days'] for a in atomic if a['composition_status']=='primary_provisional'),bounded_date_convention_days=sum(a['days'] for a in atomic if a['bounded_affiliation_ids'] or a['bounded_service_ids']),builder_sha256=sha(Path(__file__)),input_hashes=semantic,input_hash_kind='semantic canonical rows sha256; source snapshot and generated hashes in manifest.json',build_command='python3 -B scripts/build_release.py --output build/reconstructed',operational_rules=['contemporaneous personal formal affiliation','half-open daily closing-state intervals','titular retained during ordinary delegation; vacancy actors count','party renames stable identities; mergers applied at dated effect','UNKNOWN never converted to unaffiliated','unidentified intervals retain full calendar denominator','latest admissible bounded date baseline'],evidence_limitations=['Reviewed compilation service boundaries are adjudicated, not all independently verified legal acts.','Person-specific external research and retained raw assertions are linked in completion_research_register.csv; unresolved facts remain completion blockers.','Primary adjudications preserve credible alternatives separately. A candidate with unidentified days is incomplete and cannot be promoted.','Specific chronology conflicts and date conventions are in decisions and affiliation tables.','Atlas is a second compilation; source agreement is not presumed independent.'],attribution='Original coding prepared for this repository; Atlas and cited source attribution retained. No new license claim over third-party materials.',file_hashes={p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file() and p.name not in ('metadata.json','coding_freeze.json')})
 metadata.update(extras)
 metadata['schema_version']=3
 metadata['extension_sha256']=sha(ROOT/'release_outputs.py')
 metadata['build_command']='python3 -B scripts/build_release.py --output build/reconstructed'
 metadata['complete']=metadata['unidentified_days']==0
 metadata['primary_complete']=metadata['primary_uncovered_days']==0
 metadata['completion_semantics']='complete and identified_days refer to historically established party sets; primary_complete additionally permits explicitly flagged user-authorized assumptions'
 metadata['file_hashes']={p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file() and p.name not in ('metadata.json','manifest.json','scope_validation.json')}
 dump(output/'metadata.json',metadata)
 dump(output/'manifest.json',dict(data_version=VERSION,code_sha256={'build.py':sha(ROOT/'build.py'),'release_outputs.py':sha(ROOT/'release_outputs.py')},generated_file_sha256={p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file() and p.name not in ('manifest.json','scope_validation.json')},source_snapshot_sha256={r['snapshot_path']:r['sha256'] for r in data['evidence_snapshot_links']}))
 return metadata
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--inputs',type=Path,default=INPUTS);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();print(json.dumps(build(args.inputs,args.output),sort_keys=True,indent=2))
