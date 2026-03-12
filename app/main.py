from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import AnalyzeRequest, OptimizeRequest
from app.services.analysis import analyze_product
from app.services.classification import classify_product, official_sources
from app.services.optimizer import optimize_bom
from app.services.upload import parse_uploaded_file

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
INDEX_FILE = FRONTEND_DIR / "index.html"
LEGAL_SOURCES_FILE = FRONTEND_DIR / "legal-sources.html"
TARIFF_GUIDE_FILE = FRONTEND_DIR / "tariff-guide.html"

app = FastAPI(title="ECFA Tariff Optimizer API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")


@app.get("/")
def root():
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return {
        "name": app.title,
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "classify": "POST /classify",
            "analyze": "POST /analyze",
            "optimize": "POST /optimize",
            "upload_bom": "POST /upload-bom",
            "official_sources": "GET /official-sources.json",
        },
        "note": "Frontend entry file was not found, so API metadata is returned instead.",
    }


@app.get("/legal-sources")
def legal_sources_page():
    if LEGAL_SOURCES_FILE.exists():
        return FileResponse(LEGAL_SOURCES_FILE)
    raise HTTPException(status_code=404, detail="legal-sources page not found")


@app.get("/tariff-guide")
def tariff_guide_page():
    if TARIFF_GUIDE_FILE.exists():
        return FileResponse(TARIFF_GUIDE_FILE)
    raise HTTPException(status_code=404, detail="tariff-guide page not found")


@app.get("/api-info")
def api_info():
    return {
        "name": app.title,
        "version": app.version,
        "docs": "/docs",
        "health": "/health",
        "frontend": "/",
        "pages": {
            "legal_sources": "/legal-sources",
            "tariff_guide": "/tariff-guide",
        },
        "endpoints": {
            "classify": "POST /classify",
            "analyze": "POST /analyze",
            "optimize": "POST /optimize",
            "upload_bom": "POST /upload-bom",
            "official_sources": "GET /official-sources.json",
        },
        "note": "MVP API for ECFA tariff legal precheck, pre-classification, and commercial optimization suggestions.",
    }


@app.get("/official-sources.json")
def official_sources_endpoint():
    return official_sources()


@app.get("/health")
def health():
    return {"ok": True, "version": app.version}


@app.post("/classify")
def classify(req: AnalyzeRequest):
    return classify_product(req)


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    return analyze_product(req)


@app.post("/optimize")
def optimize(req: OptimizeRequest):
    return optimize_bom(req)


@app.post("/upload-bom")
async def upload_bom(file: UploadFile = File(...)):
    try:
        return await parse_uploaded_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
