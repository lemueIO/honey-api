<div align="center">
  <img src="app/static/logo_bear.png" width="150" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>Schnelle Daten-Brücke für Sicherheit</strong></p>

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
> *Honey Cloud Intelligence ist ein Programm für Sicherheit. Es sammelt Daten über Gefahren aus dem Internet (Honeypots und Listen). Es verhält sich wie die ThreatBook v3 API und ist sehr schnell, weil es kompatibel und optimiert ist.*

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

## 🚀 Was kann das Programm?

| Kategorie | Beschreibung |
| :--- | :--- |
| **Daten sammeln** | Es nimmt Daten von innen (Honeypots) und außen (**10+ Quellen**). |
| **Schnelligkeit** | Es ist **sehr schnell** (benutzt Redis). |
| **Kompatibilität** | Es spricht die gleiche Sprache wie **ThreatBook v3**. |
| **Filtern & Aufräumen** | Man kann erlaubte und verbotene Adressen eintragen. Es löscht alte Daten **automatisch**. |
| **Besseres Logbuch** | Das Protokoll ist **bunt und übersichtlich**. Mit einem schönen Logo. |
| **Überwachung** | Es prüft selbst, ob es erreichbar ist. Es gibt Links zum Testen. |
| **Aussehen** | Es gibt eine schöne Übersicht (**Dashboard**) im Dark Mode. |
| **Status-Seite** | Es gibt eine **öffentliche Seite**, die jeder sehen kann. |
| **Sprachen** | Es gibt Hilfe in **Englisch**, **Deutsch** und **Ukrainisch**. |
| **Einfachheit** | Einfache Installation mit **Docker**. |

## 🔑 Zugang und Schlüssel

> [!IMPORTANT]
> **Schlüssel sind geheim.**
> Nicht jeder darf das Programm benutzen. Man braucht einen Schlüssel (API Key). Den bekommt man nur vom Administrator. Bitte fragen Sie nach einem Schlüssel.

## 📦 Installation

<details>
<summary><strong>Klicken für Anleitung</strong></summary>

1.  **Programm herunterladen:**
    ```bash
    git clone https://github.com/lemueIO/honey-api.git
    cd honey-api
    ```

2.  **Starten:**
    ```bash
    docker compose up -d --build
    ```

3.  **Ansehen:**
    -   Gehen Sie auf: `http://localhost:8080/login`
    -   Passwort: `admin` (Bitte sofort ändern!)

</details>

## 💻 Benutzung

### 🔄 Daten senden
Andere Programme (HFish) können Daten hierhin schicken. Die Adresse ist:
`http://<deine-server-ip>:8080/api/v1/webhook`

### 🕵️ Nach Gefahren fragen
Sie können fragen, ob eine IP-Adresse gefährlich ist:
```bash
curl "http://localhost:8080/v3/scene/ip_reputation?apikey=DEIN_SCHLUESSEL&resource=1.2.3.4"
```

## 📖 API Dokumentation (Für Entwickler)

### 🧠 1. IP prüfen (ThreatBook v3)
Hier fragt man ab, ob eine IP böse ist.

| Methode | Adresse | Beschreibung |
| :--- | :--- | :--- |
| `GET` | `/v3/scene/ip_reputation` | Prüft eine IP-Adresse. |

**Was man braucht:**
- `apikey`: Den Schlüssel.
- `resource`: Die IP-Adresse.

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

### 🎣 2. Daten empfangen (Webhook)
Hier kommen die Daten von den Fallen an.

| Methode | Adresse | Beschreibung |
| :--- | :--- | :--- |
| `POST` | `/webhook` | Empfängt Daten von HFish. |

### 💓 3. Status prüfen (Health)
Prüfen, ob das System läuft.

| Methode | Adresse | Beschreibung |
| :--- | :--- | :--- |
| `GET` | `/health` | Gibt "ok" zurück. |

## 🛠️ Technik

<div align="center">

| Komponente | Technologie |
| :--- | :--- |
| **Programmierung** | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi) (Python 3.9+) |
| **Speicher** | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white) (Key-Value) |
| **Aussehen** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=flat&logo=bootstrap&logoColor=white) (Dunkles Design) |
| **Starten** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) & Docker Compose |

</div>

---

<div align="center">
  <p>Gemacht von der <strong>Honey-Scan Community</strong> und <a href="https://github.com/lemueIO"><strong>lemueIO</strong></a> ❤️</p>
</div>
