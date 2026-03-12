# SPEC.md

# ECFA 關稅優惠最佳化平台｜開發規格

---

## 1. 產品名稱

ECFA 關稅優惠最佳化平台

---

## 2. 產品定位

本系統定位為：

> **ECFA 前期判斷 + BOM 商業最佳化決策工具**

不是：
- 純展示網站
- 純聊天機器人
- 最終報關法律認定系統

而是：
- 幫使用者快速判斷某商品是否值得進一步做 ECFA 申請評估
- 幫使用者找出 BOM / 來源 / 製程中最值得優先調整的槓桿點
- 區分法規前置結論與商業最佳化建議

---

## 3. 適用範圍

### 第一階段範圍
- 地區：**台灣出口中國大陸**
- 協議：**ECFA**
- 類別：**食品類**
- 測試產品：
  - 珍珠奶茶
  - 佳德鳳梨酥
  - 阿聰師芋頭酥

---

## 4. 使用者目標

使用者希望透過系統完成：

1. 上傳或輸入商品 BOM
2. 判斷商品是否有 ECFA 評估價值
3. 找出目前卡點
4. 確認還缺哪些資料與文件
5. 產出可執行的 BOM 調整候選方案
6. 排序出「最小改動、最大優惠」的候選方向

---

## 5. 使用者輸入規格

## 5.1 商品基本資料
- `product_name`
- `destination_country`
- `current_hs_code`
- `current_tariff_rate`
- `declared_origin_country`
- `product_category`

## 5.2 BOM item 欄位
每筆至少包含：
- `material_name`
- `ratio`
- `cost`
- `origin_country`
- `adjustable`

可選：
- `hs_code`
- `supplier_name`
- `notes`

## 5.3 真實案例欄位（前端表單）
由使用者自行輸入：
- 商品名稱
- 目的地
- 目前稅率
- 目標
- 卡點
- 可調整材料
- 不可調整材料
- 成本容忍

## 5.4 最佳化原則（前端表單）
由使用者自行輸入/選擇：
- 優先目標
  - 最小改動
  - 最大降稅
  - 成本最低
  - 風險最低
- 最大成本增加
- 不能動的條件

## 5.5 Constraints 欄位
- `max_cost_increase_pct`
- `locked_materials`
- `target_origin_ratio`
- `max_material_adjustment_count`
- `notes`

---

## 6. 功能模組規格

## 6.1 BOM 上傳與解析
### 需求
- 支援 CSV / XLSX
- 回傳欄位辨識結果
- 顯示前幾筆 preview

### API
- `POST /upload-bom`

### 輸出
- `filename`
- `columns`
- `row_count`
- `preview`

---

## 6.0 產品入口 / API 入口
### 路由
- `GET /`：前端 MVP 首頁
- `GET /api-info`：API 與入口摘要
- `GET /health`：健康檢查
- `GET /docs`：Swagger 文件

## 6.1.1 稅則判定模組（Tariff Classification Module）
### 功能定位
在 `ecfa_precheck` 前先做 **pre-classification**，輸出候選號列、判定依據、風險提示、缺資料與人工覆核點。

### 核心原則
- 只能做前期稅則判定，不冒充最終海關裁定
- 候選號列可作為 ECFA 清單比對入口，不等於最終報關號列
- 若分類不穩，`ecfa_precheck` 與 `optimize` 都必須降級呈現

### 建議輸入欄位
除既有商品基本資料與 `bom_items` 外，建議新增：
- `product_description`
- `intended_use`
- `sales_form`
- `physical_form`
- `is_ready_to_eat`
- `is_mixed_set`
- `main_ingredients`
- `manufacturing_process`
- `supporting_documents`

### 建議輸出欄位
- `classification_status`
- `confidence_level`
- `declared_hs_code_check`
- `candidate_classifications`
- `missing_information`
- `risk_flags`
- `manual_review_points`
- `downstream_impacts`
- `legal_boundary`

### 串接方式
- `POST /analyze`：先跑 `tariff_classification`，再跑 `ecfa_precheck`
- `POST /optimize`：讀取分類結果，若分類風險高則在 scenario 加註 `classification_dependency` 與 `reclassification_trigger_risk`
- 詳見：`docs/tariff-classification-module-spec.md`

## 6.2 ECFA 法規前置判斷
### API
- `POST /analyze`

### 功能目標
將商品資訊與 BOM 轉成：
- ECFA 前期判斷
- 原產地可能性前置判斷
- 文件需求
- 缺資料欄位
- 風險訊號

