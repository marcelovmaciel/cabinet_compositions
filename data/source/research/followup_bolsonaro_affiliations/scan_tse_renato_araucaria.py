"""Research-only public TSE affiliation lookup. Retains scoped officeholder names only.
No non-match is treated as non-affiliation; current registry may omit old cancelled records.
"""
import requests,json,pathlib,time,hashlib,unicodedata,concurrent.futures
P=pathlib.Path(__file__).parent
URL='https://filia2-consulta.tse.jus.br/filia-consulta/rest/v1/relacao-filiados'
NAMES=['RENATO DE LIMA FRANCA']
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s or '') if not unicodedata.combining(c)).upper().strip()
KEEP={'nmEleitor','sgPartido','dtFiliacao','dtDesfiliacao','dtCancelamento','dtExclusao','stRegistroFiliacao','cdMotivoCancelamento','cdMotivoDesfiliacao','desSituacaoEleitor','sgUe','nomLocalidade','sqRegistroFiliacao','indOrigem','indPendencia','tpSexo','tsCadastroDesfiliacao'}
def scan(party):
 log={'party':party['sgPartido'],'id':party['id'],'pages':[],'matches':[]};page=0
 while True:
  params={'sgUe':'PR','cdMunicipio':'5787','sqPartido':party['id'],'currentPage':page,'pageSize':10000}
  try:
   r=requests.get(URL,params=params,timeout=55);data=r.json()
   if r.status_code!=200:log['error']={'status':r.status_code,'body':r.text[:300]};break
   rows=data.get('entitys',[]);log['pages'].append({'url':r.url,'records':len(rows),'totalElements':data.get('totalElements'),'response_sha256':hashlib.sha256(r.content).hexdigest(),'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
   for row in rows:
    if norm(row.get('nmEleitor')) in NAMES:
     out={k:v for k,v in row.items() if k in KEEP};out['public_registry_voter_identity_sha256']=hashlib.sha256(str(row.get('nrTituloEleitor')).encode()).hexdigest();out['public_registry_identity_sha256']=hashlib.sha256(str(row.get('numCpf')).encode()).hexdigest();log['matches'].append(out)
   if (page+1)*10000>=data['totalElements']:break
   page+=1
  except Exception as e:log['error']=str(e);break
 return log
parties=json.loads((P/'tse_partidos.json').read_text())
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for result in ex.map(scan,parties):
  (P/('tse_renato_araucaria_'+str(result['id'])+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
  print(result['party'],sum(x['records']for x in result['pages']),result.get('error','OK'),result['matches'],flush=True)
