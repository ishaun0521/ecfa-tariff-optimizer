import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.schemas import AnalyzeRequest, OptimizeRequest
from app.services.analysis import analyze_product
from app.services.classification import classify_product, official_sources
from app.services.optimizer import optimize_bom
from app.services.upload import parse_uploaded_file
from app.services.usage_log import log_request, log_frontend_event, get_logs, clear_logs, ADMIN_TOKEN

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
SAMPLE_BOM_DIR = BASE_DIR / "data" / "sample_boms"
INDEX_FILE = FRONTEND_DIR / "index.html"
LEGAL_SOURCES_FILE = FRONTEND_DIR / "legal-sources.html"
TARIFF_GUIDE_FILE = FRONTEND_DIR / "tariff-guide.html"
CHANGELOG_FILE = FRONTEND_DIR / "changelog.html"

app = FastAPI(title="ECFA Tariff Optimizer AI Assistant API", version="0.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
if SAMPLE_BOM_DIR.exists():
    app.mount("/sample-boms", StaticFiles(directory=SAMPLE_BOM_DIR), name="sample-boms")


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
            "sample_boms": "GET /sample-boms/<filename>",
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


@app.get("/changelog")
def changelog_page():
    if CHANGELOG_FILE.exists():
        return FileResponse(CHANGELOG_FILE)
    raise HTTPException(status_code=404, detail="changelog page not found")


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
            "changelog": "/changelog",
        },
        "endpoints": {
            "classify": "POST /classify",
            "analyze": "POST /analyze",
            "optimize": "POST /optimize",
            "upload_bom": "POST /upload-bom",
            "official_sources": "GET /official-sources.json",
            "sample_boms": "GET /sample-boms/<filename>",
        },
        "note": "MVP API for ECFA tariff legal precheck, pre-classification, and commercial optimization suggestions.",
    }


@app.get("/official-sources.json")
def official_sources_endpoint():
    return official_sources()


@app.get("/health")
def health():
    return {"ok": True, "version": app.version}


# ============================================
# Frontend tracking endpoint
# ============================================

@app.post("/api/track")
async def track_event(request: Request):
    """
    Receive frontend tracking events
    
    This endpoint is called by the JavaScript tracking code
    to log page views, clicks, form submissions, etc.
    """
    try:
        body = await request.json()
        
        # Get client IP for the tracking data
        client_ip = request.client.host if request.client else "unknown"
        
        # Get IP geolocation
        from app.services.usage_log import _get_ip_info
        ip_info = _get_ip_info(client_ip)
        
        # Add IP info to the event
        body["ip"] = client_ip
        body["ip_info"] = ip_info
        
        # Log the event
        log_frontend_event(body)
        
        return {"success": True}
    except Exception as e:
        # Silently fail - don't break the frontend
        return {"success": False}


@app.post("/classify")
def classify(req: AnalyzeRequest, request: Request = None, user_agent: Optional[str] = Header(None)):
    # Log the request
    if request:
        client_ip = request.client.host if request.client else "unknown"
        log_request(
            endpoint="/classify",
            ip=client_ip,
            method="POST",
            user_agent=user_agent,
            request_body=req.model_dump() if req else None
        )
    return classify_product(req)


@app.post("/analyze")
def analyze(req: AnalyzeRequest, request: Request = None, user_agent: Optional[str] = Header(None)):
    # Log the request
    if request:
        client_ip = request.client.host if request.client else "unknown"
        log_request(
            endpoint="/analyze",
            ip=client_ip,
            method="POST",
            user_agent=user_agent,
            request_body=req.model_dump() if req else None
        )
    return analyze_product(req)


@app.post("/optimize")
def optimize(req: OptimizeRequest, request: Request = None, user_agent: Optional[str] = Header(None)):
    # Log the request
    if request:
        client_ip = request.client.host if request.client else "unknown"
        log_request(
            endpoint="/optimize",
            ip=client_ip,
            method="POST",
            user_agent=user_agent,
            request_body=req.model_dump() if req else None
        )
    return optimize_bom(req)


@app.post("/upload-bom")
async def upload_bom(file: UploadFile = File(...), request: Request = None, user_agent: Optional[str] = Header(None)):
    # Log the request
    if request:
        client_ip = request.client.host if request.client else "unknown"
        log_request(
            endpoint="/upload-bom",
            ip=client_ip,
            method="POST",
            user_agent=user_agent,
            request_body={"filename": file.filename}
        )
    try:
        return await parse_uploaded_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# Admin endpoints (Shaun only)
# ============================================

@app.get("/admin/usage-logs")
def admin_get_logs(
    request: Request,
    token: Optional[str] = Header(None, alias="X-Admin-Token"),
    limit: int = 100,
    offset: int = 0,
):
    """
    Get usage logs (admin only)
    
    Usage: GET /admin/usage-logs?limit=50&offset=0
    Headers: X-Admin-Token: <your-admin-token>
    
    Or use query param: ?token=<your-admin-token>
    """
    # Check token
    admin_token = token or request.query_params.get("token")
    if not admin_token:
        return {"error": "Admin token required", "hint": "Use X-Admin-Token header or ?token= query param"}
    
    return get_logs(admin_token, limit=limit, offset=offset)


@app.delete("/admin/usage-logs")
def admin_clear_logs(
    request: Request,
    token: Optional[str] = Header(None, alias="X-Admin-Token"),
):
    """
    Clear all usage logs (admin only)
    
    Usage: DELETE /admin/usage-logs
    Headers: X-Admin-Token: <your-admin-token>
    """
    admin_token = token or request.query_params.get("token")
    if not admin_token:
        return {"error": "Admin token required", "hint": "Use X-Admin-Token header or ?token= query param"}
    
    return clear_logs(admin_token)


# ============================================
# Request logging middleware for all endpoints
# ============================================

@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    """Log all incoming requests"""
    # Skip logging for admin endpoints and health checks
    if not request.url.path.startswith("/admin") and request.url.path != "/health":
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Get request body if present (for POST/PUT)
        body = None
        if request.method in ("POST", "PUT"):
            # We can't read body here easily, just log the method
            body = {"method": request.method}
        
        log_request(
            endpoint=request.url.path,
            ip=client_ip,
            method=request.method,
            user_agent=user_agent,
            request_body=body
        )
    
    response = await call_next(request)
    return response
