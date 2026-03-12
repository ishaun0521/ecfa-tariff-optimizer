# Tariff Classification Module Spec

> 目的：為現有 ECFA MVP 增加一個**稅則判定模組**，作為 `ecfa_precheck` 之前的前置層。
>
> 邊界：本模組只做 **pre-classification / precheck**，不輸出海關最終裁定。

---

## 1. 模組定位

流程位置：

1. `product_facts_intake`
2. `tariff_classification_module` ← 本文件
3. `ecfa_coverage_check`
4. `origin_precheck`
5. `document_check`
6. `optimization`

本模組負責：

- 整理商品事實
- 輸出候選稅則號列
- 說明判定依據
- 標記缺資料與高風險點
- 給後續 ECFA 覆蓋 / 原產地 / 文件模組使用

---

## 2. 輸入欄位

## 2.1 必填

- `product_name`: 商品名稱
- `product_description`: 商品描述
- `destination_market`: 目的地市場，固定應支援 `CN`
- `bom_items`: BOM / 成分清單
- `manufacturing_process`: 製程說明
- `packaging_form`: 包裝型態
- `intended_use`: 用途

## 2.2 建議填寫

- `brand`
- `model`
- `net_weight`
- `ingredient_percentages`
- `source_countries`
- `retail_or_bulk`
- `supporting_documents`
- `current_declared_code`（若已有既用號列）

---

## 3. 輸出結構

```json
{
  "candidate_hs_codes": [
    {
      "code": "string",
      "confidence": "low|medium|high",
      "basis_summary": "string",
      "why_it_may_fit": ["string"],
      "why_it_may_not_fit": ["string"],
      "missing_facts": ["string"],
      "risk_level": "low|medium|high"
    }
  ],
  "selected_working_hs_code": "string|null",
  "classification_status": "preliminary|needs_manual_review|insufficient_data",
  "classification_basis_summary": "string",
  "key_missing_facts": ["string"],
  "warnings": ["string"],
  "recommended_next_checks": ["string"],
  "customs_boundary_notice": "string"
}
```

---

## 4. 與 ECFA 模組的串接

### 4.1 輸入給 `ecfa_coverage_check`

- `selected_working_hs_code`
- `candidate_hs_codes`
- `classification_status`

### 4.2 輸入給 `origin_precheck`

- `bom_items`
- `source_countries`
- `manufacturing_process`
- `selected_working_hs_code`

### 4.3 輸入給 `document_check`

- `supporting_documents`
- `key_missing_facts`
- `warnings`

---

## 5. 判定規則原則

1. 先根據商品事實輸出 **候選號列**，不要一開始硬定唯一答案。
2. 只有在資料相對完整時，才輸出 `selected_working_hs_code`。
3. 若關鍵事實不足，應回 `needs_manual_review` 或 `insufficient_data`。
4. 不得把 ECFA 覆蓋結果倒推成稅則結論。
5. 不得在輸出中宣稱「中國海關一定接受」。

---

## 6. 合法合規聲明

固定輸出：

```json
{
  "customs_boundary_notice": "This result is a pre-classification only. Final tariff classification, import duty treatment, and preferential eligibility remain subject to acceptance, review, or advance ruling by the competent China Customs authority."
}
```

---

## 7. 人工覆核觸發條件

遇到下列情況，系統應強制提示人工覆核：

- 候選號列差異大
- 主要成分比例不明
- 複合食品 / 複合製品
- 製程是否構成實質轉型有爭議
- 中國端可能需要預裁定
- 文件之間存在明顯不一致

---

## 8. 官方來源基礎

- 台灣端：財政部關務署 ECFA 原產地規則、貨品清單、統一規章、稅則查詢入口
- 中國端：海關總署官網、年度《進出口稅則》、預裁定/正式審核制度與單一窗口系統

詳細來源見：`docs/tariff-classification-research.md`
