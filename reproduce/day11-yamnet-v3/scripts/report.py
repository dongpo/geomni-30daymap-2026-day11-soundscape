from pathlib import Path
import json,html,datetime,hashlib
P=Path(__file__).resolve().parents[1];b=json.loads((P/'evidence/inference-benchmark.json').read_text());q=json.loads((P/'evidence/data-verification.json').read_text());a=json.loads((P/'evidence/acquisition.json').read_text());m=json.loads((P/'model/provenance.json').read_text())
notes=f'''Day11 YAMNet v3 / 2026-11-11 / 本機審稿，未批准未公開

實際範圍
從v2的18,044筆環境典藏中選取CC BY3.0或Public Domain Mark標示之8,542筆候選；固定亂數種子20261111，按0.25度網格輪替取得。71個有候選的網格，最終300筆涵蓋70格、298組相異座標、300個相異音檔雜湊。這是空間分散樣本，不是臺灣聲景的統計代表樣本。
依候選順序嘗試310筆；8筆沒有小於22MB的MP3而排除、2筆原站HTTP500失敗，按順序補足300筆。逐筆原因保存於evidence/acquisition.json。不得稱取得過程零失敗。
原始錄音總長{b['original_audio_seconds']/3600:.2f}小時；本輪每筆僅分析前30秒，共9,000秒／150分鐘。沒有把這些標籤套到整段原音。開頭片段可能不代表錄音後段。
288/300筆來自Wu,Tsan-Cheng（吳燦政），有明顯錄音者偏差；年代也不均衡。這一輪不包含自然聲景協會50筆授權未解的錄音。

真正執行的模型
TensorFlow 2.16.2、tf-keras 2.16.0、Python 3.11.9、arm64 CPU；未使用GPU、外部生成式音訊API或替代模型。
官方YAMNet程式版本commit {m['repository_commit']}
官方權重 https://storage.googleapis.com/audioset/yamnet.h5
權重SHA256 {m['files']['yamnet.h5']['sha256']}
完整model/provenance.json、Apache-2.0授權、官方原始碼、權重與AudioSet ontology已保存。
官方synthetic test：testRandom、testSine、testZeros三項通過；test_session為框架預設跳過，不能稱四項功能測試通過。此測試證明模型環境可執行，不代表臺灣聲景分類準確。

前處理與時間軸
由libsndfile解碼原始MP3，取前30秒，立體聲以算術平均轉單聲道；scipy resample_poly重採樣為16kHz float32。未作音量正規化、降噪或聲音分離。保存解碼後模型輸入的雜湊；原始MP3全部保留。
YAMNet原生521類輸出；0.48秒hop，0.96秒log-mel patch實際波形支援約0.975秒。每筆62框，原始521維分數全保存在results/*-scores.npz；不是用標題或描述推測分類。
六個顯示群組依AudioSet ontology子孫階層：人聲與人體聲、音樂、動物聲、自然聲、交通工具、引擎／機械／工具。group-mapping.json保存每個原始類別對應。群組分數為當框群組內最大類別分數，允許跨群組重疊，不總和為100%。
群組分數≥0.30連續至少2框才顯示一段候選事件。相鄰分段的支援範圍可能輕微重疊。起訖是模型視窗範圍，不是精準音源發聲起訖。標籤取該連續事件中最高分那一框的原始類別；不表示整段每個時間都只有該類聲音。
0.30是探索性顯示門檻，未經臺灣人工標註校準，不能保證保守、準確或高召回。未達門檻不表示安靜。14筆未出現六大類達門檻事件，仍保留並可播放。
地圖單點顏色為前30秒候選事件聯集覆蓋時間最長的群組；聯集秒數不是能量／分貝／正確率。群組符號統一深綠，數字是錄音筆數。未分析點不套用模型結果。

實測
成功300／300，推論失敗0。來源取得338.45秒（含2筆HTTP500及替補）；純模型推論{b['inference_seconds']:.4f}秒；前處理{b['preprocessing_seconds']:.4f}秒；模型載入{b['model_load_seconds']:.3f}秒；暖機{b['warmup_seconds']:.3f}秒。程序內91.38秒含等待資料取得但不含Python／TensorFlow匯入與安裝；上述範圍不同且部分重疊，不能相加當完整工作耗時，也不能把21.9秒當成從零完成時間。
總共1,539個群組候選事件；類型可以重疊。原始分數9,690,600個均檢查有限值與0–1範圍；300音檔雜湊一致，全部事件落在0–30秒。
門檻0.20：293筆有事件、1,908事件；0.30：286筆、1,539事件；0.50：253筆、1,148事件。這是敏感度比較，不是準確率評估。

人工確認與限制
初始人工確認為0。沒有獨立人工參考標記，precision／recall／F1不提供。不能把原標題與模型一致當成準確率；不能由模型候選推論物種存在、聲壓或地方環境品質。
使用者可在地圖選片段、實際聆聽、填姓名並提交相符／不符／無法判斷。紀錄保存原始類別、錄音ID、音檔雜湊、時間與核對者於瀏覽器localStorage，可匯出JSON；不會自動同步或修改本機結果檔。模型標籤始終保留，人工判斷另列。
不同MP3解碼器會對編碼器延遲／padding處理稍有不同；實測瀏覽器與libsndfile總時長差約0.14秒。時間軸提供約1秒模型視窗尺度的定位，未聲稱取樣點級同步。

播放器
原始音檔已下載保存於audio/，播放與分析來源雜湊一致。為避免既有本機HTTP服務未提供Range導致跳轉回零，分析樣本由瀏覽器讀取本機MP3為Blob再播放；不改變音檔內容。切換錄音停止上一筆，逐次載入，沒有自動串流300段。
未分析的18,094筆索引仍可切換查看，但不會出現模型時間軸。v2自然錄音授權與聲音記憶資料庫缺口仍保留；本版不公開部署。背景陸地與原始資料說明沿用v2，保存其完整說明副本。

重現
work/day11-yamnet-env/bin/python scripts/acquire.py  # 需網路，原始檔存在則使用快取
work/day11-yamnet-env/bin/python scripts/get_model.py # 網路；已保存固定版本權重，重現優先使用現存model/
work/day11-yamnet-env/bin/python scripts/infer.py
work/day11-yamnet-env/bin/python scripts/verify.py
python3 scripts/build_ui.py
python3 scripts/report.py
以上scripts路徑以本成果目錄為準；虛擬環境位於專案根目錄work/day11-yamnet-env。pip install -r requirements-lock.txt可建立同版本依賴；尚未在另一台電腦重建驗證。
由專案根目錄提供HTTP服務，開啟outputs/day11-yamnet-v3/index.html。
'''
(P/'DATA-NOTES.txt').write_text(notes)
(P/'SOURCE-NOTES-v2.txt').write_text((P.parent/'day11-soundscape-v2/DATA-NOTES.txt').read_text())
head='''<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Day11 YAMNet 實測結果</title><style>body{max-width:940px;margin:40px auto;padding:0 24px;color:#173d40;background:#f6f3e9;font:16px/1.8 system-ui}h1{font-size:32px}table{border-collapse:collapse;width:100%;background:#fffdf6}td,th{text-align:left;border-bottom:1px solid #ccd7ca;padding:10px}a{color:#276b61}.note{background:#e8eee2;padding:20px}pre{white-space:pre-wrap;font:13px/1.8 system-ui}summary{cursor:pointer}</style><h1>300 段真實錄音，模型實際找到了什麼？</h1><p><a href="index.html">開啟聲音地圖與時間軸 →</a></p><p class="note">這是模型候選事件的實測，並非辨識準確率。每筆僅分析前30秒，全部標為模型推測；人工確認0筆。</p>'''
labels={'human':'人聲與人體聲','music':'音樂','animal':'動物聲','nature':'風、水與其他自然聲','transport':'交通工具','mechanical':'引擎、機械與工具'}
table='<table><tr><th>模型候選類型</th><th>有候選片段的錄音</th><th>候選片段數</th></tr>'+''.join(f'<tr><td>{labels[k]}</td><td>{q["group_recordings"][k]} / 300</td><td>{q["group_events"][k]}</td></tr>' for k in labels)+'</table><p>同一段錄音可以出現多種類型，因此各列不能相加當成300筆互斥分類。</p>'
summary=f'<p>成功分析300筆，共150分鐘音訊，產生1,539個候選片段；14筆未達顯示門檻。純模型推論21.9秒，音檔取得338.4秒，安裝與其他處理另計。原始錄音總長16.35小時，本輪沒有分析後續部分。</p><p>300筆涵蓋298組座標、70個0.25度網格。288筆出自吳燦政的長期採錄；地理分散不等於臺灣聲景的代表性普查。</p><p>顯示門檻從0.20提高到0.50，有候選事件的錄音從293筆降為253筆。沒有人工參考標記，不能由此推算準確率。</p><details><summary>展開完整資料、方法、重現與限制</summary><pre>{html.escape(notes)}</pre></details><p><a href="evidence/inference-benchmark.json">原始效能紀錄</a> · <a href="evidence/data-verification.json">資料檢查與門檻敏感度</a> · <a href="sample.json">300筆樣本清單</a></p>'
(P/'RESULTS.html').write_text(head+table+summary)
(P/'human-reviews.json').write_text(json.dumps({'schema':'geomni.day11.human-review.v1','reviews':[],'note':'No independent human annotations yet; browser annotations require explicit reviewer input and export.'},ensure_ascii=False,indent=2))
(P/'evidence/official-model-test.json').write_text(json.dumps({'source':'actual yamnet_test.py invocation observed in tool output','passed':['testRandom','testSine','testZeros'],'skipped':['test_session'],'test_suite_seconds':.585,'note':'Runtime smoke test only; not Taiwan classification accuracy.'},indent=2))
print('Report saved')
