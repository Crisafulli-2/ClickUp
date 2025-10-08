#!/usr/bin/env python3
"""
Info Synthesizer Runner - main orchestrator.
Gathers sources, normalizes, synthesizes, and publishes to Google Docs and/or ClickUp Docs.
"""

import os
import sys
import argparse
import yaml
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, repo_root)

# Load .env from repo root
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(repo_root, ".env"))

# Import synth modules
from normalizer import normalize_sources, SourceBlob
from synthesizer import synthesize
from sentiment_provider import annotate_sentiment
from slack_adapter import fetch_threads
from google_docs_publisher import upsert_google_doc
from clickup_docs_publisher import upsert_clickup_doc


def main():
    """Main entry point for the Info Synthesizer."""
    parser = argparse.ArgumentParser(description="Info Synthesizer - Provider-agnostic synthesis tool")
    parser.add_argument(
        "--config",
        type=str,
        default="synth/config/config.yaml",
        help="Path to config.yaml file",
    )
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Generate run ID
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\n" + "="*70)
    print("🔮 INFO SYNTHESIZER")
    print("="*70)
    print(f"Run ID: {run_id}")
    print(f"Project: {config.get('project_name', 'Unknown')}")
    print(f"Config: {args.config}")
    print("="*70 + "\n")
    
    # Step 1: Determine period
    period_start, period_end = calculate_period(config.get("period", {}))
    print(f"📅 Period: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}")
    print()
    
    # Step 2: Gather sources
    print("📥 Gathering sources...")
    sources = gather_sources(config, period_start, period_end)
    print(f"   Collected {len(sources)} total sources")
    print()
    
    # Step 3: Normalize sources
    print("🔄 Normalizing sources...")
    # Sources are already normalized in gather_sources
    print(f"   {len(sources)} sources normalized")
    print()
    
    # Step 4: Optional sentiment analysis
    if config.get("synthesis", {}).get("sentiment", {}).get("enabled", False):
        print("💭 Analyzing sentiment...")
        sources = annotate_sentiment(sources, config)
        print(f"   Sentiment added to {len(sources)} sources")
        print()
    
    # Step 5: Synthesize
    print("⚗️  Synthesizing brief...")
    result = synthesize(sources, config, period_start, period_end)
    result["metadata"]["run_id"] = run_id
    result["metadata"]["project_name"] = config.get("project_name", "Project")
    print(f"   Generated {len(result['markdown'])} characters of content")
    print(f"   Extracted {len(result['actions'])} action items")
    print()
    
    # Step 6: Publish
    print("📤 Publishing...")
    links = {}
    
    # Publish to Google Docs
    publish_config = config.get("publish", {})
    if publish_config.get("google_doc", {}).get("enabled", False):
        gdoc_link = upsert_google_doc(publish_config.get("google_doc", {}), result)
        links["google_doc"] = gdoc_link
    
    # Publish to ClickUp Docs
    if publish_config.get("clickup_doc", {}).get("enabled", False):
        clickup_link = upsert_clickup_doc(publish_config.get("clickup_doc", {}), result)
        links["clickup_doc"] = clickup_link
    
    print()
    
    # Step 7: Output summary
    summary = {
        "run_id": run_id,
        "links": links,
        "actions_count": len(result["actions"]),
        "sentiment": result["sentiment_summary"],
        "sources_count": len(sources),
        "period": {
            "start": period_start.isoformat(),
            "end": period_end.isoformat(),
        },
    }
    
    print("="*70)
    print("✅ SYNTHESIS COMPLETE")
    print("="*70)
    print(json.dumps(summary, indent=2))
    print("="*70 + "\n")


def load_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    return config


def calculate_period(period_config: Dict[str, Any]) -> tuple:
    """
    Calculate period start and end dates.
    
    Args:
        period_config: Period section from config.yaml
    
    Returns:
        (start_date, end_date) tuple
    """
    mode = period_config.get("mode", "rolling")
    
    if mode == "rolling":
        days = period_config.get("days", 7)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
    elif mode == "fixed":
        start_date = datetime.fromisoformat(period_config["start_date"])
        end_date = datetime.fromisoformat(period_config["end_date"])
    else:
        raise ValueError(f"Unknown period mode: {mode}")
    
    return start_date, end_date


def gather_sources(
    config: Dict[str, Any],
    period_start: datetime,
    period_end: datetime,
) -> List[SourceBlob]:
    """
    Gather and normalize sources from all configured inputs.
    
    Args:
        config: Full configuration dict
        period_start: Start of reporting period
        period_end: End of reporting period
    
    Returns:
        List of normalized SourceBlobs
    """
    sources = []
    inputs_config = config.get("inputs", {})
    
    # ClickUp tasks
    if inputs_config.get("clickup", {}).get("enabled", False):
        print("   Fetching ClickUp tasks...")
        clickup_sources = fetch_clickup_tasks(inputs_config.get("clickup", {}), period_start, period_end)
        sources.extend(clickup_sources)
        print(f"      ✓ {len(clickup_sources)} ClickUp tasks")
    
    # Slack threads
    if inputs_config.get("slack", {}).get("enabled", False):
        print("   Fetching Slack threads...")
        slack_config = inputs_config.get("slack", {})
        slack_messages = fetch_threads(
            channels=slack_config.get("channels", []),
            lookback_days=slack_config.get("lookback_days", 7),
            mode=slack_config.get("mode", "hybrid"),
            include_threads=slack_config.get("include_threads", True),
            include_pins=slack_config.get("include_pins", True),
            include_reactions=slack_config.get("include_reactions", True),
            config=config,
        )
        if slack_messages:
            slack_sources = normalize_sources(slack_messages, "slack")
            sources.extend(slack_sources)
            print(f"      ✓ {len(slack_sources)} Slack messages")
        else:
            print(f"      ⚠️  No Slack messages (stub mode)")
    
    # TODO: Add Gmail, Calendar, Docs sources when implemented
    
    return sources


def fetch_clickup_tasks(
    clickup_config: Dict[str, Any],
    period_start: datetime,
    period_end: datetime,
) -> List[SourceBlob]:
    """
    Fetch ClickUp tasks and normalize them.
    
    Args:
        clickup_config: ClickUp section from config.yaml
        period_start: Start of reporting period
        period_end: End of reporting period
    
    Returns:
        List of normalized SourceBlobs
    
    TODO: Implement ClickUp task fetching
    - Import src/clickup_service.py
    - Call get_tasks_from_list with list_id from config
    - Optionally fetch comments and descriptions based on config flags
    - Filter by date range (period_start to period_end)
    - Normalize using normalize_clickup_task
    """
    list_id = clickup_config.get("list_id", "REPLACE_ME")
    
    if list_id == "REPLACE_ME":
        print("      ⚠️  ClickUp list_id not configured, using placeholder data")
        # Return placeholder data for demo
        return [
            SourceBlob(
                source_type="clickup",
                source_id="placeholder_1",
                timestamp=datetime.now(),
                content="**Placeholder Task 1**\n\nThis is a placeholder task for demo purposes.",
                metadata={"status": "in progress", "priority": "normal"},
                url="https://app.clickup.com/t/placeholder_1",
            ),
            SourceBlob(
                source_type="clickup",
                source_id="placeholder_2",
                timestamp=datetime.now(),
                content="**Placeholder Task 2**\n\nAnother placeholder task.",
                metadata={"status": "open", "priority": "high"},
                url="https://app.clickup.com/t/placeholder_2",
            ),
        ]
    
    # TODO: Implement real ClickUp fetching
    print("      TODO: Implement ClickUp task fetching from clickup_service")
    return []


if __name__ == "__main__":
    main()

