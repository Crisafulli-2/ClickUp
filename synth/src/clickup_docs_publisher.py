"""
ClickUp Docs Publisher - creates/updates ClickUp Docs with synthesized content.
Reuses existing ClickUp authentication from clickup_service.
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Add repo root to path to import existing services
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, repo_root)


def upsert_clickup_doc(
    config: Dict[str, Any],
    result: Dict[str, Any],
) -> str:
    """
    Create or update a ClickUp Doc with synthesis results.
    
    Args:
        config: ClickUp Doc config section from config.yaml
        result: Synthesis result dict with keys: markdown, actions, sentiment_summary, metadata
    
    Returns:
        ClickUp Doc URL
    
    TODO: Implement ClickUp Docs API integration
    - Reuse ClickUp API token from .env (via clickup_service)
    - Use ClickUp Docs API v2: https://clickup.com/api/clickupreference/operation/CreateDocs/
    - Upsert by deterministic title (search first, create if not found)
    - Format markdown content for ClickUp (supports Markdown)
    """
    
    if not config.get("enabled", True):
        print("⏭️  ClickUp Doc publishing is disabled")
        return ""
    
    print("📋 Publishing to ClickUp Docs...")
    
    # Extract config
    parent_type = config.get("parent_type", "folder")  # folder | list | space
    parent_id = config.get("parent_id", "REPLACE_ME")
    title_format = config.get("title_format", "Weekly Info Synthesis — {project} — {date}")
    
    # Build title
    project = result["metadata"].get("project_name", "Project")
    date_str = datetime.now().strftime("%Y-%m-%d")
    title = title_format.format(project=project, date=date_str)
    
    print(f"   Title: {title}")
    print(f"   Parent {parent_type} ID: {parent_id}")
    
    # Get markdown content
    markdown = result["markdown"]
    
    # TODO: Implement actual ClickUp Docs API calls
    print("   TODO: Import clickup_service to get API token and headers")
    print("   TODO: Search for existing doc by title")
    print("   TODO: Create or update doc with markdown content")
    
    # Stub: return fake URL
    doc_url = f"https://app.clickup.com/doc/PLACEHOLDER_{title.replace(' ', '_')}"
    print(f"   ✅ (Stub) ClickUp Doc: {doc_url}")
    
    return doc_url


def _get_clickup_client():
    """
    Get ClickUp API client (reuse from clickup_service).
    
    TODO: Import and instantiate ClickUpService
    - from src.clickup_service import ClickUpService
    - Return client instance with auth headers
    """
    pass


def _find_clickup_doc_by_title(
    client,
    workspace_id: str,
    title: str,
) -> Optional[str]:
    """
    Find a ClickUp Doc by title in workspace.
    
    Args:
        client: ClickUp client
        workspace_id: Workspace ID
        title: Doc title to search for
    
    Returns:
        Document ID if found, None otherwise
    
    TODO: Implement ClickUp Docs search
    - Use GET /api/v2/team/{team_id}/docs endpoint
    - Filter by title match
    """
    pass


def _create_clickup_doc(
    client,
    parent_type: str,
    parent_id: str,
    title: str,
    content: str,
) -> str:
    """
    Create a new ClickUp Doc.
    
    Args:
        client: ClickUp client
        parent_type: Parent type (folder | list | space)
        parent_id: Parent ID
        title: Document title
        content: Markdown content
    
    Returns:
        Document ID
    
    TODO: Implement ClickUp Docs creation
    - POST /api/v2/{parent_type}/{parent_id}/docs
    - Body: {name: title, content: content, format: "markdown"}
    """
    pass


def _update_clickup_doc(
    client,
    doc_id: str,
    content: str,
) -> None:
    """
    Update an existing ClickUp Doc.
    
    Args:
        client: ClickUp client
        doc_id: Document ID
        content: Markdown content
    
    TODO: Implement ClickUp Docs update
    - PUT /api/v2/docs/{doc_id}
    - Body: {content: content, format: "markdown"}
    """
    pass

