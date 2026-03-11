from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalyzeRequest, OptimizeRequest
from app.services.analysis import analyze_product
from app.services.optimizer import optimize_bom
from app.services.upload import parse_uploaded_file

app = FastAPI(title="ECFA Tariff Optimizer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

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
