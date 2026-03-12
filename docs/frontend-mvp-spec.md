# ECFA Tariff Optimizer 前端 MVP 規格

## 1. 產品定位

### 核心任務
幫使用者把「目前產品 + 目的地 + BOM + 成本限制 + 不可動條件」整理成可分析的結構化輸入，並快速得到：
1. 是否具備進一步做 ECFA 優惠評估的資料完整度
2. 哪些材料 / 來源是優先檢查點
3. 在可接受成本增加下，有哪些可討論的商業最佳化方案

### MVP 不做什麼
- 不承諾正式法規判定
- 不自動產出最終報關結論
- 不取代關務 / 法遵審核
- 不做複雜多人協作 / 權限

---

## 2. 目標使用者
- 貿易商 / 出口商
- 食品、加工品、輕工製造業 PM / 採購 / 關務人員
- 想先快速測試 BOM 調整是否有潛在降稅空間的人

---

## 3. 使用者輸入資料範圍

### 必填欄位
- 商品名稱 `product_name`
- 目的地 `destination_country`
- 目前稅率 `current_tariff_rate`
- BOM 明細（手動輸入或上傳）

### 建議填寫欄位
- 目前 HS Code `current_hs_code`
- 目標 `optimization_goal`
  - 例：希望稅率降到 0%、希望提高 ECFA 適用機會、希望先找高風險原料
- 目前卡點 `pain_points`
  - 例：主要原料來自中國、關鍵配方不能動、不確定比例是否能調
- 最佳化原則 `optimization_principle`
  - 例：優先降稅、優先穩供、優先低改動、優先低成本
- 成本容忍等級 `cost_tolerance_level`
  - 低 / 中 / 高
- 最大成本增加 % `max_cost_increase_pct`
- 不能動條件 `immutable_conditions[]`
  - 例：品牌口感不能變、主原料 A 不可替換、單位成本不能超過 3%
- 鎖定不可調整材料 `locked_materials[]`

### BOM 欄位
每列材料包含：
- 材料名稱 `material_name`
- 比例 `ratio`
- 成本 `cost`
- 原產地 `origin_country`
- 是否可調整 `adjustable`

---

## 4. 前端資訊架構

MVP 採單頁式 5 區塊：
1. **Hero / 產品定位**
2. **基本資料表單**
3. **BOM 輸入區**
4. **最佳化條件區**
5. **分析結果區**

結果區雖仍在同頁，但視覺上應呈現為「產品化的決策卡片」，而不是 JSON dump。

---

## 5. 頁面流程

### Flow A：手動輸入
1. 使用者填商品基本資料
2. 新增 BOM 列
3. 填最佳化條件
4. 點擊「先做資料分析」
5. 查看 BOM 完整度、來源結構、ECFA 前置判斷與缺欄位
6. 再點「產出最佳化方案」
7. 查看推薦方案、候選方案與後續建議

### Flow B：先上傳 BOM
1. 使用者上傳 CSV / XLSX
2. 預覽欄位與前 5 筆資料
3. 系統提示是否符合建議欄位
4. 使用者補基本資料與條件
5. 執行分析 / 最佳化

### Flow C：資料不完整
1. 使用者缺 BOM 或比例總和不等於 100
2. 系統以黃色提示顯示「仍可分析，但結果可信度較低」
3. 允許繼續，但在結果卡上明示風險與缺欄位

---

## 6. 頁面區塊與文案

### 6.1 Hero
**標題**  
ECFA 關稅優惠最佳化平台

**副標**  
先把產品、 BOM 與成本限制整理清楚，再快速找到潛在降稅與原料調整方向。

**提醒文字**  
目前為 MVP，結果屬於前置分析與商業建議，不等同正式關務判定。

---

### 6.2 基本資料區
欄位：
- 商品名稱
- 目的地
- 目前 HS Code
- 目前稅率
- 本次目標
- 最佳化原則
- 目前卡點

按鈕：
- 載入範例資料
- 清空表單

---

### 6.3 BOM 區
#### 模式一：手動輸入表格
欄位：
- 材料名稱
- 比例 (%)
- 成本
- 原產地
- 可調整
- 刪除

表格下操作：
- 新增一列

#### 模式二：檔案上傳
- 接受 `.csv`, `.xlsx`, `.xls`
- 上傳成功後顯示：
  - 檔名
  - 欄位名稱
  - 列數
  - 前 5 筆預覽

