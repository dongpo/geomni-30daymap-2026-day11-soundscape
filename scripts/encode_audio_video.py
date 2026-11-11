from pathlib import Path
import json,subprocess,bisect,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];V=P/'video/with-audio';rows=json.loads((V/'capture.json').read_text());rows=[r for r in rows if not r['before']['paused'] and r['before']['ready']==4];ts=[(r['before']['time']+r['after'])/2 for r in rows];start=ts[0];duration=22;fps=24
assert all(b>a for a,b in zip(ts,ts[1:]));width,height=Image.open(V/'frames'/rows[0]['name']).size
ff=Path('work/day07-env/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v9.0').resolve();source=P.parent/'day11-yamnet-v3/audio/aporee_39957_45649.mp3';out=V/'Geomni-Day11-Soundscape-Pulse.mp4';font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',22)
cmd=[str(ff),'-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height+88}','-r',str(fps),'-i','pipe:0','-ss',str(start),'-i',str(source),'-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','libx264','-crf','21','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)]
log=(V/'encode.log').open('w');proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log);last=None
for i in range(duration*fps):
 r=rows[max(0,bisect.bisect_right(ts,start+i/fps)-1)]
 if r['name']!=last:
  im=Image.open(V/'frames'/r['name']).convert('RGB');assert im.size==(width,height);canvas=Image.new('RGB',(width,height+88),'#183630');canvas.paste(im,(0,0));d=ImageDraw.Draw(canvas)
  for y,line in enumerate(['聆聽：屏東滿州港仔海岸 / Listening: Gangzai coast, Pingtung','原音：吳燦政 Wu, Tsan-Cheng · CC BY 3.0 · Radio Aporee / Internet Archive','所選錄音同步原音；其他點只呈現模型候選，沒有混音 / Selected recording only']):d.text((16,height+3+28*y),line,font=font,fill='white')
  buf=canvas.tobytes();last=r['name']
 proc.stdin.write(buf)
proc.stdin.close();assert proc.wait()==0;log.close();canvas.save(V/'preview.png')
manifest={'duration_seconds':duration,'resolution':[width,height+88],'original_capture_resolution':[width,height],'image_scale':[1,1],'encoded_fps':fps,'capture_count':len(rows),'source_id':'aporee_39957_45649','audio_source':'https://archive.org/details/aporee_39957_45649','audio_license':'https://creativecommons.org/licenses/by/3.0/','audio_credit':'Wu,Tsan-Cheng','source_audio_start_seconds':start,'audio':'Original MP3 excerpt muxed against measured browser playback clock; no system-audio capture, no narration, no background music or mixing. AAC transcoding, original gain.','max_capture_interval_seconds':max(b-a for a,b in zip(ts,ts[1:])),'sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest()};(V/'video-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print(json.dumps(manifest,ensure_ascii=False))
