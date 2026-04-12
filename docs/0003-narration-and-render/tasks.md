# Tasks: Sprint 0003 — Narration and Render

## TDD 適用性

本 sprint 有 2 個 Python script（`synthesize_tts.py`、`render_video.py`），可直接跑測試。Prompt files 同前兩個 sprint 用 Done 條件驗收。

## 平行評估

M1 內部：AGENTS.md → narrate SKILL / render SKILL 可平行但檔案小不值得。synthesize_tts.py 與 render_video.py 理論上可平行（不改同檔），但 render 依賴 TTS 產出做整合測試，工程上串接最安全。全部序列。

---

## Milestone 1: Plugin 擴充 + Scripts（序列）

> **預期結果**：2 個新 SKILL + 2 個 Python script + AGENTS.md 更新。plugin validate 通過、`/edu.narrate` `/edu.render` 出現在 slash command 清單。scripts 可獨立跑。
> **驗證方式**：plugin validate + print mode 識別 + script 單獨 smoke test。

- [ ] **Task 1.1：更新 `references/AGENTS.md`**
  - 新增 narration / audio / frames / dist 命名規則
  - **Done**：新段落存在、無 bare 路徑
  - **對應 AC**：前置

- [ ] **Task 1.2：撰寫 `scripts/synthesize_tts.py`**
  - 接收 txt + output mp3 + --voice
  - Edge-TTS async call
  - 錯誤處理：edge-tts 未安裝 / 網路失敗 → exit 1 + stderr
  - **Done**：`py scripts/synthesize_tts.py test.txt test.mp3` → mp3 存在且可播放
  - **對應 AC**：AC-4

- [ ] **Task 1.3：撰寫 `scripts/render_video.py`**
  - Playwright 逐頁截圖 + ffprobe 取音檔時長 + ffmpeg 逐段合成 + concat
  - 錯誤處理：Playwright / ffmpeg 未安裝 → exit 1 + stderr
  - 清理 frames/ segments/
  - **Done**：餵 sample HTML + sample audio → 輸出 mp4 可播放
  - **對應 AC**：AC-8

- [ ] **Task 1.4：撰寫 `skills/edu.narrate/SKILL.md`**
  - 解析 slides.md speaker notes → 逐頁 txt → 呼叫 synthesize_tts.py → mp3
  - 前置/衝突檢查
  - **Done**：YAML 合法、流程完整、邊界案例覆蓋
  - **對應 AC**：AC-1, AC-2, AC-3

- [ ] **Task 1.5：撰寫 `skills/edu.render/SKILL.md`**
  - 前置檢查 → 自動 build HTML (if needed) → 呼叫 render_video.py → mp4
  - 前置/衝突檢查
  - **Done**：YAML 合法、流程完整、邊界案例覆蓋
  - **對應 AC**：AC-5, AC-6, AC-7

## Milestone 2: 環境安裝（序列）

> **預期結果**：Edge-TTS / Playwright / ffmpeg 都可用。
> **驗證方式**：version check + smoke test。

- [ ] **Task 2.1：安裝 Edge-TTS + Playwright + ffmpeg**
  - `pip install edge-tts playwright`
  - `playwright install chromium`
  - `ffmpeg -version`（若沒有，提示使用者安裝）
  - **Done**：三個工具都 exit 0
  - **對應 AC**：AC-4, AC-8 前置

## Milestone 3: 端到端驗收（序列）

> **預期結果**：library-ethics 跑完 /edu.narrate → /edu.render → `dist/library-ethics.mp4` 可播放。9 條 AC 全綠。
> **驗證方式**：subprocess print mode + 人工播放 mp4。

- [ ] **Task 3.1：`/edu.narrate library-ethics`（AC-1, AC-2）**
  - 驗：narration/*.txt 存在 + audio/*.mp3 存在且可播放
- [ ] **Task 3.2：重跑 `/edu.narrate library-ethics` 衝突中止（AC-3）**
- [ ] **Task 3.3：`/edu.render library-ethics`（AC-5, AC-6）**
  - 驗：dist/library-ethics.mp4 存在、可播放、有畫面 + 聲音
- [ ] **Task 3.4：重跑 `/edu.render library-ethics` 衝突中止（AC-7）**
- [ ] **Task 3.5：端到端品質驗收（AC-9）**
  - 播放 mp4：畫面清晰？語音同步？每頁停留時間合理？
- [ ] **Task 3.6：迭代修正**（條件性）

## Sprint 完成條件

- [ ] M1 + M2 + M3 全部完成
- [ ] 9 條 AC 全綠
- [ ] `lessons/library-ethics/dist/library-ethics.mp4` 存在且可播放
- [ ] git commit（需使用者同意）
- [ ] **MVP pipeline 完成標誌**：5 commands 從主題到 mp4
