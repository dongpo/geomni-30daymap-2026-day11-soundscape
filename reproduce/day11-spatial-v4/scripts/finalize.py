from pathlib import Path
import json,datetime,shutil,hashlib
from PIL import Image
P=Path(__file__).resolve().parents[1];root=P.parents[1];now=datetime.datetime.now().astimezone().isoformat()
for name in ['north-coast','river-valley']:
 im=Image.open(P/'evidence'/f'{name}.jpg');im.save(P/f'day11-{name}.png')
browser={'tested_at':now,'browser':'ChatGPT in-app browser','viewport':[1600,900],'checks':[{'case':'bird_timeline_seek','requested_seconds':11.52,'observed_seconds':11.667097,'paused':False},{'case':'stream_timeline_seek','requested_seconds':6.24,'observed_seconds':6.303183,'paused':False},{'case':'coast_within_500m_filter','observed_count':118},{'case':'coast_500m_and_nature_model_filter','observed_count':72},{'case':'river_distance_focus','feature':'小坑仔溪','display':'約290m','geometry_and_distance_line_visible':True},{'case':'river_recording','feature':'牡丹溪','distance_display':'<10m','road_display':'60m','residential_display':'10m'},{'case':'empty_feeling_submission','result':'rejected; name and self-report required'},{'case':'console_errors','observed':[]},{'case':'switch_recording','result':'previous audio paused and source reset'}],'human_feelings_created':0,'human_model_confirmations_created':0,'screenshots':['day11-north-coast.png','day11-river-valley.png'],'note':'Actual browser playback and time progression tested, not human acoustic ground truth.'}
(P/'evidence/browser-checks.json').write_text(json.dumps(browser,ensure_ascii=False,indent=2))
qa=json.loads((P/'evidence/spatial-qa.json').read_text())
review={'day':11,'status':'READY_FOR_REVIEW','review_status':'SPATIAL_SOUNDSCAPE_V4_READY_FOR_LOCAL_MAP_REVIEW','actual_delivery_date':'2026-11-11','artifact_path':str(P),'parent_version':'outputs/day11-yamnet-v3','user_approval':False,'local_requested_implementation_complete':True,'public_release_status':'NOT_AUTHORIZED / no new publication','accuracy_validation_status':'NOT_EVALUATED / no independent human labels','scope':'300 recordings; inherited 30sec YAMNet results; real OSM coast/river/major roads/residential geometry and distance comparisons','checks':{'spatial':qa,'independent_distance_checks':40,'browser':browser},'remaining_limits':['Recordings 2012–2025 versus 2026 OSM snapshot; no historical reconstruction','Residential polygons exclude multipolygon relations; not full settlement extents','288/300 recordings same author; not representative sampling','First30sec only; model scores not calibrated accuracy','Euclidean proximity is not sound origin or causation; no interpolated sound field','No human feelings or confirmations invented'],'evidence':['evidence/spatial-qa.json','evidence/independent-checks.json','evidence/browser-checks.json','day11-north-coast.png','day11-river-valley.png']}
gov=root/'governance';stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');hist=gov/'history'/('day11-before-spatial-v4-'+stamp);hist.mkdir(parents=True)
for name in ['backlog.json','reviews/day11.json']:shutil.copy2(gov/name,hist/Path(name).name)
(gov/'reviews/day11.json').write_text(json.dumps(review,ensure_ascii=False,indent=2))
b=json.loads((gov/'backlog.json').read_text());b['updated']='2026-11-11'
for d in b['days']:
 if d['id']=='D11':
  d.update(status='READY_FOR_REVIEW',review_status=review['review_status'],artifact_path=str(P),implementation='300段YAMNet＋時間軸；OSM海岸／河流／主要道路／住宅用地真實幾何與距離、地景×模型交叉比較、獨立人的感受欄',blocker='無本機地圖交付阻礙；尚未人工審稿／核准，模型準確率與人的感受未驗證',next_action='本人先審v4實際地圖；不自動發布',actual_delivery_date='2026-11-11',evidence_scope='81245筆有效地物；300筆空間對照；40項獨立距離核對；實測點選跳播與篩選；原資料程式保留')
(gov/'backlog.json').write_text(json.dumps(b,ensure_ascii=False,indent=2))
with (gov/'CHANGELOG.txt').open('a') as f:f.write('\n'+now+' Day11 v4: real spatial soundscape map delivered locally; 300 inherited YAMNet records, 81245 geometries, 40 independent distance checks and browser QA. Awaiting map review; no publication. Previous v3 preserved.\n')
manifest=[]
for f in sorted(P.rglob('*')):
 if f.is_file() and f.name!='manifest.json':manifest.append({'path':str(f.relative_to(P)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(P/'manifest.json').write_text(json.dumps({'created':now,'dependencies':['../day11-yamnet-v3 (preserved original recordings, model output, timeline and Leaflet)'],'files':manifest},ensure_ascii=False,indent=2))
print('Saved PNGs, QA, governance and manifest')
