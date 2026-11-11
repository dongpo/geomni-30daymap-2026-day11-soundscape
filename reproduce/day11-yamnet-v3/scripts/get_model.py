from pathlib import Path
import requests,json,hashlib
P=Path(__file__).resolve().parents[1];base='https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/'
commit='c14bf9ad91962cf189f9f58db2132c06247fcd53';base=base.replace('/master/','/'+commit+'/')
urls={n:base+n for n in ['yamnet.py','features.py','params.py','yamnet_class_map.csv','yamnet_test.py','README.md']};urls['yamnet.h5']='https://storage.googleapis.com/audioset/yamnet.h5';urls['LICENSE']='https://raw.githubusercontent.com/tensorflow/models/'+commit+'/LICENSE'
manifest={'repository_commit':commit,'files':{}}
for n,u in urls.items():
 r=requests.get(u,timeout=90);r.raise_for_status();(P/'model'/n).write_bytes(r.content);manifest['files'][n]={'url':u,'sha256':hashlib.sha256(r.content).hexdigest()}
(P/'model/provenance.json').write_text(json.dumps(manifest,indent=2));print(commit)
