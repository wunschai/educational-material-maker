---
name: edu.slides
description: >
  教材製作 pipeline 的第三階段：從 outline.md + topic.research.md 產出
  Marp 簡報 lessons/<slug>/slides.md（15-25 頁，含 speaker notes）。
  寫完後自動觸發 edu-reviewer 審查教學品質。
  Trigger: "/edu.slides", "做簡報", "產出 slides", "generate slides",
  "寫投影片", "edu.slides"。
  大綱確認後的下一步，後續接 /edu.narrate（Sprint 0003）或 build script。
---

# edu.slides — Marp 簡報

`/edu.slides <slug>`

從教學大綱與研究摘要產出 Marp 簡報。是 pipeline 的第三棒。寫完自動觸發 edu-reviewer。

## 前置閱讀

執行前先用 `Read` tool 讀 `${CLAUDE_PLUGIN_ROOT}/references/AGENTS.md`，特別是：

- §9 slides.md schema
- §10 edu-reviewer 審查維度
- §1 語系規則

> **路徑變數說明**：`${CLAUDE_PLUGIN_ROOT}` 指向 plugin 安裝目錄。**任何**提到 plugin 內部檔案的地方都要用此前綴，連 prompt 範本裡的也要。

## 參數解析

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 指向有 `outline.md` + `topic.research.md` 的 lesson |

## 流程

### Step 1：前置檢查

1. `lessons/<slug>/outline.md` 是否存在 → 不存在則中止：「請先跑 `/edu.outline <slug>`」
2. `lessons/<slug>/topic.research.md` 是否存在 → 不存在則中止：「請先跑 `/edu.research`」
3. `lessons/<slug>/slides.md` 是否已存在 → **存在則中止**：「slides.md 已存在，請刪除後重跑」

### Step 2：讀取來源

讀兩份檔案：
- `lessons/<slug>/outline.md` — 結構、學習目標、章節骨架、時長估
- `lessons/<slug>/topic.research.md` — 事實、引用、核心概念

### Step 3：在 context 內產出 Marp slides

**main agent 直接寫**（ADR-8：不走 subagent）。依照以下規則產出 slides.md：

#### Marp 結構

```markdown
---
marp: true
theme: edu-default
paginate: true
---

<!-- _class: lead -->

# <Topic>

<副標題：課程名稱 / 適用對象 / 日期>

<!-- 
Speaker notes: 歡迎各位。今天我們要來學習 <Topic>。
-->

---

## <章節 1 標題>

![bg right:40%](https://images.unsplash.com/photo-xxxxxxx?w=800)

<key message + 佐證>

<!-- 
Speaker notes: <2-3 句講課稿>
-->

---

...（更多 slides）...

---

<!-- _class: summary -->

## 今日重點回顧

- 重點 1
- 重點 2
- 重點 3

---

## 引用來源

1. <來源 1> — <URL>
2. <來源 2> — <URL>
```

#### 版型 class 使用規則（edu-default theme）

slides.md 中透過 `<!-- _class: xxx -->` 切換版型。**必須使用以下 class**：

| Class | 用在哪 | 效果 |
|---|---|---|
| `lead` | **標題頁 + 章節封面頁**（必用） | 深藍漸層背景、白字、置中大標題 |
| `invert` | 強調頁 / 對比頁 | 深色底、白字 |
| `quote` | 引言 / 名言 / 定義頁 | 大字引言框、灰底 |
| `card` | 重點整理頁 | 白色卡片風、圓角陰影 |
| `summary` | **總結頁**（必用） | 深藍漸層 + 橘色重點 |

**版型節奏建議**：不是每頁都要加 class。一般內容頁不加（用預設白底藍字），class 用於**節奏變化**——大約每 4-5 頁穿插一次 class 頁，避免視覺疲勞。

#### 圖片嵌入規則（Sprint 0004 新增）

**每個章節的第一頁**應嵌入一張相關圖片，使用 Marp 的背景圖語法：

```markdown
![bg right:40%](https://url-to-image)
```

