---
name: edu.research
description: >
  教材製作 pipeline 的第一階段：根據主題進行結構化研究，產出
  lessons/<slug>/topic.research.md，包含學習關鍵字、子問題拆解、
  5-8 個核心概念、5-10 條引用。研究工作強制透過 edu-researcher subagent
  執行，避免在 main agent context 內展開大量搜尋結果。
  Trigger: "/edu.research", "研究主題", "幫我研究", "備課第一步",
  "prepare a lesson research", "investigate a topic for teaching",
  "edu.research"。
  老師備課的起點，後續接 /edu.outline。
---

# edu.research — 主題研究

`/edu.research <topic> [--slug=<slug>] [--from=web]`

從主題到一份結構化研究 markdown。是 Educational Material Maker 五階段 pipeline 的第一棒。

> **Sprint 0001 範圍**：本 skill 在 Sprint 0001 只支援 `--from=web`。`--from=files` 與 `--depth` 在後續 sprint 開放。

## 前置閱讀

執行任何邏輯前，**必須**先用 `Read` tool 讀取 `${CLAUDE_PLUGIN_ROOT}/references/AGENTS.md`，特別是：

- §3 Slug 自動生成規則
- §4 Schema 必填項清單（schema 規則的 SSOT）
- §5 Subagent 使用原則

> **路徑變數說明**：`${CLAUDE_PLUGIN_ROOT}` 是 Claude Code 自動展開的環境變數，指向本 plugin 的安裝目錄。所有引用 plugin 內部檔案的地方都應該用這個變數，**不要**寫成相對路徑——main agent 的 CWD 是使用者專案，不是 plugin 目錄。

## 參數解析

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<topic>` | 是 | — | 研究主題；含空白須加引號 |
| `--slug=<value>` | 否 | 自動生成 | 覆寫資料夾名稱 |
| `--from=<value>` | 否 | `web` | **本 sprint 只接受 `web`**，其他值（如 `files`）一律拒絕並回報「Sprint 0001 不支援」 |
| `--depth=<value>` | — | — | **本 sprint 不開放**。若使用者傳入，回報「Sprint 0001 固定為 medium，--depth 在後續 sprint 開放」 |

解析失敗（缺 topic、未知參數、`--from` 值非 `web`、出現 `--depth`）→ 立即中止並向使用者回報具體錯誤，**不**進入後續流程。

## 流程

### Step 1：決定 slug

- 若使用者提供 `--slug=<value>`：直接採用。檢查值是否含路徑分隔符（`/`、`\`）或非法檔名字元（`:`、`*`、`?`、`"`、`<`、`>`、`|`），若有則回報錯誤要求使用者重下。
- 若沒有：依 `${CLAUDE_PLUGIN_ROOT}/references/AGENTS.md` §3 三步驟自動生成。
  1. 主題為英文：lowercase + 空白轉 `-` + 移除非 `[a-z0-9-]` 字元
  2. 主題為中文/其他：翻譯為 1-3 個英文單字描述後套用步驟 1
  3. 結果為空字串或無法生成：fallback 為 `lesson-<YYYYMMDD-HHMM>`（時間取本地當下）

決定後，把 slug 顯示給使用者作為流程開始的第一個訊息（讓使用者立即知道資料夾位置）。

### Step 2：衝突檢查（中止優先）

檢查 `lessons/<slug>/topic.research.md` 是否已存在：

- **存在**：立即中止整個流程。回報訊息應包含：
  - 既有檔案的完整路徑
  - 提示：「請刪除舊檔，或使用 `--slug=<新名稱>` 重新執行」
  - **不**靜默覆寫
  - **不**實作 `--force` 旗標（Sprint 0001 範圍外）
- **不存在**：建立 `lessons/<slug>/` 資料夾（若不存在），繼續 Step 3。

### Step 3：派工到 `edu-researcher` subagent

**強制走 subagent**——這是 spec.md ADR-1 的硬規定。main agent **不**在自己的 context 內執行 `WebSearch` / `WebFetch`。

#### 派工前：取得當下 ISO 8601 timestamp

派工前 main agent **必須**取得當下時間作為 `generated_at` 傳給 subagent，避免 subagent 用 placeholder 時間污染 metadata。可用：

```bash
py -c "from datetime import datetime, timezone; print(datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds'))"
```

或等價的 PowerShell / date 指令。取得結果範例：`2026-04-11T19:30:42+08:00`。

#### Task tool 呼叫

用 `Task` tool 呼叫 `edu-researcher`，傳入下面 prompt 範本（**注意 `generated_at` 是必填欄位**）：

