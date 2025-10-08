"""
Synthesizer - converts normalized sources into a structured markdown brief.
"""

from typing import Dict, List, Any
from datetime import datetime
from normalizer import SourceBlob


def synthesize(
    sources: List[SourceBlob],
    config: Dict[str, Any],
    period_start: datetime,
    period_end: datetime,
) -> Dict[str, Any]:
    """
    Synthesize a structured brief from normalized sources.
    
    Args:
        sources: List of normalized SourceBlobs
        config: Synthesis configuration from config.yaml
        period_start: Start of reporting period
        period_end: End of reporting period
    
    Returns:
        Dict with keys: markdown, actions, sentiment_summary, metadata
    """
    project_name = config.get("project_name", "Project")
    sections = config.get("synthesis", {}).get("sections", [])
    
    # TODO: Implement AI-driven synthesis (Gemini/GPT) or rule-based extraction
    # For now, create a basic structured template with placeholder content
    
    markdown = _build_markdown_template(
        project_name=project_name,
        period_start=period_start,
        period_end=period_end,
        sources=sources,
        sections=sections,
    )
    
    # Extract action items (stub)
    actions = _extract_actions(sources)
    
    # Summarize sentiment (stub)
    sentiment_summary = _summarize_sentiment(sources)
    
    metadata = {
        "sources_count": len(sources),
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "generated_at": datetime.now().isoformat(),
    }
    
    return {
        "markdown": markdown,
        "actions": actions,
        "sentiment_summary": sentiment_summary,
        "metadata": metadata,
    }


def _build_markdown_template(
    project_name: str,
    period_start: datetime,
    period_end: datetime,
    sources: List[SourceBlob],
    sections: List[str],
) -> str:
    """Build markdown document with structured sections."""
    
    date_range = f"{period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}"
    
    md = f"""# Weekly Info Synthesis — {project_name} — {date_range}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
    
    # Add each configured section
    for section in sections:
        md += f"## {section}\n\n"
        
        if section == "Highlights":
            md += _generate_highlights_section(sources)
        elif section == "What's New/Changed":
            md += _generate_whats_new_section(sources)
        elif section == "Decisions":
            md += _generate_decisions_section(sources)
        elif section == "Risks & Blockers":
            md += _generate_risks_section(sources)
        elif section == "Action Items":
            md += _generate_actions_table(sources)
        elif section == "Validation/Release Status":
            md += _generate_validation_section(sources)
        elif section == "Sources":
            md += _generate_sources_section(sources)
        elif section == "Sentiment & Hotspots":
            md += _generate_sentiment_section(sources)
        else:
            md += "_TODO: Content for this section_\n\n"
        
        md += "\n"
    
    return md


def _generate_highlights_section(sources: List[SourceBlob]) -> str:
    """Generate highlights section (stub)."""
    # TODO: Use AI to extract key highlights
    return f"- {len(sources)} total items reviewed this period\n- TODO: AI-extracted highlights\n\n"


def _generate_whats_new_section(sources: List[SourceBlob]) -> str:
    """Generate what's new section (stub)."""
    # TODO: Detect new/changed items
    clickup_sources = [s for s in sources if s.source_type == "clickup"]
    slack_sources = [s for s in sources if s.source_type == "slack"]
    
    content = ""
    if clickup_sources:
        content += f"- {len(clickup_sources)} ClickUp tasks reviewed\n"
    if slack_sources:
        content += f"- {len(slack_sources)} Slack messages reviewed\n"
    content += "- TODO: AI-detected new items and changes\n\n"
    
    return content


def _generate_decisions_section(sources: List[SourceBlob]) -> str:
    """Generate decisions section (stub)."""
    # TODO: Extract decisions from content
    return "- TODO: Extract decisions from discussions\n\n"


def _generate_risks_section(sources: List[SourceBlob]) -> str:
    """Generate risks and blockers section (stub)."""
    # TODO: Use keywords + sentiment to detect risks
    return "- TODO: Detect risks and blockers using keywords and sentiment\n\n"


def _generate_actions_table(sources: List[SourceBlob]) -> str:
    """Generate action items table (stub)."""
    # TODO: Extract action items
    table = """| Action Item | Owner | Due Date | Status |
|------------|-------|----------|--------|
| TODO: Extract action items | TBD | TBD | Pending |

"""
    return table


def _generate_validation_section(sources: List[SourceBlob]) -> str:
    """Generate validation/release status section (stub)."""
    # TODO: Extract validation/release info
    return "- TODO: Extract validation and release status\n\n"


def _generate_sources_section(sources: List[SourceBlob]) -> str:
    """Generate sources list."""
    content = ""
    
    # Group by source type
    by_type = {}
    for source in sources:
        if source.source_type not in by_type:
            by_type[source.source_type] = []
        by_type[source.source_type].append(source)
    
    for source_type, items in by_type.items():
        content += f"### {source_type.upper()}\n\n"
        for item in items[:10]:  # Limit to first 10
            if item.url:
                content += f"- [{item.source_id}]({item.url})\n"
            else:
                content += f"- {item.source_id}\n"
        if len(items) > 10:
            content += f"- ... and {len(items) - 10} more\n"
        content += "\n"
    
    return content


def _generate_sentiment_section(sources: List[SourceBlob]) -> str:
    """Generate sentiment and hotspots section (stub)."""
    # TODO: Aggregate sentiment data
    return "- TODO: Aggregate sentiment analysis and identify hotspots\n\n"


def _extract_actions(sources: List[SourceBlob]) -> List[Dict[str, Any]]:
    """Extract action items from sources (stub)."""
    # TODO: Use AI or rules to extract action items
    return [
        {
            "text": "TODO: Implement action extraction",
            "owner": "TBD",
            "due_date": None,
            "status": "pending",
        }
    ]


def _summarize_sentiment(sources: List[SourceBlob]) -> Dict[str, Any]:
    """Summarize sentiment across all sources (stub)."""
    # TODO: Aggregate sentiment scores
    positive = sum(1 for s in sources if s.sentiment and s.sentiment.get("label") == "positive")
    negative = sum(1 for s in sources if s.sentiment and s.sentiment.get("label") == "negative")
    neutral = sum(1 for s in sources if s.sentiment and s.sentiment.get("label") == "neutral")
    
    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "total": len(sources),
    }

