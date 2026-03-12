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

### A. 產品入口與後端 MVP API

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

### C. 測試 BOM

已建立示意測試案例：
- 珍珠奶茶
- 佳德鳳梨酥
- 阿聰師芋頭酥

### D. 法規前置判斷框架（已初步落成）

後端已可輸出 `ecfa_precheck`，內容包含：
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

### E. 商業最佳化框架（已初步落成）

後端已可輸出：
- `recommended_scenario`
- `candidate_scenarios`
- `scenario_score`
- `feasibility_score`
- `target_origin_ratio_pct`
- `current_taiwan_ratio_pct`
- `origin_ratio_gap_pct`
- `legal_basis_summary`

### F. 本地可運行性驗證

已驗證可正常運作：
- `/`
- `/health`
- `/docs`
- `/analyze`
- `/optimize`
- `/upload-bom`
- CSV/XLSX upload

### G. Docker / 部署準備

已完成：
- `Dockerfile` 整理
- `.dockerignore` 新增
- `README.md` 補強

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

### A. 食品類個別產品的細緻法規映射

目前僅做到：
- 商品家族級別的初步映射
- 候選 HS 類別
- 前置法規判斷框架

尚未做到：
- 對個別產品形成穩定、細緻、可直接採用的產品級判斷

### B. 完整前端 UI 成品

目前尚未交付完整可操作的 Web UI：
- 商品輸入表單
- BOM 上傳頁
- 分析結果頁
- 最佳化結果頁

### C. Zeabur 正式部署成功

目前 Zeabur 仍有 `502`，尚未完成正式可用部署。

---

## 6. 目前專案狀態判斷

### 已完成的層級
- 技術骨架
- 後端 API
- BOM 解析
- 法規前置判斷框架
- 商業最佳化框架
- 測試資料
- 本地可跑

### 未完成的層級
- 更細食品法規映射
- 前端成品整合
- 正式部署交付

### 狀態一句話

> 目前已具備 **可運行的後端骨架 + 初步法規前置判斷 + 商業最佳化框架**，但尚未達到可直接交付商業使用的完整 MVP。

---

## 7. 下一步建議順序

### 第一優先
補強食品類個別產品規則：
- 珍珠奶茶
- 鳳梨酥
- 芋頭酥

### 第二優先
完成前端 UI：
- 商品輸入
- BOM upload
- 法規前置結果
- 最佳化候選方案

### 第三優先
整合本地可用版本後，再處理 Zeabur 正式部署

---

## 8. 重要原則

1. 不把最佳化推估假裝成法規結論
2. 不把 demo 分數當成最終法律判定
3. 所有 ECFA 結果必須標示：
   - 法規依據
   - 仍需人工確認的點
   - 文件需求
4. 這個平台定位是：
   - 前期判斷工具
   - 商業決策輔助工具
   - 非最終海關裁定工具
