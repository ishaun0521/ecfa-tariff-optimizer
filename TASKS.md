# TASKS.md

# ECFA 關稅優惠最佳化平台｜開發任務清單

最後更新：2026-03-12（台灣時間）

---

## 0. 目標

把目前的 ECFA 專案從：
- 後端骨架 + 初步規則框架

推進到：
- **可操作的前端 + 可解讀的法規前置判斷 + 有產品差異的商業最佳化結果**

原則：
1. 不把 heuristic 假裝成法律結論
2. 不把前端展示假裝成已完成產品
3. 文件、API、前端必須同步
4. 先完成本地可用 MVP，再處理 Zeabur

---

## 執行看板（2026-03-12 台灣時間）

### 主協調
- **Juli（main）**：總整、驗收、更新 `TASKS.md`、判斷是否達到「有商業邏輯的 MVP」目標

### 已委派工作回收狀態
- **CIO**
  - 範圍：`app/main.py`、`app/schemas.py`、`app/services/*.py`、`examples/*`
  - 任務：P0 API contract 對齊 + P1 案例級商業邏輯補強
  - 目前狀態：`COMPLETED`（成果已回收）
- **CSO**
  - 範圍：`frontend/index.html`、`docs/frontend-mvp-spec.md`
  - 任務：P0 前端/API 對齊 + P2 結果頁與 UX 補強
  - 目前狀態：`COMPLETED`（成果已回收）
- **Infra**
  - 範圍：`README.md`、`Dockerfile`、本地驗收與 deploy-readiness
  - 任務：P0 README 對齊 + P3 本地驗收 / 容器驗證
  - 目前狀態：`COMPLETED`（成果已回收）
- **Juli（main）**
  - 任務：整合、補最後 blocker、端到端驗收、更新 `TASKS.md`
  - 目前狀態：`INTEGRATING`

### 協作規則
- 各 agent 優先處理自己負責的檔案，避免互相覆寫
- 各 agent 先在 workspace 直接修改，不自行 push；由 Juli 驗收後統一整合
- 若驗收後仍未達目標，Juli 需補任務、再拆派下一輪

---

## 1. 當前主要缺口

### Gap A：Docker 實機驗證尚未完成
- 這台環境沒有 Docker CLI
- 尚未完成 `docker build` / `docker run` 實機驗證

### Gap B：Zeabur 前端/後端已可存取，但部署驗收仍未完全收尾
- 已確認 `https://ecfa-tariff-api.zeabur.app/` 可開啟前端首頁
- 已確認 `/health`、`/analyze`、`/optimize` 在線可用
- 但尚未做完整 Docker 實機驗證與 upload mapping 深化

### Gap C：Upload 欄位 mapping 尚未做完
- `/upload-bom` 目前先做 preview
- 尚未正式映射成分析用 `bom_items`

---

## 2. 里程碑規劃

## Milestone P0：規格與前後端對齊（最高優先）
目標：讓文件、後端、前端說同一種語言。

### P0-1 更新前端規格文件
- [x] 更新 `docs/frontend-mvp-spec.md`
- [x] 將舊欄位 `mock_ecfa_result` 改為 `ecfa_precheck`
- [x] 將舊欄位 `note` 改為 `commercial_note`
- [x] 補上 `commercial_assessment` 的用途與顯示方式

**完成標準**
- 文件中的 analyze / optimize response 與後端實際欄位一致

### P0-2 對齊 README
- [x] 更新 `README.md`
- [x] 移除「mock ECFA eligibility pre-check」等過時描述
- [x] 改為「legal precheck + commercial optimization suggestions」
- [x] 補上前端如何啟用與驗收方式

**完成標準**
- README 與 `PROJECT-STATUS.md` / `SPEC.md` 一致

### P0-3 明確 API Contract
- [x] 確認 `/analyze` response contract
- [x] 確認 `/optimize` response contract
- [x] 確認 examples 與 schema 一致
- [x] 更新 `examples/analyze-request-food.json`
- [x] 更新 `examples/optimize-request.json`

**完成標準**
- examples 可直接拿來跑 API
- 回傳欄位與文件一致

### P0-4 前端正式接線
- [x] 讓 FastAPI `/` 直接 serve `frontend/index.html`
- [x] 補靜態檔案路由（若需要）
- [x] 前端改用 `ecfa_precheck`
- [x] 前端改用 `commercial_assessment`
- [x] 前端改用 `commercial_note`

**完成標準**
- 打開 `/` 就能看到前端頁
- 點分析 / 最佳化按鈕可正常顯示結果

---

## Milestone P1：商業邏輯補強（案例級）
目標：讓三個食品案例跑出「像真的在看案件」的結果。

### P1-1 建立案例模板
- [x] 珍珠奶茶 case template
- [x] 鳳梨酥 case template
- [x] 芋頭酥 case template

每個模板至少包含：
- 候選產品類別
- 候選 HS code
- 關鍵原料
- 常見風險
- 原產地常見卡點
- 文件需求
- 優先調整槓桿

