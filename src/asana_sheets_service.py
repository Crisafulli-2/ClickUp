import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class AsanaSheetsService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        # Wurl Account Tracker spreadsheet ID
        self.SPREADSHEET_ID = "1xv3wcnaGK9WOEnqh9fuEbJ2YnWUfT9KtlCQxeo9ga1E"
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        creds = None
        
        # Try multiple paths for credentials
        possible_paths = [
            'credentials.json',
            '../credentials.json',
            '../../credentials.json'
        ]
        
        creds_path = None
        token_path = None
        
        for path in possible_paths:
            if os.path.exists(path):
                creds_path = path
                token_path = path.replace('credentials.json', 'token.json')
                break
        
        if not creds_path:
            raise FileNotFoundError("credentials.json not found")
        
        print(f"🔑 Using credentials from: {creds_path}")
        
        # Check for existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('sheets', 'v4', credentials=creds)
    
    def get_sheet_tabs(self):
        """Get all available tabs in the spreadsheet"""
        try:
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.SPREADSHEET_ID).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            tab_names = []
            for sheet in sheets:
                tab_name = sheet['properties']['title']
                tab_names.append(tab_name)
            
            return tab_names
        except Exception as e:
            print(f"❌ Error getting sheet tabs: {e}")
            return []
    
    def create_tab(self, tab_name):
        """Create a new tab in the spreadsheet"""
        try:
            requests = [{
                'addSheet': {
                    'properties': {
                        'title': tab_name
                    }
                }
            }]
            
            body = {'requests': requests}
            response = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.SPREADSHEET_ID,
                body=body
            ).execute()
            
            print(f"✅ Created new tab: '{tab_name}'")
            return True
        except Exception as e:
            print(f"❌ Error creating tab '{tab_name}': {e}")
            return False
    
    def export_asana_data(self, tasks):
        """Export Asana tasks - EACH SECTION GETS ITS OWN TAB"""
        try:
            print(f"📊 Organizing {len(tasks)} tasks by section into separate tabs...")
            
            # Group tasks by section - CRITICAL: Each section = separate tab
            sections = {}
            for task in tasks:
                section_name = task['section']
                if section_name not in sections:
                    sections[section_name] = []
                sections[section_name].append(task)
            
            print(f"\n📋 Will create {len(sections)} separate tabs:")
            for section, task_list in sections.items():
                print(f"   📁 '{section}' → {len(task_list)} tasks ONLY")
            
            # Get existing tabs
            available_tabs = self.get_sheet_tabs()
            
            success_count = 0
            total_sections = len(sections)
            
            # Process EACH section separately - one tab per section
            for section_name, section_tasks in sections.items():
                tab_name = self._clean_tab_name(section_name)
                
                print(f"\n🔄 Creating tab for section: '{section_name}'")
                print(f"📝 Tab name: '{tab_name}'")
                print(f"📊 Tasks in THIS section only: {len(section_tasks)}")
                
                # Create tab if it doesn't exist
                if tab_name not in available_tabs:
                    print(f"⚠️ Creating new tab: '{tab_name}'")
                    if not self.create_tab(tab_name):
                        print(f"❌ Failed to create tab: '{tab_name}'")
                        continue
                    available_tabs.append(tab_name)
                else:
                    print(f"📝 Using existing tab: '{tab_name}'")
                
                # Write ONLY this section's tasks to its tab
                if self.write_section_to_tab(tab_name, section_tasks, section_name):
                    success_count += 1
                    print(f"✅ Successfully wrote {len(section_tasks)} tasks to '{tab_name}' tab")
                else:
                    print(f"❌ Failed to write to '{tab_name}' tab")
            
            # Create a summary tab
            self.create_summary_tab(sections)
            
            print(f"\n🎉 EXPORT COMPLETE!")
            print(f"✅ Successfully created/updated {success_count}/{total_sections} section tabs")
            print(f"📊 Total tasks exported across all tabs: {len(tasks)}")
            print(f"🔗 View at: https://docs.google.com/spreadsheets/d/{self.SPREADSHEET_ID}")
            
            return success_count == total_sections
            
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return False
    
    def write_section_to_tab(self, tab_name, section_tasks, section_name):
        """Write ONLY the tasks from ONE specific section to its dedicated tab"""
        try:
            print(f"📝 Writing {len(section_tasks)} tasks from '{section_name}' to tab '{tab_name}'")
            
            # Prepare data rows - ONLY for this section
            rows = []
            
            # Add section header and info
            rows.append([f"ASANA SECTION: {section_name}"])
            rows.append([f"Tasks in this section: {len(section_tasks)}"])
            rows.append([f"Last Updated: {self._get_current_timestamp()}"])
            rows.append([])  # Empty row for spacing
            
            # Add column headers
            headers = ['Channel Name', 'Assigned To', 'Email', 'Date Created', 'Status', 'Last Update']
            rows.append(headers)
            
            # Add ONLY the tasks from this specific section
            for task in section_tasks:
                # Verify this task belongs to the correct section
                if task['section'] != section_name:
                    print(f"⚠️ Warning: Task '{task['channel_name']}' doesn't belong to section '{section_name}'")
                    continue
                
                data_row = [
                    task['channel_name'],
                    task['assigned_to'], 
                    task['email'],
                    task['date_created'],
                    task['status'],
                    task['last_update']
                ]
                rows.append(data_row)
            
            # Write to sheets - use simple range format
            body = {'values': rows}
            range_name = f"{tab_name}!A1:F{len(rows)}"
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            actual_task_rows = len(rows) - 5  # Subtract header rows
            print(f"✅ Wrote {actual_task_rows} task rows to '{tab_name}' tab (section: {section_name})")
            return True
            
        except Exception as e:
            print(f"❌ Error writing to tab '{tab_name}': {e}")
            return False
    
    def _clean_tab_name(self, section_name):
        """Clean section name to be a valid tab name"""
        # Remove special characters and limit length
        clean_name = section_name.replace(" - ", " ").replace("/", " ").replace("'", "")
        if len(clean_name) > 30:  # Google Sheets tab name limit
            clean_name = clean_name[:27] + "..."
        return clean_name
    
    def _get_current_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def create_summary_tab(self, sections):
        """Create a summary tab with section counts and overview"""
        try:
            summary_tab = "Asana Summary"
            
            # Create summary tab if it doesn't exist
            available_tabs = self.get_sheet_tabs()
            if summary_tab not in available_tabs:
                self.create_tab(summary_tab)
            
            # Prepare summary data
            rows = []
            rows.append(["ASANA DASHBOARD SUMMARY"])
            rows.append([f"Generated: {self._get_current_timestamp()}"])
            rows.append([])
            
            # Section breakdown
            rows.append(["SECTION", "TASKS IN SECTION", "STATUS"])
            rows.append(["=" * 30, "=" * 15, "=" * 20])
            
            total_tasks = 0
            for section_name, tasks in sections.items():
                task_count = len(tasks)
                total_tasks += task_count
                
                # Get status context
                status = self._get_section_status(section_name, task_count)
                
                rows.append([section_name, task_count, status])
            
            rows.append([])
            rows.append(["TOTAL TASKS ACROSS ALL SECTIONS:", total_tasks, ""])
            rows.append([])
            rows.append(["📋 Each section has its own dedicated tab"])
            rows.append(["📊 No section data is mixed with another"])
            
            # Write summary
            body = {'values': rows}
            range_name = f"{summary_tab}!A1:C{len(rows)}"
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Created summary tab with section breakdown")
            
        except Exception as e:
            print(f"❌ Error creating summary: {e}")
    
    def _get_section_status(self, section_name, count):
        """Get status description for section"""
        if count == 0:
            return "Empty Section"
        
        section_lower = section_name.lower()
        if 'live' in section_lower:
            return f"{count} Live Channels"
        elif 'hold' in section_lower:
            return f"{count} On Hold"
        elif 'qa' in section_lower:
            return f"{count} In QA"
        elif 'ready' in section_lower:
            return f"{count} Ready for Handoff"
        elif 'onboard' in section_lower:
            return f"{count} Onboarding"
        elif 'cancel' in section_lower:
            return f"{count} Cancelled"
        elif 'submit' in section_lower:
            return f"{count} Submitted"
        elif 'bootstrap' in section_lower or 'config' in section_lower:
            return f"{count} Configured"
        else:
            return f"{count} Items"