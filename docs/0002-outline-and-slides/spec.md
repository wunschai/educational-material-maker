# Sprint 0002 — Outline and Slides

## 目標

延伸 Sprint 0001 的 pipeline，從「研究摘要」走到「可預覽的簡報 + 品質審查報告」。具體交付：

1. `/edu.outline <slug> [--level=basic|standard|full]` — 從 research 產出教學大綱
2. `/edu.slides <slug>` — 從 outline + research 產出 Marp slides + 自動觸發 reviewer
3. `edu-reviewer` subagent（簡化版）— 審查學習目標覆蓋度 + 內容正確性
4. `scripts/build_slides.sh` — Marp-cli wrapper，把 slides.md 編成 HTML/PDF
5. 端到端驗收：sample lesson 跑完 research → outline → slides → build → review

## 非目標

- narration / TTS / 影片渲染（Sprint 0003）
- 圖片生成或搜圖功能（Sprint 0004 polish）
- Schema profile registry / config-driven profile 機制（`--level` 用 inline preset，見 ADR-9）
- edu-reviewer 進階維度：教學節奏、認知負荷、視覺設計、引用一致性（留待後續 sprint）
- slides 主題 (theme) 客製化 UI（使用者手改 frontmatter 即可）
- `--force` 覆寫旗標（同 Sprint 0001，衝突一律中止）

## User Story

### Story 1：產出教學大綱

作為一個已經有 `topic.research.md` 的老師，
我想要在 Claude Code 中輸入 `/edu.outline <slug>` 並選擇詳細度（basic / standard / full），
就能在 `lessons/<slug>/outline.md` 拿到一份以學習目標為核心的教學大綱，
以便我審閱結構後再進到簡報階段、或手改大綱調整教學節奏。

### Story 2：產出簡報

作為一個已經有 `outline.md` 的老師，
我想要在 Claude Code 中輸入 `/edu.slides <slug>`，
就能在 `lessons/<slug>/slides.md` 拿到 15-25 頁的 Marp 簡報（含 speaker notes），
並自動收到一份教學品質 review 報告，
以便我在瀏覽器或 PDF 中預覽簡報、根據 review 結果修改後拿去上課。

### Story 3：品質審查

作為老師，
我不想手動呼叫 reviewer——我希望 `/edu.slides` 寫完 slides 後自動跑品質審查，
讓我只需要看一份「哪些學習目標被漏掉 / 哪些事實跟研究不一致」的報告就好。

### 驗收條件

- [ ] AC-1：執行 `/edu.outline <slug>` 後，main agent 讀 `lessons/<slug>/topic.research.md`，以 `basic` 為預設 level，產出 `lessons/<slug>/outline.md`，schema 符合 §outline.md schema (basic)。
- [ ] AC-2：執行 `/edu.outline <slug> --level=standard` 與 `--level=full` 各一次，產出的 outline.md 分別包含 standard / full 規定的額外段落（先備知識、教學方法、評量等）。
- [ ] AC-3：若 `lessons/<slug>/outline.md` 已存在，`/edu.outline` 中止並提示使用者。不靜默覆寫。
- [ ] AC-4：執行 `/edu.slides <slug>` 後，main agent 讀 `outline.md` + `topic.research.md`，產出 `lessons/<slug>/slides.md`，內容為合法 Marp markdown（`marp: true` frontmatter + `---` 分頁），頁數在 15-25 頁。
- [ ] AC-5：`slides.md` 每張 slide 都在 Marp comment block `<!-- ... -->` 內含 speaker notes（≥ 1 句話）。
- [ ] AC-6：`/edu.slides` 寫完 `slides.md` 後，main agent 自動透過 Task tool 呼叫 `edu-reviewer` subagent，不需使用者手動觸發。
- [ ] AC-7：`edu-reviewer` 回傳的 review 報告包含兩個維度的逐項審查結果：(a) 學習目標覆蓋度 (b) 內容正確性。報告格式符合 §edu-reviewer 輸出格式。
- [ ] AC-8：`scripts/build_slides.sh` 接收 `slides.md` 路徑，輸出 HTML 到 `lessons/<slug>/slides.html`（或 PDF 到 `slides.pdf`），exit code 0。
- [ ] AC-9：以一個 sample lesson 跑完 `/edu.research` → `/edu.outline` → `/edu.slides` → `scripts/build_slides.sh` 全鏈，最終產出可在瀏覽器預覽的 `slides.html`。

