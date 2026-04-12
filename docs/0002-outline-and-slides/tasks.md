# Tasks: Sprint 0002 — Outline and Slides

## TDD 適用性

同 Sprint 0001：prompt-only 交付物不用 Red/Green。唯一例外是 `scripts/build_slides.sh`——這是可執行的 shell script，可以直接跑測試（餵 sample slides.md，看 exit code + 輸出檔）。

## 平行評估結論

全部序列。M1 內部 AGENTS.md → reviewer / outline (可平行) → slides (依賴前兩者)，但檔案都小、worktree 切換成本 > 收益。M2 和 M3 本質序列。

---

## Milestone 1: Plugin 擴充 — prompt files（序列）

> **預期結果**：4 個新/修改檔案就位（AGENTS.md 更新 + edu-reviewer + outline SKILL + slides SKILL），plugin 載入不報錯，`/edu.outline`、`/edu.slides`、`edu-reviewer` 出現在可用清單。
> **驗證方式**：`claude plugin validate` + print mode 確認 skill/agent 識別。

- [ ] **Task 1.1：更新 `references/AGENTS.md`**
  - 新增 §outline.md schema（3 levels 規則）
  - 新增 §slides.md schema（頁數 / speaker notes / 引用格式規則）
  - 新增 §edu-reviewer 審查維度（目標覆蓋 + 內容正確性）
  - 所有新 schema 標 `Sprint 0002: hardcoded preset. Future: profile-driven.`
  - **Done**：AGENTS.md 新增 3 段，無 bare 相對路徑
  - **對應 AC**：AC-1/2/4/5/7 的前置

- [ ] **Task 1.2：撰寫 `agents/edu-reviewer.md`**
  - YAML frontmatter（name / description / model / tools）
  - system prompt：讀 outline + slides + research → 審查 2 維度 → 回傳 review 報告
  - 輸出格式：spec §edu-reviewer 輸出格式（總評 + 目標覆蓋表 + 正確性表 + 建議）
  - 失敗回報：`REVIEW_FAILED: <原因>`
  - **Done**：YAML 合法、2 維度審查流程明確、輸出契約明確
  - **對應 AC**：AC-6、AC-7

- [ ] **Task 1.3：撰寫 `skills/edu.outline/SKILL.md`**
  - YAML frontmatter + trigger
  - 參數解析（slug 必填、--level 預設 basic）
  - 衝突檢查（outline.md 已存在 → 中止）
  - 前置檢查（research.md 不存在 → 中止）
  - 3 個 level preset 的 schema 模板（inline hardcoded，ADR-9）
  - main agent 直接在 context 內產出（ADR-8）
  - 路徑變數：所有 plugin 內部引用用 `${CLAUDE_PLUGIN_ROOT}`
  - **Done**：3 level preset 齊備、衝突/前置檢查邏輯明確、trigger 含 zh-TW + en
  - **對應 AC**：AC-1、AC-2、AC-3

- [ ] **Task 1.4：撰寫 `skills/edu.slides/SKILL.md`**
  - YAML frontmatter + trigger
  - 參數解析（slug 必填）
  - 前置檢查（outline.md + research.md 都存在）
  - 衝突檢查（slides.md 已存在 → 中止）
  - Marp slides 產出規則（15-25 頁、frontmatter、speaker notes 格式）
  - 超頁裁剪邏輯
  - **自動觸發 edu-reviewer**：寫完 slides 後用 Task tool 派工到 edu-reviewer，等回傳後呈現 review 報告，Critical 問題用 AskUserQuestion 問使用者
  - **Done**：slides schema 明確、reviewer 自動觸發流程完整、超頁/缺檔/reviewer 失敗邊界案例全覆蓋
  - **對應 AC**：AC-4、AC-5、AC-6

---

## Milestone 2: Build script（序列）

