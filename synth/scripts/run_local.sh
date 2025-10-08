#!/bin/bash
# Run the Info Synthesizer locally

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Set PYTHONPATH to include both project root and synth/src
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/synth/src:$PYTHONPATH"

# Default config path
CONFIG_PATH="${1:-synth/config/config.yaml}"

echo "======================================"
echo "🔮 Info Synthesizer - Local Run"
echo "======================================"
echo "Project Root: $PROJECT_ROOT"
echo "Config: $CONFIG_PATH"
echo "======================================"
echo ""

# Run the synthesizer
python synth/src/runner.py --config "$CONFIG_PATH"

