# Honey Cloud Intelligence

<div align="center">
  <img src="app/static/logo_bear.png" width="120" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>High-Performance Threat Intelligence Bridge & Aggregator</strong></p>

  [![Version](https://img.shields.io/badge/version-v1.2.0-blue?style=for-the-badge&logo=none)](https://github.com/lemueIO/honey-api/releases/tag/v1.2.0)
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

Honey Cloud Intelligence is a high-performance Threat Intelligence Bridge designed to aggregate, manage, and serve threat data from local HFish honeypots and global OSINT sources. It emulates the **ThreatBook v3 API**, allowing seamless integration with existing security tools without hitting external rate limits.

<div align="center">
  <img src="assets/dashboard_preview.png" width="80%" alt="Dashboard Preview">
  <br>
  <em>Honey Cloud Intelligence Dashboard with Dark Mode and IP Stats</em>
</div>

## Features

-   **Threat Aggregation**: Combines local honeypot data with external OSINT feeds.
-   **High Performance**: Powered by Redis for sub-millisecond response times.
-   **API Emulation**: Fully compatible with the ThreatBook v3 API standard.
-   **Smart Filtering**:
    -   **Whitelist/Blacklist**: Supports exact IP matches and CIDR ranges (e.g., `10.0.0.0/24`).
    -   **Prioritization**: Custom logic to prioritize local threats and manual lists over OSINT data.
-   **Modern UI**: Dark-themed dashboard for managing lists, API keys, and viewing statistics.
-   **Containerized**: Built with Docker and Docker Compose for easy deployment.

## Access & API Keys

> [!IMPORTANT]
> **API Keys are not public.**
> Access to the Honey Cloud Intelligence API is strictly controlled. API keys are issued only via direct contact with the administrator. Please contact the project maintainer to request an API key.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/lemueIO/honey-api.git
    cd honey-api
    ```

2.  Start the services using Docker Compose:
    ```bash
    docker compose up -d --build
    ```

3.  Access the dashboard:
    -   URL: `http://localhost:8080/login`
    -   Default Admin Password: `admin` (Change this immediately in `docker-compose.yml`!)

## Usage

### Syncing Data
The bridge accepts data from HFish nodes via a webhook endpoint. Ensure your HFish nodes are configured to push data to:
`http://<your-server-ip>:8080/api/v1/webhook`

### Querying Reputation
Query the API emulating the ThreatBook format:
```bash
curl "http://localhost:8080/v3/scene/ip_reputation?apikey=YOUR_API_KEY&resource=1.2.3.4"
```

## Technology Stack

-   **Backend**: FastAPI (Python)
-   **Database**: Redis
-   **Frontend**: Jinja2 Templates, Bootstrap 5 (Dark Mode)
-   **Deployment**: Docker

---

Maintained by the Honey-Scan Community and [lemueIO](https://github.com/lemueIO) ❤️
