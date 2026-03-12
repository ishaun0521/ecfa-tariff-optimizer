# Local Validation Report

最後更新：2026-03-12（台灣時間）

## 本次驗證目的

確認這個 repo 目前是否已具備：
- 單網址可直接打開前端首頁
- 核心 API 可正常回應
- 稅則前置判定 / ECFA 前置分析 / 最佳化流程可本地跑通
- 官方法規來源頁、稅則教學頁、改版歷程頁可正常開啟
- Docker / PORT 路徑不存在明顯配置錯誤

## 執行環境限制

這次驗證所在機器：
- **沒有 `docker` CLI**
- 可使用系統 Python 啟動 FastAPI
- 可做本機 HTTP smoke test

因此本次採用：
- `python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8018`
- `curl` / `urllib` 對本機服務做 smoke test
- Dockerfile 做靜態檢查

## 實際 smoke test 結果

### 啟動命令

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8018
```

### 驗證項目

| 項目 | 結果 | 備註 |
|---|---|---|
| `GET /` | ✅ 200 | 回傳前端 HTML 首頁 |
| `GET /legal-sources` | ✅ 200 | 官方法規來源頁可開 |
| `GET /tariff-guide` | ✅ 200 | 稅則判定教學頁可開 |
| `GET /changelog` | ✅ 200 | 改版歷程頁可開 |
| `GET /official-sources.json` | ✅ 200 | 官方來源 JSON 可取 |
| `GET /health` | ✅ 200 | 回傳 `{"ok": true, "version": "0.5.0"}` |
| `GET /api-info` | ✅ 200 | 顯示前端頁 / API / sample BOM endpoint |
| `GET /sample-boms/*.csv` | ✅ 200 | 三個範例 BOM 可下載 |
| `POST /classify` | ✅ 200 | 稅則前置判定可用 |
| `POST /analyze` | ✅ 200 | 已含 `tariff_classification` 與 `customs_boundary_notice` |
| `POST /optimize` | ✅ 200 | 已含 `tariff_classification`、方案與邊界聲明 |
| `POST /upload-bom` | ✅ 200 | CSV preview 可用 |

## 關鍵觀察

### 1. FastAPI 已正式 serve 前端首頁

目前：
- `GET /` 直接回前端 HTML
- 使用者不再需要另外開靜態伺服器才能 demo

### 2. 稅則前置判定模組已接入

目前：
- `POST /classify` 可直接取得候選號列、缺資料、風險與人工覆核提示
- `/analyze` 與 `/optimize` 都已帶入：
  - `tariff_classification`
  - `customs_boundary_notice`

### 3. 前端已具備教育與信任頁面

目前可直接開啟：
- `/legal-sources`：展示官方法規來源與 URL
- `/tariff-guide`：展示稅則判定教學與流程圖
- `/changelog`：展示改版歷程、版號與更新時間

### 4. 範例 BOM 下載已加入首頁流程

目前：
- 三個 sample BOM CSV 可直接下載
- 使用者可先看格式，再改成自己的 BOM 上傳
- 首頁已明示目前主要聚焦於**食品類**，其他類別後續擴充

### 5. 入站邊界聲明確認彈窗已上線

目前：
- 使用者進入首頁會先看到免責 / 邊界聲明確認彈窗
- 必須勾選並按「我已了解」後，才會進入平台操作

## Docker / PORT 檢查結論

### 已確認
- 容器啟動命令使用 `${PORT:-8000}`
- `EXPOSE 8000` 合理
- Zeabur / PaaS 若注入 `PORT`，理論上可相容

### 尚未實機驗證
因環境沒有 Docker CLI，以下仍待補：

```bash
docker build -t ecfa-tariff-optimizer .
docker run --rm -p 8000:8000 -e PORT=8000 ecfa-tariff-optimizer
curl http://localhost:8000/health
```

## 距離正式交付仍待補什麼

### 主要未完項
1. **Docker 實機驗證**
   - 目前只做靜態檢查與本地 Python 啟動驗證
   - 尚未完成 `docker build` / `docker run` 實測

2. **Upload mapping 深化**
   - `/upload-bom` 目前先做 preview
   - 尚未把上傳欄位正式映射進分析用 `bom_items`

3. **Zeabur production handoff 收尾**
   - 需要在平台端確認最新版本是否已吃到最新部署
   - 並再驗一次 `/legal-sources`、`/tariff-guide`、`/changelog` 線上是否都正常

## 結論

目前這個 repo 已經是：
- **單網址可直接展示的 Web MVP**
- 具備 **稅則前置判定 + ECFA 前置分析 + 商業最佳化**
- 有 **邊界聲明、官方來源頁、教學頁、改版歷程頁、範例 BOM 下載**

也就是說，從產品展示、教育、可信度與基本流程來看，MVP 已經成立；剩下主要是 Docker / Zeabur / upload mapping 的正式交付收尾工作。
