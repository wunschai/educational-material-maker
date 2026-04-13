# Sprint 0004 — Slide Visuals（圖片 + 版型優化）

## 背景 (Background)

MVP pipeline 跑通了，但 slides 目前是 Marp default theme 的黑字白底 + 純文字。老師拿去上課的話視覺品質不夠。Sprint 0004 要做兩件事讓簡報「看起來像有設計過」：

1. **投影片加圖片**：每個章節配一張相關圖片（不是每頁都配，避免雜亂）
2. **版型優化**：多欄佈局、重點卡片、引言區塊、標題頁設計等，用 Marp CSS class 實現

## 粗略目標 (High-level Goals)

1. **自訂 Marp theme CSS** (`themes/edu-default.css`)：定義配色、字型、佈局 class（two-column、lead、quote、card）
2. **更新 `/edu.slides` SKILL.md**：指示 LLM 在生成 slides 時使用 layout class + 搜尋並嵌入圖片
3. **圖片策略**：main agent 在生成 slides 時用 WebSearch 搜 Creative Commons / Wikimedia 圖片 URL，直接嵌入 Marp `![bg right](url)` 語法。每個章節 1 張，全簡報約 5-8 張圖
4. **更新 `scripts/build_slides.sh`**：傳入自訂 theme 路徑給 marp-cli
5. **端到端**：用新主題或重跑 library-ethics，產出「有設計感」的簡報 + mp4

## 可能的方向 (Potential Directions)

### 方案 A（推薦）：main agent 生成 slides 時順便搜圖 + 套版型

- `/edu.slides` 的 prompt 更新：在生成每個章節時，用 WebSearch 搜 1 張相關圖片（關鍵字 = 概念名 + "wikimedia commons" 或 "unsplash"），把 URL 嵌入 Marp 語法
- 自訂 theme CSS 提供 class：`lead`（標題頁大字）、`two-col`（左文右圖）、`quote`（引言高亮）、`card`（重點框）
- 圖片數量目標：5-8 張（每章節 1 張，不是每頁都配）
- 不新增 skill 或 subagent——只改 SKILL.md prompt + 加 theme CSS + 改 build script

**優點**：最小改動、不擴大 plugin 架構、main agent 本來就有 WebSearch
**缺點**：搜圖會多用 5-8 次 WebSearch，加長 slides 生成時間；圖片 URL 可能失效

### 方案 B：新增 `/edu.enhance` 後處理 skill

先用現有 `/edu.slides` 產出純文字版，再跑 `/edu.enhance <slug>` 後處理加圖 + 改版型。

**優點**：保持 `/edu.slides` 不變、後處理可重跑
**缺點**：多一個 skill、兩步操作、版型 class 需要在原始 slides.md 中預留（否則後處理很難插入 CSS class）

### 方案 C：用 subagent（edu-designer）搜圖

把搜圖工作丟給 subagent 隔離 context。

**優點**：不燒 main agent context
**缺點**：subagent 回傳圖片 URL list 後，main agent 還是要自己把圖嵌進 slides——分兩步反而更複雜。而且 5-8 次 WebSearch 不算多，不到 AGENTS.md §5 的 subagent 門檻。

**推薦方案 A。**

## Theme CSS 設計方向

```css
/* themes/edu-default.css */

/* 配色：深藍主色 + 淺灰背景 + 橘色強調 */
:root {
  --color-primary: #1a365d;
  --color-accent: #e67e22;
  --color-bg: #f8f9fa;
}

/* 標題頁 */
section.lead { ... }

/* 兩欄：左文右圖 */
section.two-col { ... }

/* 引言高亮 */
section.quote { ... }

/* 重點卡片 */
section.card { ... }
```

具體 CSS 在 spec/work 階段實作，plan 只定方向。

## 圖片來源策略

| 來源 | 方式 | 優缺 |
|---|---|---|
| Wikimedia Commons | WebSearch「<概念> site:commons.wikimedia.org」→ 取圖片 URL | 免費、教育用途合法、品質參差 |
| Unsplash | WebSearch「<概念> site:unsplash.com」→ 取圖片 URL | 高品質、免費授權、但中文主題可能找不到好圖 |
| 直接 Google Images（CC 授權） | WebSearch「<概念> 圖片 creative commons」 | 最靈活、但授權需確認 |

建議策略：**先搜 Unsplash，沒好圖再 fallback Wikimedia**。嵌入用 Marp `![bg right:40%](url)` 語法。

## 待釐清事項 (Open Questions)

- Marp 自訂 theme 需要 `--theme` 或 `--theme-set` flag 傳給 marp-cli，build_slides.sh 要改
- 圖片 URL 若失效（404），slides 會顯示破圖。要不要加 fallback 機制？MVP 建議不加，老師手改即可
- 自訂 font：是否要嵌入 Google Fonts（如 Noto Sans TC）？會讓 HTML 需要網路才能正確顯示

## 下一步 (Next Step)

確認 plan 後 `/ddd.spec`。
