# Independent brute-force nearest-distance checks against original extracted OSM geometry.
from pathlib import Path
import json,hashlib
from shapely.geometry import Point,LineString,Polygon
from shapely.ops import transform
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];tr=Transformer.from_crs(4326,3826,always_xy=True).transform
raw=json.loads((P/'source/osm-pbf.json').read_text())['elements'];by={}
for e in raw:
 t=e['tags'];k='coast' if t.get('natural')=='coastline' else 'river' if t.get('waterway')=='river' else 'road' if 'highway'in t else 'residential' if t.get('landuse')=='residential' else 'place'
 try:
  if e['type']=='node':g=Point(e['lon'],e['lat'])
  else:
   xy=[(x['lon'],x['lat']) for x in e['geometry']];g=Polygon(xy) if k=='residential' and xy[0]==xy[-1] else LineString(xy)
   if k=='residential' and g.geom_type!='Polygon':continue
  if not g.is_valid or g.is_empty:continue
  by.setdefault(k,[]).append(transform(tr,g))
 except Exception:continue
rows=json.loads((P.parent/'day11-yamnet-v3/sample.json').read_text());rels=json.loads((P/'data/spatial-relations.json').read_text());checks=[]
for r in rows[::30]:
 p=transform(tr,Point(r['lon'],r['lat']))
 for k in ['coast','river','road','residential']:
  d=min(p.distance(g) for g in by[k]);v=rels[r['id']].get(k);ok=(v is None and d>5000) or (v is not None and abs(v['distance_m']-d)<=.051)
  assert ok,(r['id'],k,d,v);checks.append(dict(id=r['id'],kind=k,distance_m=d,pass_check=bool(ok)))
features=json.loads((P/'data/context-features.geojson').read_text())['features'];ids={f['properties']['id'] for f in features};assert len(rels)==300
assert all(v['feature_id'] in ids for rr in rels.values() for v in rr.values() if v)
report={'independent_brute_force_checks':checks,'all_relation_references_valid':True,'record_count':300,'pbf_sha256':hashlib.sha256((P/'source/taiwan-261109.osm.pbf').read_bytes()).hexdigest()}
(P/'evidence/independent-checks.json').write_text(json.dumps(report,indent=2));print('40 independent distance checks PASS; 300 records linked')
