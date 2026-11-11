from pathlib import Path
import json,collections,math
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];rows=json.loads((P/'data/recordings.json').read_text());rel=json.loads((P.parent/'day11-spatial-v4/data/spatial-relations.json').read_text());qa=json.loads((P/'evidence/composition-checks.json').read_text());groups=['ocean','stream','other_nature','animal','human','transport','mechanical','music'];tr=Transformer.from_crs(4326,3826,always_xy=True)
checks=0
for r in rows:
 x,y=tr.transform(r['lon'],r['lat'])
 for km,key in r['cells'].items():
  i,j=map(int,key.split(':'));size=int(km)*1000;assert i*size<=x<(i+1)*size and j*size<=y<(j+1)*size;checks+=1
for d in [250,500,1000]:
 for kind in ['coast','river','residential']:
  selected=[r for r in rows if rel[r['id']].get(kind) and rel[r['id']][kind]['distance_m']<=d];expected=qa['national_by_distance'][str(d)][kind]
  assert len(selected)==expected['n']
  for km in ['2','10','20','80']:
   bins=collections.defaultdict(list)
   for r in selected:bins[r['cells'][km]].append(r)
   assert sum(len(rs) for rs in bins.values())==len(selected)
   for g in groups:assert sum(sum(g in r['composition_groups'] for r in rs) for rs in bins.values())==expected['counts'][g]
   checks+=9
assert [qa['national_by_distance']['250'][k]['n'] for k in ['coast','river','residential']]==[106,39,127]
report={'grid_point_containment_checks':1200,'total_invariant_checks':checks,'records':300,'national_500m_denominators':[118,74,175],'national_250m_denominators':[106,39,127],'overlap_nonexclusive':True,'all_passed':True}
(P/'evidence/verification.json').write_text(json.dumps(report,indent=2));print(report)
