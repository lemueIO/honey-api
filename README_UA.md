<div align="center">
  <img src="app/static/logo_bear.png" width="150" alt="Honey Cloud Intelligence Logo">
  <h1>Honey Cloud Intelligence</h1>
  <p><strong>Високопродуктивний міст та агрегатор розвідки загроз</strong></p>

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
> *Honey Cloud Intelligence — це високопродуктивний міст розвідки загроз, розроблений для агрегації, управління та обслуговування даних про загрози з локальних приманок HFish та глобальних джерел OSINT. Він емулює ThreatBook v3 API, що дозволяє безшовну інтеграцію з існуючими інструментами безпеки без досягнення зовнішніх лімітів швидкості.*

<div align="center">
  <br>
  <a href="https://api.sec.lemue.org/status">
    <img src="assets/status_preview_v220.png" width="90%" alt="Перегляд панелі керування" style="border-radius: 10px; box-shadow: 0 0 20px rgba(123, 44, 191, 0.3);">
  </a>
  <br>
  <br>
  <em>Панель статусу Honey Cloud Intelligence - <a href="https://api.sec.lemue.org/status"><strong>Перегляд наживо</strong></a></em>
  <br>
</div>

---

## 🚀 Особливості

| Категорія | Опис |
| :--- | :--- |
| **Агрегація загроз** | Поєднує дані в реальному часі з **локальних приманок** (HFish) та **10+ джерел OSINT**. |
| **Висока продуктивність** | Працює на **FastAPI** та **Redis** для миттєвого відгуку. |
| **Емуляція API** | Повністю сумісний зі стандартом **ThreatBook v3 API**. |
| **Розумна фільтрація** | Підтримує **білий/чорний список** (IP/CIDR) і **швидке очищення**. |
| **Розширене логування** | Кольорові логи (**ANSI**) та візуальний відгук при запуску. |
| **Надійний моніторинг** | **Резильєнтна перевірка** доступності, зовнішні тести та `/health` ендпоінт. |
| **Сучасний інтерфейс** | Панель у **темному режимі** з живою статистикою та управлінням ключами. |
| **Сторінка статусу** | Публічний дашборд (`/status`), доступний без реєстрації. |
| **Багатомовність** | Документація **англійською**, **німецькою** та **українською**. |

## 🔑 Доступ та ключі API

> [!IMPORTANT]
> **Ключі API не є публічними.**
> Доступ до Honey Cloud Intelligence API суворо контролюється. Ключі API видаються тільки через прямий контакт з адміністратором. Будь ласка, зв'яжіться з супроводжувачем проекту, щоб отримати ключ API.

## 📦 Встановлення

<details>
<summary><strong>Натисніть для інструкції</strong></summary>

1.  **Клонуйте репозиторій:**
    ```bash
    git clone https://github.com/lemueIO/honey-api.git
    cd honey-api
    ```

2.  **Запустіть сервіси:**
    ```bash
    docker compose up -d --build
    ```

3.  **Відкрийте панель керування:**
    -   URL: `http://localhost:8080/login`
    -   Пароль адміністратора: `admin` (Негайно змініть його!)

</details>

## 💻 Використання

### 🔄 Синхронізація даних
Міст приймає дані від вузлів HFish через веб-хук. Налаштуйте HFish на:
`http://<ip-вашого-сервера>:8080/api/v1/webhook`

### 🕵️ Запит репутації
Зробіть запит до API (формат ThreatBook):
```bash
curl "http://localhost:8080/v3/scene/ip_reputation?apikey=ВАШ_API_КЛЮЧ&resource=1.2.3.4"
```

## 📖 Документація API

### 🧠 1. Перевірка репутації (ThreatBook v3)
Запит даних про репутацію IP.

| Метод | Ендпоінт | Опис |
| :--- | :--- | :--- |
| `GET` | `/v3/scene/ip_reputation` | Перевіряє репутацію IP. |

**Параметри:**
- `apikey`: Ваш ключ.
- `resource`: IP-адреса.

<details>
<summary><strong>Приклад відповіді</strong></summary>

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

### 🎣 2. Вебхук (HFish)
Отримання журналів атак.

| Метод | Ендпоінт | Опис |
| :--- | :--- | :--- |
| `POST` | `/webhook` | Приймає логи атак. |

### 💓 3. Перевірка здоров'я
Моніторинг стану.

| Метод | Ендпоінт | Опис |
| :--- | :--- | :--- |
| `GET` | `/health` | Статус "ok". |

## 🛠️ Технологічний стек

<div align="center">

| Компонент | Технологія |
| :--- | :--- |
| **Бекенд** | ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi) (Python 3.9+) |
| **База даних** | ![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white) (Key-Value) |
| **Фронтенд** | ![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=flat&logo=bootstrap&logoColor=white) (Темна тема) |
| **Rozgortannya** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) & Docker Compose |

</div>

---

<div align="center">
  <p>Підтримується спільнотою <strong>Honey-Scan</strong> та <a href="https://github.com/lemueIO"><strong>lemueIO</strong></a> ❤️</p>
</div>
