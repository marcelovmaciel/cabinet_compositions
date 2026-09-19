"""Bounded identity check of twelve historical same-name affiliation rows."""
import requests,json,pathlib,hashlib,unicodedata,concurrent.futures,time
P=pathlib.Path(__file__).parent
BASE='https://filia2-consulta.tse.jus.br/filia-consulta/rest/v1/'
CASES=[('MG','POUSO ALEGRE','PR','PL'),('RS','NOVO HAMBURGO','PDT','PDT'),('SP','IBIUNA','PP','PP'),('SP','MIGUELOPOLIS','PP','PP'),('SP','OSASCO','PSB','PSB'),('SP','SUMARE','PSB','PSB'),('ES','VITORIA','PDT','PDT'),('MT','RIBEIRAO CASCALHEIRA','PMDB','MDB'),('PR','UMUARAMA','PMDB','MDB'),('PR','UMUARAMA','PP','PP'),('MG','ALPINOPOLIS','PTDOB','AVANTE'),('MG','ITAUNA','PP','PP')]
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s or '')if not unicodedata.combining(c)).upper().strip()
parties=json.loads((P/'tse_partidos.json').read_text());ufs=json.loads((P/'tse_uf.json').read_text());metadata={}
for state in {x[0]for x in CASES}:
 uf=next(x for x in ufs if x['sglUf']==state);metadata[state]=requests.get(BASE+'localidade/'+uf['codObjeto']+'/municipios',timeout=35).json()
def scan(case):
 uf,name,old,new=case;city=next(x for x in metadata[uf]if norm(x['nomLocalidade'])==name);party=next(x for x in parties if x['sgPartido']==new)
 r=requests.get(BASE+'relacao-filiados',params={'sgUe':uf,'cdMunicipio':city['codObjeto'],'sqPartido':party['id'],'currentPage':0,'pageSize':10000},timeout=40);j=r.json();rows=j.get('entitys',[]);matches=[]
 for row in rows:
  if norm(row.get('nmEleitor'))!='SERGIO JOSE PEREIRA':continue
  item={k:v for k,v in row.items()if k in {'nmEleitor','sgPartido','dtFiliacao','dtDesfiliacao','dtCancelamento','dtExclusao','stRegistroFiliacao','indPendencia','cdMotivoDesfiliacao','nomLocalidade','sgUe','sqRegistroFiliacao'}}
  item['public_registry_identity_sha256']=hashlib.sha256(str(row.get('numCpf')).encode()).hexdigest();item['public_registry_voter_sha256']=hashlib.sha256(str(row.get('nrTituloEleitor')).encode()).hexdigest();matches.append(item)
 return {'historical_city':name,'uf':uf,'historical_party':old,'queried_current_party':new,'url':r.url,'status':r.status_code,'totalElements':j.get('totalElements'),'records_inspected':len(rows),'response_sha256':hashlib.sha256(r.content).hexdigest(),'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'matches':matches}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as ex:
 for result in ex.map(scan,CASES):results.append(result);print(result,flush=True)
(P/'sergio_twelve_current_checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