#### 即時驗證
- 比例總和是否等於 100
- 是否至少有 1 筆 BOM
- 是否有空白材料名稱
- 成本是否為負數（目前建議列為下一版補強）

---

### 6.4 最佳化條件區
欄位：
- 成本容忍等級（低 / 中 / 高）
- 最大成本增加 %
- 不可調整材料（逗號分隔）
- 不能動條件（逐條換行）

建議 placeholder：
- 不可調整材料：`例如：奶粉、鳳梨餡核心配方`
- 不能動條件：
  `例如：`
  `1. 口感不能明顯改變`
  `2. 單位成本最多增加 3%`
  `3. 主要供應商不可更換`

操作按鈕：
- `先做資料分析`
- `產出最佳化方案`

---

### 6.5 結果區
結果區分成兩種模式：

#### A. 分析結果模式（/analyze）
1. **案件摘要卡**
   - 商品名稱 / 目的地 / 目前稅率
   - BOM 筆數
   - 比例總和
   - 可調整材料數
   - BOM 比例是否合理的產品化說明

2. **ECFA 貨品清單卡**
   - 顯示 `ecfa_precheck.ecfa_goods_list_status`
   - 顯示 `ecfa_precheck.ecfa_goods_list_reason`

3. **原產地前置判斷卡**
   - 顯示 `ecfa_precheck.origin_precheck_status`
   - 顯示 `ecfa_precheck.origin_logic`

4. **商業評估定位卡**
   - 顯示 `commercial_assessment.status`
   - 顯示 `commercial_assessment.message`

5. **關鍵材料卡**
   - 前 5 大材料
   - 材料名稱、比例、來源、是否可調整
   - 若後端有提供，也顯示 `hs_code`、`supplier_name`

6. **來源結構卡**
   - 顯示 `origin_breakdown[]`
   - 用來源國別彙總材料數與占比

7. **缺少資料 / 補件提醒卡**
   - 顯示 `missing_fields[]`
   - 顯示 `ecfa_precheck.document_requirements[]`

8. **風險與提醒卡**
   - 顯示 `warnings[]`
   - 顯示 `candidate_hs_codes[]`

#### B. 最佳化結果模式（/optimize）
1. **最佳化總覽卡**
   - 候選方案數
   - 目前台灣來源比重
   - 目標比重差距
   - 顯示 `commercial_note`

2. **推薦方向卡**
   - 顯示 `recommended_scenario`
   - 方案名稱、摘要、預估新稅率、成本增加、可行性

3. **限制條件摘要卡**
   - 顯示 `constraints.max_cost_increase_pct`
   - 顯示 `constraints.locked_materials[]`
   - 顯示 `missing_fields[]`

4. **候選最佳化方案卡群**
   每個方案至少顯示：
   - `scenario_name`
   - `summary`
   - `estimated_new_tariff_rate`
   - `tariff_reduction_pct`
   - `estimated_cost_increase_pct`
   - `feasibility_score`
   - `scenario_score`
   - `risk_level`
   - `bom_changes[]`
   - `legal_basis_summary[]`
   - `warnings[]`

5. **全局風險提醒卡**
   - 顯示 `warnings[]`

6. **下一步建議卡**
   固定文案：
   1. 確認成品 HS Code 與 ECFA 貨品清單是否匹配
   2. 驗證推薦方案的採購可行性、供應穩定度與配方影響
   3. 準備原產地證明、製程說明與供應商文件，再進入正式享惠評估

---

## 7. 元件與狀態規格

### 按鈕狀態
- 預設：可點
- Loading：顯示 `分析中...` / `產生方案中...`
- Disabled：缺必要欄位時不可點（目前為前端下一版可再補強）

### 訊息條
- 成功：綠色
- 警告：黃色
- 失敗：紅色
- 提醒：藍色

### 狀態標籤
前端需根據 API status 顯示對應色彩：
- success / eligible / ready → 綠色
- warn / check / partial / review → 黃色
- fail / blocked / ineligible → 紅色
- 其他未知狀態 → 藍色

### 空狀態
分析前顯示：
- `尚未產生結果。先填基本資料與 BOM，再開始分析。`

---

## 8. 前後端串接規格

### 8.1 分析 API
`POST /analyze`

前端送出：
- `product_name`
- `destination_country`
- `current_hs_code`
- `current_tariff_rate`
- `bom_items[]`
- `optimization_brief`

