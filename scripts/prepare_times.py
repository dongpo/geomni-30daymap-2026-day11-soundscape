from pathlib import Path
import json,re,collections
P=Path(__file__).resolve().parents[1];rows=json.loads((P.parent/'day11-composition-v5/data/recordings.json').read_text());corrections={x['id']:x for x in json.loads((P/'source/time-reconciliation.json').read_text())};out={};hour=collections.Counter();excluded=[]
for r in rows:
 original=r.get('recorded_date',''); correction=corrections.get(r['id'],{}); raw=correction.get('effective') or original;m=re.fullmatch(r'(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}):(\d{2}) (.+)',raw)
 valid=bool(m and m[5] in ['Asia/Taipei','Asia/Shanghai'])
 out[r['id']]={'raw':original,'effective':raw,'corrected':bool(correction.get('confirmed')),'evidence':correction.get('source_url'),'eligible':valid,'date':m[1] if m else None,'zone':m[5] if m else None,'minute':int(m[2])*60+int(m[3])+int(m[4])/60 if valid else None,'reason':None if valid else '來源時區與採錄地不一致，待核對，未擅自換算'}
 if valid:hour[int(m[2])]+=1
 else:excluded.append({'id':r['id'],'raw':raw})
assert sum(hour.values())==299 and len(excluded)==1
(P/'data/recording-times.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));(P/'data/recording-times.js').write_text('const RECORDING_TIMES='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';')
(P/'evidence/time-audit.json').write_text(json.dumps({'eligible':299,'excluded':1,'corrected':34,'hour_counts':dict(sorted(hour.items())),'excluded_records':excluded,'policy':'34 stale archive labels reconciled against exact sound ID in current originating catalogue; original wall clock unchanged; 1 unresolved Europe/Berlin; index_date not used'},ensure_ascii=False,indent=2));print(dict(sorted(hour.items())))
