from pathlib import Path
from PIL import Image
import json,datetime,shutil,hashlib,collections
P=Path(__file__).resolve().parents[1];root=P.parents[1];now=datetime.datetime.now().astimezone().isoformat();Image.open(P/'evidence/day.jpg').save(P/'day11-one-day-soundscape.png')
counts=collections.Counter()
for r in json.loads((P.parent/'day11-composition-v5/data/recordings.json').read_text()):
 for e in []:pass
 # Relative mode check counts each recording once per active group, independent of timezone.
 active=set()
 for e in json.loads((P.parent/'day11-yamnet-v3/results'/(r['id']+'.json')).read_text())['events']:
  if not e['start']<=1<e['end']:continue
  if e['group'] in ['transport','human']:active.add(e['group'])
  elif e['group']=='nature' and e['class_name'] in ['Ocean','Waves, surf']:active.add('ocean')
  elif e['group']=='nature' and e['class_name'] in ['Stream','Waterfall']:active.add('stream')
 counts.update(active)
assert [counts[g] for g in ['ocean','stream','transport','human']]==[25,7,31,52]
qa={'date':'2026-11-11','viewport':[1600,900],'day_checks':'evidence/day-verification.json','relative_mode_at1_second_counts':[25,7,31,52],'relative_mode_independent_check':True,'day_audio_test':{'day_clock':'12:00','audio_time':12.562845,'paused':False,'day_clock_stays_fixed':True},'day_playback_observed':'12:00 ->12:06','console_errors':[],'tool_issue':'One click report timed out, next UI observation confirmed action completed; no repeated mutation required','human_confirmations_added':0,'human_feelings_added':0}
(P/'evidence/browser-checks.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));(P/'alt-text.txt').write_text('全臺一天聲景模式暫停在12:00，畫面以11:00至12:00的跨日期採錄呈現漣漪。24段可用採錄，18段包含海浪、溪流、交通、人聲四類之一。圖例以固定顏色標示模型候選，樣本不足使用虛線波紋。時間模式可切回每段0至30秒，也可定位清晨、白天、傍晚、夜間；頁首與主圖明示不是同一天的即時聲景，35段時區待核對未納入一天模式。')
gov=root/'governance';h=gov/'history'/('day11-before-day-v9-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));h.mkdir(parents=True)
for name in ['backlog.json','reviews/day11.json']:shutil.copy2(gov/name,h/Path(name).name)
r={'day':11,'status':'READY_FOR_REVIEW','review_status':'DAY_SOUNDSCAPE_V9_READY_FOR_LOCAL_REVIEW','actual_delivery_date':'2026-11-11','artifact_path':str(P),'user_approval':False,'local_requested_implementation_complete':True,'public_release_status':'NOT_AUTHORIZED / not deployed','scope':'Clock-time cross-date composite with rolling60-minute window;265 explicitUTC+8 records;35 timezone conflicts excluded; original relative0–30sec mode retained','checks':{'time_audit':'evidence/time-audit.json','five_day_windows':json.loads((P/'evidence/day-verification.json').read_text()),'browser':qa},'remaining_limits':['Cross-date composite, not same-day/live soundscape','35 inconsistent source timezones excluded pending verification','Uneven hourly sampling; absence of samples is not quiet','Day window displays first30sec candidate union, not an hour-long sound event','Ripples visual metaphor only; models not independently accuracy-validated','Sparse flags recomputed within time window; threshold3 is not statistical reliability'],'evidence':['evidence/time-audit.json','evidence/day-verification.json','evidence/browser-checks.json','day11-one-day-soundscape.png']};(gov/'reviews/day11.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
b=json.loads((gov/'backlog.json').read_text())
for d in b['days']:
 if d['id']=='D11':d.update(artifact_path=str(P),review_status=r['review_status'],implementation='一天聲景按來源UTC+8採錄時刻播放；跨日期最近60分鐘概況＋漣漪；原0–30秒模式保留',next_action='本人審v9一天聲景；35段時區待核對；不公開發布',evidence_scope='五個日內時窗各300點核對通過；相對時間模式、跨午夜與原音聆聽保持日內時窗均實測')
(gov/'backlog.json').write_text(json.dumps(b,ensure_ascii=False,indent=2))
with (gov/'CHANGELOG.txt').open('a') as f:f.write('\n'+now+' Day11 v9：新增跨日期一天聲景，採265段明列UTC+8時刻；35段時區衝突暫排除。五時窗（含午夜）逐點核對、片段模式及原音操作驗證完成。舊版保留；未發布。\n')
(P/'manifest.json').write_text(json.dumps({'created':now,'dependencies':['../day11-yamnet-v3','../day11-spatial-v4','../day11-composition-v5'],'files':[{'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in P.rglob('*') if f.is_file() and f.name!='manifest.json']},ensure_ascii=False,indent=2));print('Saved day-mode evidence, screenshot and review record')
