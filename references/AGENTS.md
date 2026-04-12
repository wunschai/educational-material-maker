# AGENTS.md — Educational Material Maker 共用指令

> 本檔是 plugin 內所有 skills 與 subagents 共用的規範與規則來源。任何 skill / subagent 在運作時都應視本檔為 single source of truth。
>
> **Hardcoded presets. Future: profile-driven.** —— 本檔目前的 schema（research / outline / slides）是寫死的固定 preset，未來會由 schema profile 機制依課程類型動態決定。詳見 `docs/0001-skeleton/spec.md` ADR-6 與 `docs/0002-outline-and-slides/spec.md` ADR-9。

---

## 1. 預設語系

- **預設輸出語系**：繁體中文（zh-TW）。
- 使用者輸入若為英文 / 簡中 / 日文，研究與整理過程可使用該語系；最終 markdown 輸出仍以 zh-TW 為主，原文專有名詞可在括號內保留（例：「光合作用 (photosynthesis)」）。
- 引用標題保留原文。
- 簡報、講稿、影片旁白都遵循同一語系規則。

## 2. 引用格式

- **格式**：markdown footnote。引用標記寫在句末，引用區放檔案最底部。
- **必含欄位**：標題、URL、存取日期（ISO 8601 `YYYY-MM-DD`）。
- **格式範例**：

```markdown
光合作用是植物將光能轉化為化學能的過程 [^1]。

## 引用

[^1]: Photosynthesis — https://en.wikipedia.org/wiki/Photosynthesis （accessed 2026-04-11）
```

- **不使用** inline 連結（`[文字](url)`）作為主要引用方式——footnote 才是 SSOT。inline 連結僅用於補充說明、外部資源指引等非引用情境。

## 3. Slug 自動生成規則

當 `/edu.research <topic>` 沒有 `--slug` 參數時，由 main agent 依下列三步驟自動生成：

1. **主題為英文**：lowercase → 空白轉 `-` → 移除非 `[a-z0-9-]` 字元 → 去除頭尾的 `-`。
2. **主題為中文 / 其他語系**：main agent 翻譯為 1-3 個英文單字描述（例：「光合作用」→ `photosynthesis`、「歐洲文藝復興」→ `european-renaissance`），再套用步驟 1 的標準化。
3. **失敗 fallback**：若上述兩步結果為空字串、純符號、或無法生成合理英文，使用 `lesson-<YYYYMMDD-HHMM>` 為 slug（時間取執行當下的本地時間）。

使用者透過 `--slug=<value>` 明確指定時，以使用者提供的值為準（不做大小寫轉換、不檢查字元——但要避免路徑分隔符與非法檔名字元，必要時報錯讓使用者重下）。

## 4. Schema 必填項清單

> **Sprint 0001: hardcoded schema. Future: profile-driven.**
>
> 以下表格描述 `lessons/<slug>/topic.research.md` 在 Sprint 0001 的固定 schema。未來引入 schema profile 機制後，「必填/選填」會依課程類型（純介紹、概念講解、文獻綜述…）動態決定。任何 skill / subagent 引用本表時，請保留這條未來性提醒，避免把假設寫死進 prompt。

| 區段 | 必填？ | 備註 |
|---|---|---|
| H1 標題 | 必填 | 即主題名稱（zh-TW） |
| Metadata block | 必填 | `slug` / `generated`（ISO 8601）/ `source mode`（`web` 或 `files`）/ `depth`（`medium`） |
| 學習關鍵字 | 必填 | unordered list，3-8 個 |
| 子問題拆解 | 必填 | researcher 在搜尋前拆出的 4-6 個探索方向 |
| 核心概念 | 必填 | 5-8 個概念，每個目標 100-200 字（硬性容忍 95-200） |
| 常見誤解 | **選填** | 若主題沒有典型誤解可省略 |
| Open Questions | **選填** | researcher 認為都答完了可省略 |
| 引用 | 必填 | footnote 格式，5-10 條 |

**內容量級規則**（亦為硬規格）：

- 核心概念數量：5 ≤ N ≤ 8
- 每個核心概念字數：**目標 100-200**，硬性容忍範圍 **95 ≤ words ≤ 200**（zh-TW 字元數約等於 words）。下限 95 為 xreview 後放寬，理由見 spec.md ADR-7。
- 引用數量：5 ≤ N ≤ 10
- 每個核心概念至少有 1 個 footnote 引用，且**至少 1 個 unique source**（同一 footnote 在同一概念內重複標記不計為額外引用，例如 `[^3][^3]` 等同單一來源）

## 5. Subagent 使用原則

main agent 在以下情境**必須**透過 `Task` tool 派工到 subagent，不可在 main context 內直接執行：

- 預期會超過 5 次 `WebSearch` 呼叫的研究任務
- 預期會超過 3 次 `WebFetch` 呼叫的內容擷取
- 預期會處理超過 10,000 字以上的原文資料
- 任何 spec 中明確要求走 subagent 的流程（例：Sprint 0001 的 `/edu.research` 強制走 `edu-researcher`）

派工時，main agent 提供結構化 prompt（topic / slug / depth / 輸出契約），subagent 自行決定內部搜尋策略。subagent 回傳結果後，main agent 只做最終格式檢查與落檔，不重新展開原始資料。

