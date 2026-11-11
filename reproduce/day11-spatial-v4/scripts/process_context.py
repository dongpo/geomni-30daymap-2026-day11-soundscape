from pathlib import Path
import json,collections,hashlib,datetime
import geopandas as gpd
from shapely.geometry import Point,LineString,Polygon,mapping,box
from shapely.ops import transform,nearest_points
from shapely.strtree import STRtree
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];V=P.parent/'day11-yamnet-v3'
to_m=Transformer.from_crs(4326,3826,always_xy=True).transform;to_ll=Transformer.from_crs(3826,4326,always_xy=True).transform
seen=set();features=[];metas=[];invalid=[]
for file in sorted((P/'source').glob('osm-*.json')):
 j=json.loads(file.read_text());assert 'remark' not in j;metas.append({'file':file.name,'osm_base':j.get('osm3s',{}).get('timestamp_osm_base'),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
 for e in j['elements']:
  key=e['type']+'/'+str(e['id'])
  if key in seen:continue
  seen.add(key);t=e.get('tags',{})
  kind='coast' if t.get('natural')=='coastline' else 'river' if t.get('waterway')=='river' else 'road' if 'highway'in t else 'residential' if t.get('landuse')=='residential' else 'place'
  try:
   if e['type']=='node':geom=Point(e['lon'],e['lat'])
   else:
    xy=[(a['lon'],a['lat']) for a in e.get('geometry',[])];geom=Polygon(xy) if kind=='residential' and xy[0]==xy[-1] else LineString(xy)
    if kind=='residential' and geom.geom_type!='Polygon':continue
   if geom.is_empty or not geom.is_valid:invalid.append(key);continue
   name=t.get('name:zh') or t.get('name') or t.get('ref') or {'coast':'海岸線','river':'未具名河流','road':'未具名主要道路','residential':'住宅用地','place':'未具名聚落'}[kind]
   features.append({'type':'Feature','properties':{'id':key,'kind':kind,'name':name,'subtype':t.get('highway') or t.get('waterway') or t.get('place') or t.get('landuse') or t.get('natural'),'source_url':'https://www.openstreetmap.org/'+key},'geometry':mapping(geom)})
  except Exception as ex:invalid.append(key+':'+str(ex))
# Store full geometries for measurement; only display geometries simplified by 8m.
bykind={};for_display=[]
for f in features:
 from shapely.geometry import shape
 geom=transform(to_m,shape(f['geometry']));bykind.setdefault(f['properties']['kind'],[]).append((f,geom));display=transform(to_ll,geom.simplify(8,preserve_topology=True));for_display.append({**f,'geometry':mapping(display)})
indexes={k:STRtree([g for f,g in items]) for k,items in bykind.items()};rows=json.loads((V/'sample.json').read_text());contexts={}
for r in rows:
 p=transform(to_m,Point(r['lon'],r['lat']));out={}
 for kind,items in bykind.items():
  idx=int(indexes[kind].nearest(p));f,geom=items[idx];dist=p.distance(geom)
  if dist>5000:out[kind]=None;continue
  a,b=nearest_points(p,geom);bll=transform(to_ll,b)
  out[kind]={'feature_id':f['properties']['id'],'name':f['properties']['name'],'kind':kind,'distance_m':round(dist,1),'nearest_lon':bll.x,'nearest_lat':bll.y,'inside':geom.covers(p) if kind=='residential' else False,'source_url':f['properties']['source_url']}
 contexts[r['id']]=out
(P/'data/context-features.geojson').write_text(json.dumps({'type':'FeatureCollection','features':for_display},ensure_ascii=False,separators=(',',':')))
(P/'data/spatial-relations.json').write_text(json.dumps(contexts,ensure_ascii=False,indent=2))
(P/'data/context.js').write_text('const CONTEXT_FEATURES='+json.dumps({'type':'FeatureCollection','features':for_display},ensure_ascii=False,separators=(',',':'))+';\nconst SPATIAL='+json.dumps(contexts,ensure_ascii=False,separators=(',',':'))+';')
qa={'source_snapshots':metas,'features':dict(collections.Counter(f['properties']['kind'] for f in features)),'invalid_excluded':invalid,'records':len(contexts),'within500m':{k:sum(bool(x.get(k)) and x[k]['distance_m']<=500 for x in contexts.values()) for k in bykind},'measurement_crs':'EPSG:3826','display_simplification_m':8,'nearest_search_limit_m':5000,'geometry_measurement':'unsimplified original OSM geometry; Euclidean distance; point within residential polygon=0; settlement point distance is to named center not boundary','retrieved_at':datetime.datetime.now().astimezone().isoformat()}
(P/'evidence/spatial-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(json.dumps(qa,ensure_ascii=False))
