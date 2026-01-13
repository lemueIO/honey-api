<div align="center">
  <img src="app/static/logo_bear.png" width="150" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>High-Performance Threat Intelligence Bridge & Aggregator</strong></p>

  [![Version](https://img.shields.io/badge/version-v2.4.1-7B2CBF?style=for-the-badge&logo=git)](https://github.com/lemueIO/honey-api/releases/tag/v2.4.1)
  [![Python](https://img.shields.io/badge/python-3.9%2B-5A189A?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Docker](https://img.shields.io/badge/docker-enabled-3C096C?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![Status](https://img.shields.io/badge/status-active-240046?style=for-the-badge&logo=activity&logoColor=white)](https://github.com/lemueIO/honey-api)

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
> *Honey Cloud Intelligence is a high-performance Threat Intelligence Bridge designed to aggregate, manage, and serve threat data from local HFish honeypots and global OSINT sources. It emulates the ThreatBook v3 API, allowing for seamless integration into existing security tools without hitting external rate limits.*

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

## 🚀 Features

| Feature category | Description |
| :--- | :--- |
| **Threat Data Aggregation** | Combines real-time data from local **honeypots** (via HFish) with **10+ external OSINT feeds**. |
| **High Performance** | Powered by **FastAPI** and **Redis** for sub-millisecond response times. |
| **API Emulation** | Fully compatible with the **ThreatBook v3 API** standard. |
| **Intelligent Filtering** | Supports **exact IP matches** and **CIDR ranges** (e.g., `10.0.0.0/24`). Optimized database pruning via pre-fetched blacklist scanning. |
| **Advanced Logging** | Structural logging with color-coded ANSI tags (`[SYSTEM]`, `[CLEAN:DB]`) and visual feedback. |
| **Robust Monitoring** | Resilient **socket-level reachability verification**, external Check-Host.net links, and a dedicated `/health` endpoint. |
| **Modern UI** | Sleek **dark-mode dashboard** with real-time statistics, API key management, and list control. |
| **Status Page** | A simplified, **public status dashboard** available without login. |
| **International** | Full documentation in **English**, **German** (Standard & Simple), and **Ukrainian**. |

## 🔑 Access & API Keys

> [!IMPORTANT]
> **API Keys are not public.**
> Access to the Honey Cloud Intelligence API is strictly controlled. API keys are only granted after direct contact with the administrator. Please contact the project maintainer to request an API key.

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

## 💻 Usage

### 🔄 Synchronizing Data
The bridge accepts data from HFish nodes via a webhook endpoint. Ensure your HFish nodes are configured to send data to:
`http://<your-server-ip>:8080/api/v1/webhook`

### 🕵️ Querying Reputation
Query the API emulating the ThreatBook format:
```bash
curl "http://localhost:8080/v3/scene/ip_reputation?apikey=YOUR_API_KEY&resource=1.2.3.4"
```

## 📖 API Documentation

### 🧠 1. Reputation Check (ThreatBook v3 Compatible)
Query IP reputation intelligence.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/v3/scene/ip_reputation` | Checks the reputation of a specific IP resource. |

**Parameters:**
- `apikey`: Your personal API key.
- `resource`: The IP address to check.

<details>
<summary><strong>View Response Example</strong></summary>

```json
{
    "code": 0,
    "data": {
        "1.2.3.4": {
            "severity": "high",
            "judgments": ["permanent blacklist"],
            "update_time": "2024-01-01 12:00:00"
        }
    },
    "message": "success"
}
```
</details>

### 🎣 2. Webhook (HFish Compatible)
Receive attack logs from HFish nodes.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/webhook` | Ingests attack logs from HFish instances. |

### 💓 3. Health Check
Monitor system status.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Returns system operational status. |

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
