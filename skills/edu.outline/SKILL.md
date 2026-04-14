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

`/edu.outline <slug> [--level=basic|standard|full] [--type=lecture|proposal|briefing|report]`

從研究摘要產出大綱。支援 4 種簡報類型。是 pipeline 的第二棒。

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
| `--type` | 否 | 自動判斷 | `lecture`（教學講座）/ `proposal`（計畫提案）/ `briefing`（研究技術簡報）/ `report`（進度成果報告） |

### Type 自動判斷邏輯

如果使用者沒指定 `--type`，main agent 應**讀完 topic.research.md 後自動判斷**：

| 判斷依據 | 推斷 type |
|---|---|
| 內容有「學習目標」「教學」「課程」「學生」 | `lecture` |
| 內容有「提案」「計畫」「預算」「時程」「KPI」 | `proposal` |
| 內容有「研究方法」「實驗」「數據」「發現」「文獻」 | `briefing` |
| 內容有「進度」「里程碑」「已完成」「待辦」「下一步」 | `report` |

**如果無法判斷**（多種信號混合或都不明顯），用 `AskUserQuestion` 問使用者：
```
這份內容適合用哪種簡報類型？
- lecture（教學講座）
- proposal（計畫提案）
- briefing（研究/技術簡報）
- report（進度/成果報告）
```

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
- 建議版型節奏：`lead+bg → highlight-box → key-point`

### 2. <章節名稱>（約 X 分鐘）
- 重點：<概述>
- 對應研究概念：<research.md 的概念 M 標題>
- 建議版型節奏：`lead+bg → comparison → quote`

（4-7 章節。每章節含重點 + 時長估 + 對應研究概念 + **建議版型節奏**。）

**建議版型節奏**（Sprint 0005 P3 新增）：每章節標註 2-4 頁的版型序列，給 `/edu.slides` 的 Step 2.5 版型規劃當參考。版型選擇依據：
- 有 A vs B → `comparison`
- 有步驟 → `process`
- 有數據 → `big-number`
- 有重點條列 → `highlight-box`
- 有核心結論 → `key-point`
- 有引言/定義 → `quote`
- 普通敘述 → 預設（不標）

章節順序應有教學節奏——從基礎到進階、從定義到應用。

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

### Type: proposal（計畫提案）

以下 schema **取代** lecture 的 schema（不使用學習目標/章節骨架）。`--level` 仍有效（basic 少段、full 多段）。

```markdown
# <計畫名稱> — 提案大綱

> **Slug**: <slug>
> **Type**: proposal
> **Level**: <level>
> **Generated**: <ISO 8601>
> **Based on**: topic.research.md

## 執行摘要
<一段話概述：要做什麼、為什麼、預期成果>

## 問題陳述
- 現況痛點 1
- 現況痛點 2
（為什麼需要這個計畫？）

## 計畫目標
- 目標 1（可量化）
- 目標 2（可量化）

## 策略與方法
### 1. <策略名稱>
- 做法：<概述>
- 預期效果：<概述>

### 2. <策略名稱>
- 做法：<概述>
- 預期效果：<概述>

## 時程規劃
| 階段 | 時間 | 里程碑 |
|---|---|---|
| 第一階段 | <時間> | <里程碑> |
| 第二階段 | <時間> | <里程碑> |

## 資源需求（standard 以上）
- 人力：<需求>
- 預算：<需求>
- 工具/設備：<需求>

## 風險評估（full 才有）
| 風險 | 可能性 | 影響 | 應對策略 |
|---|---|---|---|

## 預期成果與 KPI（full 才有）
- KPI 1：<指標> → <目標值>
- KPI 2：<指標> → <目標值>
```

**版型節奏建議（proposal）**：
- 執行摘要 → `key-point` 或 `statement`
- 問題陳述 → `highlight-box`
- 策略 → `process` 或 `cols`
- 時程 → 表格頁（預設版型）
- 風險 → `comparison`（風險 vs 應對）
- 結尾 → `end`（Next Steps / Call to Action）

---

### Type: briefing（研究/技術簡報）

```markdown
# <主題> — 簡報大綱

> **Slug**: <slug>
> **Type**: briefing
> **Level**: <level>
> **Generated**: <ISO 8601>
> **Based on**: topic.research.md

## 研究背景
<為什麼要做這個研究/技術探索>

## 研究問題 / 假設
- 問題 1
- 問題 2（或假設 H1, H2）

## 方法論
### 方法 1：<名稱>
- 描述：<概述>
- 資料來源：<概述>

### 方法 2：<名稱>
- 描述：<概述>

## 發現與結果
### 發現 1：<標題>
- 關鍵數據：<概述>
- 意義：<概述>

### 發現 2：<標題>
- 關鍵數據：<概述>

## 討論（standard 以上）
- 與既有文獻的關係
- 局限性
- 意外發現

## 結論
- 結論 1
- 結論 2

## 未來方向（full 才有）
- 下一步研究 1
- 下一步研究 2
```

**版型節奏建議（briefing）**：
- 背景/問題 → `highlight-box`
- 方法 → `process` 或 `cols`
- 發現 → `big-number`（有數據時）或 `key-point`
- 討論 → `comparison`（正反觀點）或 `quote`
- 結論 → `statement`
- 結尾 → `end`

---

### Type: report（進度/成果報告）

```markdown
# <報告標題> — 報告大綱

> **Slug**: <slug>
> **Type**: report
> **Level**: <level>
> **Generated**: <ISO 8601>
> **Based on**: topic.research.md

## 執行摘要
<一段話概述：報告期間、主要成果、關鍵數字>

## 目標回顧
| 原定目標 | 達成狀態 | 說明 |
|---|---|---|
| 目標 1 | ✅ / ⚠️ / ❌ | <簡述> |
| 目標 2 | ✅ / ⚠️ / ❌ | <簡述> |

## 已完成工作
### 1. <工作項目>
- 描述：<做了什麼>
- 成果：<產出什麼>

### 2. <工作項目>
- 描述：<做了什麼>
- 成果：<產出什麼>

## 關鍵成果 / 數據
- 指標 1：<數值>（vs 目標 <數值>）
- 指標 2：<數值>

## 問題與挑戰（standard 以上）
- 問題 1：<描述> → 應對：<處理方式>
- 問題 2：<描述> → 應對：<處理方式>

## 下一步計畫
- 下一階段 1：<時間> — <目標>
- 下一階段 2：<時間> — <目標>

## 建議事項（full 才有）
- 建議 1：<描述>
- 建議 2：<描述>
```

**版型節奏建議（report）**：
- 執行摘要 → `key-point` 或 `statement`
- 目標回顧 → 表格頁（預設版型）
- 已完成工作 → `highlight-box`
- 關鍵數據 → `big-number`
- 問題 → `comparison`（問題 vs 應對）
- 下一步 → `process`
- 結尾 → `end`

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
