# Makefile for Info Synthesizer

.PHONY: setup run test clean help

# Default target
.DEFAULT_GOAL := help

# Project root (parent of synth/)
PROJECT_ROOT := $(shell cd .. && pwd)

help: ## Show this help message
	@echo "Info Synthesizer - Makefile"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies (reuses project requirements.txt)
	@echo "📦 Installing dependencies..."
	@cd "$(PROJECT_ROOT)" && pip install -r requirements.txt
	@echo "✅ Dependencies installed"

run: ## Run the Info Synthesizer with default config
	@echo "🔮 Running Info Synthesizer..."
	@cd "$(PROJECT_ROOT)" && PYTHONPATH=.:synth/src python3 synth/src/runner.py --config synth/config/config.yaml

test: ## Run tests
	@echo "🧪 Running tests..."
	@cd "$(PROJECT_ROOT)" && PYTHONPATH=.:synth/src python3 synth/tests/test_synthesizer.py

clean: ## Clean temporary files
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ Clean complete"

