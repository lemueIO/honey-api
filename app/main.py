import os
import uuid
import json
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Optional, List

import socket
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
GLOBAL_BLACKLIST_URL = "https://raw.githubusercontent.com/derlemue/honey-scan/refs/heads/main/sidecar/scan-blacklist.conf"

app = FastAPI(title="Threat Intelligence Bridge", version="2.3.1")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.middleware("http")
async def fix_double_slashes(request: Request, call_next):
    if "//" in request.scope["path"]:
        request.scope["path"] = request.scope["path"].replace("//", "/")
    response = await call_next(request)
    return response

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- Bridge Redirects for Uptime Kuma (Subpath Support) ---
@app.get("/icon.svg")
async def get_icon_bridge():
    return RedirectResponse(url="/cloud/icon.svg")

@app.get("/api/status-page/{path:path}")
async def status_page_bridge(path: str):
    return RedirectResponse(url=f"/cloud/api/status-page/{path}")

@app.get("/upload/{path:path}")
async def upload_bridge(path: str):
    return RedirectResponse(url=f"/cloud/upload/{path}")


# --- Logging Colors ---
C_YELLOW = "\033[93m"
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_logo():
    # Attempt to find logo in current directory or app directory
    logo_path = os.path.join(os.path.dirname(__file__), "hsec_ascii.logo")
    if os.path.exists(logo_path):
        with open(logo_path, "r") as f:
            print(f"{C_YELLOW}{f.read()}{C_RESET}")
    else:
        logger.warning(f"{C_RED}[SYSTEM] Logo file {logo_path} not found{C_RESET}")

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
KEY_STATS_LOCAL = "stats:total_local"
KEY_STATS_OSINT = "stats:total_osint"

# --- Auth Dependency ---
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    return user

# --- Logic ---

def is_ip_in_cidr_list(ip: str, blacklist_members: set) -> bool:
    """
    Check if an IP is in a provided set of members (exact match or CIDR).
    Optimized to avoid repeated Redis calls.
    """
    # 1. Try exact match first
    if ip in blacklist_members:
        return True
    
    # 2. Iterate through all members to check for CIDR ranges
    try:
        target_ip = ipaddress.ip_address(ip)
    except ValueError:
        return False # Invalid IP input

    for member in blacklist_members:
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
    blacklist_members = REDIS_CLIENT.smembers(KEY_BLACKLIST)
    # 1. Whitelist
    if is_ip_in_cidr_list(ip, REDIS_CLIENT.smembers(KEY_WHITELIST)):
        return "clean", ["whitelist"]
    
    # 2. Blacklist
    if is_ip_in_cidr_list(ip, blacklist_members):
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
            logger.info(f"{C_CYAN}[FETCH:OSINT] Starting OSINT feed update cycle...{C_RESET}")
            count = 0 
            
            def process_text_feed(url, timeout=10):
                local_count = 0
                logger.info(f"{C_BLUE}[FETCH:OSINT] Processing feed: {url}{C_RESET}")
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
                    else:
                        logger.warning(f"{C_RED}[FETCH:OSINT] Failed to fetch {url} - Status: {r.status_code}{C_RESET}")
                except Exception as ex:
                    logger.error(f"{C_RED}[FETCH:OSINT] Error fetching {url}: {ex}{C_RESET}")
                return local_count

            # 1. Feodo Tracker
            new_feodo = process_text_feed("https://feodotracker.abuse.ch/downloads/ipblocklist.txt")
            count += new_feodo
            
            # 2. IPSum (Top level)
            new_ipsum = 0
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
                                     new_ipsum += 1
                                 REDIS_CLIENT.setex(key, timedelta(days=90), datetime.now().isoformat())
            except Exception as e:
                logger.error(f"❌ Error fetching IPSum: {e}")
            count += new_ipsum

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

            # 9. ThreatFox (CSV parsing)
            new_threatfox = 0
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
                                   new_threatfox += 1
                               REDIS_CLIENT.setex(key, timedelta(days=90), datetime.now().isoformat())
            except Exception as e:
                logger.error(f"❌ Error fetching ThreatFox: {e}")
            count += new_threatfox

            # Update stats
            REDIS_CLIENT.set("stats:last_osint_count", count)
            REDIS_CLIENT.incrby(KEY_STATS_OSINT, count)
            logger.info(f"{C_GREEN}[FETCH:OSINT] Feeds updated. Added {count} new IPs.{C_RESET}")
        except Exception as e:
            logger.error(f"{C_RED}[FETCH:OSINT] Critical error fetching OSINT: {e}{C_RESET}")
        
        await asyncio.sleep(24 * 3600) # Every 24 hours