前端使用回傳：
- `summary`
- `origin_breakdown[]`
- `top_materials[]`
- `warnings[]`
- `missing_fields[]`
- `ecfa_precheck`
- `commercial_assessment`

### 8.2 最佳化 API
`POST /optimize`

前端送出：
- 基本資料
- `bom_items[]`
- `constraints`
- `optimization_brief`

前端使用回傳：
- `summary`
- `warnings[]`
- `missing_fields[]`
- `ecfa_precheck`
- `recommended_scenario`
- `candidate_scenarios[]`
- `commercial_note`
- `constraints`

### 8.3 上傳 API
`POST /upload-bom`

前端使用回傳：
- `filename`
- `columns[]`
- `row_count`
- `preview[]`

---

## 9. 前端顯示與 API 欄位對映

### /analyze
| API 欄位 | 前端呈現 |
| --- | --- |
| `summary.bom_item_count` | 案件摘要卡 |
| `summary.total_ratio` | 案件摘要卡 |
| `summary.adjustable_item_count` | 案件摘要卡 |
| `summary.ratio_warning` | 案件摘要卡的風險文案 |
| `origin_breakdown[]` | 來源結構卡 |
| `top_materials[]` | 關鍵材料卡 |
| `ecfa_precheck.ecfa_goods_list_status` | ECFA 貨品清單卡 |
| `ecfa_precheck.ecfa_goods_list_reason` | ECFA 貨品清單卡 |
| `ecfa_precheck.origin_precheck_status` | 原產地前置判斷卡 |
| `ecfa_precheck.origin_logic` | 原產地前置判斷卡 |
| `ecfa_precheck.document_requirements[]` | 缺少資料 / 補件提醒卡 |
| `ecfa_precheck.candidate_hs_codes[]` | 風險與提醒卡 |
| `warnings[]` | 風險與提醒卡 |
| `missing_fields[]` | 缺少資料 / 補件提醒卡 |
| `commercial_assessment.status` | 商業評估定位卡 |
| `commercial_assessment.message` | 商業評估定位卡 |

### /optimize
| API 欄位 | 前端呈現 |
| --- | --- |
| `summary.generated_scenario_count` | 最佳化總覽卡 |
| `summary.current_taiwan_ratio_pct` | 最佳化總覽卡 |
| `summary.origin_ratio_gap_pct` | 最佳化總覽卡 |
| `recommended_scenario` | 推薦方向卡 |
| `candidate_scenarios[]` | 候選最佳化方案卡群 |
| `candidate_scenarios[].bom_changes[]` | 方案內建議調整區塊 |
| `candidate_scenarios[].legal_basis_summary[]` | 方案內法規依據摘要 |
| `candidate_scenarios[].warnings[]` | 方案內風險提醒 |
| `commercial_note` | 最佳化總覽卡 |
| `constraints.locked_materials[]` | 限制條件摘要卡 |
| `warnings[]` | 全局風險提醒卡 |
| `missing_fields[]` | 限制條件摘要卡 |

---

## 10. 驗收標準（MVP）

### 使用者能完成
- 手動輸入 BOM 並送出分析
- 上傳 BOM 並看到預覽
- 設定不可調整材料與成本限制
- 看到 1 組以上候選最佳化方案
- 從結果頁直接看懂「先補資料 / 先查法規 / 先試哪個商業方案」

### 工程上完成
- 首頁可直接打開使用
- API 錯誤能在前端顯示
- BOM 比例異常有警告
- 支援範例資料快速測試
- 前端不再依賴 `mock_ecfa_result` / `note`
- 分析與最佳化結果以卡片化資訊呈現，而非 raw JSON

---

## 11. 待主程式串接點

1. **正式 ECFA 規則引擎持續補強**
   - 目前已改以前端消費 `ecfa_precheck`，但內容深度仍取決於後端規則完整度
2. **最佳化方案仍為 heuristic / mock 商業建議**
   - 雖已改成產品化顯示，但估算邏輯仍需後端持續強化
3. **BOM 欄位對映**
   - upload preview 目前僅預覽，尚不能一鍵映射為 `bom_items`
4. **儲存 / 匯出能力**
   - 儲存專案、匯出 PDF / Excel 報告
5. **更細的 UI 互動**
   - loading disabled state、欄位級錯誤提示、方案比較模式
6. **正式 demo 所需補件**
   - 真實案例 seed data
   - 更完整的 ECFA 文件需求與法規來源說明
