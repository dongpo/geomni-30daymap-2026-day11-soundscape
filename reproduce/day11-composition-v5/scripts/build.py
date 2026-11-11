from pathlib import Path
import json,hashlib
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];V=P.parent/'day11-yamnet-v3';S=P.parent/'day11-spatial-v4'
rows=json.loads((V/'sample.json').read_text());rel=json.loads((S/'data/spatial-relations.json').read_text());xy=Transformer.from_crs(4326,3826,always_xy=True);ll=Transformer.from_crs(3826,4326,always_xy=True)
cells={str(k):{} for k in [2,10,20,80]};groups=['ocean','stream','other_nature','animal','human','transport','mechanical','music']
for r in rows:
 r['audio']='../day11-yamnet-v3/'+r['audio_file'];r['year']=int(r['recorded_date'][:4]);r['cells']={};x,y=xy.transform(r['lon'],r['lat'])
 for km in [2,10,20,80]:
  size=km*1000;i,j=int(x//size),int(y//size);key=f'{i}:{j}';r['cells'][str(km)]=key
  if key not in cells[str(km)]:
   lon,lat=ll.transform((i+.5)*size,(j+.5)*size);corners=[ll.transform(xx,yy) for xx,yy in [(i*size,j*size),((i+1)*size,j*size),((i+1)*size,(j+1)*size),(i*size,(j+1)*size),(i*size,j*size)]]
   cells[str(km)][key]={'lat':lat,'lon':lon,'geometry':{'type':'Polygon','coordinates':[corners]}}
 results=json.loads((V/'results'/(r['id']+'.json')).read_text());r['candidate_groups']=sorted(set(e['group'] for e in results['events']));r['composition_groups']=sorted(set(('ocean' if e['class_name'] in ['Ocean','Waves, surf'] else 'stream' if e['class_name'] in ['Stream','Waterfall'] else 'other_nature') if e['group']=='nature' else e['group'] for e in results['events']))
# Independently reproducible national denominators and overlapping group counts.
qa={}
for d in [250,500,1000]:
 qa[d]={}
 for k in ['coast','river','residential']:
  rs=[r for r in rows if rel[r['id']].get(k) and rel[r['id']][k]['distance_m']<=d]
  counts={g:sum(g in r['composition_groups'] for r in rs) for g in groups};assert all(0<=n<=len(rs) for n in counts.values())
  qa[d][k]={'n':len(rs),'counts':counts,'percent':{g:round(100*n/len(rs),1) if rs else None for g,n in counts.items()},'recording_ids':[r['id'] for r in rs]}
assert qa[500]['coast']['n']==118 and qa[500]['river']['n']==74 and qa[500]['residential']['n']==175
(P/'data/recordings.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
(P/'data/recordings.js').write_text('const RECORDS='+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';\nconst GRID_CELLS='+json.dumps(cells,ensure_ascii=False,separators=(',',':'))+';')
(P/'evidence/composition-checks.json').write_text(json.dumps({'metric':'fraction of recordings with >=1 displayed candidate in group; overlapping groups, NOT a partition','grid_crs':'EPSG:3826','grid_km':[2,10,20,80],'national_by_distance':qa},ensure_ascii=False,indent=2))
page=(P/'scripts/page.html').read_text().replace('/*TIMELINE_CODE*/',(V/'scripts/timeline.js').read_text());(P/'index.html').write_text(page)
print('Built v5; national 500m:',{k:{'n':v['n'],'counts':v['counts']} for k,v in qa[500].items()})
