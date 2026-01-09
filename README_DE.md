# Honey Cloud Intelligence

<div align="center">
  <img src="app/static/logo_bear.png" width="120" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>Hochperformante Threat Intelligence Bridge & Aggregator</strong></p>

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
    <a href="README_DE2.md">🇩🇪 Einfache Sprache</a>
  </h4>
</div>

Honey Cloud Intelligence ist eine hochperformante Threat Intelligence Bridge, die entwickelt wurde, um Bedrohungsdaten von lokalen HFish-Honeypots und globalen OSINT-Quellen zu aggregieren, zu verwalten und bereitzustellen. Sie emuliert die **ThreatBook v3 API** und ermöglicht so eine nahtlose Integration in bestehende Sicherheitstools ohne externe Ratenbegrenzungen.

<div align="center">
  <img src="assets/dashboard_preview.png" width="80%" alt="Dashboard Vorschau">
  <br>
  <em>Honey Cloud Intelligence Dashboard mit Dark Mode und IP-Statistiken</em>
</div>

## Funktionen

-   **Bedrohungsdatenerfassung**: Kombiniert lokale Honeypot-Daten mit externen OSINT-Feeds.
-   **Hohe Performance**: Basiert auf Redis für Antworten im Sub-Millisekunden-Bereich.
-   **API-Emulation**: Vollständig kompatibel mit dem ThreatBook v3 API-Standard.
-   **Intelligente Filterung**:
    -   **Whitelist/Blacklist**: Unterstützt exakte IP-Übereinstimmungen und CIDR-Bereiche (z. B. `10.0.0.0/24`).
    -   **Priorisierung**: Benutzerdefinierte Logik zur Priorisierung lokaler Bedrohungen und manueller Listen gegenüber OSINT-Daten.
-   **Modernes UI**: Dashboard im Dark Mode zur Verwaltung von Listen, API-Schlüsseln und zur Ansicht von Statistiken.
-   **Containerisiert**: Erstellt mit Docker und Docker Compose für eine einfache Bereitstellung.

## Zugriff & API-Schlüssel

> [!IMPORTANT]
> **API-Schlüssel sind nicht öffentlich.**
> Der Zugriff auf die Honey Cloud Intelligence API wird streng kontrolliert. API-Schlüssel werden nur nach direktem Kontakt mit dem Administrator vergeben. Bitte wenden Sie sich an den Projektbetreuer, um einen API-Schlüssel zu beantragen.

## Installation

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

## Nutzung

### Daten synchronisieren
Die Bridge akzeptiert Daten von HFish-Knoten über einen Webhook-Endpunkt. Stellen Sie sicher, dass Ihre HFish-Knoten so konfiguriert sind, dass sie Daten an folgende Adresse senden:
`http://<ihre-server-ip>:8080/api/v1/webhook`

### Risiko abfragen
Fragen Sie die API im ThreatBook-Format ab:
```bash
curl "http://localhost:8080/v3/scene/ip_reputation?apikey=IHR_API_KEY&resource=1.2.3.4"
```

## Technologie-Stack

-   **Backend**: FastAPI (Python)
-   **Datenbank**: Redis
-   **Frontend**: Jinja2 Templates, Bootstrap 5 (Dark Mode)
-   **Deployment**: Docker

---

Gepflegt von der Honey-Scan Community und [lemueIO](https://github.com/lemueIO) ❤️
