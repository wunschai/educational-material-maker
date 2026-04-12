# Sprint 0002 — Outline and Slides

## 背景 (Background)

Sprint 0001 交付了 plugin 骨架 + `/edu.research`（搜尋 → `topic.research.md`）。目前 pipeline 只到「研究摘要」就停。Sprint 0002 要接上第二棒與第三棒：把研究轉成教學大綱（outline），再從大綱寫成 Marp 簡報（slides），中間插一個品質審查員（edu-reviewer）確保 slides 沒偏離教學目標。

老師的使用流程（Sprint 0002 結束後）：

```
/edu.research 光合作用          → lessons/photosynthesis/topic.research.md
/edu.outline photosynthesis     → lessons/photosynthesis/outline.md
    ↕ 老師手改 outline          （階段化 + 可中斷審閱的核心價值）
/edu.slides photosynthesis      → lessons/photosynthesis/slides.md
    → edu-reviewer 自動跑       → review 報告呈現給老師
    ↕ 老師依 review 結果修改     
    → marp build               → 可預覽的 HTML / PDF
```

## 粗略目標 (High-level Goals)

1. **`/edu.outline <slug> [--level=basic|standard|full]`**：讀 `topic.research.md`，根據 level 產出不同詳細度的教學大綱 `outline.md`。
2. **`/edu.slides <slug>`**：讀 `outline.md` + `topic.research.md`，產出 Marp markdown `slides.md`（15-25 頁、含 speaker notes 預留給未來 narration 階段）。
3. **`edu-reviewer` subagent**（簡化版）：slides 寫完後自動被 `/edu.slides` 呼叫，審查兩個維度：(a) 學習目標覆蓋度 (b) 內容正確性（對照 research）。回傳 review 報告，不修改檔案。
4. **`scripts/build_slides.sh`**（或 `.py`）：Marp-cli wrapper，把 `slides.md` 編成 HTML/PDF。**這是 plugin 的第一個 wrapper script**，Sprint 0003 (render) 會再加 TTS + ffmpeg。
5. **端到端驗收**：拿一個 sample lesson（例如 library-ethics 或新主題），跑完 research → outline → slides → build → review 全鏈，產出可預覽的 HTML/PDF。

## 可能的方向 (Potential Directions)

### 方案 A（推薦）：main agent 寫 outline + slides，reviewer 走 subagent

- `/edu.outline` 與 `/edu.slides` 都由 main agent 在 context 內直接完成——不新增 subagent。理由：
  - 不需要 web search（不觸發 AGENTS.md §5 的 subagent 門檻）
  - research.md 通常 < 5000 字、outline.md < 3000 字、slides.md ≈ 5000-8000 字（15-25 頁）——加總 < 16000 字，main agent context 完全能消化
  - 如果走 subagent，老師的「中途審閱 + 互動修改」就很難做（subagent 跑完才回來，沒有互動窗口）
- `edu-reviewer` 走 subagent，用 Task tool 派工。理由：reviewer 不需要互動、審查完回傳報告就好。走 subagent 也能隔離 context，main agent 不被 review 細節污染。
- `scripts/build_slides.sh`：thin shell wrapper 包 `npx @marp-team/marp-cli slides.md -o slides.html`。

**優點**：最小工程量、保留階段化互動、reviewer 隔離乾淨。
**缺點**：如果老師一次要出很長的 slides（50+頁），main agent 的 context 可能不夠。但我們把 slides 限在 15-25 頁，暫時不是問題。

### 方案 B：slides 也走 subagent（edu-slide-author）

跟 A 一樣，但 `/edu.slides` 把生成工作丟給 `edu-slide-author` subagent。

**優點**：slides 生成不消耗 main agent context。
**缺點**：(1) 老師無法在 slides 生成中途互動修改——subagent 回來才行 (2) 多一個 subagent file 要維護 (3) 15-25 頁的 slides main agent 完全能做，引入 subagent 是 over-engineering。

### 方案 C：outline + slides 合成一步

沒有 `/edu.outline`，直接從 research 跳到 slides。outline 邏輯內嵌在 slides 生成中。

**優點**：少一個 skill、使用者少一步操作。
**缺點**：直接違反使用者選擇的「階段化 + 可中斷審閱」原則——沒有 outline.md 可以中途審閱。

**推薦方案 A。**

## outline.md 三個 level（hardcoded preset，未來可抽為 schema profile）

本 sprint 的 `--level` 機制以 inline preset 實作（SKILL.md 內含 3 個 schema 模板），不引入完整的 profile registry 或 config file。未來 Sprint 真的需要動態 profile 機制時，從這裡抽出來即可。

