---
name: edu.slides
description: >
  教材製作 pipeline 的第三階段：從 outline.md + topic.research.md 產出
  Marp 簡報 lessons/<slug>/slides.md（15-25 頁，含 speaker notes）。
  寫完後自動觸發 edu-reviewer 審查教學品質。
  Trigger: "/edu.slides", "做簡報", "產出 slides", "generate slides",
  "寫投影片", "edu.slides"。
  大綱確認後的下一步，後續接 /edu.narrate（Sprint 0003）或 build script。
---

# edu.slides — Marp 簡報

`/edu.slides <slug>`

從教學大綱與研究摘要產出 Marp 簡報。是 pipeline 的第三棒。寫完自動觸發 edu-reviewer。

## 前置閱讀

執行前先用 `Read` tool 讀 `${CLAUDE_PLUGIN_ROOT}/references/AGENTS.md`，特別是：

- §9 slides.md schema
- §10 edu-reviewer 審查維度
- §1 語系規則

> **路徑變數說明**：`${CLAUDE_PLUGIN_ROOT}` 指向 plugin 安裝目錄。**任何**提到 plugin 內部檔案的地方都要用此前綴，連 prompt 範本裡的也要。

## 參數解析

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 指向有 `outline.md` + `topic.research.md` 的 lesson |

## 流程

### Step 1：前置檢查

1. `lessons/<slug>/outline.md` 是否存在 → 不存在則中止：「請先跑 `/edu.outline <slug>`」
2. `lessons/<slug>/topic.research.md` 是否存在 → 不存在則中止：「請先跑 `/edu.research`」
3. `lessons/<slug>/slides.md` 是否已存在 → **存在則中止**：「slides.md 已存在，請刪除後重跑」

### Step 2：讀取來源

讀兩份檔案：
- `lessons/<slug>/outline.md` — 結構、學習目標、章節骨架、時長估
- `lessons/<slug>/topic.research.md` — 事實、引用、核心概念

### Step 3：在 context 內產出 Marp slides

**main agent 直接寫**（ADR-8：不走 subagent）。依照以下規則產出 slides.md：

#### Marp 結構

```markdown
---
marp: true
theme: default
paginate: true
---

# <Topic>

<副標題：課程名稱 / 適用對象 / 日期>

<!-- 
Speaker notes: 歡迎各位。今天我們要來學習 <Topic>。
-->

---

## <章節 1 標題>

<key message + 佐證>

<!-- 
Speaker notes: <2-3 句講課稿，解釋這張 slide 要怎麼講>
-->

---

...（更多 slides）...

---

## 引用來源

1. <來源 1> — <URL>
2. <來源 2> — <URL>
...
```

#### 產出規則

| 規則 | 要求 |
|---|---|
| **頁數** | 15-25 頁（含標題頁 + 引用頁）。超過 25 頁 → 自行裁剪合併，不要交出超頁版 |
| **每頁密度** | 1 個 key message + 佐證。不塞滿。寧可多分一頁也不要一頁塞兩個概念 |
| **每頁 speaker notes** | **必含** `<!-- Speaker notes: ... -->`，≥ 1 句話。這是 Sprint 0003 narration 的來源，現在就要寫好 |
| **章節分隔** | 用 `## <章節標題>` 起頭。對應 outline 的章節骨架，但不必 1:1 對應（一個 outline 章節可以展開成 2-3 張 slide） |
| **頁分配** | 參照 outline 的時長估。如果某章節佔 15 分鐘（全課 50 分鐘的 30%），那它應該佔 slides 的約 30% 頁數 |
| **引用** | 最後 1-2 頁 `## 引用來源` 列表。slide 內文用上標數字 `¹²³`，不用 footnote（Marp 不原生支援） |
| **學習目標覆蓋** | 每個 outline 學習目標至少有 1 張 slide 對應覆蓋（reviewer 會查） |
| **事實來源** | slides 的每個事實都應能追溯到 research.md。不要 hallucinate 新事實 |

#### 教學設計指引

- **開場**：標題頁 + 1 張「為什麼要學這個 / 這堂課你會學到什麼」（學習目標摘要）
- **每章節起手**：先給大圖（這一節要講什麼），再分 2-3 張 slide 拆解細節
- **結尾**：1 張「今天學了什麼」摘要 + 1-2 張引用來源
- **speaker notes 風格**：口語化但不失專業，像老師在課堂上「講話」的語調（「接下來我們來看…」「這邊要注意的是…」），不是 paper 風格

### Step 4：超頁防呆

產出完 markdown 後，數一數 `---` 分頁符 → 如果超過 25 頁：
- 找出最不關鍵的 slide（佐證/補充/例子類），合併或刪除
- 重數確認 ≤ 25
- 如果仍超過（章節太多、每章節都必要），在回報中加 `> ⚠️ slides 仍有 N 頁（超過 25 頁上限），建議手動裁剪`

### Step 5：寫檔

寫入 `lessons/<slug>/slides.md`。

### Step 6：自動觸發 edu-reviewer

寫完 slides 後，**自動**用 Task tool 呼叫 `edu-reviewer` subagent：

```
你是 edu-reviewer。

- slug: <slug>
- outline_path: lessons/<slug>/outline.md
- slides_path: lessons/<slug>/slides.md
- research_path: lessons/<slug>/topic.research.md

請依照 ${CLAUDE_PLUGIN_ROOT}/agents/edu-reviewer.md 的審查流程，
針對以下兩個維度審查 slides.md：
1. 學習目標覆蓋度：outline 的每個學習目標是否都有對應的 slide 覆蓋？
2. 內容正確性：slides 的事實敘述是否與 research.md 一致？有無 hallucinate？

回傳 review 報告（純 markdown），不修改任何檔案。
第一個字元必須是 # 標題。
失敗時回傳 REVIEW_FAILED: <原因> 開頭的單行字串。
```

### Step 7：呈現 review 結果

接收 reviewer 回傳後：

**reviewer 回傳 `REVIEW_FAILED:`**：告知使用者 review 失敗原因，不 retry。

**reviewer 回傳 review 報告**：

1. 把完整 review 報告呈現給使用者
2. 如果有 🔴 Critical 問題 → 用 AskUserQuestion 問使用者：「review 發現嚴重問題，要修改 slides.md 嗎？」
3. 如果只有 🟡 Important 或全綠 → 告知使用者，不強迫修改

### Step 8：回報

- slides 路徑
- 頁數
- reviewer 結果摘要（X 個目標覆蓋、Y 個 critical、Z 個 important）
- **引導下一步**：
  - 若有問題：「建議修改後重跑 `/edu.slides`（先刪除 slides.md）」
  - 若全綠：「slides + review 完成。可以用 `bash scripts/build_slides.sh lessons/<slug>/slides.md` 預覽 HTML。下一步（Sprint 0003）：`/edu.narrate <slug>`」

## 不做的事

- ❌ 不走 subagent 產出 slides（ADR-8）
- ❌ 不做 web search（事實只來自 research.md）
- ❌ 不靜默覆寫已存在的 slides.md
- ❌ 不處理圖片 / 影片嵌入
- ❌ 不解析 speaker notes 為音檔（那是 Sprint 0003 `/edu.narrate`）
- ❌ 不自動呼叫 build_slides.sh（使用者手動呼叫或等 Sprint 0003）

## Sprint 0002 註解

> **Sprint 0002: hardcoded slides schema. Future: profile-driven.**
>
> slides 的頁數範圍 (15-25)、密度規則、speaker notes 格式都是固定的。未來可能依「5 分鐘速講」vs「90 分鐘正課」而有不同 preset。見 spec.md ADR-9。
