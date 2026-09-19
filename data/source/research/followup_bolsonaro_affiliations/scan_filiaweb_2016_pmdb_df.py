"""Read public archived list; retain target matches only, no negative inference."""
import pathlib,json,requests,bs4,concurrent.futures,hashlib,unicodedata,time
P=pathlib.Path(__file__).parent
NAMES=['IVANI DOS SANTOS','IVANY DOS SANTOS','CARLOS HENRIQUE MENEZES SOBRAL','MARIA ESTELLA DANTAS ANTONICHELLI','MARIA ESTELLA DANTAS','JONATHAS ASSUNCAO SALVADOR NERY DE CASTRO','JONATHAS ASSUNCAO DE CASTRO','HELDER MELILLO LOPES CUNHA SILVA','MARCOS PAULO CARDOSO COELHO DA SILVA','SERGIO JOSE PEREIRA','ANA CARLA MACHADO LOPES','RENATO DE LIMA FRANCA','LUIZ PONTEL DE SOUZA','OTAVIO BRANDELLI']
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s or '')if not unicodedata.combining(c)).upper().strip()
def page(n):
 r=requests.get('https://brasilia-df.filiaweb.com/filiados/pmdb',params={'page':n},timeout=30);r.encoding='utf-8';s=bs4.BeautifulSoup(r.text,'html.parser');matches=[];rows=s.select('table tr')[1:]
 for row in rows:
  cells=[x.get_text(' ',strip=True)for x in row.find_all('td')]
  if cells and norm(cells[0])in NAMES:matches.append({'name':cells[0],'masked_voter_number':cells[1],'affiliation_date':cells[2],'party':'PMDB','city':'BRASILIA','uf':'DF'})
 return {'url':r.url,'status':r.status_code,'snapshot_date_claimed_by_source':'2016-07-27','retrieved_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'page':n,'row_count':len(rows),'response_sha256':hashlib.sha256(r.content).hexdigest(),'matches':matches}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as ex:
 for r in ex.map(page,range(1,27)):
  results.append(r);print(r['page'],r['row_count'],r['matches'],flush=True)
(P/'filiaweb_2016_pmdb_df_scoped.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
