# Test querying ClickUp API and printing raw data for inspection

# Ensure src is in the Python path for imports
import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from clickup_service import ClickUpService

def test_clickup_api_raw_query():
    """Query ClickUp API and print raw data for inspection."""
    service = ClickUpService()
    # Use one of the issue boards for a sample query
    for board_name, list_id in service.issue_boards.items():
        print(f"\nQuerying board: {board_name} (ID: {list_id})")
        tasks = service.get_tasks_from_list(list_id, board_name)
        print(f"Returned {len(tasks)} tasks.")
        if tasks:
            print("Sample task:")
            import json
            print(json.dumps(tasks[0], indent=2))
        else:
            print("No tasks returned.")
        # Only query one board for brevity
        break
