---
marp: true
theme: edu-default
paginate: true
---

<!-- _class: lead -->

# Claude 全方位生產力手冊

## 從 Chatbot 到 Agent — 重新定位企業 AI

知識工作者 / 50 分鐘 / 2026

<!-- Speaker notes: 歡迎各位。今天這 50 分鐘，我們要把 Claude 拆開來看清楚——它不只是聊天機器人，而是一整套可以參與企業流程的代理系統。我們會走過五個學習目標，看完之後你會知道怎麼把它放進你的工作流。 -->

---

<!-- _class: agenda -->

## 你會學到什麼

1. **說明** Chatbot 到 Agent 的範式轉移，辨識企業評估標準如何改變
2. **比較** Claude 三大模式（Chat / Cowork / Code）的定位差異
3. **分析** Skill 與 MCP 的互補關係，與分層架構的 token 效率設計
4. **應用** Opus / Sonnet / Haiku 模型選擇策略於實際任務
5. **評估** 組織導入 Claude 建構 AI 工作系統的落地路徑

<!-- Speaker notes: 這 5 個目標是課程的骨架。每講完一個章節，我會回頭對應到目標，讓大家知道進度到哪。 -->

---

<!-- _class: lead -->

# 章節 1

## 從 Chatbot 到 Agent 的範式轉移

<!-- Speaker notes: 第一章只有一個問題：當我們說「企業要導入 AI」，到底是在導入什麼？答案在過去三年悄悄改變了。 -->

---

<!-- _class: comparison -->

## 同樣是 AI，已是兩種物種

<div class="vs-left">

### Chatbot 時代

- 被動回答問題
- 一問一答、單點互動
- 評估標準：**回答準不準**
- 上下文僅限對話本身
- 結束對話＝任務結束

</div>

<div class="vs-divider">VS</div>

<div class="vs-right">

### Agent 時代

- 主動拆解任務、調用工具
- 多步驟、跨系統協作
- 評估標準：**能不能交付成果**
- 上下文含工具、檔案、外部資料
- 任務貫穿多日多輪

</div>

<!-- Speaker notes: 左邊是 2022 年大家熟悉的 ChatGPT 時代——你問它答。右邊是 2025 年之後的 Agent 範式——它規劃、它執行、它交付。同樣叫做 AI，但已經是不同物種。 -->

---

<!-- _class: key-point -->

## 評估標準的根本改變

企業導入 AI 的問題已經從
**「能不能生成答案」**
變成
**「能不能穩定參與流程、協助完成任務、在可控範圍內產出具體成果」**

<!-- Speaker notes: 這句話請各位記住。如果你在評估 AI 工具，還在比誰的回答比較好——你已經停留在上一個時代。真正要問的是：它能不能進到我的流程裡，當一個可靠的協作者。 -->

---

<!-- _class: lead -->

# 章節 2

## Claude 四層架構全景圖

<!-- Speaker notes: 第二章是貫穿全課的地圖。Claude 的能力不是堆出來的，是分層設計的——這個分層直接決定它好不好治理、能不能規模化。 -->

---

<!-- _class: highlight-box -->

## 四層各司其職

- **Chat（大腦）**：戰略規劃、邏輯辯證——把模糊問題收斂成可執行方案
- **Skill（知識）**：把組織 SOP 模組化為可重複調用的「數位食譜」
- **MCP（手腳）**：連接外部工具與資料庫，打破資訊孤島
- **Cowork / Code（執行者）**：在受控環境交付實際成果

關鍵設計：**漸進式揭露**——依任務需求逐層啟用，降低上下文視窗稅、便於權限管理

<!-- Speaker notes: 漸進式揭露這個詞請記住。它的意思是：不是一開始就把所有 token 塞進來，而是用到才載入。這是 token 效率的核心，也是後面 Skill 三層結構要解決的問題。 -->

---

<!-- _paginate: false -->

![w:1100](diagrams/four-layer-mindmap.png)

<!-- Speaker notes: 這張心智圖把四層攤開——大家可以看到每一層下面具體有什麼。Chat 是三類任務、Skill 是三層結構、MCP 是各種工具接點、Cowork 與 Code 是執行單元。等下講到每一層時，可以回頭對照這張圖。 -->

