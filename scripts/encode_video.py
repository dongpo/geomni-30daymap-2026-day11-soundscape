from pathlib import Path
import json,subprocess,bisect,hashlib
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];V=P/'video';rows=json.loads((V/'capture.json').read_text());font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',24)
ff=Path('work/day07-env/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v9.0').resolve()
segments=[('day',12,'一天聲景：不同日期錄音，依臺灣時刻合併 / Across dates, Taiwan clock time'),('relative',12,'片段比較：各錄音開頭對齊，色彩為模型候選 / Clip-relative model predictions'),('listen',10,'點選時間軸，跳到原音片段 / Select a segment to listen on the map')]
out=V/'Geomni-Day11-Soundscape-Pulse.mp4';log=(V/'encode.log').open('w');proc=subprocess.Popen([str(ff),'-y','-f','rawvideo','-pix_fmt','rgb24','-s','1600x960','-r','24','-i','pipe:0','-an','-c:v','libx264','-crf','23','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],stdin=subprocess.PIPE,stderr=log)
for label,duration,caption in segments:
 group=[r for r in rows if r['label']==label];times=[r['t'] for r in group];last=None
 for frame in range(duration*24):
  r=group[max(0,bisect.bisect_right(times,frame/24)-1)]
  if r['name']!=last:
   im=Image.open(V/'frames'/r['name']).convert('RGB');canvas=Image.new('RGB',(1600,960),'#183630');canvas.paste(im.resize((1600,900)),(0,0));d=ImageDraw.Draw(canvas);d.text((20,902),caption,font=font,fill='white');d.text((20,931),'真實畫面分段擷取 · 無收音 / Actual screen capture · Silent video',font=font,fill='#c5ddd6');buf=canvas.tobytes();last=r['name']
  proc.stdin.write(buf)
 canvas.save(V/(label+'-preview.png'))
proc.stdin.close();assert proc.wait()==0;log.close()
(V/'video-manifest.json').write_text(json.dumps({'duration_seconds':34,'resolution':[1600,960],'encoded_fps':24,'captured_frames':len(rows),'method':'CUA timestamped browser screenshots, original elapsed time within segments; repeated frames, no synthetic motion','audio':'none; audio playback was verified in browser but system audio was not captured','sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()},indent=2));print(out,out.stat().st_size)