## 相關檔案

本 sprint 會新建：

| 路徑 | 用途 |
|---|---|
| `skills/edu.outline/SKILL.md` | `/edu.outline` slash command |
| `skills/edu.slides/SKILL.md` | `/edu.slides` slash command（含 reviewer 自動觸發） |
| `agents/edu-reviewer.md` | 教學品質審查 subagent |
| `scripts/build_slides.sh` | Marp-cli wrapper |

會修改：

| 路徑 | 修改原因 |
|---|---|
| `references/AGENTS.md` | 新增 outline.md / slides.md schema 規則 + edu-reviewer 審查維度 |

## 介面 / 資料結構

### `/edu.outline` slash command

**呼叫格式**：

```
/edu.outline <slug> [--level=basic|standard|full]
```

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 必須指向已存在的 `lessons/<slug>/topic.research.md` |
| `--level` | 否 | `basic` | 教學大綱詳細度 preset |

**流程**：

1. 檢查 `lessons/<slug>/topic.research.md` 是否存在 → 不存在則中止並提示先跑 `/edu.research`
2. 檢查 `lessons/<slug>/outline.md` 是否已存在 → 存在則中止（同 Sprint 0001 衝突規則）
3. 讀 `topic.research.md`
4. 根據 `--level` 選擇對應 preset schema
5. 以 main agent context 直接產出 outline.md（不走 subagent）
6. 寫入 `lessons/<slug>/outline.md`
7. 回報：檔案路徑、level、學習目標數、章節數、引導 `/edu.slides <slug>`

### outline.md schema

#### basic（預設）

```markdown
# <Topic> — 教學大綱

> **Slug**: <slug>
> **Level**: basic
> **Generated**: <ISO 8601>
> **Based on**: topic.research.md

## 學習目標
- <以 Bloom's 動詞開頭的目標 1>
- <目標 2>
- <目標 3>
（3-5 條）

## 章節骨架

### 1. <章節名稱>（約 X 分鐘）
- 重點：<概述>
- 對應研究概念：<research.md 的概念 N 標題>

### 2. ...
（4-7 章節）

## 預估總時長
約 XX 分鐘
```

#### standard

basic 所有段落 + 以下新增：

```markdown
## 先備知識
- <學生需要先知道的 1>
- <學生需要先知道的 2>
```

每個章節骨架項下新增：
```markdown
- 教學方法：講述 / 討論 / 實作 / 示範
```

#### full

standard 所有段落 + 以下新增：

```markdown
## 評量方式
- 形成性評量：<說明>
- 總結性評量：<說明>

## 教學資源
- <資源 1>（<來源>）
- <資源 2>（<來源>）

## 延伸學習
- <進階主題 1>
- <補充閱讀 1>
```

### `/edu.slides` slash command

**呼叫格式**：

```
/edu.slides <slug>
```

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 必須指向有 `outline.md` 與 `topic.research.md` 的 lesson |

**流程**：

1. 檢查 `lessons/<slug>/outline.md` 與 `topic.research.md` 是否都存在 → 缺一則中止並提示
2. 檢查 `lessons/<slug>/slides.md` 是否已存在 → 存在則中止
3. 讀 `outline.md` + `topic.research.md`
4. 以 main agent context 直接產出 slides.md（不走 subagent）
5. 寫入 `lessons/<slug>/slides.md`
6. **自動觸發 edu-reviewer**（Step 7）
7. 用 Task tool 呼叫 `edu-reviewer`，傳入 slug，等回傳
8. 呈現 review 報告給使用者
9. 回報：slides 路徑、頁數、reviewer 結果摘要、引導 build 或修改

