# Sprint 0005 — Slide Quality Boost (Phase 1)

## 背景

Opus 深度分析了 Presenton (4.7k)、ALLWEONE (2.7k)、Slidev (35k)、Marp (8k) 四個專案後，整理出 Top 10 可移植功能。Phase 1 聚焦「只改 prompt + SKILL.md 就能立刻提升品質」的 5 項，不寫新程式碼。

## 目標

將以下 5 個功能整合進 `/edu.slides` 和 `/edu.outline`：

1. **Verbosity 三級密度控制** (`--density=concise|standard|detailed`) — 來自 Presenton
2. **背景分割圖文版面** — 強化 Marp `![bg left/right]` 使用率，至少 20% 頁面用圖文並列
3. **Mermaid 圖表自動生成** — 內容涉及流程/關係/時間線時用 Mermaid 而非純 bullet
4. **Scoped Style 特殊頁面** — 封面/章節/重點頁用 `<style scoped>` 做獨特視覺
5. **Tone 語調控制** (`--tone=academic|casual|engaging|review`) — 來自 Presenton

## 方案

**單一方案：直接改 SKILL.md prompt**。全部 5 項都是 prompt engineering，不需要動 CSS、不需要新 script、不需要新 skill。改完跑一版 `claude-productivity-guide` 驗證。

## 下一步

直接進 `/ddd.spec`。