### basic（預設）

```markdown
# <Topic> — 教學大綱

## 學習目標
- 目標 1
- 目標 2
- 目標 3
（3-5 條，以 Bloom's 動詞開頭：說明、比較、分析、應用…）

## 章節骨架
### 1. <章節名稱>（約 X 分鐘）
- 重點 1：<概述>
- 重點 2：<概述>
- 對應研究概念：<research.md 概念 N>

### 2. ...

（4-7 章節，每章節含重點 + 時長估 + 對應研究概念）

## 預估總時長
約 XX 分鐘
```

### standard

basic + 以下段落：

```markdown
## 先備知識
- <學生需要先知道的 1>
- <學生需要先知道的 2>

（在每個章節骨架項下新增）
- 教學方法：講述 / 討論 / 實作 / 示範
```

### full

standard + 以下段落：

```markdown
## 評量方式
- <形成性評量 1>：<說明>
- <總結性評量>：<說明>

## 教學資源
- <資源 1>：<來源>
- <資源 2>：<來源>

## 延伸學習
- <進階主題 1>
- <補充閱讀 1>
```

## slides.md 設計要點

- **格式**：Marp markdown（`---` 分頁、`<!-- _class: ... -->` 控制版面）
- **Theme**：預設 `default`。使用者可在 slides.md 的 frontmatter 手改。
- **頁數**：目標 15-25 頁。標題頁 1 + 章節分隔頁 N + 內容頁 + 總結頁 1。
- **每頁密度**：1 個 key message + 1 個佐證圖表或例子。不塞滿。
- **Speaker notes**：每張 slide 在 Marp `<!-- ... -->` comment 區塊內附 speaker notes（2-3 句話的講課稿），預留給 Sprint 0003 的 `/edu.narrate` 直接抽取使用。
- **引用**：Marp 不原生支援 footnote。改用最後 1-2 頁「引用來源」列表，slide 內文以上標數字 `¹ ² ³` 標記。
- **來源**：slides 的內容來自 outline.md（結構）與 topic.research.md（事實與引用）。生成 slides 時 main agent 需讀取兩者。

## edu-reviewer 簡化版設計

- **觸發**：`/edu.slides` 寫完 `slides.md` 後**自動**呼叫 reviewer（main agent 用 Task tool 派工到 `edu-reviewer` subagent）。老師不需要手動呼叫。
- **審查維度**（只有兩個，其餘等後續 sprint 按需加）：
  1. **學習目標覆蓋度**：outline.md 列的學習目標，slides 是否每條都有對應的 slide？有沒有目標被漏掉？
  2. **內容正確性**：slides 的事實敘述跟 research.md 一致嗎？有沒有 hallucinate 出 research 沒寫的東西？
- **輸出**：review 報告（markdown），回傳給 main agent 後呈現給使用者。
- **不做**：教學節奏、認知負荷、視覺設計、引用一致性（這些是進階 review，留待後續）。

## 待釐清事項 (Open Questions)

- **Marp-cli 安裝與 Node.js 依賴**：使用者環境是否已有 Node.js？是否需要在 sprint 內處理 `npm init` + `npm install @marp-team/marp-cli`？可能需要一個 setup script 或在 works.md 記安裝步驟。
- **slides.md 的 Marp frontmatter 格式**：是否需要用 `marp: true` + `theme: default` + `paginate: true` 的完整 frontmatter？需在 spec 階段確認。
- **edu-reviewer 與使用者的互動模式**：reviewer 報告出來後，使用者要怎麼「接受/拒絕/修改」？是 main agent 用 AskUserQuestion 問？還是直接告知使用者報告內容、使用者自己決定手改 slides.md？
- **slides 的圖片/圖表**：Sprint 0002 是否支援圖片？如果是，圖片從哪來（使用者提供? 占位符? 網路搜尋?）？建議 Sprint 0002 不處理圖片、用文字描述留占位符，Sprint 0004 (polish) 再處理。

## 下一步 (Next Step)

確認 plan 後，執行 `/ddd.spec` 把以下寫成正式規格：

1. `/edu.outline` 的介面（params / schema × 3 levels / slug 延續）
2. `/edu.slides` 的介面（params / slides schema / speaker notes 格式）
3. `edu-reviewer` 的 subagent 契約（輸入 / 審查維度 / 輸出格式）
4. `scripts/build_slides.sh` 的介面（輸入 / 輸出 / 依賴）
5. 驗收條件（端到端 sample + 每個 skill 的 happy path + 邊界案例）
