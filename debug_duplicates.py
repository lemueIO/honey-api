import redis
import os

r = redis.from_url("redis://honey-api-redis-1:6379/0", decode_responses=True)

print("Scanning keys...")
local_keys = set()
for k in r.scan_iter("ti:local:*"):
    local_keys.add(k.replace("ti:local:", ""))

osint_keys = set()
for k in r.scan_iter("ti:osint:*"):
    osint_keys.add(k.replace("ti:osint:", ""))

print(f"Total Local IPs: {len(local_keys)}")
print(f"Total OSINT IPs: {len(osint_keys)}")

intersection = local_keys.intersection(osint_keys)
print(f"Intersection (IPs in both): {len(intersection)}")

if intersection:
    print("First 10 duplicates:")
    for ip in list(intersection)[:10]:
        print(f" - {ip}")
