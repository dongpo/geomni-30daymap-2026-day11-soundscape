from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import json,random,requests,time,hashlib,collections,math
P=Path(__file__).resolve().parents[1]; start=time.perf_counter()
rows=json.loads((P.parent/'day11-soundscape-v2/archive-recordings.json').read_text())
eligible=[r for r in rows if '/by/3.0/' in r['license'] or '/publicdomain/mark/' in r['license']]
# Fixed seed, equal opportunity across occupied 0.25-degree cells, then round-robin.
rng=random.Random(20261111);cells=collections.defaultdict(list)
for r in eligible:cells[(math.floor(r['lat']*4),math.floor(r['lon']*4))].append(r)
keys=sorted(cells);rng.shuffle(keys)
for v in cells.values():rng.shuffle(v)
candidates=[]
while any(cells.values()):
 for k in keys:
  if cells[k]:candidates.append(cells[k].pop())
(P/'source/candidate-order.json').write_text(json.dumps(candidates[:500],ensure_ascii=False,indent=2))
def one(r):
 t=time.perf_counter();ident=r['id'];f=P/'metadata'/f'{ident}.json'
 try:
  if f.exists():meta=json.loads(f.read_text())
  else:
   res=requests.get('https://archive.org/metadata/'+ident,timeout=40);res.raise_for_status();meta=res.json();f.write_text(res.text)
  lic=meta.get('metadata',{}).get('licenseurl',r['license']);lic=lic[0] if isinstance(lic,list) else lic
  if not ('/by/3.0/' in lic or '/publicdomain/mark/' in lic):raise ValueError('License recheck not eligible: '+lic)
  files=[x for x in meta.get('files',[]) if x.get('name','').lower().endswith('.mp3') and int(x.get('size',0))<22000000]
  files.sort(key=lambda x:(x.get('format')!='VBR MP3',x.get('source')!='original',x['name']))
  if not files:raise ValueError('No MP3 under 22MB')
  chosen=files[0];u='https://archive.org/download/'+ident+'/'+requests.utils.quote(chosen['name'],safe='');out=P/'audio'/f'{ident}.mp3'
  if not out.exists():
   z=requests.get(u,timeout=(15,70));z.raise_for_status();out.write_bytes(z.content)
  return {**r,'audio_file':str(out.relative_to(P)),'audio_url':u,'audio_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'audio_bytes':out.stat().st_size,'audio_format':chosen.get('format'),'license_verified':lic,'acquisition_seconds':round(time.perf_counter()-t,3)}
 except Exception as e:return {'id':ident,'error':str(e),'acquisition_seconds':round(time.perf_counter()-t,3)}
# Process small deterministic batches; replace failures using next candidate, no opaque cherry-picking.
ok=[];fail=[];offset=0
while len(ok)<300 and offset<500:
 batch=candidates[offset:offset+min(12,300-len(ok))];offset+=len(batch)
 with ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(one,batch))
 for r in results:
  (fail if 'error' in r else ok).append(r)
 (P/'sample.json').write_text(json.dumps(ok,ensure_ascii=False,indent=2))
 (P/'evidence/acquisition.json').write_text(json.dumps({'eligible':len(eligible),'occupied_cells':len(keys),'selected':len(ok),'attempts':offset,'failed':fail,'elapsed_seconds':time.perf_counter()-start,'selection':'seed20261111 round-robin occupied 0.25deg cells; CC BY3 or publicdomain mark only; no representativeness claim'},ensure_ascii=False,indent=2))
 print('ACQUIRED',len(ok),'FAILED',len(fail),'SECONDS',round(time.perf_counter()-start),flush=True)
print('DONE',len(ok),flush=True)
