# Changelog

All notable changes to this project will be documented in this file.

## [2.2.0] - 2026-01-11

### Added
- **Visuals**: Integrated yellow ASCII logo into the logging system (startup and 12h interval).
- **Documentation**: Added repository status badges (Repo Size, License, Last Commit, Open Issues) to READMEs.
- **Security**: Added `.gitaccounts` to `.gitignore` to prevent sensitive data leakage.

### Changed
- **Optimization**: Significant performance improvement in database cleanup via pre-fetched blacklist scanning and optimized IP matching logic.
- **Logging**: Complete overhaul of the logging system. Replaced emojis with color-coded ANSI tags (`[SYSTEM]`, `[CLEAN:DB]`, `[FETCH:OSINT]`, etc.) for better readability in Docker logs.
- **Maintenance**: Removed failing DigitalSide OSINT source to ensure stability of the feed update cycle.
- **Cleanup**: Reduced database cleanup interval to 1 hour.
- **Versioning**: Minor version bump to v2.2.0.

## [2.1.0] - 2026-01-10

### Added
- **Status Page**: New public status page available at `/status` (and `https://api.sec.lemue.org/status`) to view system health and threat statistics without authentication.
- **API Endpoint**: Public statistics endpoint `/api/public/stats` to power the status page.

### Changed
- **Versioning**: Minor version bump to v2.1.0.

## [2.0.0] - 2026-01-09

### Added
- **API Documentation**: Comprehensive documentation for API endpoints (`/v3/scene/ip_reputation`, `/webhook`, `/health`) added to READMEs in all supported languages (EN, DE, DE-Simple, UA).

### Changed
- **Versioning**: Major version bump to v2.0.0 to reflect the stability and feature completeness of the API.

## [1.2.2] - 2026-01-09

### Added
- **Visuals**: Updated dashboard screenshot (`assets/dashboard_preview.png`) to reflect recent UI improvements and data state.

### Changed
- **Documentation**: Final polish of all documentation files, ensuring consistency and clarity across all supported languages.
- **Versioning**: Officially bumped version to v1.2.2.

## [1.2.1] - 2026-01-09

### Added
- **Visuals**: Captured fresh, high-quality dashboard screenshot (`assets/dashboard_preview.png`) with sensitive data blurred.

### Changed
- **Documentation**: 
    - Comprehensive overhaul of `README.md` with complete feature descriptions, monitoring details, and architecture overview.
    - Synchronized all translations (`DE`, `DE2`, `UA`) with the new English content.
- **Versioning**: Officially bumped version to v1.2.1.

## [1.2.0] - 2026-01-09

### Added
- **Localization**: Added full Ukrainian translation (`README_UA.md`).
- **Monitoring**: 
    - Added "Check External" reachability link in Dashboard (Check-Host.net).
    - Added standalone `tools/check_external_access.py` script for external verification.
    - Added dedicated `/health` endpoint.
- **OSINT**: Expanded OSINT feed sources to 10.

### Fixed
- **Dashboard**: Fixed "API Status" indicator using resilient socket-based checks to prevent HTTP deadlocks.
- **UI**: Increased dashboard auto-refresh rate to 10 seconds.

### Changed
- **Versioning**: Officially bumped version to v1.2.0.
- **Operations**: Added explicit DNS settings (`1.1.1.1`, `1.0.0.1`) to `docker-compose.yml` for improved container resolution.

## [1.0.2] - 2026-01-09

### Fixed
-   **API Endpoint**: Fixed double slash issue in API requests by correcting HFish database configuration (removed trailing slash from `https://api.sec.lemue.org/`).
-   **API Route**: Updated API endpoint from `/v3/ip/reputation` to `/v3/scene/ip_reputation` to match ThreatBook v3 standard and HFish expectations.
-   **Middleware**: Added double slash middleware as a safety mechanism to handle malformed URLs.

### Added
-   **Enhanced Logging**: Added detailed webhook logging to differentiate between new IPs (🆕) and updates to existing IPs (🔄).
-   **Monitoring**: Improved visibility into IP collection patterns and duplicate detection.

### Changed
-   **Deployment**: Rebuilt and redeployed production container with all fixes.

## [1.0.1] - 2026-01-09

### Added
-   **WebUI Enhancements**:
    -   Added top-right navigation menu to the Login page with quick links (GitHub, Feed, Banned IPs, HFish Login).
    -   Implemented 15-second auto-refresh for both Dashboard and Login pages.
    -   Added custom favicon (`favicon-lemue.ico`) for the HFish login link.
-   **Documentation**: Added badges and improved header in `README.md`.

### Changed
-   **UI Adjustments**:
    -   Aligned Login page icons using flexbox.
    -   Resized HFish login icon to 26px for better visual consistency.
    -   Updated HFish login link to point to `https://lemue.org/` with lowercase tooltip.
-   **Sync Logic**: Verified and finalized the synchronization backlog processing (reduced from ~15k to ~0 backlog).

## [1.0.0] - 2026-01-09

### Added
-   **Initial Release**: Complete implementation of the Honey Cloud Intelligence bridge.
-   **CIDR Support**: Added support for CIDR notation (e.g., `192.168.1.0/24`) in Whitelist and Blacklist.
-   **Dark Mode**: Implemented a modern dark theme for the Dashboard and Login pages.
-   **Logo**: Added custom "Bear" logo to the header and login screen.
-   **API Emulation**: Full compatibility with ThreatBook v3 API response format.
-   **Redis Integration**: Efficient storage and retrieval of Local and OSINT IPs.
-   **Web Interface**:
    -   Dashboard for statistics and list management.
    -   API Key management (Generation, Deletion, Listing).
    -   Secure Login page.

### Changed
-   **Branding**: Renamed project from "Threat Intelligence Bridge" to "Honey Cloud Intelligence".
-   **Static Files**: Improved static file serving with relative paths to support reverse proxies.
-   **Performance**: Optimized Redis queries for high-throughput IP reputation checks.

### Security
-   **API Keys**: Implemented strict API key validation middleware.
-   **Rate Limiting**: Basic structure in place for future rate limiting.
