import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
os.environ['TF_NUM_INTRAOP_THREADS']='4';os.environ['TF_NUM_INTEROP_THREADS']='2'
from pathlib import Path
import sys,json,time,csv,math,hashlib,platform
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'model'))
import numpy as np,soundfile as sf,tensorflow as tf
from scipy.signal import resample_poly
import params,yamnet
start=time.perf_counter();model=yamnet.yamnet_frames_model(params.Params());model.load_weights(str(P/'model/yamnet.h5'));model_load=time.perf_counter()-start
classes=list(csv.DictReader((P/'model/yamnet_class_map.csv').open()));ontology={n['id']:n for n in json.loads((P/'model/ontology.json').read_text())}
def descendants(mid,seen=None):
 seen=set() if seen is None else seen
 if mid in seen:return seen
 seen.add(mid)
 for c in ontology.get(mid,{}).get('child_ids',[]):descendants(c,seen)
 return seen
def indices(roots):
 mids=set().union(*(descendants(r) for r in roots));return [i for i,c in enumerate(classes) if c['mid'] in mids]
groups=[('human','人聲與人體聲',['/m/0dgw9r'],'#a85e4e'),('music','音樂',['/m/04rlf'],'#9171ae'),('animal','動物聲',['/m/0jbk'],'#39896a'),('nature','風、水與其他自然聲',['/m/059j3w'],'#3885a3'),('transport','交通工具',['/m/07yv9'],'#b18233'),('mechanical','引擎、機械與工具',['/m/02mk9','/t/dd00077','/m/07k1x'],'#717b87')]
lookup=[dict(id=g,label=l,indices=indices(roots),roots=roots,color=color) for g,l,roots,color in groups]
(P/'results/group-mapping.json').write_text(json.dumps({'groups':lookup,'class_map':classes,'aggregation':'max class score within each group; classes may overlap groups; no probability or percentage interpretation'},ensure_ascii=False,indent=2))
# First call compile/warm-up is measured separately and excluded from per-record inference latency.
t=time.perf_counter();model(np.zeros(16000,dtype=np.float32));warmup=time.perf_counter()-t
seen=set();failed=[];wait_start=time.time()
while len(seen)<300:
 try:rows=json.loads((P/'sample.json').read_text())
 except (FileNotFoundError,json.JSONDecodeError):time.sleep(2);continue
 new=[r for r in rows if r['id'] not in seen]
 for r in new:
  ident=r['id'];t0=time.perf_counter()
  try:
   # Full MP3 retained; analyze exactly first min(30,duration) seconds only.
   with sf.SoundFile(P/r['audio_file']) as f:
    sr=f.samplerate;channels=f.channels;total_frames=len(f);wave=f.read(frames=min(total_frames,30*sr),dtype='float32',always_2d=True).mean(axis=1)
   duration=total_frames/sr;analyzed=len(wave)/sr;peak=float(np.max(np.abs(wave)));rms=float(np.sqrt(np.mean(wave**2)))
   gcd=math.gcd(sr,16000);wave=resample_poly(wave,16000//gcd,sr//gcd).astype(np.float32)
   preprocess=time.perf_counter()-t0;t=time.perf_counter();scores,emb,mel=model(wave);scores=scores.numpy();infer=time.perf_counter()-t
   assert scores.shape[1]==521 and np.isfinite(scores).all() and (scores>=0).all() and (scores<=1).all()
   np.savez_compressed(P/'results'/f'{ident}-scores.npz',scores=scores)
   average=scores.mean(axis=0);top=np.argsort(average)[-5:][::-1]
   events=[];group_summaries=[]
   for group in lookup:
    ix=group['indices'];arr=scores[:,ix];maxima=arr.max(axis=1);best=np.array(ix)[arr.argmax(axis=1)];active=maxima>=.30;group_events=[];begin=None
    for k in range(len(active)+1):
     yes=k<len(active) and active[k]
     if yes and begin is None:begin=k
     if not yes and begin is not None:
      if k-begin>=2:
       a=round(begin*.48,3);b=round(min(analyzed,(k-1)*.48+.975),3)
       if a<b:
        peakframe=begin+int(np.argmax(maxima[begin:k]));ci=int(best[peakframe]);e={'id':f'{ident}:{group["id"]}:{begin}', 'group':group['id'],'start':a,'end':b,'class_index':ci,'class_name':classes[ci]['display_name'],'score':round(float(maxima[peakframe]),4),'mean_score':round(float(maxima[begin:k].mean()),4),'status':'model_inferred','human_review':None};events.append(e);group_events.append(e)
      begin=None
    group_summaries.append({'group':group['id'],'peak_score':round(float(maxima.max()),4),'events':len(group_events)})
   out={'id':ident,'model':'YAMNet official yamnet.h5','sample_rate_input':sr,'channels_input':channels,'sample_rate_model':16000,'original_duration':duration,'analysis_start':0,'analysis_end':analyzed,'analysis_samples':len(wave),'frame_count':len(scores),'patch_hop':.48,'patch_support_seconds':.975,'threshold':.30,'min_consecutive_frames':2,'top_classes':[{'index':int(i),'label':classes[i]['display_name'],'mean_score':round(float(average[i]),4)} for i in top],'groups':group_summaries,'events':sorted(events,key=lambda e:(e['start'],e['group'])),'human_confirmed_count':0,'model_input_sha256':hashlib.sha256(wave.tobytes()).hexdigest(),'source_audio_sha256':r['audio_sha256'],'peak_input':peak,'rms_input':rms,'preprocessing_seconds':round(preprocess,4),'inference_seconds':round(infer,4),'processing_seconds':round(time.perf_counter()-t0,4)}
   (P/'results'/f'{ident}.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));seen.add(ident)
  except Exception as e:
   failed.append({'id':ident,'error':str(e)});seen.add(ident);print('FAILED',ident,str(e),flush=True)
  if len(seen)%12==0:print('INFERRED',len(seen),'FAIL',len(failed),flush=True)
 if not new:
  if time.time()-wait_start>3600:break
  time.sleep(3)
results=[json.loads(f.read_text()) for f in (P/'results').glob('aporee_*.json')];analysis_seconds=sum(r['analysis_end'] for r in results);model_seconds=sum(r['inference_seconds'] for r in results)
report={'tensorflow':tf.__version__,'python':platform.python_version(),'machine':platform.machine(),'device':[str(d) for d in tf.config.list_physical_devices()],'successful':len(results),'failed':failed,'model_load_seconds':model_load,'warmup_seconds':warmup,'total_wall_seconds_including_wait_for_acquisition':time.perf_counter()-start,'analyzed_audio_seconds':analysis_seconds,'original_audio_seconds':sum(r['original_duration'] for r in results),'inference_seconds':model_seconds,'preprocessing_seconds':sum(r['preprocessing_seconds'] for r in results),'audio_seconds_per_inference_second':analysis_seconds/model_seconds if model_seconds else None,'event_count':sum(len(r['events']) for r in results),'human_confirmed':0,'accuracy_evaluated':False,'note':'Scores are uncalibrated model outputs. No human ground truth; no accuracy claim. First min(30,duration) seconds per recording only.'}
(P/'evidence/inference-benchmark.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True)
