from pathlib import Path
import requests,re,concurrent.futures,subprocess,json,hashlib,datetime
p=Path(__file__).parent/'sources'
tasks=[(2025,11,18),(2025,11,19),(2025,11,20),(2023,12,15),(2023,12,16)]
manifest=[]
def get(t):
 y,m,d=t; name=f'dcd{y}{m:02d}{d:02d}';r=requests.get('https://imagem.camara.leg.br/dc_20b.asp',params={'selCodColecaoCsv':'D','Datain':f'{d}/{m}/{y}'},timeout=25);p.joinpath(name+'_index.html').write_bytes(r.content);hit=re.search(r'URL=(https?://[^"#]+)',r.text,re.I)
 if not hit:return {'name':name,'status':r.status_code,'error':'no PDF redirect'}
 u=hit[1].replace('http:','https:');r=requests.get(u,timeout=60);pdf=p/(name+'.pdf');pdf.write_bytes(r.content);meta={'name':name,'url':u,'status':r.status_code,'sha256':hashlib.sha256(r.content).hexdigest(),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 if not r.content.startswith(b'%PDF'):return meta
 subprocess.run(['pdftotext','-layout',str(pdf),str(pdf.with_suffix('.txt'))]);s=pdf.with_suffix('.txt').read_text();pgs=s.split('\f');start=None;end=None
 for i,page in enumerate(pgs,1):
  if 'DESPACHOS DO PRESIDENTE' in page and len(page)<2500 and start is None:start=i
  if start and i>start and 'PROPOSIÇÕES APRESENTADAS' in page and len(page)<2500:end=i;break
 print(name,'PAGES',len(pgs),'DISPATCH',start,end,flush=True)
 meta['dispatch_pages']=[start,end]
 for i,page in enumerate(pgs,1):
  if re.search('sabino',page,re.I) and any(z in page.lower() for z in ['licenci','emposs','comunic']):print('TEXTMATCH',name,i,page[:6500],flush=True)
 if start and end:
  for pg in range(start+1,end):
   f=p/f'{name}_p{pg}';subprocess.run(['pdftoppm','-f',str(pg),'-l',str(pg),'-singlefile','-scale-to','2100','-png',str(pdf),str(f)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);res=subprocess.run(['tesseract',str(f)+'.png','stdout'],capture_output=True,text=True);f.with_suffix('.ocr.txt').write_text(res.stdout)
   if re.search('sabino|turismo',res.stdout,re.I):print('OCRMATCH',name,pg,res.stdout,flush=True)
 return meta
for x in concurrent.futures.ThreadPoolExecutor(3).map(get,tasks):manifest.append(x);p.joinpath('diary_scan_manifest.json').write_text(json.dumps(manifest,indent=2))
