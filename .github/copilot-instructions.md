# Copilot Instructions for ClickUp & Asana Tracker Integration

## Big Picture Architecture
- The project integrates ClickUp and Asana APIs with Google Sheets for unified task tracking and reporting.
- Main logic is in `src/`:
  - `clickup_service.py`: Handles ClickUp API, task extraction, and export to Sheets.
  - `asana_service.py`: Handles Asana API, section/task extraction, and export to Sheets.
  - `sheets_service.py` and `asana_sheets_service.py`: Encapsulate Google Sheets API logic for each platform.
- Data flow: API → Python service → Google Sheets (each section/account gets its own tab).
- Credentials (`credentials.json`, `.env`) must be present in the project root for API access.

## Developer Workflows
- **Run ClickUp export:** `python3 src/clickup_service.py`
- **Run Asana export:** `python3 src/asana_service.py`
- **Test connection:** Each service has a `test_connection()` method for API health checks.
- **Unit tests:** Located in `tests/`, run with `pytest`.
- **Branching:** Use feature branches for refactors and PRs (see README for branch naming conventions).

## Project-Specific Conventions
- **Google Sheets Tabs:** Each client/section gets a dedicated tab; no mixing of data.
- **Delimiter Logic:** Pipe (`|`) delimiter is used to split account/subject in ClickUp tasks; logic is centralized and not hardcoded for specific clients.
- **Error Handling:** All API calls print clear error messages and return empty lists or False on failure.
- **Credentials Discovery:** Services search for `credentials.json` and `token.json` in multiple relative paths for flexibility.
- **Export Patterns:** Always append to the next available row in Sheets, never overwrite headers.
- **Section Mapping:** Asana sections are mapped to tab names using `_clean_tab_name()` for Google Sheets compatibility.

## Integration Points & Dependencies
- **ClickUp API:** Requires `CLICKUP_API_TOKEN` in `.env`.
- **Asana API:** Requires `ASANA_API_TOKEN` in `.env`.
- **Google Sheets API:** Requires `credentials.json` and `token.json`.
- **External Libraries:** `requests`, `google-auth`, `google-api-python-client`, `python-dotenv`.

## Examples & Patterns
- To export all ClickUp tasks for all clients: `python3 src/clickup_service.py allclients`
- To export Asana tasks to Wurl Sheets: `python3 src/asana_service.py`
- To add a new client or section, update the relevant mapping in the service file and ensure tab creation logic is robust.

## Key Files
- `src/clickup_service.py`: Main ClickUp logic, delimiter handling, export functions.
- `src/asana_service.py`: Main Asana logic, section extraction, export functions.
- `src/sheets_service.py`, `src/asana_sheets_service.py`: Google Sheets API wrappers.
- `tests/`: Unit tests for core logic.
- `README.md`: Architecture, setup, and workflow documentation.

---

For questions or unclear conventions, review the README or ask for clarification. Update this file as new patterns or workflows emerge.
