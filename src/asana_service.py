import requests
import os
from dotenv import load_dotenv

load_dotenv()

class AsanaService:
    def __init__(self):
        self.api_token = os.getenv('ASANA_API_TOKEN')
        self.base_url = 'https://app.asana.com/api/1.0'
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json'
        }
    
    def test_connection(self):
        """Test Asana API connection"""
        try:
            response = requests.get(f'{self.base_url}/users/me', headers=self.headers)
            if response.status_code == 200:
                user_data = response.json()
                print("✅ Asana API connection successful!")
                print(f"👤 User: {user_data['data']['name']}")
                return True
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_workspaces(self):
        """Get all workspaces"""
        try:
            response = requests.get(f'{self.base_url}/workspaces', headers=self.headers)
            if response.status_code == 200:
                return response.json()['data']
            return []
        except Exception as e:
            print(f"❌ Error getting workspaces: {e}")
            return []
    
    def get_projects(self, workspace_id):
        """Get all projects in workspace"""
        try:
            response = requests.get(
                f'{self.base_url}/projects',
                headers=self.headers,
                params={'workspace': workspace_id}
            )
            if response.status_code == 200:
                return response.json()['data']
            return []
        except Exception as e:
            print(f"❌ Error getting projects: {e}")
            return []
    
    def get_project_sections(self, project_id):
        """Get all sections/buckets in a project"""
        try:
            response = requests.get(
                f'{self.base_url}/projects/{project_id}/sections',
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()['data']
            return []
        except Exception as e:
            print(f"❌ Error getting sections: {e}")
            return []
    
    def get_tasks_in_section(self, section_id):
        """Get all tasks in a specific section with detailed info"""
        try:
            response = requests.get(
                f'{self.base_url}/tasks',
                headers=self.headers,
                params={
                    'section': section_id,
                    'opt_fields': 'name,completed,assignee.name,assignee.email,created_at,completed_at,notes'
                }
            )
            if response.status_code == 200:
                return response.json()['data']
            return []
        except Exception as e:
            print(f"❌ Error getting tasks: {e}")
            return []
    
    def get_task_comments(self, task_id):
        """Get comments/stories for a specific task"""
        try:
            response = requests.get(
                f'{self.base_url}/tasks/{task_id}/stories',
                headers=self.headers,
                params={
                    'opt_fields': 'text,created_at,created_by.name,type'
                }
            )
            if response.status_code == 200:
                stories = response.json()['data']
                # Filter for actual comments (not system updates)
                comments = [story for story in stories if story.get('type') == 'comment' and story.get('text')]
                return comments
            return []
        except Exception as e:
            print(f"❌ Error getting comments: {e}")
            return []
    
    def get_all_tasks_for_sheets(self, project_id):
        """Get all tasks formatted for Google Sheets export"""
        print("🔄 Fetching all tasks for Google Sheets export...")
        
        sections = self.get_project_sections(project_id)
        all_tasks = []
        
        for section in sections:
            print(f"📋 Processing section: {section['name']}")
            tasks = self.get_tasks_in_section(section['gid'])
            
            for task in tasks:
                # Get the last comment for this task
                comments = self.get_task_comments(task['gid'])
                last_comment = ""
                if comments:
                    # Get the most recent comment
                    last_comment = comments[-1].get('text', '')
                
                # Format task data for sheets
                task_data = {
                    'channel_name': task.get('name', ''),
                    'assigned_to': task.get('assignee', {}).get('name', 'Unassigned') if task.get('assignee') else 'Unassigned',
                    'email': task.get('assignee', {}).get('email', '') if task.get('assignee') else '',
                    'date_created': task.get('created_at', '').split('T')[0] if task.get('created_at') else '',  # Just date part
                    'status': 'Completed' if task.get('completed', False) else 'In Progress',
                    'last_update': last_comment[:500] if last_comment else 'No comments',  # Limit comment length
                    'section': section['name']  # Track which section this came from
                }
                
                all_tasks.append(task_data)
        
        print(f"✅ Found {len(all_tasks)} total tasks across all sections")
        return all_tasks
    
    def export_to_wurl_sheets(self):
        """Export Asana data to Wurl Google Sheets"""
        try:
            # Import the sheets service
            from asana_sheets_service import AsanaSheetsService
            
            print("\n🔄 Exporting Asana data to Wurl Account Tracker...")
            
            # Find the SSAI Dashboard project
            workspaces = self.get_workspaces()
            wurl_workspace = None
            for ws in workspaces:
                if 'wurl.com' in ws['name']:
                    wurl_workspace = ws
                    break
            
            if not wurl_workspace:
                print("❌ Could not find wurl.com workspace")
                return False
            
            projects = self.get_projects(wurl_workspace['gid'])
            ssai_project = None
            for project in projects:
                if 'transmit live ssai' in project['name'].lower() or 'dashboard' in project['name'].lower():
                    ssai_project = project
                    break
            
            if not ssai_project:
                print("❌ Could not find SSAI Dashboard project")
                return False
            
            # Get all tasks
            tasks = self.get_all_tasks_for_sheets(ssai_project['gid'])
            
            if not tasks:
                print("❌ No tasks found")
                return False
            
            # Export to Google Sheets
            sheets_service = AsanaSheetsService()
            return sheets_service.export_asana_data(tasks)
            
        except Exception as e:
            print(f"❌ Error exporting to sheets: {e}")
            return False

if __name__ == "__main__":
    print("🔄 Testing Asana to Wurl Sheets Export...")
    
    asana = AsanaService()
    
    if asana.test_connection():
        success = asana.export_to_wurl_sheets()
        if success:
            print("🎉 Export completed successfully!")
        else:
            print("❌ Export failed")
    else:
        print("❌ Could not connect to Asana API")