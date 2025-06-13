import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClickUpService:
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


if __name__ == "__main__":
    service = ClickUpService()
    
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