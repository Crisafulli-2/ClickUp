# Info Synthesizer

A provider-agnostic module that ingests native summaries (Gemini, ClickUp AI, etc.), pulls ClickUp task descriptions/comments and Slack threads, synthesizes weekly/daily briefs, and publishes to Google Docs and/or ClickUp Docs.

## Overview

The Info Synthesizer orchestrates the following workflow:

1. **Gather** - Collects data from multiple sources (ClickUp, Slack, Gmail, Calendar, etc.)
2. **Normalize** - Converts all sources into a unified `SourceBlob` structure
3. **Sentiment** - Optional sentiment analysis using Gemini, GPT, or Google NLP
4. **Synthesize** - Generates a structured markdown brief with sections like Highlights, Risks, Actions, etc.
5. **Publish** - Publishes to Google Docs and/or ClickUp Docs with proper formatting

## Architecture

```
synth/
├── config/
│   └── config.yaml           # Configuration (no secrets!)
├── scripts/
│   └── run_local.sh          # Local run script
├── src/
│   ├── runner.py             # Main orchestrator
│   ├── normalizer.py         # Source normalization
│   ├── synthesizer.py        # Content synthesis
│   ├── sentiment_provider.py # Sentiment analysis
│   ├── slack_adapter.py      # Slack data fetching
│   ├── google_docs_publisher.py   # Google Docs publishing
│   ├── clickup_docs_publisher.py  # ClickUp Docs publishing
│   └── utils/
│       └── markdown_to_gdoc.py    # Markdown to Google Docs converter
├── tests/
│   └── test_synthesizer.py  # Tests
├── Makefile                  # Build targets
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- Repository root must have `.env` with required credentials
- Repository root must have `credentials.json` for Google APIs

### Setup

```bash
cd synth/
make setup
```

This installs dependencies from the project's main `requirements.txt`.

### Configuration

Edit `synth/config/config.yaml`:

1. Set `project_name`
2. Replace `REPLACE_ME` placeholders:
   - `inputs.clickup.list_id` - Your ClickUp list ID
   - `publish.google_doc.parent_drive_id` - Your Google Drive folder ID
   - `publish.clickup_doc.parent_id` - Your ClickUp parent folder/list ID
3. Configure Slack channels if using Slack input
4. Adjust other settings as needed

### Run

```bash
# Using Makefile
make run

# Or using the shell script
./scripts/run_local.sh

# Or directly with Python
cd .. && PYTHONPATH=.:synth/src python synth/src/runner.py --config synth/config/config.yaml
```

### Test

```bash
make test
```

## Module Details

### `runner.py`

Main orchestrator that:
- Loads configuration
- Calculates reporting period
- Gathers sources from all enabled inputs
- Normalizes and optionally annotates sentiment
- Synthesizes the brief
- Publishes to configured destinations
- Outputs a JSON summary with run ID, links, and metrics

### `normalizer.py`

Converts various source formats into a unified `SourceBlob` structure:
- `SourceBlob` - Unified data structure with fields: source_type, source_id, timestamp, content, metadata, author, url, sentiment
- `normalize_clickup_task()` - Converts ClickUp task to SourceBlob
- `normalize_slack_message()` - Converts Slack message to SourceBlob
- Extensible for Gmail, Calendar, Docs, etc.

### `synthesizer.py`

Generates structured markdown brief with sections:
- **Highlights** - Key takeaways
- **What's New/Changed** - Recent updates
- **Decisions** - Key decisions made
- **Risks & Blockers** - Issues and blockers
- **Action Items** - Actionable table with owner, due date, status
- **Validation/Release Status** - Testing and release info
- **Sources** - List of all sources reviewed
- **Sentiment & Hotspots** - Sentiment analysis summary

### `sentiment_provider.py`

Adds sentiment annotations to sources with fallback chain:
1. Gemini (primary)
2. GPT Business
3. Google NLP
4. None (neutral)

Sentiment format: `{label: positive|negative|neutral, score: float, confidence: float}`

### `slack_adapter.py`

Fetches Slack data with multiple modes:
- **api** - Direct Slack API (requires `SLACK_BOT_TOKEN`)
- **digest** - Parse email digests from Gmail
- **dropbox** - Read Slack export files from Dropbox
- **hybrid** - Try api → digest → dropbox with fallback

Features:
- Thread support
- Pinned messages
- Reaction metadata
- Configurable lookback period

### `google_docs_publisher.py`

Publishes to Google Docs:
- Reuses existing Google auth from `src/sheets_service.py`
- Reads `credentials.json` from repo root
- Upserts doc by title (updates if exists, creates if not)
- Converts markdown to Google Docs structure
- Sets sharing permissions (anyone | domain | restricted)

### `clickup_docs_publisher.py`

Publishes to ClickUp Docs:
- Reuses ClickUp API token from `.env`
- Upserts doc by title
- Supports parent types: folder | list | space
- Uses ClickUp's native Markdown support

### `utils/markdown_to_gdoc.py`

Converts markdown to Google Docs API batch update structure:
- Parses headings, bold, italic, lists, tables, links, code blocks
- Generates Google Docs API requests for formatting
- Used by `google_docs_publisher.py`

## Configuration Reference

See `synth/config/config.yaml` for full configuration template.

Key sections:
- `project_name` - Project identifier
- `period` - Rolling or fixed date range
- `providers` - AI provider preferences
- `inputs` - Data sources (ClickUp, Slack, Gmail, Calendar, Docs)
- `synthesis` - Sentiment, risk detection, sections
- `publish` - Google Docs and ClickUp Docs settings

## Credentials

**IMPORTANT**: This module does NOT introduce new credentials. It reuses:

1. **Google APIs** - Reads `credentials.json` and `token.json` from repo root (same as `sheets_service.py`)
2. **ClickUp** - Reads `CLICKUP_API_TOKEN` from repo root `.env` (same as `clickup_service.py`)
3. **Slack** (optional) - Reads `SLACK_BOT_TOKEN` from repo root `.env`

## TODOs

This is a starter implementation with many TODOs marked for future enhancement:

- [ ] Implement full ClickUp task fetching with comments/descriptions
- [ ] Implement Slack API/digest/dropbox modes
- [ ] Implement Gmail, Calendar, Docs inputs
- [ ] Implement Gemini sentiment analysis
- [ ] Implement GPT sentiment analysis
- [ ] Implement Google NLP sentiment analysis
- [ ] Implement AI-driven synthesis (Gemini/GPT) vs rule-based
- [ ] Implement full markdown to Google Docs conversion
- [ ] Implement Google Docs API integration (create/update)
- [ ] Implement ClickUp Docs API integration (create/update)
- [ ] Add tests for all modules
- [ ] Add run ledger (append to Google Sheet)

## Testing

Run tests with:

```bash
make test
```

Current test coverage:
- `test_synthesizer.py` - Basic import and synthesis test

## Troubleshooting

### "Config file not found"
Ensure you're running from the repo root or using the correct relative path.

### "REPLACE_ME" in config
Update `config.yaml` with actual IDs before running.

### Google auth fails
Ensure `credentials.json` exists in repo root and has correct scopes.

### ClickUp API fails
Ensure `CLICKUP_API_TOKEN` is set in repo root `.env`.

## Contributing

When adding new features:
1. Keep TODOs explicit for unimplemented functionality
2. Follow the existing pattern of stub implementations
3. Do not add new credentials - reuse existing ones
4. Update this README with new functionality

## License

Internal use only.

