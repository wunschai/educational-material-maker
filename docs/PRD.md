# PRD — Educational Material Maker

## 一句話定位

一個 Claude Code plugin，讓老師輸入主題就能依序產出研究摘要、教學大綱、Marp 簡報、逐頁講稿、與帶 TTS 旁白的 mp4 教學影片。

## 背景

老師備課的痛點：
- 找資料：要在多個來源之間切換、辨別可信度、整理引用，耗時最多。
- 設計大綱：把零散資料整成「學習目標 → 概念鋪陳 → 重點」的教學節奏。
- 做簡報與講稿：手動排版、寫旁白、如果要錄製又是另一輪工。

現有 LLM 工具大多停在「問答」或「生成單一 artefact」，無法跨階段協作、缺少審閱關卡，也不會把研究過程的「過程資料」留存可追溯。

本工具把這條鏈完整托管在 Claude Code 內，每一步都產出檔案、每一步都可中斷審閱。

## 目標使用者

**主要**：個人老師（高中、大學、補習班、線上課程講師），備課時要一份完整的教學包。

**次要（不主動服務）**：教育內容創作者、自學者整理筆記。

## 範圍 (In scope)

- 「主題 → 教學包」單線流程，五個階段：研究、大綱、簡報、講稿、渲染。
- 雙資料來源模式：純網路搜尋 / 使用者提供 PDF & 文字檔。
- 中文（zh-TW）為預設語系，英文 best-effort。
- 輸出物：
  - `topic.research.md`：分點摘要 + 引用清單
  - `outline.md`：教學目標、章節骨架
  - `slides.md`：Marp markdown
  - `narration/*.txt`：逐頁講稿
  - `audio/*.mp3`：Edge-TTS 合成
  - `dist/<lesson>.mp4`：最終影片
- 階段化 slash commands，使用者可在任一階段中斷、修改、重跑下一階段。

## 範圍 (Out of scope)

- 多人協作 / 共享後端
- 自動評量題庫生成
- LMS 整合（Moodle、Canvas 等）
- 真人 / AI avatar 出鏡影片
- 互動式網頁簡報 (Reveal.js 等)
- 自建 MCP server（保留至未來 sprint 評估）
- 多語系 i18n 機制（zh-TW 為主）

## 成功條件

第一階段成功 = 老師輸入一個主題（如「光合作用」），跑完五個 slash commands 後，能拿到一支可直接拿去上課用的 mp4，過程中所有中介檔案都在 `docs/<lesson>/` 裡可追溯與重跑。

## 與 Claude 整合的程度

這是專案的核心訴求。三個機制都會用上：

| 機制 | 用途 |
|---|---|
| **Skills** | 五個 slash commands 是使用者主要操作介面 |
| **Subagents** | `edu-researcher`（保護 main context 的搜尋）、`edu-reviewer`（教學品質審查） |
| **MCP** | 第一階段使用第三方 MCP server（web search、arXiv），自建 MCP 留待未來 |

## 反目標

- ❌ 不做「一鍵到底」黑盒：使用者必須能在每個階段審閱與修改。
- ❌ 不假設特定學科：工具對學科盡量中立，prompt 與 review 邏輯不寫死於某科目。
- ❌ 不為了視覺花俏選複雜的渲染管線：Marp + Playwright + ffmpeg 是上限，不引入動畫框架。
