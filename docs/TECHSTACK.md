# Tech Stack

## 整體形態

Claude Code Plugin。安裝後在 Claude Code 內透過 slash commands 驅動。

## 目錄結構（plugin 內部）

```
educational_material_maker/
├── .claude-plugin/
│   └── plugin.json              # plugin metadata
├── skills/                      # 五個 slash command
│   ├── edu.research/SKILL.md
│   ├── edu.outline/SKILL.md
│   ├── edu.slides/SKILL.md
│   ├── edu.narrate/SKILL.md
│   └── edu.render/SKILL.md
├── agents/
│   ├── edu-researcher.md        # 搜尋與彙整 subagent
│   └── edu-reviewer.md          # 教學品質審查 subagent
├── scripts/                     # 本地工具的 wrapper（被 skill 透過 Bash 呼叫）
│   ├── build_slides.sh          # marp-cli wrapper
│   ├── synthesize_tts.py        # edge-tts wrapper
│   ├── record_slides.py         # playwright 螢幕錄製
│   └── compose_video.sh         # ffmpeg 拼接
├── references/
│   └── AGENTS.md                # 共用指令檔（coding style、命名）
├── docs/                        # DDD 文件包
│   ├── PRD.md
│   ├── TECHSTACK.md
│   └── <編號>-<名稱>/           # 每個 sprint 一個資料夾
└── lessons/                     # 使用者實際產出的教材（非 plugin 程式碼）
    └── <lesson_slug>/
        ├── topic.research.md
        ├── outline.md
        ├── slides.md
        ├── narration/
        ├── audio/
        └── dist/
```

`docs/` 是「DDD-driven 開發 plugin 自己」的工作區；`lessons/` 是「使用者用 plugin 製作教材」的工作區。兩者完全分離。

## 核心相依

| 類別 | 選擇 | 備註 |
|---|---|---|
| Plugin runtime | Claude Code | 透過 `claude plugin add` 安裝 |
| 簡報源格式 | **Markdown (Marp)** | LLM 最擅長產生、可 diff、可版控 |
| 簡報構建 | `@marp-team/marp-cli` | 將 markdown 轉 HTML / PDF |
| TTS | **edge-tts** (Python) | 免費、中文語音可接受、無 API key |
| 影片錄製 | **Playwright** (Python) | 無頭瀏覽器逐頁渲染 marp HTML |
| 影片合成 | **ffmpeg** | 影像 + 音訊軌拼接 |
| 搜尋 | Claude `WebSearch` + `WebFetch`（內建） | 主要 |
| 搜尋（補強） | 第三方 MCP server（Tavily / Firecrawl / arXiv） | Sprint 0004 評估 |

## Subagent 職責

| Agent | 職責 | 不做什麼 |
|---|---|---|
| `edu-researcher` | 對主題 deep search、過濾來源、寫摘要 + 引用 | 不寫教學大綱、不下教學判斷 |
| `edu-reviewer` | 對照教學目標審 slides + 講稿，挑出錯誤、漏洞、引用瑕疵 | 不修改檔案，只產出 review 報告 |

## Slash Command 接力

```
/edu.research <topic>     →  lessons/<slug>/topic.research.md
/edu.outline <slug>       →  lessons/<slug>/outline.md
/edu.slides <slug>        →  lessons/<slug>/slides.md
/edu.narrate <slug>       →  lessons/<slug>/narration/*.md + audio/*.mp3
/edu.render <slug>        →  lessons/<slug>/dist/<slug>.mp4
```

每一步都讀上一步的輸出，使用者可以中斷、手改 markdown、重跑下一步。

## 為什麼這樣選

- **Marp over python-pptx**：LLM 對 markdown 的掌握度遠勝 .pptx 結構化 API；diff 可審；老師也能手改。
- **Edge-TTS over 商用**：第一階段不引入金鑰管理、計費，先驗證流程可行。
- **Playwright over slide-to-video lib**：保留 marp 的 transition 與 fragment，可控、可調主題。
- **不自建 MCP**：第一階段用內建 WebSearch + 第三方 MCP 已夠用，自建 server 等明確需求出現再說。

## 開發環境前置

- Node.js（marp-cli）
- Python 3.10+（edge-tts、playwright）
- ffmpeg 在 PATH 上
- Playwright 的 Chromium 已 `playwright install`

詳細安裝指引在第一個 sprint 的 work doc 中產出。
