# ECFA Tariff Optimizer MVP

ECFA 關稅優惠最佳化平台的第一版 MVP。

定位不是最終報關或法律認定工具，而是把 **ECFA 法規前置初判** 與 **BOM 商業最佳化模擬** 分開呈現，讓使用者先判斷：

- 這個商品值不值得進一步做 ECFA 評估
- 目前卡點在哪裡
- 還缺哪些文件 / 欄位
- 哪些 BOM 調整方向可能比較值得先驗證

## 目前範圍

- 協議：ECFA
- 路線：台灣出口中國大陸
- 類別：食品類 MVP
- 型態：單機可跑的 FastAPI API + 一份前端靜態頁 prototype

## 目前功能

### 產品入口 / 前端
- `GET /`：前端 MVP 首頁
- `GET /legal-sources`：官方法規來源頁
- `GET /tariff-guide`：稅則判定教學頁
- `GET /api-info`：API 根路徑資訊
- Repo 內含前端靜態頁，已由 FastAPI 直接 serve
- 前端提供：
  - 商品基本資料輸入
  - BOM 手動編輯
  - BOM 檔案上傳預覽
  - 呼叫 `/classify`、`/analyze` 與 `/optimize`
  - 顯示稅則前置判定、法規前置判斷與最佳化摘要
  - 顯示邊界聲明與人工覆核提醒

### API
- `GET /health`：健康檢查
- `GET /official-sources.json`：官方來源 JSON
- `GET /sample-boms/<filename>`：下載範例 BOM CSV
- `POST /classify`：稅則前置判定（pre-classification）
- `POST /analyze`：ECFA 前置分析
- `POST /optimize`：BOM 最佳化商業方案
- `POST /upload-bom`：CSV / XLSX / XLS BOM 預覽解析

## 專案結構

```text
app/                FastAPI app
app/services/       分析、最佳化、上傳解析邏輯
frontend/           前端靜態頁 prototype
examples/           API 測試 payload
docs/               規格 / 研究文件
Dockerfile          容器啟動設定
```

## 本地執行

### 方式 A：直接用系統 Python 啟動

```bash
cd /home/node/.openclaw/workspace/ecfa-tariff-optimizer
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

打開：
- 前端首頁: `http://localhost:8000/`
- API info: `http://localhost:8000/api-info`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### 方式 B：使用虛擬環境（若主機已安裝 `python3-venv`）

```bash
cd /home/node/.openclaw/workspace/ecfa-tariff-optimizer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> 若你在 Debian / Ubuntu 上看到 `ensurepip is not available`，表示主機缺少 `python3-venv`，先補安裝再建立 venv。

## 前端 demo 目前怎麼跑

### 單服務 demo 方法
前端已由 FastAPI 直接提供，啟動 API 後即可直接開首頁：

```bash
cd /home/node/.openclaw/workspace/ecfa-tariff-optimizer
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

接著打開：
- 前端頁：`http://localhost:8000/`
- API info：`http://localhost:8000/api-info`
- Swagger：`http://localhost:8000/docs`

### 備用方式
若你仍想把前端獨立成靜態頁，也可以另外開：

```bash
cd /home/node/.openclaw/workspace/ecfa-tariff-optimizer/frontend
python3 -m http.server 3000
```

再用 `http://localhost:3000/index.html` 連同一台 API。

## Smoke test

### 1. 首頁

```bash
curl -I http://localhost:8000/
```

預期 HTTP `200`，且 `content-type` 為 `text/html`。

### 2. 健康檢查

```bash
curl http://localhost:8000/health
```

預期：

```json
{"ok":true,"version":"0.3.0"}
```

### 3. 開 docs

```bash
curl -I http://localhost:8000/docs
```

預期 HTTP `200`。

### 4. 分析 API

```bash
curl -X POST http://localhost:8000/analyze \
  -H 'Content-Type: application/json' \
  --data @examples/analyze-request-food.json
```

### 5. 最佳化 API

```bash
curl -X POST http://localhost:8000/optimize \
  -H 'Content-Type: application/json' \
  --data @examples/optimize-request.json
```

### 6. BOM upload

```bash
curl -X POST http://localhost:8000/upload-bom \
  -F file=@/path/to/your-bom.csv
```

實際驗證結果可見：`docs/local-validation.md`

## Docker

### Build

```bash
docker build -t ecfa-tariff-optimizer .
```

### Run

```bash
docker run --rm -p 8000:8000 -e PORT=8000 ecfa-tariff-optimizer
```

容器內啟動命令：

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers
```

### PORT 規則
- 預設容器監聽 `8000`
- 若部署平台注入 `PORT`，容器會自動改用該值
- Zeabur 上通常要確認平台實際 health check 與 exposed port 是否對到容器監聽 port

## 部署到 Zeabur 前，現在還差什麼

### 1. Docker build / runtime 需在有 Docker 的環境做最後驗證
這次工作環境沒有 `docker` CLI，所以我只能做 Dockerfile 靜態檢查與執行路徑審核；正式 deploy 前建議補一次：
- `docker build`
- `docker run -p <port>:<port>`
- `curl /health`

### 2. Zeabur 502 仍需區分平台層 vs 應用層
本地 API 已可跑，不代表 Zeabur 問題已解。正式 deploy-ready 前，至少要再確認：
- Zeabur service log 是否顯示 container ready
- 平台 health check 路徑與 port 是否正確
- 實際對外入口是否能打到容器內的 uvicorn

### 3. 產品層仍有後續可深化項目
這些不影響目前「有商業邏輯的 MVP」已達成，但會影響後續正式部署與交付完整度：
- 上傳 BOM 目前先做 preview，尚未把欄位映射成正式 `bom_items`
- 法規判斷仍屬前期 heuristic / precheck，不是最終海關認定

## 官方資料來源

- 財政部關務署原產地規則頁：`https://web.customs.gov.tw/singlehtml/715`
- ECFA 原產地認定基準：`https://web.customs.gov.tw/download/m232104`
- ECFA 原產地貨品清單：`https://web.customs.gov.tw/download/m231959`
- ECFA 統一規章含原產地證明書：`https://web.customs.gov.tw/download/m231957`

## Repo 內可直接拿來測的檔案

- `examples/analyze-request-food.json`
- `examples/optimize-request.json`
- `frontend/index.html`
- `docs/local-validation.md`
- `docs/tariff-classification-research.md`
- `docs/tariff-classification-module-spec.md`

## 一句話總結

現在這個 repo 已經是 **可直接單網址展示、具法規前置判斷與商業最佳化邏輯的 ECFA MVP**；若要進一步成為 **deploy-ready / production-handoff 版本**，仍需要在有 Docker / Zeabur 的環境補做最後一輪容器驗證，並深化 upload mapping。
