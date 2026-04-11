# Tasks: Sprint 0001 — Skeleton

## TDD 適用性說明（重要）

本 sprint 的所有交付物都是 markdown / JSON 設定檔（plugin metadata、subagent prompt、slash command 定義、共用指令檔），**不是傳統可單元測試的程式碼**。spec.md 也明確將「自動測試」列為非目標（OOS）。

因此本 sprint 的「test-first」精神改寫為：

- **先寫驗收條件、再寫檔案**：每個 task 在「Done 條件」段明確寫出本 task 完成的可觀察證據（檔案存在、欄位齊全、能被人工 review 通過、能對應到 spec 的哪一條 AC）。
- **不使用 Red/Green 標記**：因為沒有可執行的測試。
- **Sprint 結束時的「整合測試」是 Milestone 2 的端到端手動跑**——對 spec.md 的 9 條 AC 逐條人工檢查。

未來 sprint 引入 wrapper script（marp、edge-tts、playwright、ffmpeg）時，會回到正規 TDD（pytest + Red/Green）。

## 平行評估結論

按 ddd.tasks 規定做平行分析後的結論：**本 sprint 全部序列執行**。

| 候選平行對 | 依賴情況 | 決策 |
|---|---|---|
| Task 1.1 (plugin.json) ↔ Task 1.2 (AGENTS.md) | 內容上不互相依賴 | **不平行**：兩者都是極小檔案（< 100 行），worktree 切換成本 > 收益 |
| Task 1.3 (agent.md) → Task 1.2 (AGENTS.md) | agent prompt 引用 AGENTS.md 的 schema 必填項清單 | 序列 |
| Task 1.4 (SKILL.md) → Task 1.3 (agent.md) | SKILL.md 透過 Task tool 派工到 `edu-researcher`，需對齊 subagent 介面 | 序列 |
| Task 2.x（端到端驗收） | 每個 task 驗一條或多條 AC，依賴 M1 全部完成 | 序列 |

序列拆解仍符合「平行評估必做」的要求——關鍵是**評估過再決定**，而不是預設不平行。

---

## Milestone 1: Plugin 骨架就位（序列）

> **預期結果**：4 個靜態檔案完成，plugin 可被 Claude Code 載入時不報錯，metadata、共用規則、subagent prompt、slash command 都齊備。
>
> **驗證方式**：人工 review 每個檔案是否符合 spec.md 對應段落；在 Claude Code 中以 `claude plugin add <local-path>`（或等價方式）載入並確認 `/edu.research` 與 `edu-researcher` 出現在可用清單。
>
> **本 milestone 不執行 `/edu.research`**——只驗證載入。實際呼叫在 Milestone 2。

- [x] **Task 1.1：建立 `.claude-plugin/plugin.json`**
  - **內容**：依 spec §「`.claude-plugin/plugin.json`」段提供的 JSON 結構撰寫
  - **變更檔案**：新增 `.claude-plugin/plugin.json`
  - **Done 條件**：
    - 檔案存在於 `.claude-plugin/plugin.json`
    - JSON 合法（用 `python -c "import json; json.load(open('.claude-plugin/plugin.json'))"` 驗）
    - `name` = `educational-material-maker`、`version` = `0.1.0`
    - `author.name` 已替換成真實值（task 開始時詢問使用者要填什麼，不留 `TBD`）
  - **對應 AC**：AC-8 的前置

- [x] **Task 1.2：撰寫 `references/AGENTS.md`**
  - **內容**：共用指令檔，依 spec §「`references/AGENTS.md`（內容大綱）」與 ADR-6 約束撰寫
  - **變更檔案**：新增 `references/AGENTS.md`
  - **必含段落**：
    1. 預設語系規則（zh-TW 為主）
    2. 引用格式規則（markdown footnote、含 URL 與存取日期）
    3. slug 自動生成規則（複製自 spec §slug 規則）
    4. **schema 必填項清單（複製自 spec 的 8 區段表格）**——這是 ADR-6 約束之一：schema 規則必須住在 AGENTS.md，不可寫死在 agent prompt 中
    5. subagent 使用原則（超過 5 個 web search / 3 個 webfetch 必走 subagent；不在 main context 內展開大型搜尋結果）
    6. **Sprint 0001 註解**：「本檔的 schema 必填項在 Sprint 0001 為固定值，未來會由 schema profile 機制動態決定，詳見 docs/0001-skeleton/spec.md ADR-6」
  - **Done 條件**：上述 6 段全在；任何提到 schema 的地方都標註 `Sprint 0001: hardcoded schema. Future: profile-driven.`
  - **對應 AC**：AC-4、AC-5、AC-7 的前置（schema 定義來源）

