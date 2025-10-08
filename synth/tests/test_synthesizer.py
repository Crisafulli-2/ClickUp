"""
Test suite for Info Synthesizer
"""

import sys
import os
from datetime import datetime, timedelta

# Add synth/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Import modules to test
from synthesizer import synthesize
from normalizer import SourceBlob


def test_import_synthesizer():
    """Test that synthesizer module can be imported."""
    assert synthesize is not None


def test_synthesize_basic():
    """Test basic synthesis with minimal sources."""
    # Create test sources
    sources = [
        SourceBlob(
            source_type="clickup",
            source_id="test_1",
            timestamp=datetime.now(),
            content="**Test Task 1**\n\nThis is a test task.",
            metadata={"status": "open", "priority": "normal"},
            url="https://app.clickup.com/t/test_1",
        ),
        SourceBlob(
            source_type="slack",
            source_id="test_2",
            timestamp=datetime.now(),
            content="Test Slack message",
            metadata={"channel": "test-channel"},
            url=None,
        ),
    ]
    
    # Test config
    config = {
        "project_name": "Test Project",
        "synthesis": {
            "sections": [
                "Highlights",
                "What's New/Changed",
                "Decisions",
                "Risks & Blockers",
                "Action Items",
                "Validation/Release Status",
                "Sources",
                "Sentiment & Hotspots",
            ]
        }
    }
    
    # Calculate period
    period_end = datetime.now()
    period_start = period_end - timedelta(days=7)
    
    # Run synthesis
    result = synthesize(sources, config, period_start, period_end)
    
    # Verify result structure
    assert "markdown" in result
    assert "actions" in result
    assert "sentiment_summary" in result
    assert "metadata" in result
    
    # Verify markdown contains expected header
    assert "Weekly Info Synthesis" in result["markdown"]
    assert "Test Project" in result["markdown"]
    
    # Verify markdown contains all sections
    for section in config["synthesis"]["sections"]:
        assert section in result["markdown"]
    
    # Verify metadata
    assert result["metadata"]["sources_count"] == 2


def test_normalizer_import():
    """Test that normalizer module can be imported."""
    from normalizer import normalize_sources, SourceBlob, normalize_clickup_task
    
    assert normalize_sources is not None
    assert SourceBlob is not None
    assert normalize_clickup_task is not None


def test_source_blob_to_dict():
    """Test SourceBlob serialization."""
    source = SourceBlob(
        source_type="clickup",
        source_id="test_1",
        timestamp=datetime.now(),
        content="Test content",
        metadata={"key": "value"},
        author="test_user",
        url="https://example.com",
    )
    
    # Convert to dict
    source_dict = source.to_dict()
    
    # Verify structure
    assert source_dict["source_type"] == "clickup"
    assert source_dict["source_id"] == "test_1"
    assert source_dict["content"] == "Test content"
    assert source_dict["metadata"]["key"] == "value"
    assert source_dict["author"] == "test_user"
    assert source_dict["url"] == "https://example.com"


if __name__ == "__main__":
    print("Running Info Synthesizer tests...")
    print()
    
    print("✓ test_import_synthesizer")
    test_import_synthesizer()
    
    print("✓ test_synthesize_basic")
    test_synthesize_basic()
    
    print("✓ test_normalizer_import")
    test_normalizer_import()
    
    print("✓ test_source_blob_to_dict")
    test_source_blob_to_dict()
    
    print()
    print("✅ All tests passed!")