### slides.md schema

```markdown
---
marp: true
theme: default
paginate: true
---

# <Topic>

<副標題 / 課程名稱>

---

## <章節 1 標題>

<!-- 
Speaker notes: <2-3 句講課稿>
-->

<slide 內容：1 個 key message + 佐證>

---

## <章節 1 — 細節>

<!-- 
Speaker notes: <2-3 句講課稿>
-->

<slide 內容>

---

...

---

## 引用來源

1. <來源 1> — <URL>
2. <來源 2> — <URL>
...
```

**規則**：

| 項目 | 規格 |
|---|---|
| 頁數 | 15-25（含標題頁 + 引用頁） |
| 每頁 key message | 1 個 |
| Speaker notes | 每頁必含 `<!-- Speaker notes: ... -->`，≥ 1 句話 |
| 引用 | 最後 1-2 頁列出，slide 內用上標數字 `¹²³` |
| Frontmatter | `marp: true`, `theme: default`, `paginate: true` |
| 分頁符 | `---`（Marp 標準） |

### `edu-reviewer` subagent 契約

**輸入**（由 main agent 透過 Task tool prompt 傳入）：

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
```

**輸出格式**：

```markdown
# 教學品質 Review — <Topic>

## 總評
<可以用 / 建議修正 / 有嚴重問題>

## 學習目標覆蓋度
| 學習目標 | 對應 Slide | 覆蓋狀態 |
|---|---|---|
| <目標 1> | Slide 3, 4 | ✅ 覆蓋 |
| <目標 2> | — | ❌ 未覆蓋 |
| ... | ... | ... |

覆蓋率：X / Y（百分比）

## 內容正確性
| 問題 | Slide | 嚴重度 | 說明 |
|---|---|---|---|
| <問題描述> | Slide N | 🔴 Critical / 🟡 Important | <與 research 的差異> |

若無問題：「✅ 所有事實敘述與 research.md 一致」

