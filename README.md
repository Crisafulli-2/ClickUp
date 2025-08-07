
# ClickUp & Asana Tracker Integration

Automates export of tasks from ClickUp and Asana to Google Sheets for unified client tracking and reporting.

## Overview

- **ClickUp**: Exports tasks from mapped boards to client-specific Google Sheets tabs.
- **Asana**: Exports sectioned tasks to Google Sheets, each section gets its own tab.
- **Google Sheets**: Data is appended, never overwrites headers. Credentials (`credentials.json`, `.env`) required in project root.

## Project Structure

```
src/
  clickup_service.py        # ClickUp API logic, export functions
  asana_service.py          # Asana API logic, export functions
  sheets_service.py         # Google Sheets API wrapper
  asana_sheets_service.py   # Asana-specific Sheets logic
tests/
  test_clickup_service.py   # ClickUp API tests and data inspection
  test_sheets.py            # Google Sheets integration tests
credentials.json            # Google Sheets API credentials
.env                        # API tokens (not in repo)
README.md
requirements.txt
```

## Setup

1. Python 3.8+
2. Place `credentials.json` and `token.json` in project root.
3. Add `CLICKUP_API_TOKEN` and `ASANA_API_TOKEN` to `.env`.
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

- Export ClickUp tasks for all clients:
  ```bash
  python3 src/clickup_service.py allclients
  ```
- Export for a single client:
  ```bash
  python3 src/clickup_service.py yahoo
  ```
- Export Asana tasks:
  ```bash
  python3 src/asana_service.py
  ```
- Run tests:
  ```bash
  pytest tests/
  ```

## Development Notes

- Each client/section gets a dedicated tab in Sheets.
- Pipe (`|`) delimiter used for account/subject extraction in ClickUp.
- API calls print errors and return empty lists/False on failure.
- Credentials are discovered from multiple relative paths for flexibility.
- All export functions append to the next available row.

## Minimal Improvement Suggestions

- Move API data inspection logic from `/tests` to a dedicated `/scripts` or `/tools` folder for better separation of concerns.
- Consider using more specific ClickUp API endpoints or query parameters for efficient data retrieval (e.g., filter by status, assignee, or custom fields).
- Centralize configuration (board IDs, spreadsheet IDs) in a single settings file or class.
- Add type hints and docstrings for improved maintainability.
- Implement logging instead of print statements for better error tracking and debugging.

---

**Next Steps:**  
Review API data structure and optimize queries for smarter, more efficient data processing.

## 📊 Service Integrations

---

## 🎯 **ClickUp Integration**

### Current Features
- ✅ API connection and authentication
- ✅ Space and project discovery
- ✅ Task retrieval with full details
- ✅ Google Sheets export functionality
- ✅ Real-time data synchronization

### Usage
```bash
# Run ClickUp sync
python3 src/clickup_service.py
```

### Data Structure
- **Spaces**: Top-level organizational units
- **Projects**: Contains lists and tasks
- **Tasks**: Individual work items with assignees, dates, status
- **Export Format**: Organized by space/project hierarchy

### ClickUp Roadmap

#### 🎨 **Phase 1: Enhanced Formatting**
- [ ] **Consistent Styling**: Match corporate design standards
- [ ] **Column Optimization**: Auto-resize based on content
- [ ] **Header Standardization**: Uniform section headers across all sheets
- [ ] **Brand Integration**: Add company logos and color schemes

#### 🌈 **Phase 2: Conditional Formatting**
- [ ] **Status Color Coding**:
  - 🟢 **Completed**: Green background
  - 🟡 **In Progress**: Yellow background  
  - 🔴 **Blocked/On Hold**: Red background
  - 🔵 **To Do**: Blue background
  - ⚪ **Cancelled**: Gray background
- [ ] **Priority Indicators**: High/Medium/Low priority color coding
- [ ] **Date-based Alerts**: Overdue tasks highlighted in red
- [ ] **Assignee Formatting**: Color-code by team member

#### 💬 **Phase 3: Enhanced Comments & Updates**
- [ ] **Comment Threading**: Show full comment history
- [ ] **Last Update Tracking**: Real-time last modified timestamps
- [ ] **Author Attribution**: Show who made each comment/update
- [ ] **Update Notifications**: Highlight recent changes

#### 📈 **Phase 4: Advanced Analytics**
- [ ] **Burndown Charts**: Visual progress tracking
- [ ] **Velocity Metrics**: Team performance analytics
- [ ] **Time Tracking Integration**: Hours logged vs estimated
- [ ] **Custom Dashboards**: Executive summary views

---

## 🎨 **Asana Integration**

### Current Features
- ✅ API connection and workspace discovery
- ✅ Section-based task organization (Live, QA, Hold, etc.)
- ✅ Separate Google Sheets tabs per section
- ✅ Comprehensive task details including comments
- ✅ Summary dashboard with section counts
- ✅ Support for 84+ tasks across 9 sections

### Usage
```bash
# Run Asana sync
python3 src/asana_service.py
```

