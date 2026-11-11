from pathlib import Path
import osmium,json,datetime
P=Path(__file__).resolve().parents[1]
class Extract(osmium.SimpleHandler):
 def __init__(self):super().__init__();self.elements=[]
 def node(self,n):
  t=dict(n.tags)
  if t.get('place') in ['city','town','village','hamlet','suburb']:
   self.elements.append(dict(type='node',id=n.id,tags=t,lon=n.location.lon,lat=n.location.lat))
 def way(self,w):
  t=dict(w.tags)
  if not(t.get('natural')=='coastline' or t.get('waterway')=='river' or t.get('highway') in ['motorway','trunk','primary','secondary'] or t.get('landuse')=='residential'):return
  try:g=[dict(lon=n.lon,lat=n.lat) for n in w.nodes]
  except osmium.InvalidLocationError:return
  self.elements.append(dict(type='way',id=w.id,tags=t,geometry=g))
h=Extract();h.apply_file(str(P/'source/taiwan-261109.osm.pbf'),locations=True,filters=[osmium.filter.KeyFilter("place","natural","waterway","highway","landuse")])
r=osmium.io.Reader(str(P/'source/taiwan-261109.osm.pbf'));stamp=r.header().get('osmosis_replication_timestamp');r.close()
(P/'source/osm-pbf.json').write_text(json.dumps(dict(osm3s=dict(timestamp_osm_base=stamp),elements=h.elements),ensure_ascii=False))
print(len(h.elements),stamp)