## 建議
- <具體修改建議 1>
- <具體修改建議 2>
```

### `scripts/build_slides.sh`

```bash
#!/bin/bash
# 用法: ./scripts/build_slides.sh <slides.md path> [--pdf]
# 輸出: 同目錄下的 slides.html（或 --pdf 時 slides.pdf）
# 依賴: npx @marp-team/marp-cli
# Exit code: 0 成功 / 非 0 失敗
```

| 參數 | 說明 |
|---|---|
| `$1` | slides.md 的完整路徑 |
| `--pdf` | 選填。加上後輸出 PDF 而非 HTML |

**內部邏輯**：

```bash
npx @marp-team/marp-cli "$1" -o "${1%.md}.html"
# 或 --pdf 時:
npx @marp-team/marp-cli "$1" --pdf -o "${1%.md}.pdf"
```

## 邊界案例

| 情境 | 處理方式 |
|---|---|
| `lessons/<slug>/` 不存在 | `/edu.outline` 與 `/edu.slides` 中止，提示先跑 `/edu.research` |
| `topic.research.md` 不存在 | 同上 |
| `outline.md` 不存在（跑 /edu.slides 時） | 中止，提示先跑 `/edu.outline` |
| `outline.md` 已存在（跑 /edu.outline 時） | 中止，提示使用者刪除或手改 |
| `slides.md` 已存在（跑 /edu.slides 時） | 中止，提示使用者刪除或手改 |
| `--level` 值不在 basic/standard/full 中 | 拒絕並列出合法值 |
| `topic.research.md` 被手改到 schema 損壞 | main agent best-effort 讀取，缺項段落忽略，在 outline 內標 `> ⚠️ research 缺少 <段名>` |
| marp-cli 未安裝（npm / npx 不在 PATH） | `build_slides.sh` exit code 非 0，main agent 回報使用者需安裝 Node.js + marp-cli |
| slides.md 超過 25 頁 | main agent 自行裁剪到 25 頁以內再寫檔。如果無法裁剪（太多章節），在回報中加警示 |
| edu-reviewer 回傳全綠（無問題） | main agent 回報「review 通過，可進下一步」 |
| edu-reviewer 回傳有 Critical 問題 | main agent 呈現報告，用 AskUserQuestion 問使用者要修改還是忽略 |
| edu-reviewer 回傳 `REVIEW_FAILED:` | main agent 不 retry，告知使用者 review 失敗原因 |

## ADR

### ADR-8：outline + slides 由 main agent 直接寫，不走 subagent

- **決策**：`/edu.outline` 與 `/edu.slides` 都在 main agent context 內完成，不派 subagent。
- **原因**：
  1. 兩者都不做 web search（不觸發 AGENTS.md §5 的 subagent 門檻）
  2. 輸入量小（research < 5K 字 + outline < 3K 字），15-25 頁 slides 產出量 ≈ 5-8K 字，main context 可消化
  3. 走 main agent 保留了「老師中途問問題、要求修改」的互動窗口——subagent 跑完才回來就沒互動可能
- **替代方案**：slides 走 `edu-slide-author` subagent（隔離 context）。被排除因為 15-25 頁不值得 subagent 開銷，且犧牲互動性。

### ADR-9：`--level` 用 inline preset，不引入 profile registry

- **決策**：3 個 level（basic / standard / full）的 schema 以 inline preset 寫在 SKILL.md 內，不建立 `profiles/` 目錄或 config-driven 機制。
- **原因**：
  1. 3 個固定 preset 完全可以 hardcode，引入 profile registry 是 over-engineering
  2. ADR-6（Sprint 0001）把 schema profile 機制列為「未來工作」；現在只是增量引入 `--level` arg，不需要完整機制
  3. 未來真的需要動態 profile 時，從 inline 抽出來成本可控（< 1 小時工作量）
- **替代方案**：引入 `references/outline-profiles/basic.md` / `standard.md` / `full.md` 目錄結構。被排除因為 YAGNI。

### ADR-10：speaker notes 預留在 slides.md，Sprint 0002 不解析

- **決策**：`slides.md` 每張 slide 在 Marp comment block `<!-- Speaker notes: ... -->` 內附 2-3 句講課稿。Sprint 0002 只「寫進去」，Sprint 0003 的 `/edu.narrate` 才「解析出來」餵 Edge-TTS。
- **原因**：把 narration 的文字來源從 slides.md 開始就定義好，Sprint 0003 接手時不需要重新設計格式或重跑 slides。
- **替代方案**：Sprint 0002 不寫 speaker notes，Sprint 0003 另外生成 `narration/*.md`。被排除因為這樣 Sprint 0003 得重讀 slides + research 兩份檔案才能寫講稿，重複工作。

### ADR-11：edu-reviewer 簡化版（2 維度）

- **決策**：Sprint 0002 的 edu-reviewer 只審查 (a) 學習目標覆蓋度 (b) 內容正確性。不審查教學節奏、認知負荷、視覺設計、引用一致性。
- **原因**：
  1. MVP 階段 2 個維度已經夠老師判斷「slides 能不能用」
  2. 教學節奏、認知負荷等進階維度需要更複雜的 prompt 設計與更多 context（可能要讀教育心理學參考），不值得在 Sprint 0002 投入
  3. 簡化版讓我們先驗證「reviewer subagent 機制本身可行」（Sprint 0001 教訓：先驗機制再擴功能）
- **替代方案**：完整版 reviewer（5+ 維度）。被排除因為 scope creep。
