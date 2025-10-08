"""
Normalizer - converts various source formats into a unified SourceBlob structure.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class SourceBlob:
    """Unified data structure for all input sources."""
    
    def __init__(
        self,
        source_type: str,  # clickup | slack | gmail | calendar | docs
        source_id: str,
        timestamp: datetime,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        author: Optional[str] = None,
        url: Optional[str] = None,
    ):
        self.source_type = source_type
        self.source_id = source_id
        self.timestamp = timestamp
        self.content = content
        self.metadata = metadata or {}
        self.author = author
        self.url = url
        self.sentiment = None  # Added by sentiment_provider later
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "metadata": self.metadata,
            "author": self.author,
            "url": self.url,
            "sentiment": self.sentiment,
        }


def normalize_clickup_task(task: Dict[str, Any]) -> SourceBlob:
    """
    Normalize a ClickUp task into a SourceBlob.
    
    Args:
        task: Raw ClickUp task dict from API
    
    Returns:
        SourceBlob with normalized data
    """
    # TODO: Implement proper ClickUp task normalization
    # Expected keys: id, name, description, status, priority, custom_fields, comments, etc.
    
    task_id = task.get("id", "unknown")
    task_name = task.get("name", "Untitled")
    description = task.get("description", "")
    
    # Combine name and description for content
    content = f"**{task_name}**\n\n{description}"
    
    # Parse timestamp
    timestamp = datetime.fromtimestamp(
        int(task.get("date_created", 0)) / 1000
    ) if task.get("date_created") else datetime.now()
    
    metadata = {
        "status": task.get("status", {}).get("status", "Unknown"),
        "priority": task.get("priority", {}).get("priority", "normal"),
        "custom_fields": task.get("custom_fields", []),
        "tags": task.get("tags", []),
    }
    
    return SourceBlob(
        source_type="clickup",
        source_id=task_id,
        timestamp=timestamp,
        content=content,
        metadata=metadata,
        author=None,  # TODO: Extract from assignees
        url=task.get("url"),
    )


def normalize_slack_message(message: Dict[str, Any]) -> SourceBlob:
    """
    Normalize a Slack message into a SourceBlob.
    
    Args:
        message: Raw Slack message dict
    
    Returns:
        SourceBlob with normalized data
    """
    # TODO: Implement Slack message normalization when slack_adapter is ready
    
    msg_id = message.get("ts", "unknown")
    text = message.get("text", "")
    
    timestamp = datetime.fromtimestamp(
        float(message.get("ts", 0))
    ) if message.get("ts") else datetime.now()
    
    metadata = {
        "channel": message.get("channel"),
        "thread_ts": message.get("thread_ts"),
        "reactions": message.get("reactions", []),
    }
    
    return SourceBlob(
        source_type="slack",
        source_id=msg_id,
        timestamp=timestamp,
        content=text,
        metadata=metadata,
        author=message.get("user"),
        url=None,  # TODO: Build Slack permalink
    )


def normalize_sources(sources: List[Dict[str, Any]], source_type: str) -> List[SourceBlob]:
    """
    Batch normalize a list of sources.
    
    Args:
        sources: List of raw source dicts
        source_type: Type of source (clickup | slack | gmail | etc)
    
    Returns:
        List of normalized SourceBlobs
    """
    normalizers = {
        "clickup": normalize_clickup_task,
        "slack": normalize_slack_message,
        # TODO: Add more normalizers as needed
    }
    
    normalizer = normalizers.get(source_type)
    if not normalizer:
        raise ValueError(f"No normalizer found for source_type: {source_type}")
    
    return [normalizer(source) for source in sources]

