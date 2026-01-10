# System Architecture & Logic Connections

This document summarizes the relationships and data flow discovered during the investigation of the stagnant IP count on 2026-01-09.

## Component Overview

| Component | Host | Project / Container | Role |
| :--- | :--- | :--- | :--- |
| **Bridge API** | `lemue-io` | `honey-api` / `ti-bridge` | Central hub for threat intelligence. Receives webhooks and serves the WebUI. |
| **Redis** | `lemue-io` | `honey-api-redis-1` | Stores counts and unique IP data for the bridge. |
| **Honeypot Node** | `lemue-sec` | `honey-scan` / `hfish` | Active honeypot server collecting attack data. |
| **Sidecar** | `lemue-sec` | `honey-scan` / `hfish-sidecar-v2` | Monitors honeypot database and syncs data to the bridge. |
| **Honeypot Node 2** | `lemue-sec-2` | `honey-scan` / `hfish` | Second honeypot node. |

## Data Flow (Webhook Sync)

1.  **Detection**: An attack occurs on `lemue-sec`. HFish records the IP in its MariaDB (`ipaddress` table).
2.  **Monitoring**: The Sidecar (`monitor.py`) checks for records where `pushed_to_bridge = 0`.
3.  **Sync**: The Sidecar sends a `POST` request to the `THREAT_BRIDGE_WEBHOOK_URL` with the IP.
4.  **Processing**: The Bridge (`honey-api`) receives the webhook, increments counters in Redis if the IP is new, and marks the IP as local intelligence.
5.  **Acknowledge**: Sidecar updates `pushed_to_bridge = 1` in the local DB.

## Critical Configuration

- **Bridge Webhook URL**: `https://api.sec.lemue.org/webhook`
- **Internal Port**: 8080 (behind Nginx Proxy Manager on `lemue-io`).

## Lessons Learned: Stagnant IP Count Bug

### Root Cause
The `THREAT_BRIDGE_WEBHOOK_URL` in the `.env` files on `lemue-sec` and `lemue-sec-2` was incorrectly configured as:
`THREAT_BRIDGE_WEBHOOK_URL=http://127.0.0.1:4444/webhook`

Since the sidecar itself listens on port 4444 for other tasks, it was sending the data back to its own process instead of the central bridge. No errors were immediately obvious because the port was open and responding (likely with a 404 or 405), but the bridge never received the data.

### Resolution
The URL was corrected to the public API endpoint:
`THREAT_BRIDGE_WEBHOOK_URL=https://api.sec.lemue.org/webhook`

### Debugging Tips
- Check Redis counters directly: `redis-cli get stats:total_local`.
- Compare counter with unique key scan: `redis-cli --scan --pattern 'ti:local:*' | wc -l`.
- Tail bridge logs for `/webhook` hits: `docker compose logs -f ti-bridge | grep webhook`.
- Verify sidecar's perceived target: `docker exec hfish-sidecar-v2 env | grep WEBHOOK`.
