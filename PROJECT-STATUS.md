# PROJECT-STATUS.md

# ECFA 關稅優惠最佳化平台｜專案現況

最後更新：2026-03-12（台灣時間）

---

## 1. 專案目標

打造一個可操作的 Web 平台，針對 **台灣出口中國大陸** 的商品，協助使用者：

1. 輸入商品與 BOM 資料
2. 進行 **ECFA 適用性初判**
3. 進行 **原產地與文件需求前置檢查**
4. 找出 **最小 BOM 調整、最大關稅優惠** 的候選方案
5. 清楚區分：
   - 法規前置判斷
   - 商業最佳化建議
   - 風險提示

> 專案定位不是 demo，而是有商業邏輯與法規依據來源的前期判斷工具。

---

## 2. GitHub Repo

- Repo：`https://github.com/ishaun0521/ecfa-tariff-optimizer`

---

## 3. 目前已完成

### A. 產品入口 + 後端 MVP API

目前已存在：
- `GET /`（前端 MVP 首頁）
- `GET /api-info`
- `GET /health`
- `POST /analyze`
- `POST /optimize`
- `POST /upload-bom`

### B. 資料模型（Schema）

已支援：
- 商品基本資料
- BOM item 資料
- 來源國
- 成本
- 是否可調整
- 最佳化條件（constraints）

### C. 測試案例與樣本輸入

已建立可測案例：
- 珍珠奶茶
- 佳德鳳梨酥
- 阿聰師芋頭酥

### D. 法規前置判斷（案例級）

後端可輸出 `ecfa_precheck`，內容包含：
- `product_family`
- `product_family_label`
- `candidate_hs_codes`
- `ecfa_goods_list_status`
- `ecfa_goods_list_reason`
- `origin_precheck_status`
- `origin_logic`
- `document_requirements`
- `legal_findings`
- `sources`
- `origin_metrics`

並已補上 3 個案例模板：
- 珍珠奶茶
- 鳳梨酥
- 芋頭酥

每個模板都已包含：
- 候選 HS code
- 關鍵原料
- 常見風險
- 原產地卡點
- 文件需求
- 優先調整槓桿
- recommended next checks

### E. 商業最佳化（案例連動）

後端已可輸出：
- `recommended_scenario`
- `candidate_scenarios`
- `scenario_score`
- `feasibility_score`
- `target_origin_ratio_pct`
- `current_taiwan_ratio_pct`
- `origin_ratio_gap_pct`
- `legal_basis_summary`
- `commercial_assessment`
- `commercial_note`

並已補上：
- `case_insights`
- `key_risk_materials`
- `recommended_next_checks`

### F. 前端結果頁（可直接演示）

前端已對齊新版 API 欄位，結果頁可直接顯示：
- 案件摘要
- ECFA 貨品清單狀態
- 原產地前置判斷
- 商業評估定位
- 關鍵材料
- 來源結構
- 缺欄位 / 補件提醒
- 風險與提醒
- 推薦方案與候選方案比較

### G. 本地可運行性驗證

已驗證可正常運作：
- `/` → 200，回 HTML
- `/api-info` → 200
- `/health` → 200
- `/docs` → 200
- `/analyze` → 200
- `/optimize` → 200
- `/upload-bom` → 200
- CSV/XLSX upload preview 可用

### H. Docker / 部署準備

已完成：
- `Dockerfile` 整理
- `.dockerignore` 新增
- `README.md` 補強
- `docs/local-validation.md` 補上

---

## 4. 已收斂的官方資料來源

目前已採用的第一輪官方來源：

1. 財政部關務署原產地規則頁  
   `https://web.customs.gov.tw/singlehtml/715`

2. ECFA 原產地認定基準  
   `https://web.customs.gov.tw/download/m232104`

3. ECFA 原產地貨品清單  
   `https://web.customs.gov.tw/download/m231959`

4. ECFA 統一規章含原產地證明書  
   `https://web.customs.gov.tw/download/m231957`

用途分工：
- **貨品清單**：判斷是否在 ECFA 範圍內
- **原產地認定基準**：判斷是否具備原產地主張空間
- **統一規章/證明書**：判斷文件需求

---

## 5. 目前尚未完成

### A. Docker 實機驗證

目前已做 API 與啟動路徑驗證，但這台環境沒有 Docker CLI，尚未完成：
- `docker build`
- `docker run`
- 容器內 `/health` 實測

### B. Zeabur 正式部署成功

目前 Zeabur 仍有 `502`，尚未完成正式可用部署。

### C. Upload 欄位 mapping

`/upload-bom` 目前先做 preview，尚未把欄位正式映射成分析用 `bom_items`。

---

## 6. 目前專案狀態判斷

### 對「有商業邏輯的 MVP」目標
**已達成**。

原因：
- `/` 已可直接打開前端 UI
- `/analyze` 已顯示法規前置判斷
- `/optimize` 已顯示可比較候選方案
- 3 個食品案例會跑出不同重點與不同風險
- 文件 / 前端 / 後端欄位已對齊
- 結果已明確區分法規前置與商業推估

### 對「正式部署交付」目標
**尚未達成**。

目前仍需：
- Docker 實機驗證
- Zeabur 部署排錯
- upload mapping 深化

### 狀態一句話

> 目前已達成 **可直接演示、具案例差異與商業邏輯的 ECFA MVP**；尚未完成的是 Docker / Zeabur 的正式部署收尾。

---

## 7. 持續推進機制

已建立 cron 持續追蹤：
- 名稱：`ECFA MVP follow-through`
- 頻率：每 30 分鐘
- 目標：檢查 `TASKS.md`、驗收條件與 repo 現況；若有回歸或新 blocker，會繼續拆任務、委派、整合與回報。

---

## 8. 重要原則

1. 不把最佳化推估假裝成法規結論
2. 不把 heuristic 分數當成最終法律判定
3. 所有 ECFA 結果必須標示：
   - 法規依據
   - 仍需人工確認的點
   - 文件需求
4. 這個平台定位是：
   - 前期判斷工具
   - 商業決策輔助工具
   - 非最終海關裁定工具
