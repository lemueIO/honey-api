<div align="center">
  <img src="app/static/logo_bear.png" width="150" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>The Operational Brain of the Honey-Ecosystem</strong></p>

  [![Version](https://img.shields.io/badge/version-v2.4.1-7B2CBF?style=for-the-badge&logo=git)](https://github.com/lemueIO/honey-api/releases/tag/v2.4.1)
  [![Python](https://img.shields.io/badge/python-3.9%2B-5A189A?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Docker](https://img.shields.io/badge/docker-enabled-3C096C?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![Status](https://img.shields.io/badge/status-active-240046?style=for-the-badge&logo=activity&logoColor=white)](https://github.com/lemueIO/honey-api)

  <br>

  [![Stars](https://img.shields.io/github/stars/lemueIO/honey-api?style=for-the-badge&color=7B2CBF&labelColor=240046)](https://github.com/lemueIO/honey-api/stargazers)
  [![Forks](https://img.shields.io/github/forks/lemueIO/honey-api?style=for-the-badge&color=5A189A&labelColor=240046)](https://github.com/lemueIO/honey-api/network/members)
  [![Watchers](https://img.shields.io/github/watchers/lemueIO/honey-api?style=for-the-badge&color=3C096C&labelColor=240046)](https://github.com/lemueIO/honey-api/watchers)
  [![Contributors](https://img.shields.io/github/contributors/lemueIO/honey-api?style=for-the-badge&color=240046&labelColor=10002b)](https://github.com/lemueIO/honey-api/graphs/contributors)

  <br>

  [![Repo Size](https://img.shields.io/github/repo-size/lemueIO/honey-api?style=for-the-badge&color=240046&labelColor=10002b)](https://github.com/lemueIO/honey-api)
  [![License](https://img.shields.io/github/license/lemueIO/honey-api?style=for-the-badge&color=240046&labelColor=10002b)](LICENSE)
  [![Last Commit](https://img.shields.io/github/last-commit/lemueIO/honey-api?style=for-the-badge&color=240046&labelColor=10002b)](https://github.com/lemueIO/honey-api/commits/main)
  [![Open Issues](https://img.shields.io/github/issues/lemueIO/honey-api?style=for-the-badge&color=240046&labelColor=10002b)](https://github.com/lemueIO/honey-api/issues)

  <br>
  <br>

  **[ 🇬🇧 English ](README.md)** • **[ 🇩🇪 Deutsch ](README_DE.md)** • **[ 🇩🇪 Einfache Sprache ](README_DE2.md)** • **[ 🇺🇦 Українська ](README_UA.md)**
</div>

---

> [!NOTE]
> *Honey Cloud Intelligence (honey-api) is the centralized backend of the **Honey-Ecosystem**. It aggregates real-time attack data from distributed sensors (`honey-scan`), fuses it with global OSINT feeds, and exposes a high-performance Threat Intelligence API.*

<div align="center">
  <br>
  <a href="https://api.sec.lemue.org/status">
    <img src="assets/status_preview_v220.png" width="90%" alt="Dashboard Preview" style="border-radius: 10px; box-shadow: 0 0 20px rgba(123, 44, 191, 0.3);">
  </a>
  <br>
  <br>
  <em>Honey Cloud Intelligence Status Dashboard - <a href="https://api.sec.lemue.org/status"><strong>Live View</strong></a></em>
  <br>
</div>

---

## 🏗️ System Architecture

The **Honey-Ecosystem** consists of two primary components:
1.  **`honey-scan` (The Sensor)**: Runs on edge nodes (honeypots), detects attacks, and pushes raw logs to the API.
2.  **`honey-api` (The Brain)**: This repository. It receives data, manages whitelists/blacklists, and serves reputation queries.

```mermaid
graph LR
    subgraph Edge Nodes
        A[honey-scan / HFish] -- POST /webhook --> B
        A2[honey-scan / HFish] -- POST /webhook --> B
    end

    subgraph Core Cloud
        B(Honey-API)
        B -- Store --> C[(Redis Memory)]
        D[OSINT Feeds] -- Fetch Loop --> B
    end

    subgraph Security Tools
        E[Firewalls / SOAR] -- GET /v3/reputation --> B
    end
    
    style B fill:#7B2CBF,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#DC382D,stroke:#333,stroke-width:2px,color:#fff
```

## 🚀 Features

| Feature category | Description |
| :--- | :--- |
| **Central Aggregation** | Acts as the **hub** for all `honey-scan` nodes, creating a unified intelligence database. |
| **High Performance** | Powered by **FastAPI** and **Redis** for sub-millisecond response times. |
| **API Emulation** | Fully compatible with the **ThreatBook v3 API** standard for easy integration. |
| **Intelligent Filtering** | Supports **exact IP matches** and **CIDR ranges**. Automatically purges old entries. |
| **Advanced Logging** | Structural logging with color-coded ANSI tags (`[SYSTEM]`, `[CLEAN:DB]`) for ops visibility. |
| **Robust Monitoring** | Resilient **socket-level checks** and `/health` endpoints for orchestration. |

## 📡 API & Data Contracts

### 1. Ingestion Interface (Sensor -> API)
The bridge accepts data from `honey-scan` or HFish nodes via a webhook.

*   **Endpoint**: `POST /webhook`
*   **Auth**: IP-based whitelist (optional configuration via upstream proxy recommended)
*   **ContentType**: `application/json`

**Expected Payload:**
```json
{
  "attack_ip": "1.2.3.4"
}
```

### 2. Reputation Interface (Tools -> API)
Security tools query this endpoint to check if an IP is malicious. It formats data to match the ThreatBook v3 standard.

*   **Endpoint**: `GET /v3/scene/ip_reputation`
*   **Auth**: Required (`apikey` query parameter)

**Request:**
`GET /v3/scene/ip_reputation?apikey=YOUR_KEY&resource=192.168.1.5`

**Response:**
```json
{
    "code": 0,
    "data": {
        "192.168.1.5": {
            "severity": "high",
            "judgments": ["hfish honeypot"],
            "update_time": "2026-01-13 09:00:00"
        }
    },
    "message": "success"
}
```

## 🔗 Integration Setup

To connect a **`honey-scan`** node (or any HFish instance) to this API:

1.  **Deploy Honey-API**: Ensure this container is running and accessible (e.g., `http://10.0.0.5:8080`).
2.  **Configure Sensor**: In your `honey-scan` or HFish configuration, set the **Webhook URL**:
    ```bash
    # Example HFish / honey-scan configuration
    WEBHOOK_URL="http://10.0.0.5:8080/api/v1/webhook"
    ```
    *(Note: Ensure network connectivity between the sensor and the API container/host).*

## 📦 Installation

<details>
<summary><strong>Click to view Installation Steps</strong></summary>

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/lemueIO/honey-api.git
    cd honey-api
    ```

2.  **Start services with Docker Compose:**
    ```bash
    docker compose up -d --build
    ```

3.  **Access the Dashboard:**
    -   URL: `http://localhost:8080/login`
    -   Default Admin Password: `admin` (Change immediately in `docker-compose.yml`!)

</details>

## 🛠️ Technology Stack

<div align="center">

| Component | Technology |
| :--- | :--- |
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi) (Python 3.9+) |
| **Database** | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white) (Key-Value Storage) |
| **Frontend** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=flat&logo=bootstrap&logoColor=white) (Jinja2 Templates) |
| **Deployment** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) & Docker Compose |

</div>

---

<div align="center">
  <p>Maintained by the <strong>Honey-Scan Community</strong> and <a href="https://github.com/lemueIO"><strong>lemueIO</strong></a> ❤️</p>
</div>
