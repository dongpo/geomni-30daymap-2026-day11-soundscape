from pathlib import Path
import re,json
P=Path(__file__).resolve().parents[1];V=P.parent/'day11-composition-v5';s=(V/'scripts/page.html').read_text()
# Retain the tested listening drawer, audio/timeline and independent self-report components.
css=s[s.index('<style>')+7:s.index('</style>')];drawer=s[s.index('<aside id="drawer"'):s.index('<script src=')]
logic=s[s.index('function openCell('):s.index('function closeDrawer()')]
logic=logic.replace("$('cell-summary').textContent=rows.length+'段錄音；下列為實際採錄紀錄。各柱按每段是否含候選計數，並非聲音持續時間。';","$('cell-summary').textContent=rows.length+'段錄音；依候選出現的錄音筆數著色，不是音量、音源位置或人的感受。';")
logic=logic.replace("for(const k of KINDS){highlight[k].clearLayers();L.circleMarker([r.lat,r.lon],{radius:7,color:'#c27f37',weight:2,fill:false,interactive:false}).addTo(highlight[k])}","highlight.clearLayers();L.circleMarker([r.lat,r.lon],{radius:9,color:'#172a30',weight:3,fill:false,interactive:false}).addTo(highlight);")
logic=logic.replace('function openCell(', 'function showCell(').replace('function choose(r){selected=r;', 'function choose(r){pausePulse();selected=r;')
logic=logic.replace('段錄音；依候選出現的錄音筆數著色，不是音量、音源位置或人的感受。','段同格原始錄音（含目前時窗外記錄）。下方為選取錄音的原始時間，不等於目前地圖時刻。')
logic=logic.replace('esc(r.recorded_date)', "esc(RECORDING_TIMES[r.id].effective)+(RECORDING_TIMES[r.id].corrected?'（原典藏：'+esc(r.recorded_date)+'；時區依原站修正）':'')")
feel=s[s.index('let feelings={}'):s.index('/*TIMELINE_CODE*/')]
page=(P/'scripts/shell.html').read_text().replace('/*BASE_CSS*/',css).replace('<!--DRAWER-->',drawer).replace('/*DRAWER_LOGIC*/',logic).replace('/*FEELINGS*/',feel).replace('/*TIMELINE_CODE*/',(P.parent/'day11-yamnet-v3/scripts/timeline.js').read_text())
for a,b in {'關閉 ×': '關閉 / Close ×', '① 原始採錄紀錄': '① 採錄紀錄 / Recording', '播放這段錄音': '播放 / Listen', '② 模型推測 · 尚非人工確認': '② 模型推測 / Model predictions · Not verified', '原始描述與授權': '描述與授權 / Description & licence', '原始典藏': '來源 / Source', '③ 人的感受 · 聆聽者自述': '③ 聆聽感受 / Listener impressions', '寫下聆聽感受': '寫下感受 / Add an impression', '聆聽者姓名': '姓名 / Name', '儲存感受': '儲存 / Save', '匯出感受': '匯出 / Export', '只存於本瀏覽器。': '只存本瀏覽器 / Stored in this browser only.', '採錄位置 ': '採錄位置 / Location ', '尚無人的感受紀錄；不由模型推論舒適或吵雜。': '尚無感受紀錄 / No listener impressions yet.', '點時間軸聆聽候選片段；原音將繼續播放。': '點時間軸聆聽 / Select a timeline segment to listen.', '段同格原始錄音（含目前時窗外記錄）。下方為選取錄音的原始時間，不等於目前地圖時刻。': ' 段同格錄音 / recordings in this cell (including outside the current window).', '自己的感受，不等同模型分類對錯': '你的感受 / Your own listening impressions', '>暫停</button>': '>暫停 / Pause</button>'}.items():page=page.replace(a,b)
(P/'index.html').write_text(page)
print('Built day soundscape v12')
