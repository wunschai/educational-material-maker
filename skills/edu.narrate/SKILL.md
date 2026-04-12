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
| `--voice` | 否 | `zh-TW-HsiaoChenNeural` | Edge-TTS voice ID |

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

### Step 3：逐頁 TTS

對每個非空 `narration/slide-NN.txt`，呼叫：

```bash
py scripts/synthesize_tts.py lessons/<slug>/narration/slide-NN.txt lessons/<slug>/audio/slide-NN.mp3 --voice <voice>
```

**注意**：`scripts/synthesize_tts.py` 的路徑在 main agent context 中是**相對於使用者 CWD**（因為 script 在 plugin 安裝目錄裡）。正確呼叫方式：

```bash
py ${CLAUDE_PLUGIN_ROOT}/scripts/synthesize_tts.py <input> <output> --voice <voice>
```

如果某頁 TTS 失敗（exit 1）：記錄失敗頁碼，繼續處理其他頁，最後在回報中列出失敗清單。**不全部中止**。

### Step 4：回報

- narration 頁數 / audio 頁數（成功 / 失敗）
- 失敗清單（若有）
- **引導下一步**：「語音生成完成。可以先聽幾頁 audio/ 下的 mp3 確認品質。下一步：`/edu.render <slug>`」

## 不做的事

- ❌ 不修改 slides.md
- ❌ 不跑 render（那是下一棒）
- ❌ 不靜默覆寫已存在的 narration/ 或 audio/
