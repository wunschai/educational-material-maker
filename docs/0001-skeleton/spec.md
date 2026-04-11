# Sprint 0001 — Skeleton

## 目標

建立 Educational Material Maker plugin 的最小可用骨架，並驗證「main agent → subagent → 落地檔案」的端到端流程。具體交付：

1. plugin metadata (`.claude-plugin/plugin.json`)
2. 一個 slash command：`/edu.research`
3. 一個 subagent：`edu-researcher`
4. 一份共用指令檔：`references/AGENTS.md`
5. 用一個 sample lesson（光合作用）跑通一次，產出 `lessons/photosynthesis/topic.research.md`

## 非目標

- 大綱、簡報、講稿、影片渲染（Sprint 0002+）
- 使用者上傳 PDF / 文字檔模式（`--from=files` 留待後續 sprint）
- 第三方 MCP server 整合（Sprint 0004）
- `edu-reviewer` subagent（Sprint 0002）
- 異常路徑的精緻錯誤訊息（happy path 為主，邊界案例只記錄處理方向）
- 自動測試（這個 sprint 的「測試」是手動跑一次 sample lesson）
- **Schema 動態化 / 多 profile 機制**：本 sprint 用單一固定 schema，後續會視需要引入「課程類型 → schema profile」的對應機制（例如 `intro` profile 不含「常見誤解」、`literature-survey` profile 加入「主要學派」段落）。詳見 ADR-6

## User Story

作為一個準備教某個主題的老師，
我想要在 Claude Code 中輸入 `/edu.research <topic>` 並等候幾分鐘，
就能在 `lessons/<slug>/topic.research.md` 拿到一份結構化的研究摘要（包含關鍵字、子問題拆解、5-8 個核心概念、引用清單），
以便我接下來能基於這份研究往大綱與簡報走，且不必擔心研究過程把 Claude 的對話 context 燒光。

### 驗收條件

- [ ] AC-1：執行 `/edu.research 光合作用` 後，main agent 會產生一個合理的英文 kebab-case slug（預期為 `photosynthesis` 或語義相近者），建立 `lessons/<slug>/` 資料夾，並寫入 `topic.research.md`。
- [ ] AC-2：執行 `/edu.research 光合作用 --slug=photosynthesis-101` 會以 `photosynthesis-101` 為資料夾名稱（明確指定永遠優先於自動生成）。
- [ ] AC-3：若 `lessons/<slug>/` 已存在 `topic.research.md`，slash command 會中止並提示使用者用 `--force` 才能覆寫；本 sprint 不需要實作 `--force`，但要實作中止行為。
- [ ] AC-4：`topic.research.md` 結構符合 §「介面/資料結構 — topic.research.md schema」所定義的章節順序與必填項。
- [ ] AC-5：研究內容包含 5-8 個核心概念，每個概念說明字數**目標 100-200 字**（zh-TW），硬性容忍範圍 **95-200 字**（容忍下限 95 為 xreview 後放寬，理由見 ADR-7），引用 5-10 件來源。
- [ ] AC-6：研究流程透過 `edu-researcher` subagent 執行（main agent 用 Task tool 派工，不在 main context 內直接做 web search）。
- [ ] AC-7：每個核心概念至少有一個 footnote 引用，引用區包含 URL 與存取日期。
- [ ] AC-8：plugin metadata (`.claude-plugin/plugin.json`) 完整，能被 `claude plugin add` 安裝（路徑指向本地目錄）。
- [ ] AC-9：以「光合作用」實際跑一次，產出檔案被人工驗收為「可拿去做下一階段大綱」的品質。

## 相關檔案

本 sprint 會新建：

| 路徑 | 用途 |
|---|---|
| `.claude-plugin/plugin.json` | Plugin metadata |
| `skills/edu.research/SKILL.md` | `/edu.research` slash command 定義 |
| `agents/edu-researcher.md` | Researcher subagent 定義（含 system prompt） |
| `references/AGENTS.md` | 共用指令檔（命名、輸出格式、語言預設） |
| `lessons/photosynthesis/topic.research.md` | Sample lesson 的 sprint 驗收產物 |

不會動到：

- `ddd-workflow/`（已 gitignore，純參考）
- `docs/`（DDD 文件包，本 sprint 只新增 spec.md/tasks.md/works.md）

