from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,requests,time,hashlib,datetime
P=Path(__file__).resolve().parents[1]
# Main island plus offshore islands that actually occur in this sample; avoid mainland-wide box.
regions={'north':(23.8,119.4,25.4,122.1),'south':(21.8,119.8,23.8,121.7),'penghu':(23.15,119.25,23.85,119.75),'kinmen':(24.3,118.15,24.6,118.55),'matsu':(25.9,119.85,26.45,120.1)}
def run(item):
 name,b=item;f=P/'source'/f'osm-{name}.json';bbox=','.join(map(str,b));query=f'''[out:json][timeout:180];(way["natural"="coastline"]({bbox});way["waterway"="river"]({bbox});way["highway"~"^(motorway|trunk|primary|secondary)$"]({bbox});way["landuse"="residential"]({bbox});node["place"~"^(city|town|village|hamlet|suburb)$"]({bbox}););out geom;''';(P/'source'/f'query-{name}.overpassql').write_text(query)
 if f.exists():return name,len(json.loads(f.read_text())['elements'])
 t=time.perf_counter();r=requests.get('https://overpass.private.coffee/api/interpreter',params={'data':query},timeout=240);r.raise_for_status();j=r.json()
 if 'remark' in j:raise RuntimeError(j['remark'])
 f.write_text(r.text);print(name,len(j['elements']),round(time.perf_counter()-t),flush=True);return name,len(j['elements'])
with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(run,regions.items()))
(P/'evidence/acquisition.json').write_text(json.dumps({'retrieved_at':datetime.datetime.now().astimezone().isoformat(),'source':'https://overpass.private.coffee/api/interpreter','license':'OpenStreetMap contributors, ODbL 1.0','regions':regions,'counts':result},ensure_ascii=False,indent=2))
