"""Research-only public TSE affiliation lookup. Retains scoped officeholder names only.
No non-match is treated as non-affiliation; current registry may omit old cancelled records.
"""
import requests,json,pathlib,time,hashlib,unicodedata,concurrent.futures
P=pathlib.Path(__file__).parent
URL='https://filia2-consulta.tse.jus.br/filia-consulta/rest/v1/relacao-filiados'
NAMES=['IVANI DOS SANTOS','IVANY DOS SANTOS','MARIA ESTELLA DANTAS ANTONICHELLI','MARIA ESTELLA DANTAS','JONATHAS ASSUNCAO SALVADOR NERY DE CASTRO','JONATHAS ASSUNCAO DE CASTRO','HELDER MELILLO LOPES CUNHA SILVA','MARCOS PAULO CARDOSO COELHO DA SILVA','SERGIO JOSE PEREIRA','MARIO RAMOS RIBEIRO','CARLOS HENRIQUE MENEZES SOBRAL','WALLACE NUNES DA SILVA','LUIZ PONTEL DE SOUZA','OTAVIO BRANDELLI','RENATO DE LIMA FRANCA','PAULO HENRIQUE PEDROSA']
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s or '') if not unicodedata.combining(c)).upper().strip()
KEEP={'nmEleitor','sgPartido','dtFiliacao','dtDesfiliacao','dtCancelamento','dtExclusao','stRegistroFiliacao','cdMotivoCancelamento','cdMotivoDesfiliacao','desSituacaoEleitor','sgUe','nomLocalidade','sqRegistroFiliacao','indOrigem','indPendencia','tpSexo','tsCadastroDesfiliacao'}
def scan(task):
 uf,municipio,city,party=task
 log={'uf':uf,'municipio':municipio,'city':city,'party':party['sgPartido'],'id':party['id'],'pages':[],'matches':[]};page=0
 while True:
  params={'sgUe':uf,'cdMunicipio':municipio,'sqPartido':party['id'],'currentPage':page,'pageSize':10000}
  try:
   r=requests.get(URL,params=params,timeout=55);data=r.json()
   if r.status_code!=200:log['error']={'status':r.status_code,'body':r.text[:300]};break
   rows=data.get('entitys',[]);log['pages'].append({'url':r.url,'records':len(rows),'totalElements':data.get('totalElements'),'response_sha256':hashlib.sha256(r.content).hexdigest(),'retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
   for row in rows:
    if norm(row.get('nmEleitor')) in NAMES:
     out={k:v for k,v in row.items() if k in KEEP};out['public_registry_identity_sha256']=hashlib.sha256(str(row.get('numCpf')).encode()).hexdigest();log['matches'].append(out)
   if (page+1)*10000>=data['totalElements']:break
   page+=1
  except Exception as e:log['error']=str(e);break
 return log

A=P.parent/'followup_bolsonaro_affiliations'
parties=json.loads((A/'tse_partidos.json').read_text())
parties.sort(key=lambda p:({'MDB':0,'PSDB':1,'UNIAO':2,'REPUBLICANOS':3}.get(p['sgPartido'],10),p['sgPartido']))
ufs=json.loads((A/'tse_uf.json').read_text())
CITIES={'PA':['BELÉM'],'BA':['SALVADOR'],'SE':['ARACAJU'],'RJ':['RIO DE JANEIRO','BELFORD ROXO','DUQUE DE CAXIAS']}
tasks=[]
for uf in ufs:
 if uf['sglUf'] not in CITIES:continue
 municipalities=requests.get('https://filia2-consulta.tse.jus.br/filia-consulta/rest/v1/localidade/'+uf['codObjeto']+'/municipios',timeout=40).json()
 (P/('tse_municipalities_'+uf['sglUf']+'.json')).write_text(json.dumps(municipalities,ensure_ascii=False,indent=2))
 for city in municipalities:
  if city['nomLocalidade'] in CITIES[uf['sglUf']]:
   for party in parties:tasks.append((uf['sglUf'],city['codObjeto'],city['nomLocalidade'],party))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for result in ex.map(scan,tasks):
  (P/('tse_'+result['uf']+'_'+str(result['municipio'])+'_'+str(result['id'])+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2))
  print(result['city'],result['party'],sum(x['records'] for x in result['pages']),result.get('error','OK'),result['matches'],flush=True)
