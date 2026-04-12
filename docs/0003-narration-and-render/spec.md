# Sprint 0003 — Narration and Render

## 目標

補上 MVP pipeline 的最後兩棒：從 slides.md 的 speaker notes 生成語音，再把簡報截圖 + 語音拼成帶旁白的 mp4。

交付物：

1. `/edu.narrate <slug>` — 抽取 speaker notes → 逐頁 txt + Edge-TTS mp3
2. `/edu.render <slug>` — Playwright 截圖 + ffmpeg 拼接 → mp4
3. `scripts/synthesize_tts.py` — Edge-TTS wrapper
4. `scripts/render_video.py` — Playwright 截圖 + ffmpeg 編排
5. 端到端：library-ethics 5 commands → `dist/library-ethics.mp4`

## 非目標

- Marp transition / fragment 動畫錄製（方案 A 用靜態截圖，MVP 不做）
- 多語言 voice 切換 UI（使用者手改 script 參數即可）
- 影片字幕 / SRT 生成
- 背景音樂
- AI avatar
- 自動上傳到 YouTube / LMS

## User Story

### Story 1：生成語音旁白

作為一個已經有 slides.md 的老師，
我想要輸入 `/edu.narrate <slug>` 就能得到每頁的語音旁白（mp3），
以便我先聽一遍語音品質、確認沒問題再進入影片渲染。

### Story 2：渲染影片

作為一個已經有 slides + 語音的老師，
我想要輸入 `/edu.render <slug>` 就能得到一支帶旁白的 mp4 教學影片，
以便我直接拿去上課播放、上傳補課平台、或分享給學生。

### 驗收條件

- [ ] AC-1：`/edu.narrate <slug>` 解析 `slides.md` 的 `<!-- Speaker notes: ... -->` 區塊，產出 `narration/slide-01.txt` ~ `slide-NN.txt`（每頁一個 txt）。
- [ ] AC-2：`/edu.narrate` 對每個 txt 呼叫 `scripts/synthesize_tts.py`，產出 `audio/slide-01.mp3` ~ `slide-NN.mp3`。mp3 可播放、語音為 zh-TW。
- [ ] AC-3：若 `narration/` 或 `audio/` 已存在，`/edu.narrate` 中止並提示。
- [ ] AC-4：`scripts/synthesize_tts.py` 接收 txt 路徑 + voice 參數，輸出 mp3，exit 0。
- [ ] AC-5：`/edu.render <slug>` 用 Playwright 對 `slides.html` 逐頁截圖為 PNG，存入 `frames/slide-01.png` ~ `slide-NN.png`。
- [ ] AC-6：`/edu.render` 用 ffmpeg 把每張 PNG + 對應 mp3 合成一段影片，再 concat 所有段落為 `dist/<slug>.mp4`。mp4 可播放、有畫面 + 聲音。
- [ ] AC-7：若 `frames/` 或 `dist/` 已存在，`/edu.render` 中止並提示。
- [ ] AC-8：`scripts/render_video.py` 接收 HTML 路徑 + audio 目錄 + output 路徑，輸出 mp4，exit 0。
- [ ] AC-9：library-ethics 端到端跑完 5 commands，`dist/library-ethics.mp4` 可播放、720p、畫面與語音同步。

## 相關檔案

新建：

| 路徑 | 用途 |
|---|---|
| `skills/edu.narrate/SKILL.md` | 語音旁白 slash command |
| `skills/edu.render/SKILL.md` | 影片渲染 slash command |
| `scripts/synthesize_tts.py` | Edge-TTS wrapper |
| `scripts/render_video.py` | Playwright 截圖 + ffmpeg 編排 |

修改：

| 路徑 | 修改原因 |
|---|---|
| `references/AGENTS.md` | 新增 narration/audio/frames/dist 的檔案命名規則 |
| `.gitignore` | 確認 `lessons/*/audio/` 和 `lessons/*/dist/` 已排除（Sprint 0001 已加） |

## 介面 / 資料結構

### `/edu.narrate` slash command

```
/edu.narrate <slug> [--voice=<edge-tts-voice>]
```

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 指向有 `slides.md` 的 lesson |
| `--voice` | 否 | `zh-TW-HsiaoChenNeural` | Edge-TTS voice ID |

**流程**：

1. 前置檢查：`slides.md` 存在？`narration/` 或 `audio/` 已存在 → 中止
2. 解析 `slides.md`：用 regex 抓 `<!-- Speaker notes: ... -->` 或 `<!--\nSpeaker notes: ...\n-->`（含多行）
3. 為每頁產出 `narration/slide-01.txt` ~ `slide-NN.txt`
4. 對每個 txt 呼叫：`py scripts/synthesize_tts.py narration/slide-NN.txt audio/slide-NN.mp3 --voice <voice>`
5. 回報：頁數、音檔數、總時長估、引導 `/edu.render <slug>`

### `scripts/synthesize_tts.py`

```
Usage: py scripts/synthesize_tts.py <input.txt> <output.mp3> [--voice <voice>]
```

| 參數 | 說明 |
|---|---|
| `<input.txt>` | speaker notes 文字檔 |
| `<output.mp3>` | 輸出音檔路徑 |
| `--voice` | Edge-TTS voice ID，預設 `zh-TW-HsiaoChenNeural` |

內部邏輯：

```python
import edge_tts, asyncio

async def main(text, output, voice):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output)

asyncio.run(main(text, output, voice))
```

Exit code: 0 成功 / 1 失敗（stderr 輸出錯誤訊息）。

### `/edu.render` slash command

```
/edu.render <slug> [--resolution=1280x720]
```

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 指向有 `slides.html` + `audio/` 的 lesson |
| `--resolution` | 否 | `1280x720` | 輸出解析度 |

