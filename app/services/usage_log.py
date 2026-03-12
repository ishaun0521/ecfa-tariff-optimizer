"""
Usage logging service for ECFA Tariff Optimizer
"""
import json
import os
import socket
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import httpx

# Log file location
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "logs"
LOG_FILE = LOG_DIR / "usage.json"

# Admin token - should be set via environment variable
ADMIN_TOKEN = os.environ.get("ECFA_ADMIN_TOKEN", "shaun-secret-token")


def _ensure_log_dir():
    """Ensure log directory exists"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _load_logs() -> list:
    """Load existing logs from file"""
    _ensure_log_dir()
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_logs(logs: list):
    """Save logs to file"""
    _ensure_log_dir()
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def _get_ip_info(ip: str) -> dict:
    """
    Get IP geolocation info using ip-api.com (free, no API key required)
    Returns country, city, etc.
    """
    # Skip private/local IPs
    if ip in ("127.0.0.1", "localhost", "::1", "::ffff:127.0.0.1"):
        return {"country": "Local", "city": "Local", "isp": "Local"}

    # Skip internal Kubernetes/ Docker IPs
    if ip.startswith(("10.", "172.16.", "172.17.", "172.18.", "172.19.", 
                      "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                      "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                      "172.30.", "172.31.", "192.168.", "172.17.0.")):
        return {"country": "Internal", "city": "Internal", "isp": "Internal Network"}

    try:
        # Use ip-api.com free endpoint (limited to 45 requests/minute)
        response = httpx.get(
            f"http://ip-api.com/json/{ip}",
            timeout=5,
            headers={"Accept": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country", "Unknown"),
                "countryCode": data.get("countryCode", ""),
                "city": data.get("city", "Unknown"),
                "region": data.get("regionName", ""),
                "isp": data.get("isp", "Unknown"),
                "org": data.get("org", ""),
            }
    except Exception:
        pass
    
    return {"country": "Unknown", "city": "Unknown", "isp": "Unknown", "error": "lookup failed"}


def log_request(
    endpoint: str,
    ip: str,
    method: str,
    user_agent: Optional[str] = None,
    request_body: Optional[dict] = None,
) -> dict:
    """
    Log an API request
    
    Args:
        endpoint: The API endpoint path
        ip: Client IP address
        method: HTTP method
        user_agent: User agent string
        request_body: Request body (will be truncated for privacy)
    
    Returns:
        The log entry that was created
    """
    # Get IP geolocation
    ip_info = _get_ip_info(ip)
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "method": method,
        "ip": ip,
        "ip_info": ip_info,
        "user_agent": user_agent or "Unknown",
    }
    
    # Truncate request body for privacy (don't log sensitive data)
    if request_body:
        # Keep only top-level keys, truncate long values
        safe_body = {}
        for k, v in request_body.items():
            if isinstance(v, str) and len(v) > 100:
                safe_body[k] = v[:100] + "..."
            else:
                safe_body[k] = v
        log_entry["request_summary"] = safe_body
    
    # Load existing logs, add new entry, save
    logs = _load_logs()
    logs.append(log_entry)
    
    # Keep only last 1000 entries to prevent file from growing too large
    if len(logs) > 1000:
        logs = logs[-1000:]
    
    _save_logs(logs)
    
    return log_entry


def get_logs(
    admin_token: str,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """
    Get usage logs (admin only)
    
    Args:
        admin_token: The admin token to verify
        limit: Maximum number of logs to return
        offset: Number of logs to skip
    
    Returns:
        Dictionary with logs and metadata
    """
    if admin_token != ADMIN_TOKEN:
        return {"error": "Unauthorized", "valid_token_required": True}
    
    logs = _load_logs()
    total = len(logs)
    
    # Return most recent first
    reversed_logs = list(reversed(logs))
    paginated_logs = reversed_logs[offset:offset + limit]
    
    return {
        "logs": paginated_logs,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


def clear_logs(admin_token: str) -> dict:
    """Clear all logs (admin only)"""
    if admin_token != ADMIN_TOKEN:
        return {"error": "Unauthorized"}
    
    _save_logs([])
    return {"success": True, "message": "All logs cleared"}
