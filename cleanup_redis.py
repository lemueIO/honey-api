import redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CLIENT = redis.from_url(REDIS_URL, decode_responses=True)

# Keys from main.py
KEY_WHITELIST = "ti:whitelist"
KEY_BLACKLIST = "ti:blacklist"
KEY_LOCAL_PREFIX = "ti:local:"
KEY_OSINT_PREFIX = "ti:osint:"

target_ip = "::1"

def cleanup():
    print(f"Cleaning up {target_ip}...")
    
    # 1. Remove from blacklist
    removed_blacklist = REDIS_CLIENT.srem(KEY_BLACKLIST, target_ip)
    print(f"Removed from {KEY_BLACKLIST}: {removed_blacklist}")
    
    # 2. Add to whitelist
    added_whitelist = REDIS_CLIENT.sadd(KEY_WHITELIST, target_ip)
    print(f"Added to {KEY_WHITELIST}: {added_whitelist}")
    
    # 3. Remove local entry
    local_key = f"{KEY_LOCAL_PREFIX}{target_ip}"
    removed_local = REDIS_CLIENT.delete(local_key)
    print(f"Removed local entry {local_key}: {removed_local}")
    
    # 4. Remove OSINT entry
    osint_key = f"{KEY_OSINT_PREFIX}{target_ip}"
    removed_osint = REDIS_CLIENT.delete(osint_key)
    print(f"Removed OSINT entry {osint_key}: {removed_osint}")

if __name__ == "__main__":
    try:
        cleanup()
    except Exception as e:
        print(f"Error: {e}")