## 介面 / 資料結構

### `/edu.research` slash command

**呼叫格式**：

```
/edu.research <topic> [--slug=<slug>] [--from=web]
```

**參數**：

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<topic>` | 是 | — | 研究主題，支援 zh-TW / en；若包含空白須加引號 |
| `--slug` | 否 | 由 main agent 從 topic 自動產生 kebab-case | 覆寫資料夾名稱 |
| `--from` | 否 | `web` | Sprint 0001 只支援 `web`；其他值會被拒絕 |
| `--depth` | — | — | **本 sprint 不開放**，內部固定為 `medium`（5-8 概念、5-10 引用）。`/edu.research --depth=...` 會被拒絕 |

**slug 自動生成規則**：

1. 主題若為英文：lowercase + 空白轉 `-` + 移除非 `[a-z0-9-]` 字元
2. 主題若為中文：main agent 翻譯成 1-3 個英文單字描述，套用上述規則
3. 結果若為空字串：fallback 為 `lesson-<YYYYMMDD-HHMM>`

**命令的執行流程**（main agent 視角）：

1. 解析參數，決定 `<slug>`
2. 檢查 `lessons/<slug>/topic.research.md` 是否已存在 → 存在則中止並提示
3. 建立 `lessons/<slug>/` 資料夾（若不存在）
4. 用 `Task` tool 呼叫 `edu-researcher` subagent，傳入 `{ topic, slug, depth: "medium" }`
5. 接收 subagent 回傳的 markdown 字串
6. 寫入 `lessons/<slug>/topic.research.md`
7. 回報給使用者：檔案路徑、概念數量、引用數量、引導下一步 `/edu.outline <slug>`

### `edu-researcher` subagent 契約

**輸入**（由 main agent 透過 Task tool 的 prompt 傳入）：

```
你是 edu-researcher。
- topic: <主題>
- slug: <slug>
- depth: medium

請依照 references/AGENTS.md 的研究流程產出 topic.research.md 內文。
直接回傳 markdown 內文（不要包在 code fence 裡，不要寫額外說明）。
```

**內部行為**：

1. **子問題拆解**：根據 topic 拆出 4-6 個子問題（涵蓋：定義、機制/原理、應用/實例、常見誤解、相關概念）
2. **逐一搜尋**：對每個子問題用 `WebSearch`，必要時用 `WebFetch` 取頁面細節
3. **去重彙整**：把搜到的事實按概念分組，目標 5-8 個核心概念
4. **撰寫**：依 schema 寫成 markdown，引用用 footnote 形式
5. **回傳**：純 markdown 字串

**輸出**：符合下面 schema 的 markdown 字串。

### topic.research.md schema

```markdown
# <Topic>

> **Slug**: <slug>
> **Generated**: <ISO 8601 timestamp>
> **Source mode**: web
> **Depth**: medium

## 學習關鍵字
- 關鍵字 1
- 關鍵字 2
- ...

## 子問題拆解
researcher 在搜集資料前先把主題拆成下列子問題作為探索方向：

1. 子問題一
2. 子問題二
...
（4-6 個）

## 核心概念

### 1. <概念名稱>

<100-200 字的 zh-TW 說明，鋪陳定義、機制或關鍵事實。每個事實以 footnote 引用佐證。> [^1][^2]

### 2. <概念名稱>

...

（5-8 個核心概念）

## 常見誤解（選填，若研究中發現）

- 誤解一：<說明> [^n]
- 誤解二：<說明>

## Open Questions

researcher 認為值得進一步釐清、但本輪未解決的問題：

- ...

## 引用

