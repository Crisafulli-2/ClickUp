import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class GoogleSheetsService:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SPREADSHEET_ID = '13raU31sm8wDz1xCQ5WpmHPbmlYgxRok1OLaH1uvJgPo'
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Simple authentication with Google Sheets API"""
        creds = None
        
        # Try multiple paths for credentials
        possible_paths = [
            'credentials.json',           # Same directory as script
            '../credentials.json',        # Parent directory  
            '../../credentials.json'      # Two levels up
        ]
        
        creds_path = None
        token_path = None
        
        # Find the credentials file
        for path in possible_paths:
            if os.path.exists(path):
                creds_path = path
                # Set token path in same directory as credentials
                token_path = path.replace('credentials.json', 'token.json')
                break
        
        if not creds_path:
            raise FileNotFoundError("credentials.json not found in any expected location")
        
        print(f"🔑 Using credentials from: {creds_path}")
        
        # Check if we have saved credentials
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next time
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('sheets', 'v4', credentials=creds)
    
    def get_sheet_tabs(self):
        """Get all tab names in the spreadsheet"""
        try:
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.SPREADSHEET_ID
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            tab_names = []
            
            print("📋 Available tabs in the spreadsheet:")
            for sheet in sheets:
                properties = sheet.get('properties', {})
                title = properties.get('title', 'Unknown')
                sheet_id = properties.get('sheetId', 'Unknown')
                print(f"  - Tab: '{title}' (ID: {sheet_id})")
                tab_names.append(title)
            
            return tab_names
            
        except Exception as e:
            print(f"❌ Error getting sheet tabs: {e}")
            return []
    
    def write_test_data(self, formatted_data):
        """Write test data to the correct tab"""
        try:
            print("📊 Getting available tabs...")
            tab_names = self.get_sheet_tabs()
            
            if not tab_names:
                print("❌ No tabs found")
                return False
            
            # Use the first tab or look for specific tab
            target_tab = tab_names[0]  # Default to first tab
            
            # Look for common names
            for tab in tab_names:
                if 'production' in tab.lower() or 'tracker' in tab.lower():
                    target_tab = tab
                    break
            
            print(f"📊 Writing test data to tab: '{target_tab}'")
            
            # Headers
            headers = ['Ticket ID', 'Subject', 'Severity', 'Status', 'Filer Email']
            
            # Test data - just first 5 tasks
            rows = [headers]
            for task in formatted_data[:5]:
                row = [
                    task.get('Ticket ID', ''),
                    task.get('Subject', ''),
                    task.get('Severity', ''),
                    task.get('Status', ''),
                    task.get('Filer Email', '')
                ]
                rows.append(row)
            
            # Write to the correct tab
            body = {'values': rows}
            range_name = f"'{target_tab}'!A1:E{len(rows)}"
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.SPREADSHEET_ID,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Successfully wrote {len(rows)} rows to '{target_tab}' tab")
            print(f"📊 Range used: {range_name}")
            print(f"📊 Updated {result.get('updatedCells')} cells")
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False