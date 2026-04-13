# Sprint 0005 — Slide Quality Boost (Phase 1)

## 目標

透過 prompt engineering 提升 `/edu.slides` 產出的視覺品質與內容控制精度。5 項改進全部在 SKILL.md 層面完成。

## 非目標

- 新 CSS 主題（Phase 2）
- 結構化輸出 JSON 驗證（Phase 3）
- outline 版型匹配（Phase 3）

## 驗收條件

- [ ] AC-1：`/edu.slides <slug> --density=concise` 產出每頁 ≤ 3 bullet、每 bullet ≤ 12 字
- [ ] AC-2：`/edu.slides <slug> --density=detailed` 產出每頁可達 5-7 bullet、含補充說明
- [ ] AC-3：slides.md 中至少 20% 的頁面使用 `![bg left]` 或 `![bg right:XX%]` 圖文並列
- [ ] AC-4：slides.md 中至少有 1 處使用 Mermaid 語法（```mermaid 區塊）
- [ ] AC-5：slides.md 中至少有 2 頁使用 `<style scoped>` 做獨特視覺處理
- [ ] AC-6：`/edu.slides <slug> --tone=casual` 的文字風格明顯比預設（academic）更口語化
- [ ] AC-7：以 claude-productivity-guide 跑一版，build HTML，視覺自審截圖確認版型多樣性提升

## 相關檔案

修改：
- `skills/edu.slides/SKILL.md` — 加入 density / tone 參數 + Mermaid / bg split / scoped style 指引

不動：
- `themes/edu-default.css` — Phase 2 才動
- `skills/edu.outline/SKILL.md` — Phase 3 才加版型匹配

## 介面變更

### `/edu.slides` 新增參數

| 參數 | 預設 | 說明 |
|---|---|---|
| `--density` | `standard` | `concise`：每頁 ≤ 3 bullet、精簡；`standard`：每頁 3-5 bullet（現行）；`detailed`：每頁 5-7 bullet + 補充 |
| `--tone` | `academic` | `academic`：正式學術；`casual`：輕鬆口語；`engaging`：活潑互動；`review`：考前複習精簡 |

### Mermaid 使用指引

當內容涉及以下類型時，**優先用 Mermaid 而非純 bullet**：

| 內容類型 | Mermaid 圖表 |
|---|---|
| 流程/步驟 | `flowchart LR` |
| 階層/分類 | `mindmap` |
| 時間順序 | `timeline` |
| 關係/互動 | `graph TD` |
| 比較/判斷 | `flowchart` with decision nodes |

### 背景分割使用指引

- 每份簡報至少 20% 頁面（~4-5 頁/20 頁）使用 `![bg left:XX%]` 或 `![bg right:XX%]`
- 交替使用左右擺放
- 圖片來源：WebSearch 搜圖 / MCP chart / diagrams/

### Scoped Style 使用指引

至少 2 頁使用 `<style scoped>` 做特殊視覺，推薦場景：
- 封面頁：自訂背景漸層 + 大字
- 章節分隔頁：強調色帶 + 章節編號放大
- 重點摘要頁：特殊底色 + 邊框

### Tone 規則

| Tone | 文字風格 | Speaker notes 風格 |
|---|---|---|
| `academic` | 正式、精確、專業術語 | 「接下來我們來探討...」 |
| `casual` | 口語、舉例多、類比多 | 「簡單說就是...你可以想成...」 |
| `engaging` | 提問式、互動式、有節奏感 | 「大家猜猜看...沒錯！...」 |
| `review` | 極精簡、公式化、重點條列 | 「記住這三個重點...」 |
