# Local Validation Report

最後更新：2026-03-12 (UTC)

## 本次驗證目的

確認這個 repo 在不修改 `app/*` 的前提下，是否已具備：
- 本地 API 可啟動
- 核心 endpoints 可回應
- 前端 prototype 現況可被正確說明
- Docker / PORT 路徑不存在明顯配置錯誤

## 執行環境限制

這次驗證所在機器：
- **沒有 `docker` CLI**
- **沒有 `python3-venv` / `ensurepip` 可用**
- 系統 Python 已具備執行 FastAPI 所需套件

因此本次採用：
- `python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8011`
- `curl` 對本機服務做 smoke test
- Dockerfile 做靜態檢查

## 實際 smoke test 結果

### 啟動命令

```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8011
```

### 驗證項目

| 項目 | 結果 | 備註 |
|---|---|---|
| `GET /` | ✅ 200 | 回傳 JSON，不是 HTML |
| `GET /health` | ✅ 200 | 回傳 `{"ok": true, "version": "0.2.0"}` |
| `GET /docs` | ✅ 200 | Swagger 可開 |
| `POST /analyze` | ✅ 200 | `examples/analyze-request-food.json` 可用 |
| `POST /optimize` | ✅ 200 | `examples/optimize-request.json` 可用 |
| `POST /upload-bom` | ✅ 200 | CSV preview 可用 |

## 關鍵觀察

### 1. FastAPI 目前沒有 serve 前端首頁

目前：
- `GET /` 會回 API metadata JSON
- `frontend/index.html` 沒有被掛到 FastAPI route

這代表：
- API 本身可跑
- 但「單一服務直接打開網址就看到前端頁」**尚未成立**

若要完整 demo，還需要主程式層修改，例如：
- `StaticFiles(directory="frontend", html=True)`
- 或額外 route 回傳 `frontend/index.html`

### 2. 前端 prototype 可做雙服務本地 demo

因後端已開 CORS `allow_origins=["*"]`，所以目前可用以下方式 demo：

- API：`uvicorn` 跑在 `:8000`
- 前端：`python3 -m http.server 3000` 服務 `frontend/`

### 3. Dockerfile 已修正明顯 build blocker

本次調整前的 Dockerfile 有一個高風險點：

```dockerfile
COPY data ./data
```

但 repo 內目前沒有 `data/` 目錄，這會讓 `docker build` 直接失敗。

本次已改為：

```dockerfile
COPY . .
```

搭配現有 `.dockerignore`，避免因缺少不存在路徑而 build fail，也把 `frontend/`、`docs/`、`examples/` 一起帶進 image。

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

## 距離 Zeabur deploy-ready 還差什麼

### 必補 blocker
1. **FastAPI 尚未正式 serve 前端頁**
   - 目前進首頁只看到 JSON
   - 若目標是單網址完整 demo，這是最明確的 blocker

2. **尚未在 Docker / Zeabur 真實環境做最後一輪驗證**
   - 本次只能靜態檢查 Dockerfile
   - 還需要實際看 container logs / health check / port mapping

### 次要缺口
3. **BOM upload 目前只有 preview，尚未完成欄位映射進正式分析流**
4. **法規結果仍屬前期 precheck / heuristic，不能當最終海關結論**

## 建議最短收斂路徑

1. 主程式接上 `frontend/index.html`
2. 在有 Docker 的環境跑一次 `docker build` / `docker run`
3. 上 Zeabur 檢查：
   - build log
   - runtime log
   - health check path
   - 對外 URL 是否直通首頁與 `/health`
4. 再做一次端到端 demo 驗收