### 關鍵輸出欄位
- `warnings`
- `missing_fields`
- `summary`
- `origin_breakdown`
- `top_materials`
- `ecfa_precheck`
- `case_insights`
- `key_risk_materials`
- `recommended_next_checks`
- `commercial_assessment`

### `ecfa_precheck` 結構
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

---

## 6.3 商業最佳化引擎
### API
- `POST /optimize`

### 功能目標
在已知 BOM 與限制條件下，提供：
- 候選調整方案
- 優先槓桿材料
- 目標台灣來源比重
- 關稅下降推估
- 成本增加推估
- 可行性分數

### 關鍵輸出欄位
- `warnings`
- `missing_fields`
- `summary`
- `ecfa_precheck`
- `case_insights`
- `key_risk_materials`
- `recommended_next_checks`
- `commercial_assessment`
- `recommended_scenario`
- `candidate_scenarios`
- `commercial_note`

### `candidate_scenarios` 內容
每個方案至少包含：
- `scenario_name`
- `scenario_score`
- `feasibility_score`
- `legal_basis_summary`
- `warnings`
- `bom_changes`
- `estimated_new_tariff_rate`
- `tariff_reduction_pct`
- `estimated_cost_increase_pct`
- `risk_level`
- `summary`

---

## 6.4 前端 UI 模組

### 頁面 1：首頁 / 案件輸入
內容：
- 商品基本資料表單
- 真實案例欄位
- 最佳化條件欄位
- BOM upload 區塊

### 頁面 2：分析結果頁
內容：
- 商品摘要
- BOM summary
- origin breakdown
- 法規前置判斷
- 缺欄位提醒
- 文件需求

### 頁面 3：最佳化結果頁
內容：
- recommended scenario
- 候選方案列表
- 台灣來源比重差距
- 關稅下降推估
- 成本增加推估
- 風險與限制提醒

---

## 7. 法規資料來源規格

## 7.1 官方資料來源
1. 財政部關務署原產地規則頁  
   `https://web.customs.gov.tw/singlehtml/715`

2. ECFA 原產地認定基準  
   `https://web.customs.gov.tw/download/m232104`

3. ECFA 原產地貨品清單  
   `https://web.customs.gov.tw/download/m231959`

4. ECFA 統一規章含原產地證明書  
   `https://web.customs.gov.tw/download/m231957`

## 7.2 使用原則
- **貨品清單**：判斷商品是否在 ECFA 範圍內
- **原產地認定基準**：判斷原產地主張空間
- **統一規章/證明書**：判斷所需文件與程序

---

## 8. 商業邏輯原則

### 8.1 必須分開的兩層
#### 法規前置判斷
回答：
- 是否可能在 ECFA 清單範圍內
- 是否有原產地評估價值
- 還缺哪些法規關鍵資料
- 需要哪些文件

#### 商業最佳化建議
回答：
- 哪些材料最值得優先調
- 哪個方案對台灣來源比重幫助最大
- 哪個方案成本增加最小
- 哪個方案可能帶來較高關稅下降空間

### 8.2 不可混淆原則
- 最佳化建議不能偽裝成法規結論
- heuristic score 不能冒充海關認定
- 候選 HS code 不等於最終號列認定

---

## 9. 部署規格

### 9.1 第一版部署目標
- 平台：Zeabur
- project：`alice_openclaw`
- 先不上 DB

### 9.2 技術棧
- Backend：FastAPI
- Runtime：Python 3.11
- Container：Dockerfile
- Frontend：可先用靜態頁 / 後續再整合

---

## 10. 驗收標準（MVP）

### 後端驗收
- `/health` 可通
- `/docs` 可開
- `/upload-bom` 可上傳 CSV / XLSX
- `/analyze` 能回傳法規前置判斷
- `/optimize` 能回傳候選方案

### 商業邏輯驗收
- 結果要分清楚：
  - 法規前置判斷
  - 商業最佳化建議
- 需明示官方來源
- 需明示缺資料欄位
- 需明示文件需求
- 需明示哪些只是推估

### 前端驗收
- 使用者可自行輸入商品與最佳化條件
- 可上傳 BOM
- 可看到分析結果
- 可看到最佳化候選方案

---

## 11. 目前已知限制

1. 第一版聚焦食品類，尚未擴展到其他品類
2. 目前法規邏輯尚屬前期判斷，不是最終海關裁定
3. Zeabur 目前仍有部署問題需排除
4. 尚未接入正式資料庫

---

## 12. 後續擴充方向

1. 食品類個別產品更細法規映射
2. 正式 ECFA 規則表結構化
3. 真實最佳化模型（非僅 heuristic）
4. DB 儲存案件與歷史比對
5. 使用者登入與案件管理
6. 報表輸出