> **預期結果**：`scripts/build_slides.sh` 可執行，餵 sample slides.md 產出 HTML，exit 0。Node.js + marp-cli 環境就位。
> **驗證方式**：`bash scripts/build_slides.sh <test-slides.md>` → 檢查輸出 .html 存在且可在瀏覽器開。

- [ ] **Task 2.1：確認 / 安裝 Node.js + marp-cli**
  - 檢查 `node --version` / `npm --version`
  - 若沒有：提示使用者安裝或用 `nvm` / `winget`
  - 安裝 marp-cli：`npm install -g @marp-team/marp-cli`（或 project-local `npm init -y && npm install @marp-team/marp-cli`）
  - 驗證：`npx @marp-team/marp-cli --version`
  - **Done**：marp-cli 可在 PATH 上或 npx 可呼叫
  - **對應 AC**：AC-8 的前置

- [ ] **Task 2.2：撰寫 `scripts/build_slides.sh`**
  - 接收 slides.md 路徑 + 選填 `--pdf` flag
  - 呼叫 marp-cli 產出 HTML（或 PDF）
  - 錯誤處理：marp 不在 PATH → exit 1 + stderr 訊息
  - **Done**：script 存在、可執行、對 sample 檔 exit 0
  - **對應 AC**：AC-8

- [ ] **Task 2.3：測試 build script**
  - 手寫一個最小 Marp slides.md（5 頁）測 happy path
  - 驗證 HTML 輸出存在且可瀏覽
  - 測 `--pdf` 模式（如果環境有 Chrome/Chromium）
  - **Done**：HTML 輸出可在瀏覽器開啟、slide 分頁正確
  - **對應 AC**：AC-8

---

## Milestone 3: 端到端驗收（序列）

> **預期結果**：以 `library-ethics` 為 sample lesson，跑完 outline → slides → build → review 全鏈，產出 HTML 可預覽、reviewer 報告可讀。9 條 AC 全綠。
> **驗證方式**：subprocess print mode 執行 + 人工對照 AC。

- [ ] **Task 3.1：`/edu.outline library-ethics`（AC-1）**
  - 驗：outline.md 存在、schema 符合 basic preset、學習目標 3-5 條、章節 4-7 個
  - **對應 AC**：AC-1

- [ ] **Task 3.2：`/edu.outline` --level=standard 與 --level=full（AC-2）**
  - 用不同 slug 或先刪 outline 再跑
  - 驗：standard 有先備知識 + 教學方法；full 有評量 + 資源 + 延伸
  - **對應 AC**：AC-2

- [ ] **Task 3.3：重跑 `/edu.outline library-ethics` 衝突中止（AC-3）**
  - 驗：中止、不覆寫、提示訊息
  - **對應 AC**：AC-3

- [ ] **Task 3.4：`/edu.slides library-ethics`（AC-4/5/6/7）**
  - 驗：slides.md 存在、15-25 頁 Marp、每頁 speaker notes、reviewer 自動觸發、review 報告格式正確
  - **對應 AC**：AC-4、AC-5、AC-6、AC-7

- [ ] **Task 3.5：`scripts/build_slides.sh` 對 library-ethics slides（AC-8）**
  - 驗：HTML 輸出 exit 0、可在瀏覽器預覽
  - **對應 AC**：AC-8

- [ ] **Task 3.6：端到端品質驗收（AC-9）**
  - 開 HTML 預覽、讀 review 報告
  - 問自己：slides 能直接拿去上課嗎？reviewer 抓到的問題合理嗎？
  - **對應 AC**：AC-9

- [ ] **Task 3.7：迭代修正**（條件性）
  - 任一 AC 不過 → 回頭修 → 重跑

---

## Sprint 完成條件

- [ ] M1 + M2 + M3 全部 task 完成
- [ ] 9 條 AC 全綠
- [ ] `lessons/library-ethics/` 下有完整產出鏈：`topic.research.md` → `outline.md` → `slides.md` → `slides.html`
- [ ] works.md 記錄決策與迭代
- [ ] git commit（需使用者同意）
