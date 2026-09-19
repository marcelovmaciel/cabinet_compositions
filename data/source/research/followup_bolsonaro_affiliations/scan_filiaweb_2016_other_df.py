"""Bounded historical Brasília affiliation research; only target rows retained."""
import pathlib,json,requests,bs4,concurrent.futures,hashlib,unicodedata,time,math
P=pathlib.Path(__file__).parent
NAMES=['IVANI DOS SANTOS','IVANY DOS SANTOS','CARLOS HENRIQUE MENEZES SOBRAL','MARIA ESTELLA DANTAS ANTONICHELLI','MARIA ESTELLA DANTAS','JONATHAS ASSUNCAO SALVADOR NERY DE CASTRO','JONATHAS ASSUNCAO DE CASTRO','HELDER MELILLO LOPES CUNHA SILVA','MARCOS PAULO CARDOSO COELHO DA SILVA','SERGIO JOSE PEREIRA','ANA CARLA MACHADO LOPES','RENATO DE LIMA FRANCA','LUIZ PONTEL DE SOUZA','OTAVIO BRANDELLI']
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s or '')if not unicodedata.combining(c)).upper().strip()
def page(task):
 party,n=task
 try:
  r=requests.get('https://brasilia-df.filiaweb.com/filiados/'+party,params={'page':n},timeout=30);r.encoding='utf-8';s=bs4.BeautifulSoup(r.text,'html.parser');matches=[];count=0
  for row in s.select('table tr'):
   cells=[x.get_text(' ',strip=True)for x in row.find_all('td')]
   if len(cells)!=3:continue
   count+=1
   if norm(cells[0])in NAMES:matches.append({'name':cells[0],'masked_voter_number':cells[1],'affiliation_date':cells[2],'party':party.upper(),'city':'BRASILIA','uf':'DF'})
  return {'url':r.url,'status':r.status_code,'snapshot_date_claimed_by_source':'2016-07-27','retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'party':party,'page':n,'row_count':count,'response_sha256':hashlib.sha256(r.content).hexdigest(),'matches':matches}
 except Exception as exc:return {'party':party,'page':n,'error':str(exc)}
r=requests.get('https://brasilia-df.filiaweb.com/',timeout=30);r.encoding='utf-8';s=bs4.BeautifulSoup(r.text,'html.parser');tasks=[];parties=[]
for tr in s.select('tr'):
 cells=tr.find_all('td')
 if len(cells)!=3:continue
 link=cells[0].find('a');party=link['href'].split('/')[-1].strip();count=int(cells[2].get_text(strip=True));parties.append({'party':party,'source_count':count})
 if party=='pmdb':continue
 tasks.extend((party,i)for i in range(1,math.ceil(count/1000)+1))
(P/'filiaweb_2016_df_party_metadata.json').write_text(json.dumps(parties,indent=2))
print('tasks',len(tasks),flush=True)
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as ex:
 for r in ex.map(page,tasks):
  results.append(r)
  if r.get('matches')or r.get('error'):print(r,flush=True)
  (P/'filiaweb_2016_other_df_scoped.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('complete',len(results),'rows',sum(x.get('row_count',0)for x in results),'matches',[m for x in results for m in x.get('matches',[])],flush=True)
