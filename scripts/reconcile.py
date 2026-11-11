from pathlib import Path
import json,urllib.request,hashlib,datetime,concurrent.futures
P=Path(__file__).resolve().parents[1]
old=json.loads((P.parent/'day11-day-soundscape-v9/evidence/time-audit.json').read_text())['excluded_records']
def get(r):
 loc,sid=r['id'].split('_')[1:];url='https://aporee.org/api/maps/getLocationInfo?locid='+loc
 req=urllib.request.Request(url,headers={'X-Requested-With':'XMLHttpRequest','Referer':'https://aporee.org/maps/'})
 raw=urllib.request.urlopen(req,timeout=40).read();(P/'source'/f'{r["id"]}.json').write_bytes(raw)
 item=next(x for x in json.loads(raw) if str(x['id'])==sid)
 dt=datetime.datetime.strptime(item['recdate'],'%d.%m.%Y %H:%M')
 match=dt.strftime('%Y-%m-%d %H:%M')==r['raw'][:16]
 return dict(id=r['id'],original=r['raw'],current_recdate=item['recdate'],current_timezone=item['timezone'],same_wall_clock=match,confirmed=item['timezone']=='Asia/Taipei' and match,effective=dt.strftime('%Y-%m-%d %H:%M:00')+' Asia/Taipei' if item['timezone']=='Asia/Taipei' and match else None,source_url=url,sha256=hashlib.sha256(raw).hexdigest(),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),basis='Current originating catalogue matched exact sound ID. Current timezone replaces stale archive label; unchanged clock, no hour shift. Historical cause/default setting not established.')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex: rows=list(ex.map(get,old))
(P/'source/time-reconciliation.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('verified',sum(x['confirmed'] for x in rows),'/',len(rows))
for x in rows:
 if not x['confirmed']:print(x)
