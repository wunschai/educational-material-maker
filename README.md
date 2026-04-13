# Educational Material Maker

一個 Claude Code plugin，讓老師輸入主題就能產出完整教學包——從研究摘要到帶旁白的教學影片，五個階段、五個指令、全程可中斷審閱。

## 快速開始

### 前置需求

- [Claude Code](https://claude.ai/claude-code) CLI
- [Node.js](https://nodejs.org/) 18+（Marp 簡報編譯）
- [Python](https://www.python.org/) 3.10+（TTS、影片渲染）
- [ffmpeg](https://ffmpeg.org/)（影片合成）

### 安裝依賴

```bash
# Python 套件
pip install edge-tts playwright
playwright install chromium

# ffmpeg (Windows)
winget install --id Gyan.FFmpeg

# ffmpeg (macOS)
brew install ffmpeg
```

### 啟動

```bash
claude --plugin-dir /path/to/educational-material-maker
```

啟動後在 Claude Code 對話中輸入 `/edu.research <主題>` 即可開始。

## Pipeline

```
/edu.research <topic>       → 研究摘要
      ↓ 老師審閱
/edu.outline <slug>         → 教學大綱
      ↓ 老師審閱
/edu.slides <slug>          → Marp 簡報 + 品質審查
      ↓ 老師審閱
/edu.narrate <slug>         → 語音旁白
      ↓ 老師試聽
/edu.render <slug>          → mp4 教學影片
```

每個階段都會產出檔案，老師可以在任一步驟中斷、手改、重跑下一步。

### 指令速查

| 指令 | 說明 | 輸出 |
|---|---|---|
| `/edu.research <topic>` | 搜尋資料、彙整核心概念與引用 | `topic.research.md` |
| `/edu.outline <slug> [--level=basic\|standard\|full]` | 產出教學大綱（支援三種詳細度） | `outline.md` |
| `/edu.slides <slug>` | 產出 Marp 簡報 + 自動品質審查 | `slides.md` + review 報告 |
| `/edu.narrate <slug> [--voice=<id>]` | 從 speaker notes 生成 Edge-TTS 語音 | `narration/*.txt` + `audio/*.mp3` |
| `/edu.render <slug>` | 簡報截圖 + 語音 → mp4 影片 | `dist/<slug>.mp4` |

## 範例

```bash
# 啟動 plugin
claude --plugin-dir ./educational-material-maker

# 在 Claude Code 對話中：
/edu.research 圖書館倫理
/edu.outline library-ethics
/edu.slides library-ethics
/edu.narrate library-ethics
/edu.render library-ethics

# 成品在 lessons/library-ethics/dist/library-ethics.mp4
```

## 產出結構

```
lessons/<slug>/
├── topic.research.md     研究摘要（核心概念 + 引用）
├── outline.md            教學大綱（學習目標 + 章節骨架）
├── slides.md             Marp 簡報原始碼
├── slides.html           可預覽的 HTML 簡報
├── diagrams/             MCP 生成的結構性圖表（心智圖、流程圖等）
├── images/               章節封面照片
├── narration/             逐頁講稿文字
│   ├── slide-01.txt
│   └── ...
├── audio/                 逐頁 TTS 語音
│   ├── slide-01.mp3
│   └── ...
└── dist/
    └── <slug>.mp4         最終教學影片（720p, H.264+AAC）
```

## 功能特色

### 階段化 + 可中斷審閱

不是「一鍵到底」的黑盒。每個階段產出獨立的 markdown 檔案，老師可以：

- 在大綱階段調整教學節奏
- 在簡報階段修改內容或換圖
- 在語音階段替換某幾頁的音檔
- 任一步驟重跑，不影響前面的產出

### 教學大綱三種 Level

| Level | 內容 | 適用場景 |
|---|---|---|
| `basic` | 學習目標 + 章節骨架 + 時長估 | 快速備課 |
| `standard` | + 先備知識 + 教學方法 | 正式課程 |
| `full` | + 評量方式 + 教學資源 + 延伸學習 | 完整教案 |

### 自動品質審查

`/edu.slides` 完成後自動觸發 `edu-reviewer` subagent，審查：

- **學習目標覆蓋度**：outline 的每個學習目標是否都有 slide 覆蓋
- **內容正確性**：slides 的事實是否與 research 一致

### 自訂主題 + MCP 圖表

- **edu-default theme**：深藍配色、橘色強調，提供 `lead` / `summary` / `quote` / `card` / `invert` 五種版型 class
- **MCP 圖表整合**（可選）：心智圖、魚骨圖、流程圖、文氏圖等 27+ 種圖表，由 [mcp-server-chart](https://github.com/antvis/mcp-server-chart) 與 [mcp-mermaid](https://github.com/hustcc/mcp-mermaid) 提供
- **照片嵌入**：自動搜尋 Unsplash / Wikimedia Commons 圖片作為章節封面

### 視覺自審

`/edu.slides` 產出後會用 Playwright 截圖所有頁面並逐頁檢查：文字溢出、圖表遮擋、破圖、空白頁等，在交付前自動修正。

## MCP 圖表（可選）

啟動時加上 MCP 設定即可使用圖表生成功能：

```bash
claude --plugin-dir ./educational-material-maker --mcp-config .mcp.json
```

`.mcp.json` 已包含在 repo 中，配置了：

- **mcp-server-chart**：27 種圖表（心智圖、流程圖、魚骨圖、文氏圖、圓餅圖…）
- **mcp-mermaid**：Mermaid 語法圖表

不加 `--mcp-config` 也能正常運作，只是 slides 不會有 MCP 圖表（照片仍會有）。

## Subagents

| Agent | 職責 |
|---|---|
| `edu-researcher` | 主題搜尋與彙整（保護 main agent context 不被搜尋結果燒光） |
| `edu-reviewer` | 教學品質審查（學習目標覆蓋 + 內容正確性） |

## 技術棧

| 元件 | 技術 |
|---|---|
| 簡報 | [Marp](https://marp.app/)（Markdown → HTML/PDF） |
| TTS | [Edge-TTS](https://github.com/rany2/edge-tts)（免費、中文語音 `zh-TW-HsiaoChenNeural`） |
| 截圖 | [Playwright](https://playwright.dev/)（Chromium headless） |
| 影片 | [ffmpeg](https://ffmpeg.org/)（逐頁截圖 + 音檔 → mp4 拼接） |
| 圖表 | [mcp-server-chart](https://github.com/antvis/mcp-server-chart) + [mcp-mermaid](https://github.com/hustcc/mcp-mermaid)（可選 MCP） |

## Plugin 結構

```
educational-material-maker/
├── .claude-plugin/plugin.json     Plugin metadata
├── .mcp.json                      MCP server 設定（chart + mermaid）
├── skills/                        Slash commands
│   ├── edu.research/SKILL.md
│   ├── edu.outline/SKILL.md
│   ├── edu.slides/SKILL.md
│   ├── edu.narrate/SKILL.md
│   └── edu.render/SKILL.md
├── agents/                        Subagents
│   ├── edu-researcher.md
│   └── edu-reviewer.md
├── scripts/                       Wrapper scripts
│   ├── build_slides.sh
│   ├── synthesize_tts.py
│   └── render_video.py
├── themes/
│   └── edu-default.css            自訂 Marp 主題
├── references/
│   └── AGENTS.md                  共用規範（schema、命名、引用格式）
├── docs/                          DDD 開發文件
│   ├── PRD.md
│   ├── TECHSTACK.md
│   └── 0001-skeleton/
│   └── 0002-outline-and-slides/
│   └── 0003-narration-and-render/
│   └── 0004-slide-visuals/
└── lessons/                       使用者產出的教材
    ├── library-ethics/            範例：圖書館倫理（含完整 mp4）
    └── claude-pro-intro/          範例：Claude Pro 功能介紹
```

## 開發方法論

本專案使用 [ddd-workflow](https://github.com/applepig/ddd-workflow)（Document Driven Development）進行開發。每個功能都經過 plan → spec → tasks → work → xreview 的完整流程，文件保存在 `docs/` 目錄。

## License

MIT
