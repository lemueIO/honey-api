<div align="center">
  <img src="app/static/logo_bear.png" width="150" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>Hochperformante Threat Intelligence Bridge & Aggregator</strong></p>

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
> *Honey Cloud Intelligence ist eine hochperformante Threat Intelligence Bridge, die entwickelt wurde, um Bedrohungsdaten von lokalen HFish-Honeypots und globalen OSINT-Quellen zu aggregieren, zu verwalten und bereitzustellen. Sie emuliert die ThreatBook v3 API und ermöglicht so eine nahtlose Integration in bestehende Sicherheitstools ohne externe Ratenbegrenzungen.*

<div align="center">
  <br>
  <a href="https://api.sec.lemue.org/status">
    <img src="assets/status_preview_v220.png" width="90%" alt="Dashboard Vorschau" style="border-radius: 10px; box-shadow: 0 0 20px rgba(123, 44, 191, 0.3);">
  </a>
  <br>
  <br>
  <em>Honey Cloud Intelligence Status Dashboard - <a href="https://api.sec.lemue.org/status"><strong>Live Ansicht</strong></a></em>
  <br>
</div>

---

## 🚀 Funktionen

| Funktionskategorie | Beschreibung |
| :--- | :--- |
| **Bedrohungsdatenerfassung** | Kombiniert Echtzeitdaten von lokalen **Honeypots** (via HFish) mit **10+ externen OSINT-Feeds**. |
| **Hohe Performance** | Basiert auf **FastAPI** und **Redis** für Antworten im Sub-Millisekunden-Bereich. |
| **API-Emulation** | Vollständig kompatibel mit dem **ThreatBook v3 API**-Standard. |
| **Intelligente Filterung** | Unterstützt **exakte IP-Übereinstimmungen** und **CIDR-Bereiche** (z. B. `10.0.0.0/24`). Optimierte Bereinigung via Pre-Fetch. |
| **Erweitertes Logging** | Strukturiertes Logging mit farbcodierten ANSI-Tags (`[SYSTEM]`, `[CLEAN:DB]`) und visuellem Feedback. |
| **Robustes Monitoring** | Resiliente **Socket-Prüfung**, externe Check-Host.net Links und dedizierter `/health` Endpunkt. |
| **Modernes UI** | Dashboard im **Dark Mode** zur Verwaltung von Listen, API-Schlüsseln und Statistiken. |
| **Öffentliche Statusseite** | Eine vereinfachte, **öffentliche Statusseite** (`/status`), die ohne Login verfügbar ist. |
| **Mehrsprachigkeit** | Dokumentation in **Englisch**, **Deutsch** (Standard & Einfache Sprache) und **Ukrainisch**. |

## 🔑 Zugriff & API-Schlüssel

> [!IMPORTANT]
> **API-Schlüssel sind nicht öffentlich.**
> Der Zugriff auf die Honey Cloud Intelligence API wird streng kontrolliert. API-Schlüssel werden nur nach direktem Kontakt mit dem Administrator vergeben. Bitte wenden Sie sich an den Projektbetreuer, um einen API-Schlüssel zu beantragen.

## 📦 Installation

<details>
<summary><strong>Klicken für Installationsschritte</strong></summary>

1.  **Repository klonen:**
    ```bash
    git clone https://github.com/lemueIO/honey-api.git
    cd honey-api
    ```

2.  **Dienste mit Docker Compose starten:**
    ```bash
    docker compose up -d --build
    ```

3.  **Dashboard aufrufen:**
    -   URL: `http://localhost:8080/login`
    -   Standard-Admin-Passwort: `admin` (Bitte sofort in der `docker-compose.yml` ändern!)

</details>

## 💻 Nutzung

### 🔄 Daten synchronisieren
Die Bridge akzeptiert Daten von HFish-Knoten über einen Webhook-Endpunkt. Stellen Sie sicher, dass Ihre HFish-Knoten so konfiguriert sind:
`http://<ihre-server-ip>:8080/api/v1/webhook`

### 🕵️ Risiko abfragen
Fragen Sie die API im ThreatBook-Format ab:
```bash
curl "http://localhost:8080/v3/scene/ip_reputation?apikey=IHR_API_KEY&resource=1.2.3.4"
```

## 📖 API Dokumentation

### 🧠 1. Reputations-Check (ThreatBook v3 Kompatibel)
Fragt Intelligence-Daten zu einer IP ab.

| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| `GET` | `/v3/scene/ip_reputation` | Prüft die Reputation einer IP-Adresse. |

**Parameter:**
- `apikey`: Ihr persönlicher API-Schlüssel.
- `resource`: Die zu prüfende IP-Adresse.

<details>
<summary><strong>Beispielantwort ansehen</strong></summary>

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

### 🎣 2. Webhook (HFish Kompatibel)
Empfängt Angriffs-Logs von HFish-Knoten.

| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| `POST` | `/webhook` | Nimmt Angriffsdaten von HFish entgegen. |

### 💓 3. Health Check
Systemstatus überwachen.

| Methode | Endpunkt | Beschreibung |
| :--- | :--- | :--- |
| `GET` | `/health` | Gibt den operativen Status zurück. |

## 🛠️ Technologie-Stack

<div align="center">

| Komponente | Technologie |
| :--- | :--- |
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi) (Python 3.9+) |
| **Datenbank** | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white) (Key-Value Storage) |
| **Frontend** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=flat&logo=bootstrap&logoColor=white) (Jinja2 Templates) |
| **Deployment** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) & Docker Compose |

</div>

---

<div align="center">
  <p>Gepflegt von der <strong>Honey-Scan Community</strong> und <a href="https://github.com/lemueIO"><strong>lemueIO</strong></a> ❤️</p>
</div>