**圖片搜尋流程**：
1. 對每個章節，用 `WebSearch` 搜尋：`<概念關鍵字> high quality photo unsplash OR wikimedia`
2. 從搜尋結果中挑一張相關、高品質、教育適用的圖片 URL
3. 嵌入時使用 `![bg right:40%]` 或 `![bg left:35%]` 交替擺放（避免所有圖都在同一側）
4. 若找不到好圖 → **不硬塞**，該頁不放圖也可以。空圖比爛圖好

**圖片數量**：全簡報 5-8 張（≈ 每章節 1 張）。不是每頁都要圖。

**圖片禁忌**：
- ❌ 不使用可能侵權的圖（優先 Unsplash / Wikimedia / Pexels，都是 free license）
- ❌ 不使用低解析度或明顯浮水印的圖
- ❌ 不在引用頁、總結頁放圖（這些頁是文字為主）

#### MCP 圖表生成規則（Sprint 0004 新增）

如果 session 中有 MCP chart / mermaid tools 可用，**在生成 slides 之前**先為適合的概念生成結構性圖表，存到 `lessons/<slug>/diagrams/`，然後在 slides.md 中用 `![bg right:45%](diagrams/xxx.png)` 嵌入。

**何時生成圖表**（判斷指引）：

| 概念特徵 | 適用圖表類型 | MCP tool |
|---|---|---|
| 有階層/分類結構 | 心智圖 | `mcp__chart__generate_mind_map` |
| 有步驟/流程 | 流程圖 | `mcp__chart__generate_flow_diagram` 或 `mcp__mermaid__generate_mermaid_diagram` |
| 有因果/影響分析 | 魚骨圖 | `mcp__chart__generate_fishbone_diagram` |
| 有集合關係/交集 | 文氏圖 | `mcp__chart__generate_venn_chart` |
| 有組織/層級關係 | 組織圖 | `mcp__chart__generate_organization_chart` |
| 有數據比較 | 長條圖/圓餅圖 | `mcp__chart__generate_column_chart` / `generate_pie_chart` |
| 有時間序列 | 折線圖 | `mcp__chart__generate_line_chart` |
| 有關鍵字/詞頻 | 文字雲 | `mcp__chart__generate_word_cloud_chart` |

**生成流程**：

1. 讀完 outline + research 後，**先掃一遍所有概念**，決定哪些適合用圖表呈現（通常 2-4 個）
2. 對每個決定要圖表的概念，呼叫對應的 MCP tool 生成圖表
3. MCP tool 會回傳圖片 URL 或 base64。用 Bash 下載存到 `lessons/<slug>/diagrams/<name>.png`
4. **圖表必須獨立一頁**——不跟文字內容擠在同一頁

**圖表嵌入方式**（重要——跟照片不同）：

```markdown
---

## <概念名稱>

<文字說明該概念的 slide>

---

<!-- _paginate: false -->

![w:1100](diagrams/<name>.png)

<!-- Speaker notes: 大家看這張圖，... -->
```

**禁止用 `![bg contain]` 嵌入圖表**——bg 是背景層，文字會渲染在圖表上方造成遮擋。改用**行內圖片** `![w:1100]` 或 `![h:600]`，讓圖表作為頁面內容、自動置中。

- 圖表頁**不放標題、不放其他文字**——只有一張行內圖片 + speaker notes
- 用 `<!-- _paginate: false -->` 隱藏圖表頁的頁碼（圖表本身就是全頁內容，頁碼多餘）
- 圖表頁的前一頁是文字說明，後一頁繼續下一個概念——形成「文字 → 圖表 → 文字」的節奏

**圖表 vs 照片的嵌入差異**：

| | 照片 | MCP 圖表 |
|---|---|---|
| 嵌入語法 | `![bg right:40%](url)` | `![bg contain](diagrams/x.png)` |
| 是否與文字同頁 | ✅ 是（照片是背景） | ❌ 否（圖表獨佔一頁） |
| 原因 | 照片是氛圍、文字是主角 | 圖表本身就是內容，需要全頁空間才能看清楚 |

