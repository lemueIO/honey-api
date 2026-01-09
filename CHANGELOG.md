# Changelog

All notable changes to this project will be documented in this file.

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
