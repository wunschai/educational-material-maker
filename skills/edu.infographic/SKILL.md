---
name: edu.infographic
description: >
  教材製作 pipeline 的選用階段：用 NotebookLM 把 slides 逐頁轉成資訊圖表。
  可選擇全部頁面或特定頁面。產出 infographics/slide-NN.png。
  Trigger: "/edu.infographic", "資訊圖表", "infographic",
  "用 NotebookLM 做圖", "edu.infographic"。
  slides 確認後的選用步驟。有 infographics/ 時 /edu.render 會優先使用它。
---

# edu.infographic — NotebookLM 資訊圖表

`/edu.infographic <slug> [--pages=all|1,3,5-8] [--style=professional]`

把 slides.md 的每一頁（或指定頁）送 NotebookLM 生成資訊圖表。

## 前置需求

- `nlm` CLI 已安裝且已登入（`nlm notebook list` 能列出 notebooks）
- `lessons/<slug>/slides.md` 存在
- `lessons/<slug>/topic.research.md` 存在

## 參數

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 指向有 slides.md + research.md 的 lesson |
| `--pages` | 否 | 由使用者互動決定 | `all` 全部頁，或 `1,3,5-8` 指定頁碼 |
| `--style` | 否 | 由使用者互動決定 | NotebookLM 風格（見下方清單） |

## 風格選項

| Style ID | 說明 | 適合 |
|---|---|---|
| `professional` | 商務專業風（**預設推薦**） | 大部分教材 |
| `instructional` | 教學指引風 | 步驟型/操作型課程 |
| `scientific` | 學術科學風 | 理工/醫學課程 |
| `bento_grid` | Bento 格狀排列 | 多概念並列比較 |
| `editorial` | 雜誌編輯風 | 人文/社會科學 |
| `sketch_note` | 手繪筆記風 | 輕鬆/創意課程 |

## 流程

### Step 1：前置檢查 + 互動確認

1. 檢查 `slides.md` 與 `research.md` 存在
2. 解析 slides.md，計算總頁數
3. 檢查 `infographics/` 是否已存在 → 存在則中止並提示
4. **用 AskUserQuestion 問使用者**：

   **問題 1**：要跑哪些頁？
   - 選項：「全部 N 頁」/「只跑章節封面頁」/「我指定頁碼」

   **問題 2**：風格？
   - 選項：`professional`（預設推薦）/ `instructional` / `scientific` / `bento_grid` / `editorial` / `sketch_note`

### Step 2：準備每頁的 source 材料

對每個要生成的頁面：

1. **大綱檔（核心 source）**：該頁 slide 的完整 markdown 內容（含標題、bullet、表格等），存為臨時檔 `tmp/slide-NN-outline.md`

2. **參考來源 source**：從 `topic.research.md` 擷取與該頁最相關的核心概念段落（100-200 字）。判斷依據：slide 內容提到哪些 research 概念 → 取那些概念的完整段落。存為 `tmp/slide-NN-reference.md`

3. **focus prompt**：組合成一句話，格式為：

   ```
   本頁是「<主題>」教學簡報的第 N 頁。核心內容是「<該頁標題/重點>」。
   請以大綱檔為核心結構，參考資料為補充，生成一張教學用資訊圖表。
   語言使用繁體中文。
   ```

### Step 3：逐頁呼叫 NotebookLM

對每個頁面，執行以下 Bash 流程（**注意：需要設定 `PYTHONIOENCODING=utf-8`**）：

```bash
export PYTHONIOENCODING=utf-8

# 1. 建 notebook
NOTEBOOK_ID=$(nlm notebook create "edu-slide-NN" 2>&1 | grep "ID:" | awk '{print $NF}')

# 2. 加 source：大綱（核心）
nlm source add "$NOTEBOOK_ID" --text tmp/slide-NN-outline.md

# 3. 加 source：參考資料
nlm source add "$NOTEBOOK_ID" --text tmp/slide-NN-reference.md

# 4. 生成 infographic
nlm infographic create "$NOTEBOOK_ID" \
    --style <使用者選的風格> \
    --orientation landscape \
    --detail standard \
    --language zh-TW \
    --focus "<focus prompt>" \
    --confirm

# 5. 輪詢等待完成（每 15 秒查一次，最多 3 分鐘）
for i in $(seq 1 12); do
    sleep 15
    STATUS=$(nlm studio status "$NOTEBOOK_ID" 2>&1 | grep '"status"' | head -1)
    if echo "$STATUS" | grep -q "completed"; then break; fi
done

# 6. 下載 PNG
nlm download infographic "$NOTEBOOK_ID" -o infographics/slide-NN.png

# 7. 刪除臨時 notebook
nlm notebook delete "$NOTEBOOK_ID" --confirm
```

### Step 4：進度回報

每完成一頁，向使用者回報：
```
✓ Slide 3/20 — 知識自由與反審查 (professional, 4.1 MB)
```

如果某頁失敗（timeout / API error），記錄失敗頁碼，繼續處理其他頁。最後列出失敗清單。

### Step 5：完成回報

- 成功/失敗頁數
- infographics/ 目錄下的檔案清單與總大小
- **引導下一步**：
  - 「infographic 就位。`/edu.render <slug>` 會自動偵測 infographics/ 並使用它取代截圖。」
  - 或「如果要先預覽，直接打開 infographics/ 下的 PNG 看看。」

## 與 /edu.render 的銜接

`/edu.render` 的 render_video.py 需要更新：

```python
# 偵測 infographics/ 是否存在
if (lesson_dir / "infographics").exists():
    # 使用 infographics/*.png 取代 Playwright 截圖
    frames_dir = lesson_dir / "infographics"
else:
    # 原有流程：Playwright 截圖
    screenshot_slides(...)
```

**注意**：infographics/ 的 PNG 解析度可能跟 1280x720 不同。render_video.py 需要在 ffmpeg 合成時加 `-vf scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2` 確保尺寸一致。

## 不做的事

- ❌ 不在沒有 `nlm` CLI 的環境強制跑（檢查 `nlm --version`，不存在就中止並提示安裝）
- ❌ 不靜默覆寫已存在的 infographics/
- ❌ 不跳過使用者確認（風格 + 頁碼都要問）
- ❌ 不保留臨時 notebook（用完即刪）

## 每頁大約耗時

- notebook create + source add：~5 秒
- infographic create + 等待完成：~60-90 秒
- download + cleanup：~5 秒
- **每頁合計約 70-100 秒**
- 20 頁全跑 ≈ 25-35 分鐘
