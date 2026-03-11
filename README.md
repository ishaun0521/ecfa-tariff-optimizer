# ECFA Tariff Optimizer MVP

FastAPI MVP for:
- product/BOM analysis
- mock ECFA eligibility pre-check
- mock BOM optimization scenarios
- CSV/XLSX BOM upload parsing

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API
- `GET /health`
- `POST /analyze`
- `POST /optimize`
- `POST /upload-bom`

## Deploy to Zeabur
1. Push this repo to GitHub
2. In Zeabur, create a new project
3. Add a service from this GitHub repo
4. Deploy with Dockerfile
5. Set env var `PORT=8000` if needed
6. Test `/health`

## Notes
Current version is an MVP skeleton. It does not yet contain official ECFA rule tables or a mathematical optimizer.