**流程**：

1. 前置檢查：`slides.html` 存在？`audio/` 目錄存在且有 mp3？`frames/` 或 `dist/` 已存在 → 中止
2. 如果 `slides.html` 不存在但 `slides.md` 存在 → 自動跑 `build_slides.sh` 建 HTML
3. 呼叫 `py scripts/render_video.py lessons/<slug>/slides.html lessons/<slug>/audio lessons/<slug>/dist/<slug>.mp4 --resolution 1280x720`
4. 回報：mp4 路徑、檔案大小、時長、引導「MVP 完成！」

### `scripts/render_video.py`

```
Usage: py scripts/render_video.py <slides.html> <audio_dir> <output.mp4> [--resolution WxH]
```

內部流程（方案 A：截圖 + ffmpeg 拼接）：

1. **Playwright 逐頁截圖**：
   - 開 Chromium headless，viewport 設為 resolution
   - 載入 slides.html
   - 偵測總頁數（Marp 的 `section` 元素數量，或用 `document.querySelectorAll('section').length`）
   - 逐頁：navigate 到 `#N`（或用 keyboard arrow），截圖為 `frames/slide-NN.png`

2. **取得每頁音檔時長**：
   - 用 ffprobe 取 `audio/slide-NN.mp3` 的 duration
   - 每頁顯示時間 = audio duration + 1.5 秒 buffer

3. **逐段合成**：
   - 對每頁：`ffmpeg -loop 1 -i frames/slide-NN.png -i audio/slide-NN.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -t <duration> segments/seg-NN.mp4`

4. **Concat**：
   - 建 filelist.txt：`file 'segments/seg-01.mp4'\nfile 'segments/seg-02.mp4'\n...`
   - `ffmpeg -f concat -safe 0 -i filelist.txt -c copy <output.mp4>`

5. **清理**：刪除 `frames/` 和 `segments/`（中間產物），保留 `audio/`（使用者可能要重聽）和 `dist/`（最終產物）

Exit code: 0 成功 / 1 失敗。

### 產出目錄結構

```
lessons/<slug>/
├── topic.research.md          (Sprint 0001)
├── outline.md                 (Sprint 0002)
├── slides.md                  (Sprint 0002)
├── slides.html                (Sprint 0002 build)
├── narration/                 (Sprint 0003 /edu.narrate)
│   ├── slide-01.txt
│   ├── slide-02.txt
│   └── ...
├── audio/                     (Sprint 0003 /edu.narrate)
│   ├── slide-01.mp3
│   ├── slide-02.mp3
│   └── ...
└── dist/                      (Sprint 0003 /edu.render)
    └── <slug>.mp4
```

## 邊界案例

| 情境 | 處理方式 |
|---|---|
| slides.md 不存在 | /edu.narrate 中止，提示先跑 /edu.slides |
| slides.md 某頁沒有 speaker notes | 該頁 txt 寫「（無旁白）」，TTS 跑空字串會失敗 → 該頁 mp3 跳過，render 時用靜音段替代 |
| narration/ 或 audio/ 已存在 | /edu.narrate 中止，提示刪除後重跑 |
| slides.html 不存在但 slides.md 存在 | /edu.render 自動跑 build_slides.sh |
| audio/ 不存在 | /edu.render 中止，提示先跑 /edu.narrate |
| audio/ 與 slides 頁數不符 | /edu.render 中止，提示頁數不一致 |
| Edge-TTS 網路失敗 | synthesize_tts.py exit 1，/edu.narrate 回報哪幾頁失敗，不全部中止 |
| ffmpeg 不在 PATH | render_video.py exit 1 + 錯誤訊息 |
| Playwright / Chromium 未安裝 | render_video.py exit 1 + 提示安裝 |
| 某頁截圖失敗 | render_video.py 跳過並在 stderr 警示，最終 mp4 缺該頁 |

## ADR

### ADR-12：逐頁截圖 + ffmpeg 拼接，不用 Playwright 錄影

- **決策**：用 Playwright `page.screenshot()` 逐頁截靜態 PNG，再用 ffmpeg 把 PNG + mp3 合成影片段落 + concat。不用 Playwright `page.video` 錄螢幕。
- **原因**：
  1. `page.video` 需要精確控制每頁停留時間 = 音檔長度，時間同步在不同機器上 flaky
  2. 截圖 + ffmpeg 是確定性流程，結果可重現，不依賴渲染速度
  3. 犧牲的是 Marp transition 動畫——但 MVP 不需要 transition，硬切已夠用
- **替代方案**：Playwright page.video 全程錄（更自然但 flaky）。留給 Sprint 0004 polish。

### ADR-13：narrate 與 render 保持分離

- **決策**：`/edu.narrate` 和 `/edu.render` 是兩個獨立 skill，不合併。
- **原因**：老師可能想在 TTS 生成後先聽一遍、手動替換某幾頁的音檔、或用別的 TTS 工具重錄，再 render。合併會失去這個中途審閱窗口。
- **替代方案**：一個 `/edu.render` 做全部。被排除因為違反「階段化 + 可中斷審閱」。

### ADR-14：中間產物（frames/ segments/）render 後自動刪除

- **決策**：`render_video.py` 完成後刪除 `frames/` 和 `segments/`，只保留 `audio/` 和 `dist/`。
- **原因**：frames 和 segments 是純中間產物（幾十到幾百 MB），留著沒價值、佔空間。audio 保留因為老師可能要重聽或替換。dist 是最終產物。
- **替代方案**：全部保留。被排除因為每個 lesson 會多出 100+ MB 垃圾。
