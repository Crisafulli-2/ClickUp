"""
Slack Adapter - fetches Slack threads and messages.
Supports multiple modes: api | digest | dropbox | hybrid
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


def fetch_threads(
    channels: List[str],
    lookback_days: int,
    mode: str = "hybrid",
    include_threads: bool = True,
    include_pins: bool = True,
    include_reactions: bool = True,
    config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch Slack messages and threads from specified channels.
    
    Args:
        channels: List of channel names or IDs
        lookback_days: Number of days to look back
        mode: "api" | "digest" | "dropbox" | "hybrid"
        include_threads: Include threaded replies
        include_pins: Include pinned messages
        include_reactions: Include reaction metadata
        config: Optional config dict for credentials
    
    Returns:
        List of Slack message dicts (SourceBlob-compatible)
    
    TODO: Implement each mode:
    - api: Use slack_sdk to fetch via Slack API (requires SLACK_BOT_TOKEN in .env)
    - digest: Parse email digests from Gmail (if user has Slack digest emails)
    - dropbox: Read from Slack export files in Dropbox (if user has exports)
    - hybrid: Try api first, fallback to digest or dropbox
    """
    
    print(f"🔔 Fetching Slack threads (mode: {mode}, lookback: {lookback_days} days)")
    print(f"   Channels: {', '.join(channels)}")
    print(f"   Options: threads={include_threads}, pins={include_pins}, reactions={include_reactions}")
    
    if mode == "api":
        return _fetch_via_api(channels, lookback_days, include_threads, include_pins, include_reactions, config)
    elif mode == "digest":
        return _fetch_via_digest(channels, lookback_days, config)
    elif mode == "dropbox":
        return _fetch_via_dropbox(channels, lookback_days, config)
    elif mode == "hybrid":
        try:
            return _fetch_via_api(channels, lookback_days, include_threads, include_pins, include_reactions, config)
        except Exception as e:
            print(f"⚠️ API mode failed: {e}, trying digest...")
            try:
                return _fetch_via_digest(channels, lookback_days, config)
            except Exception as e2:
                print(f"⚠️ Digest mode failed: {e2}, trying dropbox...")
                return _fetch_via_dropbox(channels, lookback_days, config)
    else:
        raise ValueError(f"Unknown Slack mode: {mode}")


def _fetch_via_api(
    channels: List[str],
    lookback_days: int,
    include_threads: bool,
    include_pins: bool,
    include_reactions: bool,
    config: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Fetch via Slack API.
    
    TODO: Implement with slack_sdk
    - from slack_sdk import WebClient
    - Read SLACK_BOT_TOKEN from repo root .env
    - Use conversations.history for each channel
    - Use conversations.replies for threads if include_threads
    - Filter by oldest timestamp (lookback_days)
    - Include pins.list if include_pins
    """
    print("TODO: Implement Slack API fetching with slack_sdk")
    print("      Need SLACK_BOT_TOKEN in .env")
    
    # Stub: return empty list
    return []


def _fetch_via_digest(
    channels: List[str],
    lookback_days: int,
    config: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Fetch via email digests.
    
    TODO: Implement digest parsing
    - Use Gmail API to fetch Slack digest emails
    - Parse HTML/text to extract message summaries
    - Match channels from config
    """
    print("TODO: Implement Slack digest email parsing")
    return []


def _fetch_via_dropbox(
    channels: List[str],
    lookback_days: int,
    config: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Fetch from Slack export in Dropbox.
    
    TODO: Implement Dropbox export reading
    - Use Dropbox API to access Slack export JSON files
    - Parse channel JSON files
    - Filter by date range
    """
    print("TODO: Implement Slack Dropbox export reading")
    return []

