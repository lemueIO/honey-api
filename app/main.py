import os
import uuid
import json
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Optional, List

import ipaddress
import requests
import redis
from fastapi import FastAPI, Request, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CLIENT = redis.from_url(REDIS_URL, decode_responses=True)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "change-me-at-all-costs")

app = FastAPI(title="Threat Intelligence Bridge")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

@app.middleware("http")
async def fix_double_slashes(request: Request, call_next):
    if "//" in request.scope["path"]:
        request.scope["path"] = request.scope["path"].replace("//", "/")
    response = await call_next(request)
    return response

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Models ---
class HFishWebhook(BaseModel):
    attack_ip: str

# --- Database Keys ---
KEY_WHITELIST = "ti:whitelist"
KEY_BLACKLIST = "ti:blacklist"
KEY_LOCAL = "ti:local:"  # ti:local:{ip} -> date
KEY_OSINT = "ti:osint:"   # ti:osint:{ip} -> date
KEY_API_KEYS = "ti:api_keys"
KEY_API_KEYS_V2 = "ti:api_keys_v2" # Hash: key -> name

# --- Auth Dependency ---
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    return user

# --- Logic ---

def is_ip_in_cidr_list(ip: str, redis_key: str) -> bool:
    """
    Check if an IP is in a Redis set, handling both exact matches and CIDR ranges.
    """
    # 1. Try exact match first (O(1) in Redis)
    if REDIS_CLIENT.sismember(redis_key, ip):
        return True
    
    # 2. If not found, iterate through all members to check for CIDR ranges
    members = REDIS_CLIENT.smembers(redis_key)
    try:
        target_ip = ipaddress.ip_address(ip)
    except ValueError:
        return False # Invalid IP input

    for member in members:
        try:
            # Check if member is a CIDR range (e.g., "10.0.0.0/24")
            if "/" in member:
                network = ipaddress.ip_network(member, strict=False)
                if target_ip in network:
                    return True
        except ValueError:
            continue # Ignore invalid entries
            
    return False

def get_ip_reputation(ip: str):
    # 1. Whitelist
    if is_ip_in_cidr_list(ip, KEY_WHITELIST):
        return "clean", ["whitelist"]
    
    # 2. Blacklist
    if is_ip_in_cidr_list(ip, KEY_BLACKLIST):
        return "high", ["permanent blacklist"]
    
    # 3. Local Data
    if REDIS_CLIENT.exists(f"{KEY_LOCAL}{ip}"):
        return "high", ["hfish honeypot"]
    
    # 4. OSINT
    if REDIS_CLIENT.exists(f"{KEY_OSINT}{ip}"):
        return "medium", ["osint feed"]
    
    return "clean", []

