# Sprint 0003 — Narration and Render

## 背景 (Background)

Sprint 0002 結束時，pipeline 已能跑到「可預覽的 HTML 簡報 + review 報告」。但老師最終要的是「帶旁白的 mp4 教學影片」——Sprint 0003 補上最後兩棒：從 slides.md 的 speaker notes 生成語音，再把簡報畫面 + 語音合成影片。

Sprint 0003 結束後的完整 pipeline：

```
/edu.research <topic>       → topic.research.md
/edu.outline <slug>         → outline.md
/edu.slides <slug>          → slides.md + review
/edu.narrate <slug>         → narration/*.txt + audio/*.mp3
/edu.render <slug>          → dist/<slug>.mp4
```

**這是 MVP 的最後一塊拼圖。**

## 粗略目標 (High-level Goals)

1. **`/edu.narrate <slug>`**：從 slides.md 抽取每頁 speaker notes → 存為 `narration/slide-NN.txt` → 跑 Edge-TTS 存為 `audio/slide-NN.mp3`
2. **`/edu.render <slug>`**：marp build HTML → Playwright 逐頁開 HTML + 播音檔 → 錄螢幕 → ffmpeg 拼成 `dist/<slug>.mp4`
3. **`scripts/synthesize_tts.py`**：Edge-TTS wrapper（接收文字 + voice → 輸出 mp3）
4. **`scripts/render_video.py`**：Playwright + ffmpeg 編排（接收 HTML + audio 目錄 → 輸出 mp4）
5. **端到端**：library-ethics 跑完 5 個 slash commands → 拿到 mp4

## 可能的方向 (Potential Directions)

### 方案 A（推薦）：逐頁錄製 + ffmpeg 拼接

1. `/edu.narrate` 把 speaker notes 拆成逐頁 txt + 逐頁 mp3
2. `/edu.render` 流程：
   - marp build HTML（已有 `build_slides.sh`）
   - `render_video.py` 用 Playwright 開 HTML，逐頁截圖為 PNG（不錄影片、只截靜態圖）
   - 對每張 slide：用 ffmpeg 把 PNG + 對應 mp3 → 合成一段影片片段（圖片持續時間 = 音檔長度 + 1 秒 buffer）
   - 最後 ffmpeg concat 所有片段 → `dist/<slug>.mp4`

**優點**：
- 不需要 Playwright 真的「播放」slides + 音檔同步錄螢幕（同步邏輯很難寫、容易 flaky）
- 截圖 + ffmpeg 拼接是確定性流程，結果可重現
- 每頁音檔獨立，老師可以只重錄某一頁

**缺點**：
- 不會錄到 Marp 的 transition / fragment 動畫（靜態截圖）
- 但 MVP 階段 transition 不重要，先出影片再說

### 方案 B：Playwright 全程錄螢幕

Playwright 用 `page.video` 錄整段播放，每張 slide 停留 N 秒（= 對應音檔長度），音檔在 Playwright 內播放或事後合併。

**優點**：能錄到 transition。
**缺點**：Playwright 錄影 + 音訊同步極其 flaky、需精確計時、不同機器速度不同可能導致音畫不同步。

### 方案 C：合併 narrate + render 為一個 skill

不分兩步，一個 `/edu.render` 做完一切。

**優點**：使用者少一步。
**缺點**：違反「階段化 + 可中斷審閱」——老師無法在 TTS 生成後、render 前先聽一下語音品質再決定要不要繼續。

**推薦方案 A。** 理由：確定性最高、可重現、MVP 最快能跑通。Transition 動畫等 Sprint 0004 polish 再處理（如果真的需要的話）。

## 技術預設（plan 階段就能定的）

| 項目 | 決定 | 理由 |
|---|---|---|
| TTS 引擎 | Edge-TTS（`edge-tts` Python 套件） | brainstorming 階段已定，免費、中文品質可接受 |
| 預設 voice | `zh-TW-HsiaoChenNeural`（女聲） | Edge-TTS 的 zh-TW 中品質最穩定的一個 |
| 音檔格式 | mp3 | 通用、ffmpeg 原生支援 |
| 截圖格式 | PNG | 無損、ffmpeg 原生支援 |
| 輸出解析度 | 1280×720（720p） | Marp default slide ratio 16:9、720p 夠用且渲染快 |
| 每頁 buffer | 音檔長度 + 1.5 秒 | 頭尾各留一點呼吸空間 |
| Transition | 無（硬切） | MVP 不做 transition，Sprint 0004 可加 fade |
| ffmpeg concat | `concat demuxer`（filelist.txt） | 最穩定的多段拼接方式 |

## 待釐清事項 (Open Questions)

- **Edge-TTS 安裝**：`pip install edge-tts`。使用者環境的 Python 是 3.13，需確認 edge-tts 相容性。
- **Playwright Python**：`pip install playwright && playwright install chromium`。Sprint 0002 用 npx marp-cli（Node），Sprint 0003 用 playwright（Python）。兩個語言 runtime 並存，如果複雜就統一到 Node playwright。但 Edge-TTS 只有 Python 版，所以 Python 無法避免。
- **ffmpeg 安裝**：需要在 PATH 上。使用者環境可能沒有，M2 測試時安裝。
- **中文 voice 品質**：`zh-TW-HsiaoChenNeural` 在長文（100+ 字）的語調自然度需實測。如果不好，替代有 `zh-TW-YunJheNeural`（男聲）。
- **slides.html 的截圖解析度**：Playwright `page.screenshot()` 需要設 viewport size 以匹配 1280×720。Marp 的 HTML 在特定 viewport 下的渲染品質需實測。

## 下一步 (Next Step)

確認 plan 後，執行 `/ddd.spec`。