---

<!-- _class: lead -->

# 章節 3

## Chat 模式：決策者的指揮中心

<!-- Speaker notes: Chat 不只是聊天介面。對知識工作者來說，它是邏輯整形層——把零散資訊變成決策。 -->

---

<!-- _class: cols-3 -->

## Chat 的三類高價值任務

<div class="c1">

### 問題定義

把模糊需求轉為可執行方案

*例：「業績不好」→ 拆出 6 個診斷面向與優先順序*

</div>

<div class="c2">

### 方案比較

利弊分析與風險辨識

*例：A/B/C 三方案，各列出優點、成本、風險、實施難度*

</div>

<div class="c3">

### 邏輯整理

零散資訊轉為提案架構

*例：30 條會議筆記 → 結構化的提案大綱*

</div>

<!-- Speaker notes: 這三類任務的共通點是：它們的價值不在「答案」，而在「思考過程被外顯化」。你會發現自己變得更會問問題，因為你必須把問題講清楚才能得到好答案。 -->

---

<!-- _class: quote -->

## 模型選擇是成本策略，不是面子問題

> 用最強的模型≠最聰明。
> Opus 4 解決深度推理，Sonnet 4 是日常主力，Haiku 4 處理高頻篩選——
> **任務分流，才是企業級的成本控制。**

<!-- Speaker notes: 很多公司一上來就要求「全部用最強的」。算一下成本就知道為什麼這不對——一個高頻分類任務跑 Opus，成本是跑 Haiku 的二三十倍。下一張流程圖會說明怎麼分流。 -->

---

<!-- _paginate: false -->

![w:1100](diagrams/model-selection-flow.png)

<!-- Speaker notes: 任務進來，先判斷複雜度——多步推理走 Opus，日常知識工作走 Sonnet，前線分類標籤走 Haiku。實務上你會在 Skill 或 Agent 層級設定預設模型，讓分流自動發生，不需要人工每次選。 -->

---

<!-- _class: lead -->

# 章節 4

## Cowork 模式：個人數位工作助理

<!-- Speaker notes: Chat 是想，Cowork 是做。這一章看 Claude 怎麼從給建議變成實際操作。 -->

---

<!-- _class: highlight-box -->

## Cowork 的五大能力

- **環境隔離**：受控沙盒執行，保護資料主權
- **多模態處理**：紙本 → Excel → Word 自動轉換，跨格式無縫接力
- **子代理並行**：拆任務給多個 sub-agent，避免目標模糊
- **自動化排程**：節奏化執行（每日報表、週會準備）
- **遠端調度**：行動化辦公，不在電腦前也能下指令

定位：企業知識工作的**中台執行層**

<!-- Speaker notes: 這五項能力是 Cowork 跟 Chat 的根本差異。Chat 結束對話就沒了；Cowork 會持續執行、會跨工具、會排程。所以它解決的不是「問題」，而是「流程」。 -->

---

<!-- _class: lead -->

# 章節 5

## 戰略三角：Code × Skill × MCP

<!-- Speaker notes: 這一章是技術濃度最高的一段，也是企業導入時最容易誤解的一段。我會花多一點時間。 -->

---

<!-- _class: process -->

## Code 模式：Vibe Coding 的三個關鍵

<div class="steps">

<div class="step">
<div class="step-num">1</div>
<div class="step-text"><b>情境工程</b><br/>CLAUDE.md 寫專案備忘，讓 AI 一進場就懂上下文</div>
</div>

<div class="step">
<div class="step-num">2</div>
<div class="step-text"><b>計畫模式</b><br/>先架構、後實作，避免「邊寫邊改」失控</div>
</div>

<div class="step">
<div class="step-num">3</div>
<div class="step-text"><b>Git 整合</b><br/>每步可回復，失敗實驗成本接近零</div>
</div>

</div>

<!-- Speaker notes: Vibe Coding 不是「AI 隨便寫」。是有方法的——情境先寫好、計畫先對齊、版控隨時回退。這三件事做對，AI 才能真的當你的開發夥伴而不是亂源。 -->

---