- [x] **Task 1.3：撰寫 `agents/edu-researcher.md`**
  - **內容**：subagent 定義檔，包含 YAML frontmatter + system prompt
  - **變更檔案**：新增 `agents/edu-researcher.md`
  - **必含結構**：
    1. YAML frontmatter：`name: edu-researcher`、`description:` 含觸發條件範例
    2. system prompt 開頭引用 `references/AGENTS.md`（要求 subagent 讀過該檔的 schema 與引用規則）
    3. **`<SCHEMA>...</SCHEMA>` 區塊**：把 spec §「topic.research.md schema」的 markdown 模板包在這對 tag 裡（ADR-6 約束：未來 profile 機制要從這裡注入不同 schema）
    4. 子問題拆解流程說明（4-6 個方向：定義、機制、應用、誤解、相關概念；ADR-3 要求拆解過程要寫進輸出檔的「子問題拆解」段）
    5. 邊界案例處理指引（spec §邊界案例的對應條目：來源不足時加 `> ⚠️`、網路失敗時自動重試一次後回報失敗）
    6. 輸出契約：純 markdown 字串、不包 code fence、不加額外說明
  - **Done 條件**：上述 6 項齊備；prompt 中**不**直接列出 schema 必填項（這些必填項只能透過讀 AGENTS.md 取得，避免兩處重複）；inline 註解標明 ADR-6 約束
  - **對應 AC**：AC-6 的前置（subagent 機制）

- [x] **Task 1.4：撰寫 `skills/edu.research/SKILL.md`**
  - **內容**：slash command 定義，包含 YAML frontmatter + 流程指引
  - **變更檔案**：新增 `skills/edu.research/SKILL.md`
  - **必含結構**：
    1. YAML frontmatter：`name: edu.research`、`description:` 含 trigger 範例（zh-TW + en）
    2. 參數解析規則：`<topic>`（必填）、`--slug`（選填、覆寫自動生成）、`--from`（預設 `web`，其他值拒絕）
    3. **slug 自動生成規則 + fallback**：依 spec §「slug 自動生成規則」三步驟（英文標準化 → 中文翻 1-3 英文字 → 失敗 fallback 為 `lesson-<YYYYMMDD-HHMM>`）
    4. **slug 衝突中止流程**：偵測到 `lessons/<slug>/topic.research.md` 已存在時直接中止，提示使用者「請刪除舊檔或改 `--slug`」，**不**靜默覆寫、**不**實作 `--force`
    5. **派工流程**：強制透過 Task tool 呼叫 `edu-researcher` subagent，附上 spec §「`edu-researcher` subagent 契約 / 輸入」段的 prompt 範本
    6. **接收與 schema 防呆**：接收 subagent 回傳的 markdown 字串 → 偵測必填段是否缺項 → 若缺項，補加空章節並在缺處插入 `> ⚠️ schema 缺項：<段名>` 警示，**不**重跑 subagent（spec §邊界案例規則：避免無限迴圈）
    7. 寫入 `lessons/<slug>/topic.research.md`、回報使用者（檔案路徑、概念數、引用數、引導下一步 `/edu.outline <slug>`）
    8. 失敗處理：subagent 回報失敗 → 不寫檔、向使用者回報原因
  - **Done 條件**：上述 8 項齊備；YAML frontmatter 中的 trigger 列表至少含「研究主題」「edu.research」「prepare a lesson」三類觸發詞
  - **對應 AC**：AC-1〜AC-3、AC-6、AC-9 的前置；同時涵蓋 spec §邊界案例的「slug 自動生成失敗」與「subagent 回傳不符 schema」兩條

---

## Milestone 2: 端到端驗收（序列）

> **預期結果**：執行 `/edu.research 光合作用`，main agent 透過 Task tool 派工給 `edu-researcher`，產出 `lessons/<slug>/topic.research.md` 符合 spec.md 的所有 schema 與內容量級要求。spec.md 9 條 AC 全綠，sample lesson 通過人工品質驗收。
>
> **驗證方式**：在 Claude Code 中實際載入本地 plugin、執行 slash command、人工對照 spec.md 的 9 條 AC 逐條打勾。