**圖表數量**：全簡報 2-4 張 MCP 圖表。不是每個概念都需要圖表——只有「結構化資訊」才值得圖表化。每張圖表佔 1 頁，所以 4 張圖表 = 多出 4 頁，規劃時要算進 15-25 頁上限。

**圖表 + 照片並用**：
- MCP 圖表用在「需要結構化呈現」的概念（流程、分類、比較）→ 獨佔整頁
- Unsplash 照片用在「需要情境感」的章節封面頁 → `bg right:40%` 側邊
- 兩者不要放在同一頁

**MCP 不可用時的 fallback**：如果 session 中沒有 MCP chart/mermaid tools（使用者沒配 `.mcp.json`），就跳過圖表生成，只用照片。不要因為沒有 MCP 就中止流程。

#### 產出規則

| 規則 | 要求 |
|---|---|
| **Theme** | `edu-default`（在 frontmatter 寫 `theme: edu-default`）|
| **頁數** | 15-25 頁（含標題頁 + 引用頁）。超過 25 頁 → 自行裁剪合併 |
| **每頁密度** | 1 個 key message + 佐證。不塞滿 |
| **每頁 speaker notes** | **必含** `<!-- Speaker notes: ... -->`，≥ 1 句話 |
| **版型 class** | 標題頁必用 `lead`、總結頁必用 `summary`、其餘酌用 `quote` / `card` / `invert` |
| **圖片** | 每章節第一頁盡量配一張 `![bg right:40%]` 或 `![bg left:35%]`，全簡報 5-8 張 |
| **章節分隔** | 用 `## <章節標題>` 起頭 |
| **頁分配** | 參照 outline 的時長估 |
| **引用** | 最後 1-2 頁列表。slide 內用上標 `¹²³`。**引用頁字體用 `<!-- _class: references -->` 或手動加 `<style scoped>section{font-size:18px}</style>`**，避免文字溢出導致 Marp 自動產生重複頁面。每頁最多放 5 條引用，超過就分成多頁並用 `---` 顯式分頁 |
| **學習目標覆蓋** | 每個 outline 學習目標至少有 1 張 slide |
| **事實來源** | 只寫 research.md 有的事實 |

#### 教學設計指引

- **開場**：`<!-- _class: lead -->` 標題頁 + 1 張「這堂課你會學到什麼」（學習目標摘要）
- **每章節起手**：章節封面用 `lead` class + 右側圖片，再分 2-3 張 slide 拆解細節
- **定義 / 名言**：用 `quote` class 搭配 blockquote
- **重點整理**：用 `card` class
- **結尾**：`summary` class 的「今日重點回顧」+ 引用來源頁
- **speaker notes 風格**：口語化但不失專業，像老師在課堂上「講話」的語調

### Step 4：超頁防呆

產出完 markdown 後，數一數 `---` 分頁符 → 如果超過 25 頁：
- 找出最不關鍵的 slide（佐證/補充/例子類），合併或刪除
- 重數確認 ≤ 25
- 如果仍超過（章節太多、每章節都必要），在回報中加 `> ⚠️ slides 仍有 N 頁（超過 25 頁上限），建議手動裁剪`

### Step 5：寫檔

寫入 `lessons/<slug>/slides.md`。

### Step 5.5：視覺自審（Visual Self-Review）

寫完 slides.md 後、觸發 reviewer 前，**必須自己先用瀏覽器看一遍**：

1. 執行 `bash ${CLAUDE_PLUGIN_ROOT}/scripts/build_slides.sh lessons/<slug>/slides.md` 產出 HTML
2. 用 Playwright 截圖所有頁面：

```python
from playwright.sync_api import sync_playwright
from pathlib import Path

html = Path('lessons/<slug>/slides.html').resolve().as_uri()
out = Path('lessons/<slug>/preview')
out.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})
    page.goto(html, wait_until='networkidle')
    count = page.evaluate('document.querySelectorAll("section").length')
    for i in range(count):
        if i > 0:
            page.keyboard.press('ArrowRight')
        page.wait_for_timeout(500)
        page.screenshot(path=str(out / f'slide-{i+1:02d}.png'))
    browser.close()
```

