import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClickUpService:
    def format_task_row(self, task, has_pipe):
        """Format a single task row for spreadsheet output."""
        task_name = task.get('name', '') or ''
        priority = task.get('priority', {})
        severity = priority.get('priority', 'normal') if priority else 'normal'
        status = task.get('status', {})
        current_status = status.get('status', 'Unknown') if status else 'Unknown'
        filer_email = ""
        custom_fields = task.get('custom_fields', [])
        for field in custom_fields:
            if field.get('name') == 'Work email address?':
                filer_email = field.get('value', '')
                break
        if not filer_email or filer_email.strip() == "":
            filer_email = "Not Available"
        if has_pipe:
            parts = task_name.split('|', 1)
            account = parts[0].strip()
            subject = parts[1].strip() if len(parts) > 1 else ''
            return [
                account,
                task.get('url', ''),
                subject,
                severity,
                current_status,
                filer_email,
                task.get('board_name', '')
            ]
        else:
            return [
                '',
                task.get('url', ''),
                task_name if task_name else 'No Title',
                severity,
                current_status,
                filer_email,
                task.get('board_name', '')
            ]

    def calculate_data_ranges(self, start_row, rows_with_customer, rows_without_pipe):
        """Calculate spreadsheet ranges for customer and non-customer rows, with label row immediately after customer rows."""
        range_name1 = f"A{start_row}:G{start_row + len(rows_with_customer) - 1}"
        label_row_index = start_row + len(rows_with_customer)
        range_label = f"A{label_row_index}:G{label_row_index}"
        range_name2 = f"A{label_row_index + 1}:G{label_row_index + len(rows_without_pipe)}"
        return range_name1, range_label, range_name2
    def export_single_client_to_spreadsheet(self, client_name):
        """Export all tasks for a single client to their specific spreadsheet, writing to the 'production' tab only, with sectioning as in the test template export."""
        try:
            from src.sheets_service import GoogleSheetsService
        except ModuleNotFoundError:
            import sys, os
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
            from src.sheets_service import GoogleSheetsService
        spreadsheet_id = self.CLIENT_SPREADSHEET_IDS.get(client_name)
        if not spreadsheet_id:
            print(f"❌ No spreadsheet ID found for client: {client_name}")
            return False
        # Use 'Production' as the tab name for Dirt Vision, and match case-insensitively for all
        default_tab = "Production"
        target_tab = default_tab

        print(f"\n🔄 Exporting ALL tasks for {client_name} to their spreadsheet (production tab)...")
        all_tasks = []
        # Define aliases for each client for fuzzy matching
        client_aliases = {
            'Dirt Vision': ['dirt vision', 'dirtvision', 'dv'],
            'Gotham/Yes': ['gotham', 'yes'],
            'Marquee': ['marquee'],
            'Wurl': ['wurl'],
            'Yahoo': ['yahoo']
        }
        aliases = client_aliases.get(client_name, [client_name])
        aliases = [a.lower() for a in aliases]

        # Only fetch tasks from boards that are likely to contain Dirt Vision tickets
        # (If you want to further optimize, you could filter by board name or ID here)
        for board_name, list_id in {**self.issue_boards, **self.feature_boards}.items():
            # Optionally skip boards not relevant to Dirt Vision
            # For now, fetch all, but could add: if 'dirt' not in board_name.lower(): continue
            tasks = self.get_tasks_from_list(list_id, board_name)
            for task in tasks:
                customer = self.extract_customer_name(task.get('name', ''))
                if customer:
                    customer_lc = customer.lower()
                    if any(alias in customer_lc for alias in aliases):
                        all_tasks.append(task)

        # Prepare headers and rows for tasks with a customer name
        headers = ['Account', 'Ticket ID/Link', 'Subject', 'Severity', 'Status', 'Ticket Filed By', 'Board']
        rows_with_customer = []
        rows_without_pipe = []
        for task in all_tasks:
            task_name = task.get('name', '') or ''
            has_pipe = '|' in task_name
            priority = task.get('priority', {})
            severity = priority.get('priority', 'normal') if priority else 'normal'
            status = task.get('status', {})
            current_status = status.get('status', 'Unknown') if status else 'Unknown'
            filer_email = ""
            custom_fields = task.get('custom_fields', [])
            for field in custom_fields:
                if field.get('name') == 'Work email address?':
                    filer_email = field.get('value', '')
                    break
            if not filer_email or filer_email.strip() == "":
                filer_email = "Not Available"
            if has_pipe:
                # Split on first pipe
                parts = task_name.split('|', 1)
                account = parts[0].strip()
                subject = parts[1].strip() if len(parts) > 1 else ''
                data_row = [
                    account,
                    task.get('url', ''),
                    subject,
                    severity,
                    current_status,
                    filer_email,
                    task.get('board_name', '')
                ]
                rows_with_customer.append(data_row)
            else:
                data_row = [
                    '',
                    task.get('url', ''),
                    task_name if task_name else 'No Title',
                    severity,
                    current_status,
                    filer_email,
                    task.get('board_name', '')
                ]
                rows_without_pipe.append(data_row)

        sheets_service = GoogleSheetsService()
        sheets_service.SPREADSHEET_ID = spreadsheet_id

        # Check if the tab exists (case-insensitive), and use the correct case if found
        try:
            sheet_metadata = sheets_service.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheet_names = [s['properties']['title'] for s in sheet_metadata.get('sheets', [])]
            found_tab = None
            for name in sheet_names:
                if name.lower() == target_tab.lower():
                    found_tab = name
                    break
            if found_tab:
                target_tab = found_tab  # Use the actual case from the sheet
            else:
                print(f"Tab '{target_tab}' not found. Creating it...")
                add_sheet_request = {
                    'requests': [{
                        'addSheet': {
                            'properties': {
                                'title': target_tab
                            }
                        }
                    }]
                }
                sheets_service.service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body=add_sheet_request
                ).execute()
                print(f"✅ Created tab '{target_tab}'")
        except Exception as e:
            print(f"❌ Error checking/creating tab '{target_tab}': {e}")
            return False

        # Prepare label row for printing and writing
        label_text = "TASKS WITHOUT PIPE DELIMITER"
        label_row = [[label_text] + ["" for _ in range(6)]]

        # Print output for user review before writing
        print("\n--- Would write the following rows to the sheet (with customer) ---")
        for row in rows_with_customer:
            print(row)
        print("\n--- Would write the following label row ---")
        print(label_row[0])
        print("\n--- Would write the following rows to the sheet (without pipe) ---")
        for row in rows_without_pipe:
            print(row)

        # Always write header to A1:G1
        header_range = f"'{target_tab}'!A1:G1"
        header_body = {'values': [headers]}
        try:
            sheets_service.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=header_range,
                valueInputOption='RAW',
                body=header_body
            ).execute()
        except Exception as e:
            print(f"⚠️ Could not write header row: {e}")

        # Find the last non-empty row after writing header
        try:
            existing_range = f"'{target_tab}'!A:G"
            existing_result = sheets_service.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=existing_range
            ).execute()
            existing_values = existing_result.get('values', [])
            last_row_index = -1
            for i in range(len(existing_values)-1, -1, -1):
                row = existing_values[i]
                if any(cell.strip() for cell in row if cell):
                    last_row_index = i
                    break
            start_row = max(last_row_index + 2, 2)  # Always start at row 2 or after last row
        except Exception as e:
            print(f"⚠️ Could not read existing data, starting at row 2: {e}")
            start_row = 2

        # Calculate ranges based on start_row
        range_name1 = f"'{target_tab}'!A{start_row}:G{start_row + len(rows_with_customer) - 1}"
        body1 = {'values': rows_with_customer}
        start_row2 = start_row + len(rows_with_customer) + 1
        range_label = f"'{target_tab}'!A{start_row2}:G{start_row2}"
        range_name2 = f"'{target_tab}'!A{start_row2+1}:G{start_row2+len(rows_without_pipe)}"
        body2 = {'values': rows_without_pipe}
        try:
            print(f"\n[DEBUG] Spreadsheet ID: {spreadsheet_id}")
            print(f"[DEBUG] Tab name: '{target_tab}'")
            print(f"[DEBUG] Range for customer rows: {range_name1}")
            print(f"[DEBUG] Range for label row: {range_label}")
            print(f"[DEBUG] Range for without pipe rows: {range_name2}")

            print(f"Writing {len(rows_with_customer)-1} tasks with customer to {range_name1}")
            resp1 = sheets_service.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name1,
                valueInputOption='RAW',
                body=body1
            ).execute()
            print(f"[DEBUG] API response for customer rows: {resp1}")

            print(f"Writing label row to {range_label}")
            resp_label = sheets_service.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_label,
                valueInputOption='RAW',
                body={'values': label_row}
            ).execute()
            print(f"[DEBUG] API response for label row: {resp_label}")

            print(f"Writing {len(rows_without_pipe)-1} tasks without pipe to {range_name2}")
            resp2 = sheets_service.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name2,
                valueInputOption='RAW',
                body=body2
            ).execute()
            print(f"[DEBUG] API response for without pipe rows: {resp2}")

            print(f"✅ Wrote {len(rows_with_customer)-1} tasks with customer and {len(rows_without_pipe)-1} tasks without pipe to tab: {target_tab}")
            return True
        except Exception as e:
            print(f"❌ Error writing to tab {target_tab}: {e}")
            import traceback
            traceback.print_exc()
            return False
    # Mapping of client names to their spreadsheet IDs
    CLIENT_SPREADSHEET_IDS = {
        'Dirt Vision': '10Tt5pcc_6_KJSisTCwEaUUnToXgVK6pX3aKpeeuc3Vs',
        'Gotham/Yes': '1rJQKdH4qS39jDmh75e0k4_4bdTn0Em9qw4-SjDYaQoE',
        'Marquee': '1bTsbi39_tJTi5MD0nXihnPVJB4otT71eIc7w9CEy1Og',
        'Wurl': '1xv3wcnaGK9WOEnqh9fuEbJ2YnWUfT9KtlCQxeo9ga1E',
        'Yahoo': '18iLa6Kiv3TssAR3CDw2NC4nClaVuUiHThADPWVh6xKo',
    }
    def export_all_accounts_to_test_template(self):
        """Export all tasks from all boards to the test template spreadsheet, writing to the 'production' tab only, with an Account column."""
        from src.sheets_service import GoogleSheetsService
        test_spreadsheet_id = "13raU31sm8wDz1xCQ5WpmHPbmlYgxRok1OLaH1uvJgPo"
        target_tab = "production"

        print("\n🔄 Exporting ALL tasks to test template spreadsheet (production tab)...")
        all_tasks = []
        for board_name, list_id in {**self.issue_boards, **self.feature_boards}.items():
            tasks = self.get_tasks_from_list(list_id, board_name)
            all_tasks.extend(tasks)

        # Prepare headers and rows for tasks with a customer name
        headers = ['Account', 'Ticket ID/Link', 'Subject', 'Severity', 'Status', 'Ticket Filed By', 'Board']
        rows_with_customer = []
        rows_without_pipe = []
        for task in all_tasks:
            customer = self.extract_customer_name(task.get('name', ''))
            has_pipe = '|' in (task.get('name', '') or '')
            priority = task.get('priority', {})
            severity = priority.get('priority', 'normal') if priority else 'normal'
            status = task.get('status', {})
            current_status = status.get('status', 'Unknown') if status else 'Unknown'
            filer_email = ""
            custom_fields = task.get('custom_fields', [])
            for field in custom_fields:
                if field.get('name') == 'Work email address?':
                    filer_email = field.get('value', '')
                    break
            if not filer_email or filer_email.strip() == "":
                filer_email = "Not Available"
            data_row = [
                customer if has_pipe else '',
                task.get('url', ''),
                task.get('name', 'No Title'),
                severity,
                current_status,
                filer_email,
                task.get('board_name', '')
            ]
            if has_pipe and customer:
                rows_with_customer.append(data_row)
            else:
                rows_without_pipe.append(data_row)

        sheets_service = GoogleSheetsService()
        sheets_service.SPREADSHEET_ID = test_spreadsheet_id

        # Always write header to A1:G1
        header_range = f"'{target_tab}'!A1:G1"
        header_body = {'values': [headers]}
        try:
            sheets_service.service.spreadsheets().values().update(
                spreadsheetId=test_spreadsheet_id,
                range=header_range,
                valueInputOption='RAW',
                body=header_body
            ).execute()
        except Exception as e:
            print(f"⚠️ Could not write header row: {e}")

        # Find the last non-empty row after writing header
        try:
            existing_range = f"'{target_tab}'!A:G"
            existing_result = sheets_service.service.spreadsheets().values().get(
                spreadsheetId=test_spreadsheet_id,
                range=existing_range
            ).execute()
            existing_values = existing_result.get('values', [])
            last_row_index = -1
            for i in range(len(existing_values)-1, -1, -1):
                row = existing_values[i]
                if any(cell.strip() for cell in row if cell):
                    last_row_index = i
                    break
            start_row = max(last_row_index + 2, 2)  # Always start at row 2 or after last row
        except Exception as e:
            print(f"⚠️ Could not read existing data, starting at row 2: {e}")
            start_row = 2

        # Calculate ranges based on start_row
        range_name1 = f"'{target_tab}'!A{start_row}:G{start_row + len(rows_with_customer) - 1}"
        body1 = {'values': rows_with_customer}
        start_row2 = start_row + len(rows_with_customer) + 1
        label_text = "TASKS WITHOUT PIPE DELIMITER"
        label_row = [[label_text] + ["" for _ in range(6)]]
        range_label = f"'{target_tab}'!A{start_row2}:G{start_row2}"
        range_name2 = f"'{target_tab}'!A{start_row2+1}:G{start_row2+len(rows_without_pipe)}"
        body2 = {'values': rows_without_pipe}
        try:
            print(f"Writing {len(rows_with_customer)-1} tasks with customer to {range_name1}")
            sheets_service.service.spreadsheets().values().update(
                spreadsheetId=test_spreadsheet_id,
                range=range_name1,
                valueInputOption='RAW',
                body=body1
            ).execute()
            print(f"Writing label row to {range_label}")
            sheets_service.service.spreadsheets().values().update(
                spreadsheetId=test_spreadsheet_id,
                range=range_label,
                valueInputOption='RAW',
                body={'values': label_row}
            ).execute()
            print(f"Writing {len(rows_without_pipe)-1} tasks without pipe to {range_name2}")
            sheets_service.service.spreadsheets().values().update(
                spreadsheetId=test_spreadsheet_id,
                range=range_name2,
                valueInputOption='RAW',
                body=body2
            ).execute()
            print(f"✅ Wrote {len(rows_with_customer)-1} tasks with customer and {len(rows_without_pipe)-1} tasks without pipe to tab: {target_tab}")
        except Exception as e:
            print(f"❌ Error writing to tab {target_tab}: {e}")
    def __init__(self):
        self.api_token = os.getenv('CLICKUP_API_TOKEN')
        self.team_id = os.getenv('CLICKUP_TEAM_ID')
        self.base_url = 'https://api.clickup.com/api/v2'
        
        self.headers = {
            'Authorization': self.api_token,
            'Content-Type': 'application/json'
        }
        
        # Define boards - Issues go to production, Features go to Project Summary
        self.issue_boards = {
            'Client Issues (External)': '75793048',
            'Issues (Internal)': '901103923965'
        }
        
        self.feature_boards = {
            'Feature Requests': '901110903380'  # From the li/ URL
        }

    def extract_customer_name(self, task_name):
        """Extracts the customer name from a task name using the convention: 'Customer Name' | Short Description, or Customer Name | Short Description (no quotes)."""
        import re
        # Try quoted first
        match = re.match(r'"([^"]+)"\s*\|', task_name)
        if match:
            return match.group(1).strip()
        # Fallback: unquoted, take everything before the first pipe
        match = re.match(r'([^|]+)\s*\|', task_name)
        if match:
            return match.group(1).strip()
        return None

    def get_customer_tab_name(self, customer_name):
        """Returns a valid tab name for the customer, or None if not found."""
        if not customer_name:
            return None
        # Google Sheets tab name limit is 100 chars, but keep it short for clarity
        return customer_name[:30]
    
    def test_connection(self):
        """Test the ClickUp API connection"""
        try:
            url = f"{self.base_url}/team"
            print(f"🔗 Testing connection to: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print("✅ ClickUp API connection successful!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ ClickUp API connection failed: {e}")
            return False
    
    def get_tasks_from_list(self, list_id, list_name="Unknown"):
        """Get tasks from a specific ClickUp list"""
        try:
            url = f"{self.base_url}/list/{list_id}/task"
            print(f"📋 Fetching tasks from {list_name} (ID: {list_id})...")
            
            params = {
                'archived': 'false',
                'include_closed': 'true'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            tasks = response.json().get('tasks', [])
            print(f"✅ Found {len(tasks)} tasks in {list_name}")
            
            # Add board context to each task
            for task in tasks:
                task['board_name'] = list_name
                task['board_id'] = list_id
            
            return tasks
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching tasks from {list_name}: {e}")
            return []
    
    def get_issue_tasks(self):
        """Get tasks from issue boards (External + Internal) for production tab"""
        all_issues = []
        
        print("\n🚀 Fetching ISSUE tasks for production tab...")
        
        for board_name, list_id in self.issue_boards.items():
            tasks = self.get_tasks_from_list(list_id, board_name)
            all_issues.extend(tasks)
        
        print(f"📊 Total issue tasks: {len(all_issues)}")
        return all_issues
    
    def get_feature_tasks(self):
        """Get tasks from feature boards for Project Summary tab"""
        all_features = []
        
        print("\n🚀 Fetching FEATURE tasks for Project Summary tab...")
        
        for board_name, list_id in self.feature_boards.items():
            tasks = self.get_tasks_from_list(list_id, board_name)
            all_features.extend(tasks)
        
        print(f"📊 Total feature tasks: {len(all_features)}")
        return all_features
    
    def export_issues_to_production(self):
        """Export issue tasks to production tab - add new rows only, don't clear existing data"""
        try:
            from sheets_service import GoogleSheetsService
            
            print("\n🔄 Exporting ISSUES to production tab...")
            
            tasks = self.get_issue_tasks()
            
            if not tasks:
                print("❌ No issue tasks found")
                return False
            
            sheets_service = GoogleSheetsService()
            target_tab = "production"
            
            # Check if data already exists
            try:
                existing_range = f"'{target_tab}'!A1:E1000"  # Check existing data
                existing_result = sheets_service.service.spreadsheets().values().get(
                    spreadsheetId=sheets_service.SPREADSHEET_ID,
                    range=existing_range
                ).execute()
                
                existing_values = existing_result.get('values', [])
                
                # Find the last row with data
                last_row = 0
                for i, row in enumerate(existing_values):
                    if any(cell.strip() for cell in row if cell):  # If any cell has content
                        last_row = i + 1
                
                # If no data exists, start at row 1 with headers
                if last_row == 0:
                    start_row = 1
                    include_headers = True
                else:
                    # Data exists, start after last row
                    start_row = last_row + 1
                    include_headers = False
                    
            except Exception as e:
                print(f"⚠️ Could not read existing data, starting at row 1: {e}")
                start_row = 1
                include_headers = True
            
            # Prepare data rows
            rows = []
            
            # Add headers only if no data exists
            if include_headers:
                headers = ['Ticket ID/Link', 'Subject', 'Severity', 'Status', 'Ticket Filed By']
                rows.append(headers)
            
            for task in tasks:
                # Get priority as-is from ClickUp
                priority = task.get('priority', {})
                severity = priority.get('priority', 'normal') if priority else 'normal'
                
                # Get status as-is from ClickUp
                status = task.get('status', {})
                current_status = status.get('status', 'Unknown') if status else 'Unknown'
                
                # Get filer email from custom fields
                filer_email = ""
                custom_fields = task.get('custom_fields', [])
                for field in custom_fields:
                    if field.get('name') == 'Work email address?':
                        filer_email = field.get('value', '')
                        break
                
                # If email is empty or None, use "Not Available"
                if not filer_email or filer_email.strip() == "":
                    filer_email = "Not Available"
                
                data_row = [
                    task.get('url', ''),              # A: Ticket ID/Link
                    task.get('name', 'No Title'),     # B: Subject
                    severity,                         # C: Severity
                    current_status,                   # D: Status  
                    filer_email                       # E: Ticket Filed By
                ]
                
                rows.append(data_row)
            
            # Write new data - only 5 columns (A-E)
            body = {'values': rows}
            range_name = f"'{target_tab}'!A{start_row}:E{start_row + len(rows) - 1}"
            
            # NO CLEARING - just write new data
            result = sheets_service.service.spreadsheets().values().update(
                spreadsheetId=sheets_service.SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ SUCCESS! Added {len(rows)} rows to production tab starting at row {start_row}")
            print(f"📊 Range used: {range_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting issues: {e}")
            return False
        
    def export_features_to_project_summary(self):
        """Export feature requests to Project Summary tab - write only if no data exists"""
        try:
            from sheets_service import GoogleSheetsService
            
            print("\n🔄 Exporting FEATURES to Project Summary tab...")
            
            tasks = self.get_feature_tasks()
            
            if not tasks:
                print("❌ No feature tasks found")
                return False
            
            sheets_service = GoogleSheetsService()
            target_tab = "Project Summary"
            
            # Check if data already exists in the table section
            try:
                existing_range = f"'{target_tab}'!A15:E15"  # Check first data row
                existing_result = sheets_service.service.spreadsheets().values().get(
                    spreadsheetId=sheets_service.SPREADSHEET_ID,
                    range=existing_range
                ).execute()
                
                existing_values = existing_result.get('values', [])
                
                # If data exists, don't write anything
                if existing_values and any(cell.strip() for row in existing_values for cell in row if cell):
                    print("✅ Data already exists in Project Summary - leaving as is")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Could not check existing data: {e}")
            
            # No data exists, write new data
            headers = ['Type of Request', 'Summary / Requirements', 'Notes/Next Steps', 'Status', 'Owner/Group']
            rows = [headers]
            
            for task in tasks:
                # Get status as-is from ClickUp
                status = task.get('status', {})
                current_status = status.get('status', 'Unknown') if status else 'Unknown'
                
                # Get assignees for Owner/Group
                assignees = task.get('assignees', [])
                owner = assignees[0].get('username', '') if assignees else ''
                
                data_row = [
                    'Feature Request',  # Type of Request
                    task.get('name', 'No Title'),  # Summary / Requirements
                    '',  # Notes/Next Steps (blank for now)
                    current_status,  # Status
                    owner  # Owner/Group
                ]
                
                rows.append(data_row)
            
            # Write to Project Summary tab starting at row 14
            body = {'values': rows}
            range_name = f"'{target_tab}'!A14:E{13 + len(rows)}"
            
            result = sheets_service.service.spreadsheets().values().update(
                spreadsheetId=sheets_service.SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ SUCCESS! Wrote {len(rows)-1} feature tasks to Project Summary tab")
            return True
            
        except Exception as e:
            print(f"❌ Error exporting features: {e}")
            return False
    
    def export_all(self):
        """Export both issues and features to their respective tabs"""
        issues_success = self.export_issues_to_production()
        features_success = self.export_features_to_project_summary()
        
        return issues_success and features_success

    def export_all_clients_to_spreadsheets(self):
        """Export all tasks for each client to their specific spreadsheet, using the efficient last-row logic."""
        for client_name, spreadsheet_id in self.CLIENT_SPREADSHEET_IDS.items():
            print(f"\n{'='*60}\nExporting for client: {client_name}\n{'='*60}")
            try:
                self.export_single_client_to_spreadsheet(client_name)
            except Exception as e:
                print(f"❌ Error exporting for {client_name}: {e}")


if __name__ == "__main__":
    import sys
    service = ClickUpService()
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'dirtvision':
        # Only export for Dirt Vision
        if service.test_connection():
            print("\n" + "="*60)
            print("🎯 CLICKUP TRACKER - DIRT VISION ONLY")
            print("="*60)
            service.export_single_client_to_spreadsheet('Dirt Vision')
            print("\n🎉 Dirt Vision export complete!")
    elif len(sys.argv) > 1 and sys.argv[1].lower() == 'allclients':
        # Export for all mapped clients
        if service.test_connection():
            print("\n" + "="*60)
            print("🎯 CLICKUP TRACKER - ALL CLIENTS")
            print("="*60)
            service.export_all_clients_to_spreadsheets()
            print("\n🎉 All client exports complete!")
    else:
        if service.test_connection():
            print("\n" + "="*60)
            print("🎯 CLICKUP TRACKER - ISSUES & FEATURES")
            print("="*60)
            # Export both types
            service.export_all()
            print("\n🎉 Export complete!")
            print("📋 Available commands:")
            print("  - service.export_issues_to_production() - Export issues only")
            print("  - service.export_features_to_project_summary() - Export features only")
            print("  - service.export_all() - Export both")
            print("  - python src/clickup_service.py dirtvision   # Export only Dirt Vision")
            print("  - python src/clickup_service.py allclients   # Export all mapped clients")