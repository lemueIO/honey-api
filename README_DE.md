# Honey Cloud Intelligence

<div align="center">
  <img src="app/static/logo_bear.png" width="120" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>Hochperformante Threat Intelligence Bridge & Aggregator</strong></p>

  [![beta](https://img.shields.io/badge/beta-v2.4.1-blue?style=for-the-badge&logo=none)](https://github.com/lemueIO/honey-api/releases/tag/v2.4.1)
  [![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Docker](https://img.shields.io/badge/docker-enabled-blue?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
  [![Status](https://img.shields.io/badge/status-active-success?style=for-the-badge&logo=activity&logoColor=white)](https://github.com/lemueIO/honey-api)
  <br>
  [![Repo Size](https://img.shields.io/github/repo-size/lemueIO/honey-api?style=for-the-badge&logo=github&logoColor=white)](https://github.com/lemueIO/honey-api)
  [![License](https://img.shields.io/github/license/lemueIO/honey-api?style=for-the-badge&logo=github&logoColor=white)](LICENSE)
  [![Last Commit](https://img.shields.io/github/last-commit/lemueIO/honey-api?style=for-the-badge&logo=github&logoColor=white)](https://github.com/lemueIO/honey-api/commits/main)
  [![Open Issues](https://img.shields.io/github/issues/lemueIO/honey-api?style=for-the-badge&logo=github&logoColor=white)](https://github.com/lemueIO/honey-api/issues)
</div>

<div align="center">
  <h4>
    <a href="README.md">🇬🇧 English</a> | 
    <a href="README_DE.md">🇩🇪 Deutsch</a> | 
    <a href="README_DE2.md">🇩🇪 Einfache Sprache</a> |
    <a href="README_UA.md">🇺🇦 Українська</a>
  </h4>
</div>

---

Honey Cloud Intelligence ist eine hochperformante Threat Intelligence Bridge, die entwickelt wurde, um Bedrohungsdaten von lokalen HFish-Honeypots und globalen OSINT-Quellen zu aggregieren, zu verwalten und bereitzustellen. Sie emuliert die **ThreatBook v3 API** und ermöglicht so eine nahtlose Integration in bestehende Sicherheitstools ohne externe Ratenbegrenzungen.

<div align="center">
  <a href="https://api.sec.lemue.org/status">
    <img src="assets/status_preview_v220.png" width="80%" alt="Dashboard Vorschau">
  </a>
  <br>
  <em>Honey Cloud Intelligence Status Dashboard - <a href="https://api.sec.lemue.org/status">Live Ansicht</a></em>
</div>

## [🚀](#funktionen) Funktionen

-   **Bedrohungsdatenerfassung**: Kombiniert Echtzeitdaten von lokalen Honeypots (via HFish) mit über 10 externen OSINT-Feeds.
-   **Hohe Performance**: Basiert auf FastAPI und Redis für Antworten im Sub-Millisekunden-Bereich.
-   **API-Emulation**: Vollständig kompatibel mit dem **ThreatBook v3 API**-Standard.
-   **Intelligente Filterung & Bereinigung**:
    -   **Whitelist/Blacklist**: Unterstützt exakte IP-Übereinstimmungen und CIDR-Bereiche (z. B. `10.0.0.0/24`).
    -   **Hochperformante Bereinigung**: Optimierte Datenbankbereinigung durch pre-fetched Blacklist-Scanning und effiziente Redis-SCAN-Operationen.
-   **Erweitertes Logging**:
    -   **Strukturiertes Logging**: Komplett überarbeitetes System mit farbcodierten ANSI-Tags (`[SYSTEM]`, `[CLEAN:DB]`, `[FETCH:OSINT]`) für maximale Übersicht.
    -   **Visuelles Feedback**: Integriertes gelbes ASCII-Logo beim Start und in periodischen 12h-Intervallen.
-   **Robustes Monitoring**:
    -   **Resiliente Prüfung**: Integrierte Socket-Prüfung (Ports 443, 8080), die HTTP-Deadlocks vermeidet.
    -   **Externe Verifizierung**: Direkte Links zu Check-Host.net und ein portables Skript für globale Konnektivitätstests.
    -   **Health-Endpunkt**: Dedizierte `/health`-Route zur Statusüberwachung.
-   **Modernes UI**: Dashboard im Dark Mode zur Verwaltung von Listen, API-Schlüsseln und zur Ansicht von Statistiken.
-   **Öffentliche Statusseite**: Eine vereinfachte, öffentliche Statusseite (`/status`), die ohne Login verfügbar ist.
-   **Mehrsprachigkeit**: Vollständige Dokumentation in Englisch, Deutsch (Standard & Einfache Sprache) und Ukrainisch.
-   **Containerisiert**: Erstellt mit Docker und Docker Compose für eine einfache Bereitstellung.

## [🔑](#zugriff--api-schlüssel) Zugriff & API-Schlüssel

> [!IMPORTANT]
> **API-Schlüssel sind nicht öffentlich.**
> Der Zugriff auf die Honey Cloud Intelligence API wird streng kontrolliert. API-Schlüssel werden nur nach direktem Kontakt mit dem Administrator vergeben. Bitte wenden Sie sich an den Projektbetreuer, um einen API-Schlüssel zu beantragen.

## [📦](#installation) Installation

1.  Repository klonen:
    ```bash
    git clone https://github.com/lemueIO/honey-api.git
    cd honey-api
    ```

2.  Dienste mit Docker Compose starten:
    ```bash
    docker compose up -d --build
    ```

3.  Dashboard aufrufen:
    -   URL: `http://localhost:8080/login`
    -   Standard-Admin-Passwort: `admin` (Bitte sofort in der `docker-compose.yml` ändern!)

## [💻](#nutzung) Nutzung

### [🔄](#daten-synchronisieren) Daten synchronisieren
Die Bridge akzeptiert Daten von HFish-Knoten über einen Webhook-Endpunkt. Stellen Sie sicher, dass Ihre HFish-Knoten so konfiguriert sind, dass sie Daten an folgende Adresse senden:
`http://<ihre-server-ip>:8080/api/v1/webhook`

### [🕵️](#risiko-abfragen) Risiko abfragen
Fragen Sie die API im ThreatBook-Format ab:
```bash
curl "http://localhost:8080/v3/scene/ip_reputation?apikey=IHR_API_KEY&resource=1.2.3.4"
```

## [📖](#api-dokumentation) API Dokumentation

### 1. [🧠](#1-reputations-check-threatbook-v3-kompatibel) Reputations-Check (ThreatBook v3 Kompatibel)
Fragt Intelligence-Daten zu einer IP ab.

- **Endpunkt**: `/v3/scene/ip_reputation`
- **Methode**: `GET`
- **Parameter**:
  - `apikey`: Ihr persönlicher API-Schlüssel.
  - `resource`: Die zu prüfende IP-Adresse.
- **Beispiel**:
  ```bash
  curl "http://<server-ip>:8080/v3/scene/ip_reputation?apikey=IHR_KEY&resource=1.2.3.4"
  ```
- **Antwort**:
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

### 2. [🎣](#2-webhook-hfish-kompatibel) Webhook (HFish Kompatibel)
Empfängt Angriffs-Logs von HFish-Knoten.

- **Endpunkt**: `/webhook`
- **Methode**: `POST`
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
      "attack_ip": "1.2.3.4"
  }
  ```

### 3. [💓](#3-health-check) Health Check
Systemstatus überwachen.

- **Endpunkt**: `/health`
- **Methode**: `GET`
- **Antwort**: `{"status": "ok"}`

## [🛠️](#technologie-stack) Technologie-Stack

-   **Backend**: FastAPI (Python 3.9+)
-   **Datenbank**: Redis (Key-Value Storage)
-   **Frontend**: Jinja2 Templates, Bootstrap 5 (Dark Mode Design)
-   **Deployment**: Docker & Docker Compose

---

Gepflegt von der Honey-Scan Community und [lemueIO](https://github.com/lemueIO) ❤️
