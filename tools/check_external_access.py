
import requests
import sys
import time

URL = "https://api.sec.lemue.org/v3/scene/ip_reputation"
PARAMS = {
    "apikey": "test-key-for-check", # Any key will trigger auth, but we just want to check reachability
    "resource": "1.1.1.1"
}

def check_access():
    print(f"Checking access to {URL}...")
    try:
        start_time = time.time()
        response = requests.get(URL, params=PARAMS, timeout=5)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"Status Code: {response.status_code}")
        print(f"Time: {elapsed:.2f}ms")
        
        if response.status_code == 200:
            print("✅ SUCCESS: API is reachable and responding correctly.")
        elif response.status_code == 403:
             print("✅ SUCCESS: API is reachable (Access Denied as expected with test key).")
        else:
             print(f"⚠️ WARNING: API is reachable but returned status {response.status_code}")
             
    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Could not connect to server. (Connection Refused or Timeout)")
    except requests.exceptions.Timeout:
        print("❌ FAIL: Request timed out.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    check_access()
