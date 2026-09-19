from pathlib import Path
import requests,json,hashlib,datetime,concurrent.futures,re
p=Path(__file__).parent/'sources';base='https://sgip3.tse.jus.br/sgip3-consulta/api/v1/'
r=requests.get(base+'ufs/PA/municipios',timeout=30);locs=r.json();p.joinpath('sgip_municipios_pa.json').write_text(json.dumps(locs,ensure_ascii=False,indent=2));print([x for x in locs if 'BEL' in str(x).upper()][:10],flush=True)
queries=[('pa',{'tpAbrangencia':82,'sgUe':'PA'}),('df',{'tpAbrangencia':84,'sgUe':'DF'}),('national',{'tpAbrangencia':81,'sgUe':'BR'})]
belem=next(x for x in locs if any(str(v).upper()=='BELÉM' for v in x.values()));print('BELEM',belem,flush=True)
code=belem.get('sigla') or belem.get('codigo') or belem.get('sgUe'); queries.append(('belem',{'tpAbrangencia':83,'sgUeSuperior':'PA','sgUe':code}))
allorg=[];results=[]
for key,params in queries:
 params.update(sqPartido=45,isComposicoesHistoricas='true',dataInicioVigencia='01/01/2013',dataFimVigencia='19/03/2026');r=requests.get(base+'orgaoPartidario/consulta',params=params,timeout=35);j=r.json();meta={'url':r.url,'status':r.status_code,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'response':j};p.joinpath('sgip_'+key+'.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print(key,len(j),flush=True);allorg+=j

def members(o):
 i=o['sqOrgaoPartidario'];r=requests.get(base+'orgaoPartidario/comAnotacoesEMembros',params={'idOrgaoPartidario':i,'isMembrosAtivos':'false'},timeout=40);j=r.json();rows=j.get('membros') or [];matches=[x for x in rows if re.search(r'ANA.*CARLA|MACHADO.*LOPES',x.get('nomeMembro',''),re.I)]
 out={'url':r.url,'status':r.status_code,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256_response':hashlib.sha256(r.content).hexdigest(),'governing_body':o,'returned_member_count':len(rows),'scope':'Returned governing-body members, including inactive entries. Not an exhaustive affiliate list.','target_matches':matches};p.joinpath(f'sgip_members_{i}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));return out
for out in concurrent.futures.ThreadPoolExecutor(4).map(members,{x['sqOrgaoPartidario']:x for x in allorg}.values()):results.append(out);print(out['governing_body']['sqOrgaoPartidario'],out['returned_member_count'],out['target_matches'],flush=True)
p.joinpath('sgip_scan_summary.json').write_text(json.dumps({'organs':len(results),'members':sum(x['returned_member_count'] for x in results),'matches':[x for x in results if x['target_matches']]},ensure_ascii=False,indent=2))
