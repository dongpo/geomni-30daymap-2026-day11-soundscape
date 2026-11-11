from pathlib import Path
import json,shutil
P=Path(__file__).resolve().parents[1];V=P.parent/'day11-yamnet-v3'
rows=json.loads((V/'sample.json').read_text())
for r in rows:
 r['audio']='../day11-yamnet-v3/'+r['audio_file'];r['year']=int(r['recorded_date'][:4]);r['date_note']=r['recorded_date']
(P/'data/recordings.js').write_text('const RECORDS='+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';')
# Preserve tested model/timeline code and immutable analysis outputs in their original version.
s=(P/'scripts/page.html').read_text().replace('/*TIMELINE_CODE*/',(V/'scripts/timeline.js').read_text())
(P/'index.html').write_text(s)
print('Built spatial map')