[^1]: <標題> — <URL>（accessed <YYYY-MM-DD>）
[^2]: <標題> — <URL>（accessed <YYYY-MM-DD>）
...
```

**Schema 必填項（Sprint 0001 固定 schema）**：

| 區段 | 必填？ | 備註 |
|---|---|---|
| H1 標題 | 必填 | 即主題名稱 |
| Metadata block | 必填 | slug / generated / source mode / depth |
| 學習關鍵字 | 必填 | |
| 子問題拆解 | 必填 | researcher 的探索路徑，過程透明用 |
| 核心概念 | 必填 | 至少 5、至多 8 |
| 常見誤解 | **選填** | 純介紹型主題若無典型誤解可省略 |
| Open Questions | **選填** | researcher 認為都答完了可省略 |
| 引用 | 必填 | 至少 5 條 footnote |

> **未來性提醒**：本 sprint 的「必填/選填」是寫死的單一 schema。未來的 schema profile 機制會讓「哪些段落是必填、哪些是選填、有沒有額外段落」隨課程類型變動。任何在 Sprint 0001 寫入這份 spec 的 schema 假設，未來都可能被 profile 覆寫——researcher 與後續 skills 的設計要避免把這些假設綁死在 prompt 裡。詳見 ADR-6。

### `.claude-plugin/plugin.json`

```json
{
  "name": "educational-material-maker",
  "description": "從主題生成研究摘要、教學大綱、Marp 簡報、TTS 旁白與帶旁白的教學影片。階段化的 Claude Code plugin。",
  "version": "0.1.0",
  "author": { "name": "TBD" },
  "license": "MIT",
  "keywords": ["education", "teaching", "slides", "marp", "tts"]
}
```

`author.name` 在 tasks 階段會請使用者填。

### `references/AGENTS.md`（內容大綱）

- 預設語系：zh-TW
- 引用格式：markdown footnote (`[^n]`)，引用區放底部，含 URL + 存取日期
- slug 規則（引述自 spec）
- 子 agent 使用原則：超過 5 個 web search 或 3 個 webfetch 一律走 subagent
- 不得在 main context 內直接展開大型搜尋結果

## 邊界案例

| 情境 | 處理方式 |
|---|---|
| Topic 過於模糊（例：「生物」） | researcher 仍照拆子問題流程跑，但 Open Questions 段落應明確指出「本主題範圍過廣，建議下次用更聚焦的子主題」 |
| Topic 找不到足夠來源 | 若引用 < 5 件，researcher 在輸出末尾加 `> ⚠️ 來源不足，僅找到 N 件引用，請考慮擴充或更換主題` |
| Slug 衝突 | 已存在 `topic.research.md` → 直接中止，提示使用者刪除舊檔或換 `--slug` |
| Slug 自動生成失敗（中文無法翻譯、空字串） | Fallback 為 `lesson-<YYYYMMDD-HHMM>` |
| `edu-researcher` subagent 回傳的 markdown 不符 schema（缺章節） | Main agent 偵測缺項時補加空章節並標 `> ⚠️ schema 缺項` 警示，**不重跑** subagent（避免無限迴圈）。本 sprint 視為已知限制 |
| 網路失敗 / WebSearch 工具錯誤 | 由 subagent 自行重試一次；仍失敗則回傳「研究失敗」訊息，main agent 不寫檔，回報使用者 |

## ADR

### ADR-1：研究階段強制走 subagent，main agent 不直接搜

- **決策**：`/edu.research` 必須透過 Task tool 派發給 `edu-researcher` subagent，main agent 不在自己的 context 內執行 WebSearch。
- **原因**：一輪研究會吃掉大量 search/fetch 結果，若塞在 main context 會把後續對話空間燒光。subagent 隔離 context，main agent 只接收整理後的 markdown。
- **替代方案**：main agent 直接搜（更簡單，但違背 sprint 目標——本 sprint 就是要驗證 subagent 機制能跑通）。

### ADR-2：研究輸出採用 markdown 而非 JSON

- **決策**：`topic.research.md` 是 markdown 檔，不是 JSON。
- **原因**：(a) 老師可以手改、(b) 後續 skills (`edu.outline`、`edu.slides`) 也是 LLM 處理，markdown 比 JSON 更不容易在交接時失真、(c) git diff 友善。
- **替代方案**：JSON（型別嚴謹但不利人工編輯，且 LLM 生成 JSON 更容易爛尾或結構不一致）。

### ADR-3：子問題拆解寫進 markdown 內、不只是內部 prompt

- **決策**：researcher 拆出的 4-6 個子問題會以 `## 子問題拆解` 區段保留在最終檔案中。
- **原因**：(a) 老師能看到 researcher 的探索路徑、判斷是否有遺漏；(b) 後續 outline 階段可以參照子問題決定章節節奏；(c) 這是「過程透明可追溯」的具體實踐。
- **替代方案**：子問題只用在 prompt、不寫入檔案（更乾淨，但失去可追溯性）。