# --- Background Task: Global Blacklist Update ---
async def fetch_global_blacklist():
    while True:
        try:
            logger.info(f"{C_CYAN}[FETCH:BLACKLIST] Starting global blacklist update...{C_RESET}")
            r = requests.get(GLOBAL_BLACKLIST_URL, timeout=30)
            if r.status_code == 200:
                # Validate content briefly (check if it looks like a config file)
                if r.text and len(r.text) > 10:
                    with open("scan-blacklist.conf", "w") as f:
                        f.write(r.text)
                    logger.info(f"{C_GREEN}[FETCH:BLACKLIST] scan-blacklist.conf updated from Git.{C_RESET}")
                    
                    # Reload into Redis
                    await load_blacklist_from_file()
                else:
                    logger.warning(f"{C_RED}[FETCH:BLACKLIST] Downloaded content seems empty or too short.{C_RESET}")
            else:
                logger.warning(f"{C_RED}[FETCH:BLACKLIST] Failed to fetch blacklist. Status: {r.status_code}{C_RESET}")
        except Exception as e:
            logger.error(f"{C_RED}[FETCH:BLACKLIST] Error updating global blacklist: {e}{C_RESET}")
        
        await asyncio.sleep(600) # Every 10 minutes

@app.on_event("startup")
async def startup_event():
    log_logo()
    logger.info(f"{C_YELLOW}[SYSTEM] Starting application...{C_RESET}")
    # Initialize optimized counters if they don't exist
    if not REDIS_CLIENT.exists(KEY_STATS_LOCAL):
        logger.info(f"{C_BLUE}[SYSTEM] Initializing stats:total_local counter...{C_RESET}")
        local_count = len(REDIS_CLIENT.keys(f"{KEY_LOCAL}*"))
        REDIS_CLIENT.set(KEY_STATS_LOCAL, local_count)
        
    if not REDIS_CLIENT.exists(KEY_STATS_OSINT):
        logger.info(f"{C_BLUE}[SYSTEM] Initializing stats:total_osint counter...{C_RESET}")
        osint_count = len(REDIS_CLIENT.keys(f"{KEY_OSINT}*"))
        REDIS_CLIENT.set(KEY_STATS_OSINT, osint_count)
    
    asyncio.create_task(fetch_osint_feeds())
    asyncio.create_task(fetch_global_blacklist())
    asyncio.create_task(periodic_db_cleanup())
    asyncio.create_task(periodic_logo_display())

async def periodic_logo_display():
    """Displays the logo every 12 hours."""
    while True:
        await asyncio.sleep(12 * 3600)
        log_logo()

