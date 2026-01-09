# Honey Cloud Intelligence

<div align="center">
  <img src="app/static/logo_bear.png" width="120" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>Schnelle Daten-Brücke für Sicherheit</strong></p>

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
    <a href="README_DE2.md">🇩🇪 Einfache Sprache</a>
  </h4>
</div>

Honey Cloud Intelligence ist ein Programm für Sicherheit. Es sammelt Daten über Gefahren aus dem Internet. Es holt Daten von eigenen Fallen (Honeypots) und von vielen öffentlichen Listen (über 10 Quellen). Es verhält sich wie die **ThreatBook v3 API**. Das bedeutet, man kann es einfach mit anderen Programmen benutzen. Es ist sehr schnell.

<div align="center">
  <img src="assets/dashboard_preview.png" width="80%" alt="Dashboard Vorschau">
  <br>
  <em>Das Dashboard zeigt Statistiken und ist dunkel gestaltet.</em>
</div>

## Was kann das Programm?

-   **Daten sammeln**: Es nimmt Daten von innen und außen (Echtzeit + OSINT).
-   **Schnelligkeit**: Es benutzt Redis. Das macht es sehr schnell.
-   **Kompatibilität**: Es spricht die gleiche Sprache wie ThreatBook v3.
-   **Filtern**:
    -   **Listen**: Man kann erlaubte und verbotene Adressen eintragen (auch ganze Bereiche wie `10.0.0.0/24`).
    -   **Wichtigkeit**: Eigene Daten sind wichtiger als fremde Daten.
-   **Überwachung**:
    -   **Konnektivität**: Es prüft automatisch, ob es von außen erreichbar ist (vermeidet Fehler).
    -   **Hilfen**: Es gibt Links und Skripte, um die Verbindung weltweit zu testen.
    -   **Status**: Es gibt einen speziellen `/health` Link für die Überwachung.
-   **Aussehen**: Es gibt eine schöne Übersicht (Dashboard) im Dark Mode.
-   **Sprachen**: Es gibt das Programm und die Hilfe in Englisch, Deutsch und Ukrainisch.
-   **Einfachheit**: Es läuft in Containern (Docker). Das macht die Installation leicht.

## Zugang und Schlüssel

> [!IMPORTANT]
> **Schlüssel sind geheim.**
> Nicht jeder darf das Programm benutzen. Man braucht einen Schlüssel (API Key). Den bekommt man nur vom Administrator. Bitte fragen Sie nach einem Schlüssel.

## Installation

1.  Programm herunterladen:
    ```bash
    git clone https://github.com/lemueIO/honey-api.git
    cd honey-api
    ```

2.  Starten:
    ```bash
    docker compose up -d --build
    ```

3.  Ansehen:
    -   Gehen Sie auf: `http://localhost:8080/login`
    -   Passwort: `admin` (Bitte sofort ändern!)

## Benutzung

### Daten senden
Andere Programme (HFish) können Daten hierhin schicken. Die Adresse ist:
`http://<deine-server-ip>:8080/api/v1/webhook`

### Nach Gefahren fragen
Sie können fragen, ob eine IP-Adresse gefährlich ist:
```bash
curl "http://localhost:8080/v3/scene/ip_reputation?apikey=DEIN_SCHLUESSEL&resource=1.2.3.4"
```

## API Dokumentation (Für Entwickler)

### 1. IP prüfen (ThreatBook v3)
Hier fragt man ab, ob eine IP böse ist.

- **Adresse**: `/v3/scene/ip_reputation`
- **Art**: `GET`
- **Was man braucht**:
  - `apikey`: Den Schlüssel.
  - `resource`: Die IP-Adresse.
- **Beispiel**:
  ```bash
  curl "http://<server-ip>:8080/v3/scene/ip_reputation?apikey=DEIN_SCHLUESSEL&resource=1.2.3.4"
  ```

### 2. Daten empfangen (Webhook)
Hier kommen die Daten von den Fallen an.

- **Adresse**: `/webhook`
- **Art**: `POST`
- **Inhalt**:
  ```json
  {
      "attack_ip": "1.2.3.4"
  }
  ```

### 3. Status prüfen (Health)
Prüfen, ob das System läuft.

- **Adresse**: `/health`
- **Art**: `GET`
- **Antwort**: `{"status": "ok"}`

## Technik

-   **Programmierung**: Python 3.9+ (FastAPI)
-   **Speicher**: Redis
-   **Aussehen**: HTML & CSS (Bootstrap 5)
-   **Starten**: Docker & Docker Compose

---

Gemacht von der Honey-Scan Community und [lemueIO](https://github.com/lemueIO) ❤️