- [x] **Task 2.1：載入本地 plugin 並驗證 metadata 解析**
  - **操作**：在 Claude Code 中以本地路徑載入 plugin（具體指令在 task 開始時依當下 Claude Code 版本確認；可能是 `/plugin add <path>` 或設定檔註冊）
  - **Done 條件**：
    - Claude Code 顯示 plugin 載入成功（無 JSON parse error、無 frontmatter error）
    - `/edu.research` 出現在可用 slash commands 清單
    - `edu-researcher` 出現在可用 subagents 清單
  - **驗 AC**：AC-8

- [x] **Task 2.2：執行 `/edu.research 光合作用` 並觀察派工**
  - **操作**：在 Claude Code 對話中輸入 `/edu.research 光合作用`，全程觀察 main agent 行為
  - **Done 條件**：
    - main agent 解析參數、自動產生 slug（記下實際生成值，預期為 `photosynthesis` 或語義相近）
    - main agent **明確透過 Task tool 呼叫 `edu-researcher`**（非自己直接 WebSearch）
    - 流程不被網路或 token 上限中斷
    - 收到 subagent 回傳的 markdown 字串
    - main agent 寫檔到 `lessons/<slug>/topic.research.md`
  - **驗 AC**：AC-1、AC-6

- [x] **Task 2.3：對 `topic.research.md` 做 schema + 量級檢查**
  - **操作**：開啟產出檔案，逐項對照 spec §「topic.research.md schema」與 §「Schema 必填項」
  - **Done 條件**（逐項打勾）：
    - [ ] H1 標題正確
    - [ ] Metadata block 完整（slug / generated / source mode / depth）
    - [ ] 學習關鍵字段存在
    - [ ] 子問題拆解段存在且含 4-6 條
    - [ ] 核心概念段含 5-8 個概念，每個 100-200 字
    - [ ] 引用區含 5-10 條 footnote
    - [ ] 每個核心概念至少一個 footnote 引用
    - [ ] 引用包含 URL 與存取日期
  - **驗 AC**：AC-1、AC-4、AC-5、AC-7

- [x] **Task 2.4：驗證明確 `--slug` 覆寫**
  - **前置**：先刪除 Task 2.2 產出的資料夾，避免衝突
  - **操作**：執行 `/edu.research 光合作用 --slug=photosynthesis-101`
  - **Done 條件**：產生 `lessons/photosynthesis-101/topic.research.md`（資料夾名與指定值完全一致）
  - **驗 AC**：AC-2

- [x] **Task 2.5：驗證 slug 衝突中止行為**
  - **前置**：保留 Task 2.4 的 `lessons/photosynthesis-101/`
  - **操作**：再次執行 `/edu.research 光合作用 --slug=photosynthesis-101`
  - **Done 條件**：
    - main agent **不**靜默覆寫舊檔
    - 回報「已存在 `topic.research.md`」並提示使用者刪除或改 slug
    - 既有檔案內容未被修改
  - **驗 AC**：AC-3

- [x] **Task 2.6：人工品質驗收 sample lesson**
  - **操作**：開啟 Task 2.2 或 2.4 產出的 `topic.research.md`，問自己以下問題
  - **Done 條件**（須全部「是」）：
    - 內容是否能讓老師作為下一階段大綱的起點？
    - 引用是否真實可訪問（隨機點 2-3 個 URL 驗證）？
    - 概念之間的順序是否有教學節奏（從定義 → 機制 → 應用 → 誤解）？
    - 中文表達是否流暢、無翻譯腔？
  - **不過**：將具體缺口寫進 works.md，回頭修對應 prompt（Task 1.3 或 1.4），重跑 Task 2.2 + 2.3
  - **驗 AC**：AC-9

- [ ] **Task 2.7：迭代修正**（條件性）
  - **觸發**：Task 2.1〜2.6 任一條 AC 未過
  - **操作**：依失敗點回頭修對應的 M1 task 檔案，重跑 M2 從失敗點開始的 task
  - **Done 條件**：spec.md 9 條 AC 全綠
  - **記錄要求**：每次迭代在 `works.md` 增一段「失敗 → 修正內容 → 重跑結果」

---

## Sprint 完成條件（總驗收）

- [ ] M1 全部 task 完成
- [ ] M2 的 9 條 AC 對應 task 全綠
- [ ] `lessons/photosynthesis/topic.research.md` 與 `lessons/photosynthesis-101/topic.research.md` 留在 repo（後者作為 `--slug` 覆寫的證明，前者作為自動 slug 生成的證明；若兩次測試共用同一個資料夾名稱，至少留一份）
- [ ] `works.md` 記錄主要決策、迭代過程、Open Questions 是否解決或仍待後續 sprint
- [ ] git commit + tag `sprint-0001-done`（commit 訊息與 tag 動作仍需使用者明確同意）
