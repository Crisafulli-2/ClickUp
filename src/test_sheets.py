import sys
import os
sys.path.append('src')

from sheets_service import GoogleSheetsService

# Simple test data
test_data = [
    {
        'Ticket ID': 'TEST001',
        'Subject': 'Test Subject',
        'Severity': 'High',
        'Status': 'Open',
        'Filer Email': 'test@example.com'
    }
]

print("🧪 Testing Google Sheets connection...")
try:
    sheets_service = GoogleSheetsService()
    result = sheets_service.write_test_data(test_data)
    print(f"Result: {result}")
except Exception as e:
    print(f"❌ Error during test: {e}")