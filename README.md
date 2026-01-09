# Honey Cloud Intelligence

<div align="center">
  <img src="app/static/logo_bear.png" width="120" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>High-Performance Threat Intelligence Bridge & Aggregator</strong></p>

  [![Version](https://img.shields.io/badge/version-v2.0.0-blue?style=for-the-badge&logo=none)](https://github.com/lemueIO/honey-api/releases/tag/v2.0.0)
  [![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge&logo=none)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Docker](https://img.shields.io/badge/docker-enabled-blue?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![Status](https://img.shields.io/badge/status-active-success?style=for-the-badge&logo=activity&logoColor=white)](https://github.com/lemueIO/honey-api)
</div>

<div align="center">
  <h4>
    <a href="README.md">🇬🇧 English</a> | 
    <a href="README_DE.md">🇩🇪 Deutsch</a> | 
    <a href="README_DE2.md">🇩🇪 Einfache Sprache</a> |
    <a href="README_UA.md">🇺🇦 Українська</a>
  </h4>
</div>

Honey Cloud Intelligence is a high-performance Threat Intelligence Bridge designed to aggregate, manage, and serve threat data from local HFish honeypots and global OSINT sources. It emulates the **ThreatBook v3 API**, allowing for seamless integration into existing security tools without hitting external rate limits.

<div align="center">
  <img src="assets/dashboard_preview.png" width="80%" alt="Dashboard Preview">
  <br>
  <em>Honey Cloud Intelligence Dashboard with Dark Mode and IP Statistics</em>
</div>

## Features

-   **Threat Data Aggregation**: Combines real-time data from local honeypots (via HFish) with 10+ external OSINT feeds.
-   **High Performance**: Powered by FastAPI and Redis for sub-millisecond response times.
-   **API Emulation**: Fully compatible with the **ThreatBook v3 API** standard.
-   **Intelligent Filtering**:
    -   **Whitelist/Blacklist**: Supports exact IP matches and CIDR ranges (e.g., `10.0.0.0/24`).
    -   **Prioritization**: Custom logic to prioritize local threats and manual lists over OSINT data.
-   **Robust Monitoring**:
    -   **Resilient Check**: Built-in socket-level reachability verification (ports 443, 8080) that avoids HTTP deadlocks.
    -   **External verification**: Direct links to Check-Host.net and a portable check script for global connectivity tests.
    -   **Health Endpoint**: Dedicated `/health` route for uptime monitoring.
-   **Modern UI**: Sleek dark-mode dashboard with real-time statistics, API key management, and list control.
-   **Multi-language Support**: Full documentation available in English, German (Standard & Simple), and Ukrainian.
-   **Containerized**: Built with Docker and Docker Compose for easy deployment.

## Access & API Keys

> [!IMPORTANT]
> **API Keys are not public.**
> Access to the Honey Cloud Intelligence API is strictly controlled. API keys are only granted after direct contact with the administrator. Please contact the project maintainer to request an API key.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/lemueIO/honey-api.git
    cd honey-api
    ```

2.  Start services with Docker Compose:
    ```bash
    docker compose up -d --build
    ```

3.  Access the Dashboard:
    -   URL: `http://localhost:8080/login`
    -   Default Admin Password: `admin` (Change immediately in `docker-compose.yml`!)

## Usage

### Synchronizing Data
The bridge accepts data from HFish nodes via a webhook endpoint. Ensure your HFish nodes are configured to send data to:
`http://<your-server-ip>:8080/api/v1/webhook`

### Querying Reputation
Query the API emulating the ThreatBook format:
```bash
curl "http://localhost:8080/v3/scene/ip_reputation?apikey=YOUR_API_KEY&resource=1.2.3.4"
```

## API Documentation

### 1. Reputation Check (ThreatBook v3 Compatible)
Query IP reputation intelligence.

- **Endpoint**: `/v3/scene/ip_reputation`
- **Method**: `GET`
- **Parameters**:
  - `apikey`: Your personal API key.
  - `resource`: The IP address to check.
- **Example**:
  ```bash
  curl "http://<server-ip>:8080/v3/scene/ip_reputation?apikey=YOUR_KEY&resource=1.2.3.4"
  ```
- **Response**:
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

### 2. Webhook (HFish Compatible)
Receive attack logs from HFish nodes.

- **Endpoint**: `/webhook`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
      "attack_ip": "1.2.3.4"
  }
  ```

### 3. Health Check
Monitor system status.

- **Endpoint**: `/health`
- **Method**: `GET`
- **Response**: `{"status": "ok"}`

## Technology Stack

-   **Backend**: FastAPI (Python 3.9+)
-   **Database**: Redis (Key-Value Storage)
-   **Frontend**: Jinja2 Templates, Bootstrap 5 (Custom Dark Theme)
-   **Deployment**: Docker & Docker Compose

---

Maintained by the Honey-Scan Community and [lemueIO](https://github.com/lemueIO) ❤️
