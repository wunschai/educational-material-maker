---
name: edu.outline
description: >
  教材製作 pipeline 的第二階段：從 topic.research.md 產出教學大綱
  lessons/<slug>/outline.md。支援 --level=basic|standard|full 三個
  詳細度 preset。main agent 直接在 context 內產出（不走 subagent）。
  Trigger: "/edu.outline", "教學大綱", "寫大綱", "備課大綱",
  "create an outline", "lesson outline", "edu.outline"。
  研究完成後的下一步，後續接 /edu.slides。
---

# edu.outline — 教學大綱

`/edu.outline <slug> [--level=basic|standard|full]`

從研究摘要產出教學大綱。是 Educational Material Maker pipeline 的第二棒。

## 前置閱讀

執行前先用 `Read` tool 讀 `${CLAUDE_PLUGIN_ROOT}/references/AGENTS.md`，特別是：

- §8 outline.md schema（3 levels 必含段落表格）
- §1 語系規則

> **路徑變數說明**：`${CLAUDE_PLUGIN_ROOT}` 指向 plugin 安裝目錄。**任何**提到 plugin 內部檔案的地方都要用此前綴，連 prompt 範本裡的也要。

## 參數解析

| 參數 | 必填 | 預設 | 說明 |
|---|---|---|---|
| `<slug>` | 是 | — | 指向 `lessons/<slug>/topic.research.md` |
| `--level` | 否 | `basic` | `basic` / `standard` / `full` 三選一 |

非法 `--level` 值 → 拒絕並列出合法值。

## 流程

### Step 1：前置檢查

1. `lessons/<slug>/` 目錄是否存在 → 不存在則中止：「請先跑 `/edu.research <topic>`」
2. `lessons/<slug>/topic.research.md` 是否存在 → 不存在則同上
3. `lessons/<slug>/outline.md` 是否已存在 → **存在則中止**：「outline.md 已存在，請刪除後重跑，或直接手改」

### Step 2：讀取研究

讀 `lessons/<slug>/topic.research.md`。若 schema 損壞（缺必要段落），best-effort 讀取能讀的部分，在 outline 開頭加 `> ⚠️ research.md 格式異常，大綱可能不完整`。

### Step 3：取得 timestamp

同 `/edu.research` 的做法：

```bash
py -c "from datetime import datetime, timezone; print(datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds'))"
```

### Step 4：根據 --level 在 context 內產出 outline

**main agent 直接寫**（ADR-8：不走 subagent，保留互動性）。依使用者指定的 level 套用對應 preset schema：

---

#### Level: basic（預設）

```markdown
# <Topic> — 教學大綱

> **Slug**: <slug>
> **Level**: basic
> **Generated**: <ISO 8601>
> **Based on**: topic.research.md

## 學習目標
- <以 Bloom's 動詞開頭的目標 1>（說明、比較、分析、應用、評估…）
- <目標 2>
- <目標 3>
（3-5 條。每條以動詞開頭、明確可驗收。對應 research 的核心概念但不需一一對應。）

## 章節骨架

### 1. <章節名稱>（約 X 分鐘）
- 重點：<概述>
- 對應研究概念：<research.md 的概念 N 標題>

### 2. <章節名稱>（約 X 分鐘）
- 重點：<概述>
- 對應研究概念：<research.md 的概念 M 標題>

（4-7 章節。每章節含重點 + 時長估 + 對應研究概念。章節順序應有教學節奏——從基礎到進階、從定義到應用。）

## 預估總時長
約 XX 分鐘
```

---

#### Level: standard

basic 全部段落，**加上**：

```markdown
## 先備知識
- <學生需要先知道的 1>
- <學生需要先知道的 2>
（列出上這堂課前學生應具備的概念或技能）
```

每個章節骨架項下**新增一行**：
```markdown
- 教學方法：講述 / 討論 / 實作 / 示範（選一或組合）
```

---

#### Level: full

standard 全部段落，**加上**：

```markdown
## 評量方式
- 形成性評量：<說明>（例：課堂提問、小組討論、即時投票）
- 總結性評量：<說明>（例：課後作業、期末報告）

## 教學資源
- <資源 1>（<來源 / URL>）
- <資源 2>（<來源 / URL>）
（課堂上會用到的教材、工具、參考資料）

## 延伸學習
- <進階主題 1>
- <補充閱讀 1>
（給有興趣的學生的延伸方向）
```

---

### Step 5：寫檔

寫入 `lessons/<slug>/outline.md`。

### Step 6：回報

- 檔案路徑
- Level
- 學習目標數量
- 章節數量
- 預估時長
- **引導下一步**：「大綱完成。請審閱後執行 `/edu.slides <slug>` 產出簡報。」

## outline 產出的品質指引

- **學習目標是 outline 的核心**——slides 階段和 reviewer 都以此為錨。寫得模糊（「了解光合作用」）不如寫得可驗收（「說明光反應與暗反應的場所差異與產物」）
- **章節順序就是教學節奏**——老師看大綱就要能想像上課的流。不是 research 的概念順序複製貼上，而是教學邏輯重組（可能把 research 概念 5 放到章節 2、概念 1 拆成兩個章節）
- **時長估是承諾**——後面 slides 的頁數分配會參照這裡。如果整堂課 50 分鐘但 7 個章節加起來只有 30 分鐘，就是大綱寫得太淺。反之加起來 90 分鐘就是太滿

## 不做的事

- ❌ 不走 subagent（ADR-8）
- ❌ 不做 web search（如果 research 資料不夠，在 outline 加 `> ⚠️ 研究資料不足以支撐本章節`，不自己去搜）
- ❌ 不靜默覆寫已存在的 outline.md
- ❌ 不處理圖片 / 多媒體
- ❌ 不產出 slides（那是下一棒 `/edu.slides`）

## Sprint 0002 註解

> **Sprint 0002: hardcoded preset. Future: profile-driven.**
>
> `--level` 的 3 個 preset schema 以 inline 寫在本 SKILL.md 內。未來引入 profile mechanism 時，這些 schema 會被抽出成獨立 profile 檔案。見 spec.md ADR-9。
