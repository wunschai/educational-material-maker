# Sprint 0001 — Skeleton（plugin 骨架 + 第一個 thin slice）

## 背景 (Background)

Educational Material Maker 是一個全新的 Claude Code plugin。第一個 sprint 不追求完整功能，而是要證明三件事：

1. plugin 機制可行——`.claude-plugin/plugin.json` + `skills/` + `agents/` 可以正確被 Claude Code 載入。
2. 「主題 → 中介檔案」的單向流可行——使用者跑 `/edu.research <topic>`，能拿到一份結構化的研究摘要。
3. main agent / subagent 的分工可行——重型搜尋丟給 `edu-researcher`，main agent 不被 context 淹沒。

這是把所有後續 sprint 都會踩的「plugin + skill + subagent」三件事一次驗完的最小切片。

## 粗略目標 (High-level Goals)

- 建立 plugin 骨架（`.claude-plugin/plugin.json`、`skills/edu.research/SKILL.md`、`agents/edu-researcher.md`、`references/AGENTS.md`）。
- 完成 `/edu.research` slash command 的 happy path：
  - 接收一個主題（zh-TW）
  - 把搜尋與彙整的工作派給 `edu-researcher` subagent
  - 落地檔案到 `lessons/<slug>/topic.research.md`
  - 結構：學習關鍵字、核心概念、可信來源摘要、引用清單、Open Questions
- 用一個 sample lesson（建議：「光合作用」）跑通，作為 sprint 完成的驗收依據。

## 範圍外 (Out of scope for this sprint)

- 大綱、簡報、講稿、影片渲染（留給後續 sprint）
- 使用者上傳文件模式（research 第一階段只走網路搜尋）
- 第三方 MCP server 整合
- `edu-reviewer` subagent
- 錯誤處理 / 異常路徑（先以 happy path 為主，記錄到 `works.md` 即可）

## 可能的方向 (Potential Directions)

### 方案 A（推薦）：subagent 一次跑完，main agent 只做派工 + 落檔

`/edu.research <topic>` 觸發後：
1. main agent 把主題丟給 `edu-researcher` subagent，附上「需要哪幾段、引用格式」的指示。
2. subagent 自行決定要做幾輪搜尋、用 WebSearch / WebFetch。
3. subagent 回傳一份 markdown 草稿。
4. main agent 寫入 `lessons/<slug>/topic.research.md`，做最後格式檢查。

**優點**：main context 最乾淨、職責清楚、最貼近 ddd-workflow 的 coordinator + worker pattern。
**缺點**：subagent 第一版可能搜得太雜或太簡，第一次要花點時間調 prompt。

### 方案 B：main agent 直接搜，不用 subagent

主流程在 main agent 內完成搜尋。

**優點**：簡單、第一版能更快跑起來。
**缺點**：違背「驗證 subagent 機制」這個 sprint 目標；後續 sprint 還是要做 subagent，等於延後痛點。

### 方案 C：兩段式 subagent（搜尋 → 整理 兩個 agent）

`edu-search` 只負責 raw 蒐集，`edu-summarizer` 負責整成 markdown。

**優點**：職責更細。
**缺點**：第一個 sprint 過度切分，違反 YAGNI。

**推薦：方案 A。**

## 待釐清事項 (Open Questions)

- `lessons/<slug>` 的 `slug` 怎麼產生？目前傾向：使用者下 command 時可選 `--slug`，否則由 main agent 從主題生 kebab-case。會在 spec 階段確認。
- `topic.research.md` 的精確 schema（chapter 結構、引用格式 inline 還是 footer）會在 spec 階段定。
- `edu-researcher` 拿到主題時要不要先「擴展子問題」再搜？傾向是要，但需要在 prompt 設計時實際試試看。
- 第三方 MCP server 在這個 sprint 完全不接，但 prompt 要不要預留一個「如果有 web-search MCP，優先用之」的判斷？傾向：不要，YAGNI，等真的接了再加。

## 下一步 (Next Step)

執行 `/ddd.spec`，把 `topic.research.md` 的 schema、`edu-researcher` 的 system prompt、`/edu.research` 的接受參數寫成正式 spec。