### Data Structure
- **Workspaces**: wurl.com, transmit.live
- **Projects**: SSAI Dashboard for FAST Deliveries
- **Sections**: HOLD, Funnel, Onboarding, Live, QA, etc.
- **Export Format**: One tab per section with task details

### Section Mapping
```
ASANA SECTIONS → GOOGLE SHEETS TABS
├── HOLD - Further Review Needed → "HOLD Further Review Needed"
├── Funnel → "Funnel"  
├── Onboarding → "Onboarding"
├── Submitted to Transmit → "Submitted to Transmit"
├── Transmit Bootstrap Configured → "Transmit Bootstrap Config..."
├── Ready for Handoff → "Ready for Handoff"
├── Streamer QA → "Streamer QA"
├── Live → "Live"
├── Cancelled Configuration → "Cancelled Configuration"
└── Summary → "Asana Summary"
```

### Asana Roadmap

#### 🎨 **Phase 1: Enhanced Formatting**
- [ ] **Section Headers**: Branded headers for each Asana section
- [ ] **Live Channel Focus**: Special formatting for "Live" section (most critical)
- [ ] **Status Indicators**: Visual cues for channel health
- [ ] **Column Standardization**: Match ClickUp sheet formatting

#### 🌈 **Phase 2: Conditional Formatting**
- [ ] **Channel Status Color Coding**:
  - 🔴 **Live**: Red background (active channels)
  - 🟡 **Streamer QA**: Yellow background (testing phase)
  - 🟢 **Ready for Handoff**: Green background (ready to go live)
  - 🔵 **Onboarding**: Blue background (new channels)
  - ⏸️ **HOLD**: Orange background (needs review)
  - ❌ **Cancelled**: Gray background (cancelled configs)
- [ ] **Priority Channels**: Highlight high-priority streaming channels
- [ ] **SLA Tracking**: Color-code based on time in each section
- [ ] **Assignment Alerts**: Highlight unassigned critical tasks

#### 💬 **Phase 3: Enhanced Comments & Updates**
- [ ] **Last Comment Focus**: Change "Last Update" → "Last Comment"
- [ ] **Comment Formatting**: Better readability with author/timestamp
- [ ] **Recent Activity**: Highlight channels with recent comments
- [ ] **Escalation Tracking**: Flag channels needing attention

#### 📺 **Phase 4: Streaming-Specific Features**
- [ ] **Channel Health Dashboard**: Live channel monitoring
- [ ] **Go-Live Timeline**: Track progression through pipeline
- [ ] **Performance Metrics**: Channel success/failure rates
- [ ] **Automated Alerts**: Notify when channels move to "Live"
- [ ] **Integration Webhooks**: Real-time updates from Asana

---

## 🚀 **Cross-Platform Features** (Future)

#### 🔄 **Phase 5: Unified Dashboard**
- [ ] **Combined Overview**: ClickUp + Asana in single view
- [ ] **Cross-Platform Search**: Find tasks across both systems
- [ ] **Unified Reporting**: Combined analytics and insights
- [ ] **Workflow Integration**: Link ClickUp projects to Asana channels

#### ⚡ **Phase 6: Automation & Intelligence**
- [ ] **Auto-Sync Scheduling**: Hourly/daily automatic updates
- [ ] **Smart Notifications**: AI-powered alerts for important changes
- [ ] **Predictive Analytics**: Forecast project completion times
- [ ] **Custom Workflows**: Trigger actions based on status changes

---

## 🛠️ **Development**

### Current Branch Structure
- `main`: Stable ClickUp integration
- `test-asana-api`: Asana integration development
- Feature branches: `feature/specific-enhancement`

### Running Tests
```bash
# Test ClickUp connection
python3 src/clickup_service.py

# Test Asana connection  
python3 src/asana_service.py

# Test Google Sheets integration
python3 src/sheets_service.py
```

### Contributing
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Submit pull request with detailed description

## 📝 **API Documentation**

### ClickUp API
- **Base URL**: `https://api.clickup.com/api/v2/`
- **Authentication**: Bearer token
- **Rate Limits**: 100 requests/minute

### Asana API  
- **Base URL**: `https://app.asana.com/api/1.0/`
- **Authentication**: Personal Access Token
- **Rate Limits**: 1500 requests/hour

### Google Sheets API
- **Version**: v4
- **Authentication**: OAuth 2.0
- **Permissions**: Read/Write spreadsheets

## 🔐 **Security**

- API tokens stored in `.env` (never committed)
- Google credentials in separate `credentials.json`
- Regular token rotation recommended
- Access logs for audit trail

## 📞 **Support**

For issues or questions:
1. Check existing GitHub issues
2. Review API documentation
3. Contact development team
4. Create new issue with detailed description

---

## 📈 **Current Status**

### ✅ **Completed**
- ClickUp API integration
- Asana API integration  
- Google Sheets export functionality
- Section-based organization
- Multi-workspace support

### 🔄 **In Progress**
- Enhanced formatting and conditional formatting
- Comment system improvements
- Cross-platform unified dashboard

### 📋 **Planned**
- Advanced analytics and reporting
- Automated scheduling and notifications
- AI-powered insights and predictions

---

*Last Updated: June 14, 2025*
*Version: 2.0 (Asana Integration)*