# Info Synthesizer - Quick Start Guide

## What Was Built

A complete provider-agnostic "Info Synthesizer" module that:

✅ **Ingests** native summaries (Gemini, ClickUp AI, etc.)  
✅ **Pulls** ClickUp task descriptions/comments + Slack threads  
✅ **Synthesizes** weekly/daily briefs with structured sections  
✅ **Publishes** to Google Docs and/or ClickUp Docs  

## Directory Structure

```
synth/
├── README.md                      # Full documentation
├── QUICKSTART.md                  # This file
├── Makefile                       # Build targets (setup, run, test, clean)
├── config/
│   └── config.yaml               # Configuration file (NO SECRETS)
├── scripts/
│   └── run_local.sh              # Shell script to run locally
├── src/
│   ├── runner.py                 # Main orchestrator
│   ├── normalizer.py             # Source normalization
│   ├── synthesizer.py            # Content synthesis
│   ├── sentiment_provider.py     # Sentiment analysis
│   ├── slack_adapter.py          # Slack data fetching
│   ├── google_docs_publisher.py  # Google Docs publishing
│   ├── clickup_docs_publisher.py # ClickUp Docs publishing
│   └── utils/
│       └── markdown_to_gdoc.py   # Markdown converter
└── tests/
    └── test_synthesizer.py       # Test suite
```

## Quick Start (5 Steps)

### 1. Configure

Edit `synth/config/config.yaml` and replace these placeholders:

```yaml
inputs:
  clickup:
    list_id: "REPLACE_ME"  # Your ClickUp list ID

publish:
  google_doc:
    parent_drive_id: "REPLACE_ME"  # Your Google Drive folder ID
  
  clickup_doc:
    parent_id: "REPLACE_ME"  # Your ClickUp folder/list ID
```

### 2. Verify Credentials

Ensure these exist in the **repo root** (not in synth/):
- `.env` with `CLICKUP_API_TOKEN`
- `credentials.json` for Google APIs

### 3. Install Dependencies (Optional)

```bash
cd synth/
make setup
```

### 4. Run

```bash
# Option 1: Using Makefile
make run

# Option 2: Using shell script
./scripts/run_local.sh

# Option 3: Direct Python
cd .. && PYTHONPATH=.:synth/src python3 synth/src/runner.py --config synth/config/config.yaml
```

### 5. Review Output

The runner will:
1. ✅ Gather sources (ClickUp tasks, Slack messages)
2. ✅ Normalize data into unified format
3. ✅ Apply sentiment analysis (optional)
4. ✅ Generate structured markdown brief
5. ✅ Publish to Google Docs and/or ClickUp Docs
6. ✅ Output JSON summary with links and metrics

## Sample Output

```json
{
  "run_id": "20251007_195354",
  "links": {
    "google_doc": "https://docs.google.com/document/d/...",
    "clickup_doc": "https://app.clickup.com/doc/..."
  },
  "actions_count": 5,
  "sentiment": {
    "positive": 3,
    "negative": 1,
    "neutral": 8,
    "total": 12
  },
  "sources_count": 12,
  "period": {
    "start": "2025-09-30T19:53:54",
    "end": "2025-10-07T19:53:54"
  }
}
```

## What's Currently Stubbed (TODOs)

The implementation is functional but has placeholder TODOs for:

🔧 **Full Implementation Needed:**
- [ ] Real ClickUp task fetching with comments/descriptions
- [ ] Slack API/digest/dropbox modes
- [ ] Gmail, Calendar, Docs inputs
- [ ] AI-driven sentiment (Gemini/GPT/Google NLP)
- [ ] AI-driven synthesis vs rule-based
- [ ] Complete markdown to Google Docs conversion
- [ ] Full Google Docs API integration
- [ ] Full ClickUp Docs API integration

✅ **Currently Working:**
- ✅ Config loading and validation
- ✅ Source normalization structure
- ✅ Basic synthesis with all sections
- ✅ Placeholder data for demo
- ✅ JSON output summary
- ✅ Tests pass

## Testing

```bash
cd synth/
make test

# Or run directly
cd .. && PYTHONPATH=.:synth/src python3 synth/tests/test_synthesizer.py
```

**Note**: Tests run standalone without requiring pytest. If you want to use pytest for more advanced testing, install it with `pip3 install pytest`.

## Configuration Options

See `config/config.yaml` for full options:

- **Period**: Rolling (last N days) or fixed date range
- **Providers**: AI provider preferences (Gemini > GPT > Google NLP > none)
- **Inputs**: ClickUp, Slack, Gmail, Calendar, Docs
- **Synthesis**: Sentiment, risk detection, urgency rules, sections
- **Publish**: Google Doc and/or ClickUp Doc settings

## Credentials (IMPORTANT)

⚠️ **NO NEW CREDENTIALS** - This module reuses existing credentials:

1. **Google APIs**: Uses `credentials.json` from repo root (same as `sheets_service.py`)
2. **ClickUp**: Uses `CLICKUP_API_TOKEN` from repo root `.env` (same as `clickup_service.py`)
3. **Slack** (optional): Uses `SLACK_BOT_TOKEN` from repo root `.env`

## Next Steps

1. **Update config.yaml** with real IDs
2. **Run with placeholder data** to verify flow
3. **Implement TODOs** based on priority:
   - Start with ClickUp task fetching
   - Add Slack API mode
   - Implement AI-driven synthesis
   - Complete Google Docs publishing
4. **Test** with real data
5. **Schedule** regular runs (cron, GitHub Actions, etc.)

## Troubleshooting

**"Config file not found"**  
→ Ensure you're running from repo root or using correct path

**"REPLACE_ME" in output**  
→ Update config.yaml with actual IDs

**Google auth fails**  
→ Ensure credentials.json exists in repo root

**ClickUp API fails**  
→ Ensure CLICKUP_API_TOKEN in repo root .env

## Support

See full documentation in `README.md` for detailed module descriptions.

