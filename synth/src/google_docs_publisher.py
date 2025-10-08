"""
Google Docs Publisher - creates/updates Google Docs with synthesized content.
Reuses existing Google authentication from sheets_service.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add repo root to path to import existing services
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, repo_root)

from utils.markdown_to_gdoc import markdown_to_gdoc_structure


def upsert_google_doc(
    config: Dict[str, Any],
    result: Dict[str, Any],
) -> str:
    """
    Create or update a Google Doc with synthesis results.
    
    Args:
        config: Google Doc config section from config.yaml
        result: Synthesis result dict with keys: markdown, actions, sentiment_summary, metadata
    
    Returns:
        Google Doc URL
    
    TODO: Implement Google Docs API integration
    - Reuse Google auth from src/sheets_service.py (credentials.json from repo root)
    - Add 'https://www.googleapis.com/auth/documents' and 'drive' scopes
    - Check if doc already exists by title (in parent folder)
    - If exists: update content; if not: create new
    - Convert markdown to Google Docs structure using markdown_to_gdoc.py
    - Set sharing permissions based on config.link_share
    """
    
    if not config.get("enabled", True):
        print("⏭️  Google Doc publishing is disabled")
        return ""
    
    print("📄 Publishing to Google Docs...")
    
    # Extract config
    parent_drive_id = config.get("parent_drive_id", "REPLACE_ME")
    title_format = config.get("title_format", "Weekly Info Synthesis — {project} — {date}")
    link_share = config.get("link_share", "domain")
    
    # Build title
    project = result["metadata"].get("project_name", "Project")
    date_str = datetime.now().strftime("%Y-%m-%d")
    title = title_format.format(project=project, date=date_str)
    
    print(f"   Title: {title}")
    print(f"   Parent folder ID: {parent_drive_id}")
    
    # Convert markdown to Google Docs structure
    markdown = result["markdown"]
    doc_structure = markdown_to_gdoc_structure(markdown)
    
    # TODO: Implement actual Google Docs API calls
    print("   TODO: Authenticate with Google Docs API (reuse sheets_service auth)")
    print("   TODO: Search for existing doc by title in parent folder")
    print("   TODO: Create or update doc with structured content")
    print("   TODO: Set sharing permissions")
    
    # Stub: return fake URL
    doc_url = f"https://docs.google.com/document/d/PLACEHOLDER_{title.replace(' ', '_')}/edit"
    print(f"   ✅ (Stub) Google Doc: {doc_url}")
    
    return doc_url


def _get_google_docs_service():
    """
    Get authenticated Google Docs service.
    Reuses authentication pattern from sheets_service.
    
    TODO: Implement Google Docs service
    - Import from google.oauth2.credentials import Credentials
    - Import from googleapiclient.discovery import build
    - Reuse token.json and credentials.json from repo root
    - Add scopes: ['docs', 'drive'] in addition to sheets
    - Return service object: build('docs', 'v1', credentials=creds)
    """
    pass


def _find_doc_by_title(service, title: str, parent_folder_id: str) -> Optional[str]:
    """
    Find a Google Doc by title in a specific folder.
    
    Args:
        service: Google Drive service
        title: Doc title to search for
        parent_folder_id: Parent folder ID
    
    Returns:
        Document ID if found, None otherwise
    
    TODO: Implement Drive API search
    - Use Drive API files.list with query
    - Query: name='<title>' and '<parent_folder_id>' in parents and mimeType='application/vnd.google-apps.document'
    """
    pass


def _create_google_doc(
    service,
    title: str,
    parent_folder_id: str,
    doc_structure: Dict[str, Any],
) -> str:
    """
    Create a new Google Doc.
    
    Args:
        service: Google Docs service
        title: Document title
        parent_folder_id: Parent folder ID
        doc_structure: Structured content (from markdown_to_gdoc)
    
    Returns:
        Document ID
    
    TODO: Implement Docs API creation
    - Use documents.create() with title
    - Use documents.batchUpdate() to add content
    - Move to folder using Drive API
    """
    pass


def _update_google_doc(
    service,
    doc_id: str,
    doc_structure: Dict[str, Any],
) -> None:
    """
    Update an existing Google Doc.
    
    Args:
        service: Google Docs service
        doc_id: Document ID
        doc_structure: Structured content (from markdown_to_gdoc)
    
    TODO: Implement Docs API update
    - Clear existing content (deleteContentRange)
    - Insert new content (batchUpdate)
    """
    pass


def _set_doc_permissions(service, doc_id: str, link_share: str) -> None:
    """
    Set document sharing permissions.
    
    Args:
        service: Google Drive service
        doc_id: Document ID
        link_share: Sharing level (anyone | domain | restricted)
    
    TODO: Implement Drive API permissions
    - Use permissions.create() to set sharing
    - Map link_share to Google Drive permission types
    """
    pass