def format_threatbook_v3(ip: str, severity: str, judgments: List[str]):
    return {
        "code": 0,
        "data": {
            ip: {
                "severity": severity,
                "judgments": judgments,
                "update_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
        },
        "message": "success"
    }

# --- Background Task: OSINT Feeds ---

async def fetch_osint_feeds():
    while True:
        try:
            logger.info("Fetching OSINT feeds...")
            # Feodo Tracker
            feodo_url = "https://feodotracker.abuse.ch/downloads/ipblocklist.txt"
            r = requests.get(feodo_url, timeout=10)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    if line and not line.startswith("#"):
                        # Store for 90 days
                        REDIS_CLIENT.setex(f"{KEY_OSINT}{line.strip()}", timedelta(days=90), datetime.now().isoformat())
            
            # IPSum (Simplified, just TOP level)
            ipsum_url = "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt"
            r = requests.get(ipsum_url, timeout=10)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    if line and not line.startswith("#"):
                        parts = line.split()
                        if len(parts) > 1 and int(parts[1]) > 3: # Only high-confidence IPs
                             REDIS_CLIENT.setex(f"{KEY_OSINT}{parts[0]}", timedelta(days=90), datetime.now().isoformat())
            
            logger.info("OSINT feeds updated.")
        except Exception as e:
            logger.error(f"Error fetching OSINT: {e}")
        
        await asyncio.sleep(24 * 3600) # Every 24 hours

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(fetch_osint_feeds())

# --- API Routes ---

@app.get("/v3/scene/ip_reputation")
async def ip_reputation(resource: str, apikey: str):
    # Check both old and new keys for compatibility
    if not REDIS_CLIENT.sismember(KEY_API_KEYS, apikey) and not REDIS_CLIENT.hexists(KEY_API_KEYS_V2, apikey):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    severity, judgments = get_ip_reputation(resource)
    return format_threatbook_v3(resource, severity, judgments)

@app.post("/webhook")
async def hfish_webhook(data: HFishWebhook):
    # Store local data for 365 days
    REDIS_CLIENT.setex(f"{KEY_LOCAL}{data.attack_ip}", timedelta(days=365), datetime.now().isoformat())
    return {"status": "ok"}

# --- Auth Routes ---

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        request.session["user"] = "admin"
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid password"})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

# --- Dashboard Routes ---

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, user: str = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
        
    # Stats
    local_ips = len(REDIS_CLIENT.keys(f"{KEY_LOCAL}*"))
    osint_ips = len(REDIS_CLIENT.keys(f"{KEY_OSINT}*"))
    blacklist_count = REDIS_CLIENT.scard(KEY_BLACKLIST)
    whitelist_count = REDIS_CLIENT.scard(KEY_WHITELIST)
    
    # API Keys V2
    api_keys_dict = REDIS_CLIENT.hgetall(KEY_API_KEYS_V2)
    # Support legacy keys (no name)
    legacy_keys = REDIS_CLIENT.smembers(KEY_API_KEYS)
    for lk in legacy_keys:
        if lk not in api_keys_dict:
            api_keys_dict[lk] = "Legacy Key"
            
    blacklist = list(REDIS_CLIENT.smembers(KEY_BLACKLIST))
    whitelist = list(REDIS_CLIENT.smembers(KEY_WHITELIST))
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": {
            "local": local_ips,
            "osint": osint_ips,
            "blacklist": blacklist_count,
            "whitelist": whitelist_count
        },
        "api_keys": api_keys_dict,
        "blacklist": blacklist,
        "whitelist": whitelist
    })

@app.post("/api-key/generate")
async def generate_key(name: str = Form(...), user: str = Depends(get_current_user)):
    if not user: return RedirectResponse(url="/login")
    new_key = str(uuid.uuid4())
    REDIS_CLIENT.hset(KEY_API_KEYS_V2, new_key, name)
    return RedirectResponse(url="/", status_code=303)

@app.post("/api-key/delete")
async def delete_key(key: str = Form(...), user: str = Depends(get_current_user)):
    if not user: return RedirectResponse(url="/login")
    REDIS_CLIENT.hdel(KEY_API_KEYS_V2, key)
    REDIS_CLIENT.srem(KEY_API_KEYS, key) # Also remove from legacy just in case
    return RedirectResponse(url="/", status_code=303)

@app.post("/list/add")
async def add_to_list(ip: str = Form(...), list_type: str = Form(...), user: str = Depends(get_current_user)):
    if not user: return RedirectResponse(url="/login")
    if list_type == "blacklist":
        REDIS_CLIENT.sadd(KEY_BLACKLIST, ip)
    elif list_type == "whitelist":
        REDIS_CLIENT.sadd(KEY_WHITELIST, ip)
    return RedirectResponse(url="/", status_code=303)

@app.post("/list/remove")
async def remove_from_list(ip: str = Form(...), list_type: str = Form(...), user: str = Depends(get_current_user)):
    if not user: return RedirectResponse(url="/login")
    if list_type == "blacklist":
        REDIS_CLIENT.srem(KEY_BLACKLIST, ip)
    elif list_type == "whitelist":
        REDIS_CLIENT.srem(KEY_WHITELIST, ip)
    return RedirectResponse(url="/", status_code=303)
