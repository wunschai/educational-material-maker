---
name: edu.narrate
description: >
  教材製作 pipeline 的第四階段：從 slides.md 的 speaker notes 抽取逐頁講稿，
  並用 Edge-TTS 生成語音 mp3。產出 narration/*.txt + audio/*.mp3。
  Trigger: "/edu.narrate", "生成語音", "旁白", "narrate",
  "TTS", "配音", "edu.narrate"。
  簡報確認後的下一步，後續接 /edu.render。
---

# edu.narrate — 語音旁白

`/edu.narrate <slug> [--voice=<edge-tts-voice>]`

從 slides.md 的 speaker notes 生成逐頁語音。是 pipeline 的第四棒。

## 參數

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 指向有 `slides.md` 的 lesson |
| `--voice` | 否 | 依 `--lang` 自動選 | Edge-TTS voice ID（明確指定時覆蓋 `--lang` 的預設值） |
| `--lang` | 否 | `zh-TW` | 旁白語言。若與 slides.md 的 speaker notes 語言不同，main agent 會先翻譯再 TTS |
| `--subtitle-lang` | 否 | 不生成字幕 | 字幕語言。指定後會生成 `subtitles/<lang>.srt`。可與 `--lang` 不同實現雙語 |

### 語言 → 預設 Voice 對照

| `--lang` | 預設 Voice |
|---|---|
| `zh-TW` | `zh-TW-HsiaoChenNeural` |
| `en` | `en-US-AriaNeural` |
| `ja` | `ja-JP-NanamiNeural` |
| `ko` | `ko-KR-SunHiNeural` |

### 雙語範例

```bash
# 中文旁白 + 中文字幕（最基本）
/edu.narrate library-ethics --subtitle-lang=zh-TW

# 英文旁白 + 中文字幕（EMI 課程）
/edu.narrate library-ethics --lang=en --subtitle-lang=zh-TW

# 中文旁白 + 英文字幕
/edu.narrate library-ethics --lang=zh-TW --subtitle-lang=en
```

## 流程

### Step 1：前置檢查

1. `lessons/<slug>/slides.md` 存在？→ 不存在則中止：「請先跑 `/edu.slides`」
2. `lessons/<slug>/narration/` 或 `audio/` 已存在？→ **中止**：「narration/ 或 audio/ 已存在，請刪除後重跑」

### Step 2：解析 speaker notes

用 regex 從 slides.md 解析每頁的 speaker notes：

```
pattern: <!--\s*Speaker notes:\s*([\s\S]*?)-->
```

按 `---` 分頁符切成逐頁，每頁對應一個 speaker notes 區塊。

對每頁（從 slide-01 開始）：
- 有 speaker notes → 寫入 `narration/slide-NN.txt`
- 沒有 speaker notes → 寫入 `narration/slide-NN.txt`，內容為空字串（synthesize_tts.py 遇空字串會 skip）

### Step 2.5：翻譯（如果 `--lang` 與 speaker notes 原文語言不同）

如果使用者指定 `--lang=en` 但 speaker notes 是中文：

1. 對每頁 `narration/slide-NN.txt`，main agent 自己翻譯成目標語言
2. 翻譯後的文字覆寫同一個 txt（TTS 會讀翻譯後的版本）
3. **原文保留為 `narration/slide-NN.original.txt`**（字幕可能需要原文）

翻譯要求：口語化、適合朗讀、不是逐字翻譯。保持 speaker notes 的教學語調。

### Step 3：逐頁 TTS

決定 voice（`--voice` 明確指定 > `--lang` 對照表預設）。

對每個非空 `narration/slide-NN.txt`，呼叫：

```bash
py ${CLAUDE_PLUGIN_ROOT}/scripts/synthesize_tts.py <input> <output> --voice <voice>
```

如果某頁 TTS 失敗（exit 1）：記錄失敗頁碼，繼續處理其他頁。**不全部中止**。

### Step 3.5：生成字幕（如果有 `--subtitle-lang`）

1. 決定字幕來源文字：
   - `--subtitle-lang` == speaker notes 原文語言 → 用 `narration/slide-NN.original.txt`（或 `slide-NN.txt` 如果沒翻譯過）
   - `--subtitle-lang` != speaker notes 原文語言 且 != `--lang` → main agent 翻譯原文到字幕語言，存為 `narration/slide-NN.subtitle.txt`
   - `--subtitle-lang` == `--lang` → 直接用 `narration/slide-NN.txt`（旁白和字幕同語言）

2. 呼叫字幕生成腳本：

```bash
py ${CLAUDE_PLUGIN_ROOT}/scripts/generate_subtitles.py \
    lessons/<slug>/narration \
    lessons/<slug>/audio \
    lessons/<slug>/subtitles/<subtitle-lang>.srt
```

**注意**：如果字幕語言與旁白語言不同，需要先把字幕語言的文字寫入 `narration/slide-NN.txt`（臨時覆蓋），跑完字幕生成後再還原。或者修改 generate_subtitles.py 支援讀取 `.subtitle.txt` 後綴。

簡化做法：直接用 Bash 把所有 `.subtitle.txt`（或 `.original.txt`）臨時 rename 為 `.txt`，跑字幕，再還原。但這很 hacky。

**更好的做法**：generate_subtitles.py 加 `--text-suffix` 參數（預設空、`.original`、`.subtitle`），讓它讀 `slide-NN<suffix>.txt`。

### Step 4：回報

- narration 頁數 / audio 頁數（成功 / 失敗）
- 旁白語言 + voice
- 字幕語言 + SRT 路徑（如果有）
- 失敗清單（若有）
- **引導下一步**：
  - 有字幕：「`/edu.render <slug>` 會自動偵測 subtitles/ 並燒入字幕」
  - 無字幕：「`/edu.render <slug>`」

## 不做的事

- ❌ 不修改 slides.md
- ❌ 不跑 render（那是下一棒）
- ❌ 不靜默覆寫已存在的 narration/ 或 audio/
