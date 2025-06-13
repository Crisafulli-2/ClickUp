# ClickUp Tracker

A Python application that automatically syncs ClickUp tasks to Google Sheets for tracking and reporting purposes.

## What We've Built

### Current Features

#### 1. **Multi-Board Data Fetching**
- **External Issues**: List ID `75793048` 
- **Internal Issues**: List ID `901103923965`
- **Feature Requests**: List ID `901110903380`

#### 2. **Google Sheets Integration**
- **Production Tab**: Issues (External + Internal) → 5 columns
  - A: Ticket ID/Link
  - B: Subject  
  - C: Severity (raw ClickUp priority)
  - D: Status (raw ClickUp status)
  - E: Ticket Filed By (email from custom field or "Not Available")

- **Project Summary Tab**: Feature Requests → 5 columns (rows 14+)
  - A: Type of Request
  - B: Summary / Requirements
  - C: Notes/Next Steps
  - D: Status
  - E: Owner/Group

#### 3. **Smart Data Handling**
- **Non-destructive writes**: Checks for existing data before writing
- **Email extraction**: From ClickUp custom field "Work email address?"
- **Append-only**: Adds new rows without clearing existing manual entries
- **Raw ClickUp data**: No field mapping/translation

### Current File Structure
```
ClickUpTracker/
├── src/
│   ├── clickup_service.py     # Main ClickUp API integration
│   └── sheets_service.py      # Google Sheets API service
├── .env                       # API tokens and configuration
├── credentials.json           # Google Sheets API credentials
├── token.json                 # Google Sheets API token
└── README.md                  # This file
```

### Current Workflow
1. Connect to ClickUp API using token
2. Fetch tasks from 3 boards (2 issue boards + 1 feature board)
3. Extract email from custom fields
4. Write issues to "production" tab (append-only)
5. Write features to "Project Summary" tab (write-once)

## Current State & Limitations

### ✅ Working Features
- ClickUp API connection and data fetching
- Google Sheets writing (5 columns each tab)
- Email extraction with fallback to "Not Available"
- Non-destructive data handling
- Multi-board support

### ⚠️ Current Limitations
- No customer-specific filtering
- No dynamic board selection
- No syntax-based task categorization
- Manual list ID management
- Single spreadsheet target

## Next Steps

### Phase 1: Dynamic Board & Customer Filtering

#### 1.1 **Dynamic Board Fetching**
- Automatically discover all boards in workspace instead of hardcoded list IDs
- Allow users to select which boards to export from
- Support for board filtering by name or type

#### 1.2 **Customer Name Detection**
Design a flexible syntax system that doesn't break if not followed:

**Primary Syntax (Preferred)**
```
Format: [Customer Name] | [Project Type] | [Description]
Example: [DIRTcar] | [Bug Fix] | [Stream freezing during live events]
```

**Fallback Detection Methods** (when syntax not followed)
- Email domain mapping (`@dirtcar.com` → `DIRTcar`)
- Keyword detection in subject line
- Custom field parsing
- Default to "General" if no customer identified

#### 1.3 **Multi-Tier Customer Detection Logic**
- Check for bracketed customer syntax in task titles
- Parse email domains for known customer mappings
- Search for customer keywords in task descriptions
- Check custom fields for customer identification data
- Graceful fallback to 'General' category when no customer is identified

### Phase 2: Customer-Specific Routing

#### 2.1 **Customer Spreadsheet Mapping**
- Create mapping system for customers to their dedicated spreadsheets
- Support for customer-specific sheet templates
- Fallback to main "General" spreadsheet for unidentified customers

#### 2.2 **Dynamic Export Targets**
- Export specific customer data to their dedicated spreadsheets
- Batch processing to export all customers to respective sheets
- Option to force creation of new customer spreadsheets

### Phase 3: Enhanced Configuration

#### 3.1 **Configuration Management**
- Move hardcoded IDs to config files
- Environment-based settings (dev/prod)
- Customer mapping configuration
- Board selection presets

#### 3.2 **Error Handling & Logging**
- Detailed logging for debugging
- Graceful handling of API failures
- Data validation and cleanup
- Retry mechanisms for failed exports