3. 用 `Read` tool **逐頁看截圖**，檢查以下常見問題：

| 問題 | 怎麼看到 | 怎麼修 |
|---|---|---|
| **文字溢出產生重複頁** | section 數 > `---` 分頁數；最後幾頁內容完全相同 | 縮短該頁文字、縮小字體、或用 `---` 顯式分頁 |
| **圖表被文字遮擋** | 圖表頁上有標題文字蓋在圖表內容上 | 圖表頁不放文字、改用行內圖 `![w:1100]` 而非 `![bg]` |
| **照片 404 / 破圖** | 章節封面頁只有深藍底 + 小字，應有照片的位置是空的 | 換一張照片 URL 或改成不放照片的純 lead 頁 |
| **頁面太空** | 大片空白，只有一行字 | 合併到前一頁或加內容 |
| **字太小看不清** | 整段文字縮成很小一塊 | 拆成多頁或精簡文字 |

4. **發現問題就修 slides.md 再重新 build + 截圖驗證**。**不要帶著已知問題進入 reviewer 階段**——reviewer 看的是內容不是版面，視覺問題只有你自己能抓。

5. 清理 `preview/` 目錄（截圖是暫時的）

### Step 6：自動觸發 edu-reviewer

寫完 slides 後，**自動**用 Task tool 呼叫 `edu-reviewer` subagent：

```
你是 edu-reviewer。

- slug: <slug>
- outline_path: lessons/<slug>/outline.md
- slides_path: lessons/<slug>/slides.md
- research_path: lessons/<slug>/topic.research.md

請依照 ${CLAUDE_PLUGIN_ROOT}/agents/edu-reviewer.md 的審查流程，
針對以下兩個維度審查 slides.md：
1. 學習目標覆蓋度：outline 的每個學習目標是否都有對應的 slide 覆蓋？
2. 內容正確性：slides 的事實敘述是否與 research.md 一致？有無 hallucinate？

回傳 review 報告（純 markdown），不修改任何檔案。
第一個字元必須是 # 標題。
失敗時回傳 REVIEW_FAILED: <原因> 開頭的單行字串。
```

### Step 7：呈現 review 結果

接收 reviewer 回傳後：

**reviewer 回傳 `REVIEW_FAILED:`**：告知使用者 review 失敗原因，不 retry。

**reviewer 回傳 review 報告**：

1. 把完整 review 報告呈現給使用者
2. 如果有 🔴 Critical 問題 → 用 AskUserQuestion 問使用者：「review 發現嚴重問題，要修改 slides.md 嗎？」
3. 如果只有 🟡 Important 或全綠 → 告知使用者，不強迫修改

### Step 8：回報

- slides 路徑
- 頁數
- reviewer 結果摘要（X 個目標覆蓋、Y 個 critical、Z 個 important）
- **引導下一步**：
  - 若有問題：「建議修改後重跑 `/edu.slides`（先刪除 slides.md）」
  - 若全綠：「slides + review 完成。可以用 `bash scripts/build_slides.sh lessons/<slug>/slides.md` 預覽 HTML。下一步（Sprint 0003）：`/edu.narrate <slug>`」

## 不做的事

- ❌ 不走 subagent 產出 slides（ADR-8）
- ❌ 不做 web search（事實只來自 research.md）
- ❌ 不靜默覆寫已存在的 slides.md
- ❌ 不處理圖片 / 影片嵌入
- ❌ 不解析 speaker notes 為音檔（那是 Sprint 0003 `/edu.narrate`）
- ❌ 不自動呼叫 build_slides.sh（使用者手動呼叫或等 Sprint 0003）

## Sprint 0002 註解

> **Sprint 0002: hardcoded slides schema. Future: profile-driven.**
>
> slides 的頁數範圍 (15-25)、密度規則、speaker notes 格式都是固定的。未來可能依「5 分鐘速講」vs「90 分鐘正課」而有不同 preset。見 spec.md ADR-9。
