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
        
    def get_tasks_from_list(self, list_id):
        """Get tasks from a specific ClickUp list"""
        try:
            url = f"{self.base_url}/list/{list_id}/task"
            print(f"📋 Fetching tasks from list: {list_id}")
            
            params = {
                'archived': 'false',
                'include_closed': 'true'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            tasks = response.json().get('tasks', [])
            print(f"✅ Found {len(tasks)} tasks in list {list_id}")
            return tasks
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching tasks from list {list_id}: {e}")
            return []


if __name__ == "__main__":
    # Quick test
    service = ClickUpService()
    if service.test_connection():
        # Test with Client Issues list
        client_issues_id = os.getenv('CLIENT_ISSUES_LIST_ID')
        service.get_tasks_from_list(client_issues_id)