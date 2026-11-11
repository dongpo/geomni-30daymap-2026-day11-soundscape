from pathlib import Path
import json,collections
P=Path(__file__).resolve().parents[1]
rows=json.loads((P/'sample.json').read_text());results={r['id']:json.loads((P/'results'/f'{r["id"]}.json').read_text()) for r in rows};groups=json.loads((P/'results/group-mapping.json').read_text())['groups']
for ident,r in results.items():
 lengths={}
 for g in groups:
  intervals=sorted((e['start'],e['end']) for e in r['events'] if e['group']==g['id']);merged=[]
  for a,b in intervals:
   if merged and a<=merged[-1][1]:merged[-1][1]=max(merged[-1][1],b)
   else:merged.append([a,b])
  lengths[g['id']]=round(sum(b-a for a,b in merged),3)
 r['candidate_seconds']=lengths;r['primary_group']=max(lengths,key=lengths.get) if max(lengths.values())>0 else 'unknown'
(P/'ml-data.js').write_text('const ML_RESULTS='+json.dumps(results,ensure_ascii=False,separators=(',',':'))+';\nconst ML_GROUPS='+json.dumps([{k:g[k] for k in ['id','label','color']} for g in groups],ensure_ascii=False)+';\nconst ML_SAMPLE='+json.dumps({r['id']:{'audio':r['audio_file'],'license':r['license_verified'],'sha256':r['audio_sha256']} for r in rows},ensure_ascii=False)+';')
s=(P.parent/'day11-soundscape-v2/index.html').read_text()
s=s.replace("L.geoJSON(LAND,", "const landLayer=L.geoJSON(LAND,")
s=s.replace("opacity:.7,attribution", "opacity:1,attribution")
s=s.replace("if(map.getZoom()>=10&&!map.hasLayer(streets))streets.addTo(map);else if(map.getZoom()<10&&map.hasLayer(streets))map.removeLayer(streets)","if(map.getZoom()>=10){if(!map.hasLayer(streets))streets.addTo(map);if(map.hasLayer(landLayer))map.removeLayer(landLayer)}else{if(map.hasLayer(streets))map.removeLayer(streets);if(!map.hasLayer(landLayer))landLayer.addTo(map)}")
s=s.replace('把臺灣打開來聽','臺灣聲景，讓 AI 先做聆聽索引').replace('從街道、車站到山林與海面下，沿著錄音的位置旅行。','300 段真實錄音 × YAMNet · 選地點，看模型推測，再跳到聲音出現的片段。').replace('錄音紀錄 · 不等於不同地點','已分析錄音 · 每段前 30 秒內')
s=s.replace('grid-template-columns:245px minmax(350px,1fr) 335px','grid-template-columns:245px minmax(350px,1fr) 420px')
s=s.replace('<option value="all">所有典藏</option>','<option value="yamnet" selected>已分析的 300 段</option><option value="all">所有典藏（含未分析）</option>')
s=s.replace('<label for="year">錄音年份</label>','<label for="soundtype">模型候選類型</label><select id="soundtype"><option value="all">所有類型</option><option value="unknown">未達顯示門檻</option></select><label for="year">錄音年份</label>')
s=s.replace('綠：環境錄音　橘：自然選錄<br>雙色：混合來源群組<br>','色彩：模型候選類型（非人工確認）<br>')
s=s.replace('群組數字表示錄音筆數。放大後可選取地點；同位置可能有多段錄音。','群組數字表示錄音筆數。空白不代表安靜。未分析的錄音沒有 AI 標籤。')
s=s.replace('<div id="status">請戴上耳機，依需要調整音量。</div>','<div id="status">請戴上耳機，依需要調整音量。</div><section id="ml-panel"></section>')
s=s.replace('<script src="data.js"></script>','<script src="data.js"></script><script src="ml-data.js"></script>')
s=s.replace("$('count').textContent=RECORDS.length.toLocaleString();","for(const r of RECORDS){if(ML_SAMPLE[r.id])r.audio=ML_SAMPLE[r.id].audio} $('count').textContent=Object.keys(ML_RESULTS).length; for(const g of ML_GROUPS)$('soundtype').add(new Option(g.label,g.id));")
s=s.replace("const color=r=>isNature(r)?'#bd622d':'#277c72';","const color=r=>isNature(r)?'#bd622d':'#277c72';")
s=s.replace("s==='all'||(s==='nature'===isNature(r))","s==='all'||(s==='yamnet'?!!ML_RESULTS[r.id]:(s==='nature')===isNature(r))")
s=s.replace("&&(!q||[r.title", "&&($('soundtype').value==='all'||(ML_RESULTS[r.id]&&($('soundtype').value==='unknown'?ML_RESULTS[r.id].events.length===0:ML_RESULTS[r.id].events.some(e=>e.group===$('soundtype').value))))&&(!q||[r.title")
s=s.replace("['source','year'].forEach", "['source','year','soundtype'].forEach")
s=s.replace("c=rows.every(isNature)?'#bd622d':rows.some(isNature)?'linear-gradient(90deg,#277c72 65%,#bd622d 65%)':'#277c72'","c=n>1?'#335d60':(ML_GROUPS.find(g=>g.id===ML_RESULTS[rows[0].id]?.primary_group)?.color||'#929792')")
s=s.replace('每一個點，都有一段原始錄音','顏色為候選類型 · 不表示音量').replace('<div><i style="background:#277c72"></i>環境錄音　<i style="background:#bd622d"></i>自然選錄</div>','<div>綠 動物 · 藍 自然 · 棕 交通<br>紅 人聲 · 紫 音樂 · 灰 機械／未知</div>')
s=s.replace("if(focus)map.setView", "renderML(r);if(focus)map.setView")
s=s.replace("list(filtered,'篩選結果');render()", "list(filtered,'篩選結果');render();if(selected&&!filtered.some(r=>r.id===selected.id)){if(filtered.length)choose(filtered[0]);else{audio.pause();selected=null;$('ml-panel').innerHTML='<p>沒有符合條件的錄音。</p>';$('title').textContent='沒有符合條件的錄音';$('play').disabled=true}}")
s=s.replace("$('status').textContent='按播放才會連線取得原站音檔。';", "$('status').textContent=ML_SAMPLE[r.id]?'本輪使用已校驗的本機原始音檔；按播放或點時間軸開始。':'按播放才會連線取得原站音檔。';")
s=s.replace("filter();choose(RECORDS[0]);","filter();choose(RECORDS.find(r=>ML_RESULTS[r.id]&&ML_RESULTS[r.id].events.some(e=>e.group==='animal'))||RECORDS.find(r=>ML_RESULTS[r.id]));")
s=s.replace('<summary>資料範圍、缺口與製圖方法</summary>','<summary>資料範圍、缺口與製圖方法</summary><p>YAMNet：300筆地理分散樣本，每筆只分析前min(30秒,總長)。16kHz單聲道，0.48秒步長、約0.975秒支援範圍；類別分數≥0.30連續至少2框才顯示。六大類依AudioSet階層合併，分數取類內最大值，允許多類重疊。未達門檻不是沒有聲音，分數不是正確率。</p><p>所有初始標籤均為模型推測，人工確認0筆。人工核對需由聆聽者明確填姓名並提交；存於這個瀏覽器，可匯出JSON，未自動回寫原資料或同步。</p>')
s=s.replace('按選取載入原站音檔；未重託管、未混音、未用AI生成聲音。','已分析300段使用本機保存且校驗一致的原始音檔，其餘按選取載入原站；未混音、未用AI生成聲音。')
s=s.replace('</style>','''
#ml-panel{margin:14px -5px;padding:13px 10px;background:#f1f1e7;border:1px solid #d7ded0;border-radius:7px}.ml-title{font-size:14px;font-weight:700}.ml-note{font-size:11px;line-height:1.6;color:#667568;margin:5px 0}.lane{display:grid;grid-template-columns:74px 1fr;gap:5px;align-items:center;margin:6px 0;font-size:10px}.track{position:relative;height:23px;background:#e0e6db;border-radius:3px}.event{position:absolute;top:2px;height:19px;padding:0;border:0;border-radius:2px;min-width:3px;opacity:.85}.event:hover,.event.chosen{outline:2px solid #142e2a;opacity:1}.event.confirmed{border-top:4px solid #1e6641}.ticks{display:flex;justify-content:space-between;margin-left:79px;font-size:10px;color:#70816d}.cursor{position:absolute;top:-3px;bottom:-3px;border-left:1px solid #111;pointer-events:none;z-index:5}.eventread{font-size:12px;background:#fffef7;padding:10px;margin-top:8px;border-left:3px solid #b27b30}.eventread button{font-size:11px;padding:5px}.reviewrow{display:flex;gap:5px}.reviewrow input,.reviewrow select{width:50%;font-size:11px;padding:6px;margin:5px 0}.ml-actions{display:flex;gap:5px}.ml-actions button{font-size:10px;padding:5px}.event-list{max-height:95px;overflow:auto;margin-top:6px}.event-list button{display:block;width:100%;border:0;text-align:left;background:transparent;font-size:11px;padding:4px}.manualstatus{font-size:11px;color:#216c43}
</style>''')
# UI functions defined before startup call, use page's single audio element.
addon=(P/'scripts/timeline.js').read_text();s=s.replace('filter();choose(RECORDS.find',addon+'\nfilter();choose(RECORDS.find')
(P/'index.html').write_text(s)
(P/'evidence/ui-build.json').write_text(json.dumps({'records':len(rows),'events':sum(len(x['events']) for x in results.values()),'primary_groups':dict(collections.Counter(x['primary_group'] for x in results.values())),'all_model_inferred':all(e['human_review'] is None for x in results.values() for e in x['events'])},ensure_ascii=False,indent=2))
print('Built',len(rows))
