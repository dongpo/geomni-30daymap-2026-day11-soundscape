from pathlib import Path
import json,collections,re
P=Path(__file__).resolve().parents[1];rows=json.loads((P.parent/'day11-composition-v5/data/recordings.json').read_text());byid={r['id']:r for r in rows};groups=['ocean','stream','transport','human'];report={}
for name in ['dawn','day','dusk','night']:
 o=json.loads((P/'evidence'/(name+'.json')).read_text());clock=o['minute'];included=set()
 for r in rows:
  date,time,zone=r['recorded_date'].split(' ')
  source=P/'source'/(r['id']+'.json')
  if source.exists():
   entry=next(x for x in json.loads(source.read_text()) if str(x['id'])==r['id'].split('_')[2])
   zone=entry['timezone'];time=entry['recdate'].split(' ')[1]+':00'
  if zone not in ['Asia/Taipei','Asia/Shanghai']:continue
  h,m,s=map(int,time.split(':'));age=(clock-h*60-m-s/60)%1440
  if 0<=age<60:included.add(r['id'])
 bins=collections.Counter(byid[i]['cells']['20'] for i in included);counts=collections.Counter()
 assert len(o['markers'])==300
 for obs in o['markers']:
  r=byid[obs['id']];expect=set(r['composition_groups'])&set(groups) if r['id'] in included else set();assert set(obs['groups'])==expect,(name,r['id']);assert obs['included']==(r['id'] in included);assert obs['sparse']==(r['id'] in included and bins[r['cells']['20']]<3);counts.update(expect)
 if 'counts' in o:assert o['counts']==[str(counts[g])+'段' for g in groups]
 report[name]={'clock_minute':clock,'included':len(included),'counts':dict(counts),'record_state_checks':300,'pass':True}
(P/'evidence/day-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
