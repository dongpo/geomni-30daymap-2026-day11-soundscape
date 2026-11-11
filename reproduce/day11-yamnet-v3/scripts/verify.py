from pathlib import Path
import json,collections,hashlib,math,numpy as np
P=Path(__file__).resolve().parents[1];rows=json.loads((P/'sample.json').read_text());mapping=json.loads((P/'results/group-mapping.json').read_text());results=[json.loads((P/'results'/f'{r["id"]}.json').read_text()) for r in rows];assert len(rows)==len(results)==300;assert len({r['id'] for r in rows})==300
thresholds={str(t):{'recordings_with_events':0,'group_event_runs':0} for t in [.2,.3,.5]};eligible=0;class_counts=collections.Counter();group_recordings=collections.Counter();group_events=collections.Counter();noevents=[]
for row,r in zip(rows,results):
 assert hashlib.sha256((P/row['audio_file']).read_bytes()).hexdigest()==r['source_audio_sha256']
 scores=np.load(P/'results'/f'{r["id"]}-scores.npz')['scores'];assert scores.shape==(r['frame_count'],521);assert np.isfinite(scores).all();assert r['analysis_end']==30
 for e in r['events']:
  assert 0<=e['start']<e['end']<=30;assert e['score']>=.3;assert e['status']=='model_inferred' and e['human_review'] is None
  group_events[e['group']]+=1;class_counts[e['class_name']]+=1
 for g in set(e['group'] for e in r['events']):group_recordings[g]+=1
 if not r['events']:noevents.append(r['id'])
 for t in [.2,.3,.5]:
  runs=0
  for g in mapping['groups']:
   a=scores[:,g['indices']].max(axis=1)>=t
   starts=np.where(np.diff(np.r_[False,a,False].astype(int))==1)[0];ends=np.where(np.diff(np.r_[False,a,False].astype(int))==-1)[0];runs+=int(np.sum(ends-starts>=2))
  thresholds[str(t)]['group_event_runs']+=runs;thresholds[str(t)]['recordings_with_events']+=bool(runs)
report={'records':300,'unique_audio_hashes':len(set(r['audio_sha256'] for r in rows)),'unique_coordinates':len(set((r['lat'],r['lon']) for r in rows)),'occupied_025deg_cells':len(set((math.floor(r['lat']*4),math.floor(r['lon']*4)) for r in rows)),'authors':dict(collections.Counter(r['recordist'] for r in rows)),'licenses':dict(collections.Counter(r['license_verified'] for r in rows)),'years':dict(collections.Counter(r['recorded_date'][:4] for r in rows)),'group_recordings':dict(group_recordings),'group_events':dict(group_events),'no_displayed_events':noevents,'sensitivity_not_accuracy':thresholds,'top_event_classes':class_counts.most_common(20),'score_values_checked':sum(r['frame_count']*521 for r in results),'audio_hash_checks':300,'time_bounds_checked':sum(len(r['events']) for r in results),'human_confirmed':0,'precision_recall_f1':None,'reason':'No independent human reference labels; thresholds exploratory, not validated for Taiwan.'}
(P/'evidence/data-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