async def load_blacklist_from_file():
    """Reads scan-blacklist.conf and scan-blacklist-custom.conf to populate REDIS_CLIENT's blacklist."""
    logger.info(f"{C_CYAN}[CACHE:WEBHOOK] Initiating blacklist cache reload...{C_RESET}")
    
    # Optional: Clear existing blacklist to ensure we reflect removals
    # Using a temporary set would be atomic, but for now we simply delete and reload
    REDIS_CLIENT.delete(KEY_BLACKLIST)
    
    conf_files = ["scan-blacklist.conf", "scan-blacklist-custom.conf"]
    total_loaded = 0
    
    for conf_path in conf_files:
        if os.path.exists(conf_path):
            try:
                count = 0
                with open(conf_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Strip inline comments
                            if "#" in line:
                                line = line.split("#")[0]
                            line = line.strip()
                            if line:
                                REDIS_CLIENT.sadd(KEY_BLACKLIST, line)
                                count += 1
                total_loaded += count
                logger.info(f"{C_GREEN}[BLACKLIST] Loaded {count} IPs from {conf_path}{C_RESET}")
            except Exception as e:
                logger.error(f"{C_RED}[BLACKLIST] Error loading {conf_path}: {e}{C_RESET}")
        else:
            if conf_path == "scan-blacklist.conf":
                logger.warning(f"{C_YELLOW}[BLACKLIST] {conf_path} not found.{C_RESET}")
            else:
                logger.info(f"{C_BLUE}[BLACKLIST] {conf_path} not found (optional) - Skipping.{C_RESET}")

    final_count = REDIS_CLIENT.scard(KEY_BLACKLIST)
    logger.info(f"{C_GREEN}[CACHE:WEBHOOK] Cache reload complete. Total active rules: {final_count} (Loaded: {total_loaded}){C_RESET}")
    
    # Recalculate IP stats
    await calculate_and_cache_blacklist_stats()

async def calculate_and_cache_blacklist_stats():
    """Calculates the total number of IPs in the blacklist (expanding CIDRs) and caches it."""
    try:
        blacklist_members = REDIS_CLIENT.smembers(KEY_BLACKLIST)
        total_ips = 0
        for member in blacklist_members:
            try:
                if "/" in member:
                    total_ips += ipaddress.ip_network(member, strict=False).num_addresses
                else:
                    total_ips += 1
            except ValueError:
                continue
        
        REDIS_CLIENT.set("stats:blacklist_ip_count", total_ips)
        logger.info(f"{C_GREEN}[STATS] blacklist_ip_count updated: {total_ips} IPs.{C_RESET}")
    except Exception as e:
        logger.error(f"{C_RED}[STATS] Error calculating blacklist IPs: {e}{C_RESET}")

def purge_test_ip():
    """Specifically removes the test IP 1.2.3.4 from the database."""
    test_ip = "1.2.3.4"
    logger.info(f"{C_CYAN}[CLEAN:TEST_IP] Purging test IP: {test_ip}{C_RESET}")
    
    # Remove from local
    REDIS_CLIENT.delete(f"{KEY_LOCAL}{test_ip}")
    
    # Remove from OSINT
    REDIS_CLIENT.delete(f"{KEY_OSINT}{test_ip}")

async def periodic_db_cleanup():
    """Runs database cleanup tasks periodically."""
    while True:
        try:
            logger.info(f"{C_CYAN}[CLEAN:DB] Starting periodic database cleanup...{C_RESET}")
            
            # 1. Reload blacklist from file
            await load_blacklist_from_file()
            
            # 2. Purge test IP
            purge_test_ip()
            
            # 3. Fetch blacklist once for optimization
            blacklist_members = REDIS_CLIENT.smembers(KEY_BLACKLIST)
            if not blacklist_members:
                logger.info(f"{C_YELLOW}[CLEAN:DB] Blacklist is empty, skipping IP scan.{C_RESET}")
            else:
                # 4. Purge blacklisted IPs from DB
                removed_local = 0
                removed_osint = 0
                total_scanned = 0

                # Cleanup ti:local:*
                cursor = 0
                while True:
                    cursor, keys = REDIS_CLIENT.scan(cursor=cursor, match=f"{KEY_LOCAL}*", count=1000)
                    total_scanned += len(keys)
                    for key in keys:
                        ip = key.replace(KEY_LOCAL, "")
                        if is_ip_in_cidr_list(ip, blacklist_members):
                            logger.info(f"{C_RED}[CLEAN:DB] Removing blacklisted local IP: {ip}{C_RESET}")
                            REDIS_CLIENT.delete(key)
                            REDIS_CLIENT.decr(KEY_STATS_LOCAL)
                            removed_local += 1
                    if str(cursor) == '0':
                        break
                
                # Cleanup ti:osint:*
                cursor = 0
                while True:
                    cursor, keys = REDIS_CLIENT.scan(cursor=cursor, match=f"{KEY_OSINT}*", count=1000)
                    total_scanned += len(keys)
                    for key in keys:
                        ip = key.replace(KEY_OSINT, "")
                        if is_ip_in_cidr_list(ip, blacklist_members):
                            logger.info(f"{C_RED}[CLEAN:DB] Removing blacklisted OSINT IP: {ip}{C_RESET}")
                            REDIS_CLIENT.delete(key)
                            REDIS_CLIENT.decr(KEY_STATS_OSINT)
                            removed_osint += 1
                    if str(cursor) == '0':
                        break

                logger.info(f"{C_GREEN}[CLEAN:DB] Cleanup finished. Scanned {total_scanned} keys, removed {removed_local} local, {removed_osint} osint IPs.{C_RESET}")
        except Exception as e:
            logger.error(f"{C_RED}[CLEAN:DB] Error during periodic cleanup: {e}{C_RESET}")
        
        await asyncio.sleep(3600) # Every 1 hour

# --- API Routes ---

@app.get("/v3/scene/ip_reputation")
async def ip_reputation(resource: str, apikey: str):
    # Check both old and new keys for compatibility
    if not REDIS_CLIENT.sismember(KEY_API_KEYS, apikey) and not REDIS_CLIENT.hexists(KEY_API_KEYS_V2, apikey):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    severity, judgments = get_ip_reputation(resource)
    
    # Logging with colors
    if severity == "high":
        logger.info(f"{C_RED}[REPUTATION] High Risk IP Check: {resource} - {judgments}{C_RESET}")
    elif severity == "medium":
        logger.info(f"{C_YELLOW}[REPUTATION] Medium Risk IP Check: {resource} - {judgments}{C_RESET}")
    elif "whitelist" in judgments:
        logger.info(f"{C_GREEN}[REPUTATION] Whitelisted IP Check: {resource}{C_RESET}")
    else:
        logger.info(f"{C_BLUE}[REPUTATION] Clean IP Check: {resource}{C_RESET}")
        
    return format_threatbook_v3(resource, severity, judgments)

@app.post("/webhook")
async def hfish_webhook(data: HFishWebhook):
    # 1. Immediate filtering for Scan-Blacklist
    blacklist_members = REDIS_CLIENT.smembers(KEY_BLACKLIST)
    if is_ip_in_cidr_list(data.attack_ip, blacklist_members):
        logger.info(f"{C_RED}[WEBHOOK] Discarding attack from Scan-Blacklisted IP: {data.attack_ip}{C_RESET}")
        return {"status": "filtered", "reason": "scan-blacklist"}

    logger.info(f"{C_BLUE}[WEBHOOK] Received attack from: {data.attack_ip}{C_RESET}")
    # Store local data for 365 days
    ip_key = f"{KEY_LOCAL}{data.attack_ip}"
    is_new = not REDIS_CLIENT.exists(ip_key)
    
    if is_new:
         # Increment daily/session counter for "Last Cloud IPs"
         REDIS_CLIENT.incr("stats:cloud_new_24h")
         # Increement total local counter
         REDIS_CLIENT.incr(KEY_STATS_LOCAL)
         # Set expire only if key is new (e.g. 24h window roughly)
         if REDIS_CLIENT.ttl("stats:cloud_new_24h") == -1:
             REDIS_CLIENT.expire("stats:cloud_new_24h", 86400)
    
    REDIS_CLIENT.setex(ip_key, timedelta(days=365), datetime.now().isoformat())
    
    if is_new:
        logger.info(f"{C_GREEN}[WEBHOOK] New IP added: {data.attack_ip}{C_RESET}")
    else:
        logger.info(f"{C_CYAN}[WEBHOOK] Updated existing IP: {data.attack_ip}{C_RESET}")
    
    return {"status": "ok"}

@app.post("/api/ban")
async def manual_ban(ip: str = Form(...), user: str = Depends(get_current_user)):
    if not user: return RedirectResponse(url="/login")
    
    logger.info(f"{C_RED}[MANUAL BAN] Manually banning IP: {ip} for processing/reporting{C_RESET}")
    
    ip_key = f"{KEY_LOCAL}{ip}"
    is_new = not REDIS_CLIENT.exists(ip_key)
    
    if is_new:
         REDIS_CLIENT.incr("stats:cloud_new_24h")
         REDIS_CLIENT.incr(KEY_STATS_LOCAL)
         if REDIS_CLIENT.ttl("stats:cloud_new_24h") == -1:
             REDIS_CLIENT.expire("stats:cloud_new_24h", 86400)
    
    REDIS_CLIENT.setex(ip_key, timedelta(days=365), datetime.now().isoformat())
    return RedirectResponse(url="/", status_code=303)

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
        
    # Stats (Optimized)
    local_ips = int(REDIS_CLIENT.get(KEY_STATS_LOCAL) or 0)
    osint_ips = int(REDIS_CLIENT.get(KEY_STATS_OSINT) or 0)
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
    
    blacklist_ips = int(REDIS_CLIENT.get("stats:blacklist_ip_count") or 0)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "stats": {
            "local": local_ips,
            "osint": osint_ips,
            "blacklist": blacklist_count,
            "blacklist_ips": blacklist_ips,
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
        
    local_ips = int(REDIS_CLIENT.get(KEY_STATS_LOCAL) or 0)
    osint_ips = int(REDIS_CLIENT.get(KEY_STATS_OSINT) or 0)
    blacklist_count = REDIS_CLIENT.scard(KEY_BLACKLIST)
    whitelist_count = REDIS_CLIENT.scard(KEY_WHITELIST)
    
    blacklist_ips = int(REDIS_CLIENT.get("stats:blacklist_ip_count") or 0)

    # Check External API Status
    api_up = False
    
    # 1. Socket Check - Public (Port 443)
    # This proves api.sec.lemue.org is reachable from 'external' perspective
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        # Using the resolved IP if possible, or domain
        result = s.connect_ex(("api.sec.lemue.org", 443))
        if result == 0:
            api_up = True
        s.close()
    except Exception:
        pass
        
    # 2. Socket Check - Localhost (Port 8080) 
    # Fallback to confirm the app process is listening locally
    if not api_up:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", 8080))
            if result == 0:
                api_up = True
            s.close()
        except Exception:
            pass
        
    last_osint_count = REDIS_CLIENT.get("stats:last_osint_count")
    if last_osint_count is None: last_osint_count = 0
    
    cloud_new_24h = REDIS_CLIENT.get("stats:cloud_new_24h")
    if cloud_new_24h is None: cloud_new_24h = 0

    return {
        "local": local_ips,
        "osint": osint_ips,
        "blacklist": blacklist_count,
        "blacklist_ips": blacklist_ips,
        "whitelist": whitelist_count,
        "api_up": api_up,
        "last_osint_count": int(last_osint_count),
        "last_cloud_count": int(cloud_new_24h)
    }

# --- Public Status Routes ---

@app.get("/status", response_class=HTMLResponse)
async def status_page(request: Request):
    # Stats (Optimized)
    local_ips = int(REDIS_CLIENT.get(KEY_STATS_LOCAL) or 0)
    osint_ips = int(REDIS_CLIENT.get(KEY_STATS_OSINT) or 0)
    blacklist_count = REDIS_CLIENT.scard(KEY_BLACKLIST)
    whitelist_count = REDIS_CLIENT.scard(KEY_WHITELIST)
    
    blacklist_ips = int(REDIS_CLIENT.get("stats:blacklist_ip_count") or 0)

    return templates.TemplateResponse("status.html", {
        "request": request,
        "stats": {
            "local": local_ips,
            "osint": osint_ips,
            "blacklist": blacklist_count,
            "blacklist_ips": blacklist_ips,
            "whitelist": whitelist_count
        }
    })

@app.get("/api/public/stats")
async def get_public_stats():
    local_ips = int(REDIS_CLIENT.get(KEY_STATS_LOCAL) or 0)
    osint_ips = int(REDIS_CLIENT.get(KEY_STATS_OSINT) or 0)
    blacklist_count = REDIS_CLIENT.scard(KEY_BLACKLIST)
    whitelist_count = REDIS_CLIENT.scard(KEY_WHITELIST)
    
    blacklist_ips = int(REDIS_CLIENT.get("stats:blacklist_ip_count") or 0)

    # Check External API Status (Publicly exposed on status page)
    api_up = False
    
    # 1. Socket Check - Public (Port 443)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(("api.sec.lemue.org", 443))
        if result == 0:
            api_up = True
        s.close()
    except Exception:
        pass
        
    # 2. Socket Check - Localhost (Port 8080) - Fallback
    if not api_up:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", 8080))
            if result == 0:
                api_up = True
            s.close()
        except Exception:
            pass
        
    last_osint_count = REDIS_CLIENT.get("stats:last_osint_count")
    if last_osint_count is None: last_osint_count = 0
    
    cloud_new_24h = REDIS_CLIENT.get("stats:cloud_new_24h")
    if cloud_new_24h is None: cloud_new_24h = 0

    return {
        "local": local_ips,
        "osint": osint_ips,
        "blacklist": blacklist_count,
        "blacklist_ips": blacklist_ips,
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