## 6. 命名慣例

- **檔案 / 資料夾**：kebab-case（例：`lessons/photosynthesis/topic.research.md`）
- **slash command**：`<namespace>.<verb>` 格式（例：`/edu.research`、`/edu.outline`）
- **Subagent 名稱**：`edu-<role>` 格式（例：`edu-researcher`、`edu-reviewer`）
- **產出檔名**：固定（`topic.research.md` / `outline.md` / `slides.md`），不加日期或版本號——版本由 git 管。

## 8. outline.md schema（Sprint 0002）

> **Sprint 0002: hardcoded preset. Future: profile-driven.** —— `--level` 的 3 個 preset 以 inline 方式寫在 `/edu.outline` SKILL.md 內，本段只記錄各 level 的「必含段落」規則，供 reviewer 與後續 skill 引用。

### 三個 level 的必含段落

| 段落 | basic | standard | full |
|---|---|---|---|
| H1 標題 + metadata | 必含 | 必含 | 必含 |
| 學習目標（3-5 條，Bloom's 動詞） | 必含 | 必含 | 必含 |
| 章節骨架（4-7 章，含重點 + 時長估 + 對應研究概念） | 必含 | 必含 | 必含 |
| 預估總時長 | 必含 | 必含 | 必含 |
| 先備知識 | — | 必含 | 必含 |
| 教學方法（每章節標記） | — | 必含 | 必含 |
| 評量方式 | — | — | 必含 |
| 教學資源 | — | — | 必含 |
| 延伸學習 | — | — | 必含 |

### outline.md metadata block

```markdown
> **Slug**: <slug>
> **Level**: basic | standard | full
> **Generated**: <ISO 8601>
> **Based on**: topic.research.md
```

## 9. slides.md schema（Sprint 0002）

> **Sprint 0002: hardcoded preset. Future: profile-driven.**

| 項目 | 規格 |
|---|---|
| 格式 | Marp markdown |
| Frontmatter | `marp: true`, `theme: default`, `paginate: true` |
| 頁數 | 15-25（含標題頁 + 引用頁） |
| 分頁符 | `---`（Marp 標準） |
| 每頁 key message | 1 個 |
| Speaker notes | 每頁必含 `<!-- Speaker notes: ... -->`，≥ 1 句話 |
| 引用 | 最後 1-2 頁列出，slide 內用上標數字 `¹²³` |

### 來源

slides 同時讀取 `outline.md`（結構）與 `topic.research.md`（事實與引用）。

## 10. edu-reviewer 審查維度（Sprint 0002 簡化版）

> **Sprint 0002: 2 維度簡化版。** 進階維度（教學節奏、認知負荷、視覺設計、引用一致性）留待後續 sprint。

| 維度 | 審查內容 | 來源 |
|---|---|---|
| **學習目標覆蓋度** | outline.md 的每個學習目標，是否都有 ≥ 1 張 slide 對應覆蓋 | outline.md → slides.md |
| **內容正確性** | slides 的事實敘述是否與 research.md 一致；有無 hallucinate 出 research 沒寫的東西 | slides.md → topic.research.md |

## 12. narration / audio / render 產出規則（Sprint 0003）

> **Sprint 0003: MVP render pipeline.**

### 檔案命名

| 目錄 | 檔名格式 | 說明 |
|---|---|---|
| `narration/` | `slide-01.txt` ~ `slide-NN.txt` | 逐頁 speaker notes 文字（從 slides.md 抽取） |
| `audio/` | `slide-01.mp3` ~ `slide-NN.mp3` | Edge-TTS 逐頁語音（對應 narration/ 的 txt） |
| `dist/` | `<slug>.mp4` | 最終影片 |

編號以 01 起始、零補齊兩位數（01-99）。slide 頁碼對應 slides.md 的分頁順序（含標題頁）。

### 技術參數預設

| 項目 | 值 |
|---|---|
| TTS 引擎 | Edge-TTS (`edge-tts` Python 套件) |
| 預設 voice | `zh-TW-HsiaoChenNeural` |
| 音檔格式 | mp3 |
| 截圖格式 | PNG |
| 輸出解析度 | 1280×720 |
| 每頁 buffer | 音檔長度 + 1.5 秒 |
| Transition | 無（硬切） |
| ffmpeg concat | concat demuxer（filelist.txt） |

### 中間產物

`frames/`（截圖）和 `segments/`（逐段 mp4）在 render 完成後**自動刪除**。`audio/` 保留（老師可能要重聽或替換）。`dist/` 保留。

## 13. 反禁區（不得做）

- ❌ 不在 main agent context 內展開大型搜尋結果
- ❌ 不使用 inline 連結作為主要引用方式（用 footnote）
- ❌ 不靜默覆寫使用者已產出的 lesson 檔案
- ❌ 不假設未來的 schema profile 機制已存在
- ❌ 不繞過本檔的 schema 規則直接產出不符合的 markdown
- ❌ outline / slides 不走 subagent（ADR-8：保留 main agent 互動性）
- ❌ edu-reviewer 不修改任何檔案（只產出 review 報告）
- ❌ render 不用 Playwright page.video 錄影（ADR-12：截圖 + ffmpeg 拼接）
- ❌ narrate 不與 render 合併（ADR-13：階段化可中斷）