**完成標準**
- 三個案例在 analyze 時能產出不同重點與不同 legal findings

### P1-2 Analyze 結果補強
- [x] 新增 `case_insights`
- [x] 新增 `key_risk_materials`
- [x] 新增 `recommended_next_checks`

**完成標準**
- 分析結果不只是 generic warnings，而是有產品差異的建議

### P1-3 Optimize 結果與案例連動
- [x] 讓最佳化方案依產品類型選擇優先槓桿材料
- [x] 讓 scenario summary 反映該產品的真實卡點
- [x] 讓 legal basis 與文件需求可追溯到產品情境

**完成標準**
- 三個案例的 candidate scenarios 不能只是換名字，要能看出不同策略

---

## Milestone P2：前端呈現與 UX 補強
目標：讓結果能直接被人看懂，而不是只看 JSON。

### P2-1 分析結果頁
- [x] 顯示商品摘要
- [x] 顯示 BOM summary
- [x] 顯示 origin breakdown
- [x] 顯示 origin precheck status
- [x] 顯示 legal findings
- [x] 顯示 document requirements
- [x] 顯示 warnings / missing_fields

**完成標準**
- 使用者不看 raw JSON 也能理解案件狀態

### P2-2 最佳化結果頁
- [x] 顯示 recommended scenario
- [x] 顯示 candidate scenarios 清單
- [x] 顯示 scenario_score / feasibility_score
- [x] 顯示 estimated tariff / cost change
- [x] 顯示 legal basis summary
- [x] 顯示 bom_changes

**完成標準**
- 使用者可直接比較不同方案，不需自行閱讀 JSON 結構

### P2-3 表單與驗證補強
- [x] 補強缺欄位提示
- [x] 補強比例總和檢查
- [x] 補強 upload preview 與 manual input 的流程說明
- [x] 補強錯誤訊息文案

**完成標準**
- 使用者能知道自己缺什麼，不會只看到失敗

---

## Milestone P3：驗收、整理、部署準備
目標：把 MVP 整理成可驗收、可部署的狀態。

### P3-1 本地驗收
- [x] `/` 可打開前端
- [x] `/health` 正常
- [x] `/docs` 正常
- [x] `/upload-bom` 可上傳 CSV / XLSX
- [x] `/analyze` 可回傳法規前置判斷
- [x] `/optimize` 可回傳候選方案

### P3-2 文件同步
- [x] `README.md` 更新
- [x] `PROJECT-STATUS.md` 更新
- [x] `SPEC.md` 更新（若欄位有增修）
- [x] `TASKS.md` 勾選已完成項目

### P3-3 部署準備
- [ ] Docker image 本地驗證
- [x] 確認 `PORT` 相容
- [x] 再回頭處理 Zeabur `502`

**完成標準**
- 本地版本先可完整演示
- 文件 / API / UI 一致

---

## 3. 推薦執行順序

### 先做（最重要）
1. P0-1 ~ P0-4：規格與前後端對齊
2. P1-1 ~ P1-3：三個案例的商業邏輯差異化

### 再做
3. P2-1 ~ P2-3：把結果頁做成人看得懂

### 最後做
4. P3-1 ~ P3-3：驗收與部署

---

## 4. 本輪 MVP 驗收定義

當下列條件同時成立，才算「有商業邏輯的 MVP」：

- [x] 打開 `/` 能直接操作 Web UI
- [x] 使用者可輸入商品與 BOM
- [x] `/analyze` 顯示法規前置判斷
- [x] `/optimize` 顯示可比較的候選方案
- [x] 三個食品案例會跑出不同重點與不同風險
- [x] 文件 / 前端 / 後端欄位一致
- [x] 結果有標示哪些是法規前置、哪些是商業推估

---

## 5. 現在建議直接開工的第一批任務

### Batch 1
- [x] 更新 `docs/frontend-mvp-spec.md`
- [x] 更新 `README.md`
- [x] 讓 `/` serve `frontend/index.html`
- [x] 改前端 JS 對齊新 API 欄位

### Batch 2
- [x] 補 3 個案例模板
- [x] 補 `case_insights`
- [x] 補 `key_risk_materials`
- [x] 補 `recommended_next_checks`

### Batch 3
- [x] 改善結果頁顯示
- [x] 跑本地驗收
- [ ] 更新文件並準備 deploy

---

## 6. 自動持續推進機制

- 已建立 cron：`ECFA MVP follow-through`
- 頻率：每 30 分鐘
- 目的：檢查 `TASKS.md` / `PROJECT-STATUS.md` / repo 狀態；若未達標或出現回歸，繼續拆任務、委派、整合與驗收
- 若目標已達成且無新變化，維持安靜，不做多餘打擾

## 7. 備註

- Zeabur `502` 不是本輪最優先，除非本地版本已完整可用
- 若發現新欄位需要擴充，先更新 `SPEC.md` 與 `docs/frontend-mvp-spec.md`，再改 API 與前端
- 這份檔案是執行用 backlog，後續每完成一項就直接勾選更新
