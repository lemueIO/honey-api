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
            count = 0 
            
            def process_text_feed(url, timeout=10):
                local_count = 0
                try:
                    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Honey-API-Bridge/1.0"})
                    if r.status_code == 200:
                        for line in r.text.splitlines():
                            line = line.strip()
                            if line and not line.startswith("#") and not line.startswith("//"):
                                # Basic IP validation/cleaning
                                ip = line.split()[0].strip() # Handle potential comments
                                # Basic check if it looks like an IP
                                if len(ip) > 6 and "." in ip and not "/" in ip:
                                    key = f"{KEY_OSINT}{ip}"
                                    if not REDIS_CLIENT.exists(key):
                                        local_count += 1
                                    REDIS_CLIENT.setex(key, timedelta(days=90), datetime.now().isoformat())
                except Exception as ex:
                    logger.error(f"Error fetching {url}: {ex}")
                return local_count

            # 1. Feodo Tracker
            count += process_text_feed("https://feodotracker.abuse.ch/downloads/ipblocklist.txt")
            
            # 2. IPSum (Top level)
            try:
                r = requests.get("https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt", timeout=10)
                if r.status_code == 200:
                    for line in r.text.splitlines():
                        if line and not line.startswith("#"):
                            parts = line.split()
                            if len(parts) > 1 and int(parts[1]) > 3:
                                 ip = parts[0]
                                 key = f"{KEY_OSINT}{ip}"
                                 if not REDIS_CLIENT.exists(key):
                                     count += 1
                                 REDIS_CLIENT.setex(key, timedelta(days=90), datetime.now().isoformat())
            except Exception as e:
                logger.error(f"Error fetching IPSum: {e}")

            # 3. CINS Army
            count += process_text_feed("http://cinsscore.com/list/ci-badguys.txt")

            # 4. GreenSnow
            count += process_text_feed("https://blocklist.greensnow.co/greensnow.txt")

            # 5. Blocklist.de
            count += process_text_feed("https://lists.blocklist.de/lists/all.txt")

            # 6. Emerging Threats
            count += process_text_feed("https://rules.emergingthreats.net/blockrules/compromised-ips.txt")

            # 7. BinaryDefense
            count += process_text_feed("https://www.binarydefense.com/banlist.txt")

            # 8. DShield
            count += process_text_feed("https://feeds.dshield.org/block.txt")

            # 9. DigitalSide
            count += process_text_feed("https://osint.digitalside.it/Threat-Intel/lists/latestips.txt")

            # 10. ThreatFox (CSV parsing)
            try:
                r = requests.get("https://threatfox.abuse.ch/export/csv/ip-port/recent/", timeout=15)
                if r.status_code == 200:
                    for line in r.text.splitlines():
                        if line and not line.startswith("#") and "ip:port" in line:
                           parts = line.split(",")
                           if len(parts) > 2:
                               ioc_value = parts[2].replace('"', '')
                               if ":" in ioc_value: # strip port
                                   ioc_value = ioc_value.split(":")[0]
                               
                               key = f"{KEY_OSINT}{ioc_value}"
                               if not REDIS_CLIENT.exists(key):
                                   count += 1
                               REDIS_CLIENT.setex(key, timedelta(days=90), datetime.now().isoformat())
            except Exception as e:
                logger.error(f"Error fetching ThreatFox: {e}")

            # Store last update stats
            REDIS_CLIENT.set("stats:last_osint_count", count)
            logger.info(f"OSINT feeds updated. Added {count} new IPs.")
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
    ip_key = f"{KEY_LOCAL}{data.attack_ip}"
    is_new = not REDIS_CLIENT.exists(ip_key)
    
    if is_new:
         # Increment daily/session counter for "Last Cloud IPs"
         REDIS_CLIENT.incr("stats:cloud_new_24h")
         # Set expire only if key is new (e.g. 24h window roughly)
         if REDIS_CLIENT.ttl("stats:cloud_new_24h") == -1:
             REDIS_CLIENT.expire("stats:cloud_new_24h", 86400)
    
    REDIS_CLIENT.setex(ip_key, timedelta(days=365), datetime.now().isoformat())
    
    if is_new:
        logger.info(f"🆕 New IP added: {data.attack_ip}")
    else:
        logger.info(f"🔄 Updated existing IP: {data.attack_ip}")
    
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

@app.get("/api/stats")
async def get_stats(user: str = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    local_ips = len(REDIS_CLIENT.keys(f"{KEY_LOCAL}*"))
    osint_ips = len(REDIS_CLIENT.keys(f"{KEY_OSINT}*"))
    blacklist_count = REDIS_CLIENT.scard(KEY_BLACKLIST)
    whitelist_count = REDIS_CLIENT.scard(KEY_WHITELIST)
    
    # Check External API Status
    api_up = False
    try:
        # Try HTTPS first with no verify to avoid cert issues in container
        requests.get("https://api.sec.lemue.org/v3/scene/ip_reputation?apikey=test&resource=1.1.1.1", timeout=3, headers={"User-Agent": "Honey-API-Bridge/1.0"}, verify=False)
        api_up = True
    except Exception as e:
        logger.warning(f"HTTPS API Check failed: {e}")
        # Fallback to HTTP
        try:
             requests.get("http://localhost:8080/v3/scene/ip_reputation?apikey=test&resource=1.1.1.1", timeout=3, headers={"User-Agent": "Honey-API-Bridge/1.0"})
             api_up = True
        except Exception as e2:
             logger.error(f"API Check failed (HTTPS & HTTP): {e} | {e2}")
             api_up = False
        
    last_osint_count = REDIS_CLIENT.get("stats:last_osint_count")
    if last_osint_count is None: last_osint_count = 0
    
    cloud_new_24h = REDIS_CLIENT.get("stats:cloud_new_24h")
    if cloud_new_24h is None: cloud_new_24h = 0

    return {
        "local": local_ips,
        "osint": osint_ips,
        "blacklist": blacklist_count,
        "whitelist": whitelist_count,
        "api_up": api_up,
        "last_osint_count": int(last_osint_count),
        "last_cloud_count": int(cloud_new_24h)
    }

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
