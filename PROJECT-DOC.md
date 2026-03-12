# ECFA 關稅優惠最佳化平台

## 專案概述

這是 CAIO 提供的 ECFA 關稅優惠最佳化 AI 助手，旨在幫助企業快速判斷產品是否符合 ECFA 優惠關稅資格，並提供 BOM 調整建議與成本優化方案。

### 核心功能
- **法規前置判斷**：分析產品是否可能符合 ECFA 原產地規則
- **關稅優化建議**：提供可比較的 BOM 調整候選方案
- **商業評估**：考量成本、口感、法規風險等因素
- **樣本案例**：珍珠奶茶、鳳梨酥、芋頭酥等食品類案例

---

## 專案資訊

### GitHub Repo
- URL: `https://github.com/ishaun0521/ecfa-tariff-optimizer`

### 線上站點
- URL: `https://ecfa-tariff-api.zeabur.app/`

### API 文件
- Swagger UI: `https://ecfa-tariff-api.zeabur.app/docs`

---

## API 端點

| 端點 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 前端首頁 |
| `/health` | GET | 健康檢查 |
| `/classify` | POST | 產品分類 |
| `/analyze` | POST | 法規前置分析 |
| `/optimize` | POST | BOM 優化建議 |
| `/upload-bom` | POST | 上傳 BOM 檔案 |
| `/official-sources.json` | GET | 官方法規來源 |
| `/legal-sources` | GET | 法規說明頁面 |
| `/tariff-guide` | GET | 稅則判定教學 |
| `/changelog` | GET | 改版歷程 |

---

## 使用紀錄系統

### 查看使用紀錄

```bash
curl -s -X GET "https://ecfa-tariff-api.zeabur.app/admin/usage-logs?limit=30" -H "X-Admin-Token: <token>"
```

### Admin Token
- **預設 token**: `shaun-secret-token`
- **建議**: 在 Zeabur 環境變數設定自定義密碼：`ECFA_ADMIN_TOKEN`

### 紀錄內容
- **前端追蹤**: page_view, click, form_submit, scroll, time_on_page, user_idle
- **後端 API**: /classify, /analyze, /optimize, /upload-bom
- **包含欄位**: 時間戳、IP、IP 地點、Session ID、User-Agent、瀏覽器、操作行為

### 注意
Zeabur 有 Load Balancer，真實訪客 IP 會顯示為內部 IP (10.42.0.1)，無法取得正確地理位置。這是 Zeabur 架構限制。

---

## 開發資訊

### 技術棧
- **後端**: FastAPI + Python
- **前端**: 靜態 HTML + Tailwind CSS
- **部署**: Zeabur

### 主要目錄結構
```
ecfa-tariff-optimizer/
├── app/
│   ├── main.py              # FastAPI 主程式
│   ├── schemas.py           # API 資料模型
│   └── services/
│       ├── analysis.py      # 分析邏輯
│       ├── classification.py # 分類邏輯
│       ├── optimizer.py     # 優化邏輯
│       ├── usage_log.py     # 使用紀錄服務
│       └── ...
├── frontend/
│   ├── index.html           # 主頁面
│   ├── legal-sources.html   # 法規說明
│   ├── tariff-guide.html   # 稅則教學
│   ├── changelog.html       # 改版歷程
│   └── assets/
│       └── tracking.js     # 前端追蹤程式
├── data/
│   ├── logs/               # 使用紀錄（不含於 Git）
│   └── sample_boms/       # 範例 BOM 檔案
├── requirements.txt
└── Dockerfile
```

### 相關環境變數
- `ECFA_ADMIN_TOKEN`: 管理員密碼（用於查看使用紀錄）

---

## MVP 驗收標準（已完成）

✅ `/` 可直接打開前端 UI  
✅ `/analyze` 可回傳法規前置判斷  
✅ `/optimize` 可回傳可比較的候選方案  
✅ 珍珠奶茶 / 鳳梨酥 / 芋頭酥三個案例已具差異化商業邏輯  
✅ 結果已清楚區分法規前置判斷與商業推估  

---

## 剩餘工作（非 blocker）

- Docker 實機驗證
- `/upload-bom` 正式 mapping 成分析用 `bom_items`
- Zeabur / production handoff 收尾

---

## 聯絡方式

如有問題或建議，歡迎聯繫：
- Email: aicoach@caio.com.tw
- 網站: https://caio.com.tw