### ADR-4：sprint 0001 不接 `--from=files`

- **決策**：本 sprint 只支援網路搜尋，使用者文件模式延後。
- **原因**：files 模式需要 PDF/text 解析、可能需要一個簡易 RAG 或 chunking 策略，會把 sprint 從「驗證骨架」變成「驗證骨架 + 驗證 ingest pipeline」，scope 失焦。
- **替代方案**：兩個都做（會把 sprint 撐爆，且失去 thin slice 的價值）。

### ADR-5：使用 marp 等本地工具的 wrapper script 在 Sprint 0001 不建立

- **決策**：`scripts/` 資料夾在本 sprint 不建立。
- **原因**：本 sprint 不做 slides 與渲染，無 marp/edge-tts/playwright/ffmpeg 的使用需求。Sprint 0002 才需要第一個 wrapper script。
- **替代方案**：先建空殼。違反 YAGNI。

### ADR-7：放寬核心概念字數下限 100 → 95（xreview 後加入）

- **決策**：核心概念字數從硬限 `100 ≤ words ≤ 200` 改為「目標 100-200，硬性容忍 95-200」。上限維持 200 不動。
- **觸發事件**：xreview 階段發現 `lessons/photosynthesis-101/topic.research.md` 概念 4 = 99 字（差 1 字），但內容品質已達教學可用程度。三個 sample 共 19 個概念，其中只有這 1 個越過下限、最大字數 165 遠未碰上限。
- **原因**：
  1. 100 是當初拍腦袋的整數，沒有教育學或語言學依據；99 vs 100 對教學可用性的差別是 zero。
  2. 把硬下限定得剛好等於目標下緣，等於要求 LLM 100% 命中目標下緣，不留任何裁剪/重寫的空間。實務上 LLM 在 95-100 區間的判斷常常不穩定。
  3. 上限沒被破過（最大 165），維持 200 即可，不需要對稱放寬到 ±5%。
- **本次同步修補**：`references/AGENTS.md` §4 表格、`agents/edu-researcher.md` 第四步「硬性上限」表都同步改為 `95-200`，並標註目標仍是 100-200。
- **替代方案**：
  1. 對稱放寬為 [95, 210] —— 沒必要，上限沒問題。
  2. 維持 100，手動補字到 photosynthesis-101 概念 4 —— 治標不治本，下次仍會在邊緣翻車。

### ADR-6：Sprint 0001 採用單一固定 schema，未來引入 schema profile 機制

- **決策**：Sprint 0001 的 `topic.research.md` schema 是寫死的（章節、必填規則、概念數量範圍）。未來 sprint 會引入 schema profile / template 機制——讓不同課程類型（純介紹、概念講解、文獻綜述、操作教學、議題討論…）能套用不同 schema。
- **原因**：
  1. 課程設計本身彈性極大，「常見誤解」對純介紹型課程是冗段，對概念講解卻是必要關卡；單一 schema 終究會卡住部分使用情境。
  2. 但**第一個 sprint 就引入 profile 機制會把 scope 從「驗證骨架」變成「驗證骨架 + 設計擴充點」**，反而拖累驗證速度。
  3. 折衷做法：固定 schema 跑通一次、把 profile 機制當作後續 sprint 的明確項目（很可能是 Sprint 0002 或獨立 sprint），並要求本 sprint 的 prompt / 程式碼**不要把 schema 假設寫死到無法替換**——讓未來引入 profile 時的改動控制在可接受範圍。
- **本 sprint 的具體約束**（防止被 profile 機制反噬）：
  - `edu-researcher` 的 system prompt 中，schema 描述應放在 prompt 的可替換段落（例如以「`<SCHEMA>...</SCHEMA>`」標示），方便未來抽出成 profile
  - Schema 的「必填項」清單寫在 `references/AGENTS.md`，不是寫死在 subagent 的程式碼裡（如果有的話）
  - 任何引用、處理 schema 的地方都要加 inline 註解：「Sprint 0001: hardcoded schema. Future: profile-driven.」
- **替代方案**：
  1. **本 sprint 直接做 profile 機制**：scope 失焦，違反 thin slice 原則。
  2. **永遠固定 schema**：違背使用者明確訴求（課程設計要彈性）。
