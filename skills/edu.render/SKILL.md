---
name: edu.render
description: >
  ��材製作 pipeline 的第五（最後）階段：從 slides.html + audio/ 渲染
  帶旁白的 mp4 教學影片。Playwright 逐頁截圖 + ffmpeg 合成。
  Trigger: "/edu.render", "渲染影片", "render video", "出影片",
  "合成 mp4", "edu.render"。
  語音確認後的最後一步。MVP pipeline 的終點���
---

# edu.render — 影片渲染

`/edu.render <slug> [--resolution=1280x720]`

從簡報截圖 + 語音旁白合成帶旁白的 mp4。是 pipeline 的最後一棒。**MVP 的終點。**

## 參數

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 指向有 `slides.html`（或 `slides.md`）+ `audio/` 的 lesson |
| `--resolution` | 否 | `1280x720` | 輸出解析度 WxH |

## 流程

### Step 1：前置檢查

1. `lessons/<slug>/audio/` 存在且有 mp3？→ 不存在則中止：「請先跑 `/edu.narrate`」
2. `lessons/<slug>/dist/` 已存在？→ **中止**：「dist/ 已存在，請刪除後重跑」
3. `lessons/<slug>/slides.html` 存在？→ 不存在但 `slides.md` 存在 → **自動跑 build**：

```bash
bash ${CLAUDE_PLUGIN_ROOT}/scripts/build_slides.sh lessons/<slug>/slides.md
```

若 build 也失敗 → 中止。

### Step 2：呼叫 render script

```bash
py ${CLAUDE_PLUGIN_ROOT}/scripts/render_video.py \
    lessons/<slug>/slides.html \
    lessons/<slug>/audio \
    lessons/<slug>/dist/<slug>.mp4 \
    --resolution <resolution>
```

等待完成。script 內部流程：
1. Playwright 截圖 → frames/slide-NN.png
2. ffmpeg 逐段合成 → segments/seg-NN.mp4
3. ffmpeg concat → dist/<slug>.mp4
4. 自動清理 frames/ 和 segments/

### Step 3：驗證產出

- `dist/<slug>.mp4` 存在？
- 檔案大小 > 0？
- 用 ffprobe 取 duration（可選，若 ffprobe 可用）

### Step 4：回報

- mp4 路徑
- 檔案大小
- 時長（若可取得）
- **MVP 完成訊息**：

> 🎬 教學影片完成！
>
> 檔案：`lessons/<slug>/dist/<slug>.mp4`
>
> 這份教材是從「`/edu.research <topic>`」開始，經過大綱、簡報、語音、渲染五個階段產出的。
> 完整的 pipeline 已跑通。
>
> 如果要做另一個主題，再跑一次 `/edu.research <new-topic>` 就行。

## 不做的事

- ❌ 不用 Playwright page.video 錄影（ADR-12：截圖 + ffmpeg）
- ❌ 不加 transition / fade（MVP 硬切）
- ❌ 不加字幕 / SRT
- ❌ 不加背景音樂
- ❌ 不靜默覆寫已存在的 dist/
- ❌ 不上傳到任何外部服務