<!-- _paginate: false -->

![h:600](diagrams/skill-three-layer.png)

<!-- Speaker notes: Skill 的三層結構直接對應 token 效率。Metadata 是最上層，Claude 一進場就讀，用來判斷要不要啟用這個 Skill。Instructions 是被啟用後才讀，提供 SOP。Resources 是需要時才取——範例檔、模板、參考資料。這個分層讓你可以擁有上百個 Skill，而不會把上下文視窗灌爆。 -->

---

<!-- _class: comparison -->

## Skill vs MCP — 互補不互斥

<div class="vs-left">

### Skill：會不會做

- 封裝**方法論與 SOP**
- 解答「這件事該怎麼做」
- 三層結構控制 token 效率
- 像「教科書 + 範例」

</div>

<div class="vs-divider">VS</div>

<div class="vs-right">

### MCP：做不做得到

- 接通**外部工具與資料**
- 解答「這件事能不能做」
- 開源連接標準
- 像「工具箱 + 對外接口」

</div>

<!-- Speaker notes: 這是課程裡最重要的一張對比。常見誤解是「有 MCP 就不需要 Skill」——錯。MCP 給你工具，但不知道何時用、怎麼用；Skill 教方法，但本身不能執行。兩個都要。 -->

---

<!-- _class: lead -->

# 章節 6

## 落地：建構企業級 AI 工作系統

<!-- Speaker notes: 最後一章從技術回到組織。模型強不強已經不是競爭關鍵——誰先把它變成系統，誰才贏。 -->

---

<!-- _class: highlight-box -->

## 四項組織治理動作

- **分層**：清楚區分思考層 / 知識層 / 工具層 / 執行層，避免亂接亂用
- **制度化**：把組織 SOP 寫成 Skill，知識變成可治理資產
- **標準化**：工具接入用 MCP，避免每個團隊各搞一套
- **治理化**：人機分工有規則——誰能啟用什麼 Agent、誰負責審查產出

真正的競爭優勢：誰先建好「**可用、可管、可擴張**」的 AI 工作系統

<!-- Speaker notes: 這四件事是組織級的工作，不是個人能完成的。需要 IT、資安、業務單位一起談。提前 6 個月規劃，比事後救火便宜十倍。 -->

---

<!-- _class: quote -->

## 從工具使用者，到代理管理者

> AI 不再只是個人效率工具，
> 而是組織級的生產力引擎——
> **從「人使用工具」，演進為「人管理代理、代理執行工作」。**

<!-- Speaker notes: 這句話送給各位。下一波職場競爭，不是你會不會用 AI，而是你會不會「管理一群 AI 代理」幫你做事。今天的內容是這個能力的第一塊基礎。 -->

---

<!-- _class: summary -->

## 今日重點回顧

- ✅ **範式轉移**：評估標準從「能否答題」改為「能否交付」
- ✅ **四層架構**：Chat 想 / Skill 知 / MCP 接 / Cowork·Code 做
- ✅ **Chat 三類任務**：問題定義、方案比較、邏輯整理
- ✅ **模型分流**：Opus 戰略、Sonnet 日常、Haiku 高頻
- ✅ **Skill × MCP 互補**：方法封裝 + 工具接通，缺一不可
- ✅ **組織落地**：分層、制度化、標準化、治理化

<!-- Speaker notes: 五個學習目標都已覆蓋。如果只能記一句話，請記：分層設計才是 Claude 的核心，而不是模型本身。Q&A 時間。 -->

---

<style scoped>section{font-size:18px}</style>

## 引用來源

1. Claude 全方位生產力手冊 — 使用者提供之原始文章（accessed 2026-04-13）¹

> 註：本課程所有事實敘述、概念定義、模型選擇策略、Skill 三層結構、MCP 角色定位、企業落地路徑，皆來自上述單一原始文章。引用標記在 slide 內未逐句標註，因全簡報為單一來源綜述。

<!-- Speaker notes: 本課程資料來源單一——使用者提供的「Claude 全方位生產力手冊」。對概念有興趣深究的同學，可以回頭讀原文，或看 Anthropic 官方文件的 Skill 與 MCP 章節。 -->