```
你是 edu-researcher。

- topic: <使用者提供的原始主題字串>
- slug: <Step 1 決定的 slug>
- depth: medium
- generated_at: <當下 ISO 8601 timestamp，main agent 帶入>

請依照 ${CLAUDE_PLUGIN_ROOT}/references/AGENTS.md §4 的 schema 必填項清單與
${CLAUDE_PLUGIN_ROOT}/agents/edu-researcher.md 中的研究流程，產出 topic.research.md 內文。

Metadata block 的 Generated 欄位必須使用上面傳入的 generated_at 值，
不要自行猜測時間、不要用 placeholder（例如 00:00:00）。

直接回傳 markdown 字串：
- 不要包在 code fence 裡
- 不要前後加說明文字
- 第一個字元必須是 H1 標題的 `# `
- 失敗時回傳 RESEARCH_FAILED: <原因> 或 RESEARCH_REFUSED: <原因> 開頭的單行字串

撰寫前請務必閱讀 agents/edu-researcher.md 的「硬性上限」段——
核心概念數 ∈ [5, 8]，每段字數 ∈ [100, 200]，引用數 ∈ [5, 10]，
任一超界就裁剪後再輸出，不要交付超界版本。
```

派工後等待 subagent 回傳。

### Step 4：接收與 schema 防呆

**先檢查失敗訊號**：

- 回傳值以 `RESEARCH_FAILED:` 開頭 → 不寫檔。向使用者回報失敗原因。流程結束。
- 回傳值以 `RESEARCH_REFUSED:` 開頭 → 不寫檔。向使用者回報拒絕原因。流程結束。

**否則進入 schema 防呆**：

依 `${CLAUDE_PLUGIN_ROOT}/references/AGENTS.md` §4 的必填項清單檢查回傳的 markdown 是否含以下段落（清單為了方便已內嵌於下方）：

1. H1 標題（首行 `# `）
2. Metadata block（`> **Slug**:` 等四行）
3. `## 學習關鍵字`
4. `## 子問題拆解`
5. `## 核心概念`
6. `## 引用`

（「常見誤解」與「Open Questions」為選填，不檢查）

**缺項處理**（Sprint 0001 規則：補空段 + 警示，不重跑 subagent，避免無限迴圈）：

- 對每個缺項，在合適位置插入空章節並加警示：

  ```markdown
  ## 學習關鍵字

  > ⚠️ schema 缺項：學習關鍵字 — researcher 未產出本段，請手動補充
  ```

- 在檔案最末（`## 引用` 之後）追加一行總警示：

  ```markdown
  > ⚠️ 本檔由 schema 防呆補齊，缺項數：N。請手動審閱 N 個 ⚠️ 標記處。
  ```

> 這個防呆機制是 spec.md §邊界案例「subagent 回傳不符 schema」的明確要求。**重要：不重跑 subagent**——避免無限迴圈，缺項由人工修補。

### Step 5：寫檔

把（可能補過的）markdown 字串寫入 `lessons/<slug>/topic.research.md`。

### Step 6：回報使用者

向使用者回報以下資訊：

- 檔案路徑（`lessons/<slug>/topic.research.md`）
- 概念數量（從 `## 核心概念` 段抓 `### N. ` 計數）
- 引用數量（從 `## 引用` 段抓 `[^N]:` 計數）
- 是否觸發 schema 防呆（若有，提示使用者檢視 ⚠️ 標記）
- 是否觸發邊界案例（若有「來源不足」警示，提示使用者）
- **引導下一步**：「研究完成。下一步請執行 `/edu.outline <slug>` 拆教學大綱。」

## 不做的事

- ❌ 不在 main context 內執行 `WebSearch` / `WebFetch`（必走 subagent）
- ❌ 不靜默覆寫既有 `topic.research.md`
- ❌ 不重跑 subagent 來修 schema 缺項（補空段 + 警示即可）
- ❌ 不實作 `--force`、`--depth`、`--from=files`（Sprint 0001 範圍外）
- ❌ 不建立 `lessons/<slug>/` 以外的任何檔案

## Sprint 0001 註解

> **Sprint 0001: hardcoded schema. Future: profile-driven.**
>
> 本 skill 的 Step 4 schema 防呆檢查目前對固定的 6 個必填段做檢查。未來引入 schema profile 機制後，這份檢查清單會改為動態讀取（依當前課程類型決定哪些段落必填）。任何人在這裡新增 hardcoded 的段落判斷時，請保留這條未來性提醒。

## 對應 spec

本 skill 對應 `docs/0001-skeleton/spec.md` 的：

- §介面 — `/edu.research` slash command
- AC-1〜AC-3、AC-6（強制 subagent）、AC-9（人工品質驗收的前提）
- §邊界案例 中的「slug 衝突」「slug 自動生成失敗」「subagent 回傳不符 schema」「網路失敗」
- ADR-1（強制 subagent）、ADR-3（子問題拆解寫入輸出）、ADR-4（不接 files）、ADR-6（schema 動態化未來工作）
