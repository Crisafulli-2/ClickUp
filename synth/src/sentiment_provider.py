"""
Sentiment Provider - adds sentiment analysis to normalized sources.
Supports multiple providers: Gemini > GPT Business > Google NLP > none
"""

from typing import Dict, List, Any
from normalizer import SourceBlob


def annotate_sentiment(
    sources: List[SourceBlob],
    config: Dict[str, Any],
) -> List[SourceBlob]:
    """
    Add sentiment annotations to each SourceBlob.
    
    Args:
        sources: List of SourceBlobs to annotate
        config: Sentiment configuration from config.yaml
    
    Returns:
        Updated list of SourceBlobs with sentiment data
    """
    sentiment_cfg = config.get("synthesis", {}).get("sentiment", {})
    
    if not sentiment_cfg.get("enabled", False):
        return sources
    
    provider = sentiment_cfg.get("provider", "none")
    
    # Try primary provider, then fallback
    for attempt_provider in [provider] + config.get("providers", {}).get("sentiment_fallback", []):
        try:
            if attempt_provider == "gemini":
                return _annotate_with_gemini(sources, config)
            elif attempt_provider == "gpt_business":
                return _annotate_with_gpt(sources, config)
            elif attempt_provider == "google_nlp":
                return _annotate_with_google_nlp(sources, config)
            elif attempt_provider == "none":
                return _annotate_with_neutral(sources)
        except Exception as e:
            print(f"⚠️ Sentiment provider '{attempt_provider}' failed: {e}")
            continue
    
    # Final fallback: neutral
    return _annotate_with_neutral(sources)


def _annotate_with_gemini(sources: List[SourceBlob], config: Dict[str, Any]) -> List[SourceBlob]:
    """
    Use Gemini API for sentiment analysis.
    
    TODO: Implement Gemini API integration
    - Use google-generativeai package
    - Read GEMINI_API_KEY from .env (repo root)
    - Batch process sources for efficiency
    - Return sentiment: {label: positive|negative|neutral, score: float, confidence: float}
    """
    # Placeholder implementation
    print("TODO: Implement Gemini sentiment analysis")
    return _annotate_with_neutral(sources)


def _annotate_with_gpt(sources: List[SourceBlob], config: Dict[str, Any]) -> List[SourceBlob]:
    """
    Use GPT (OpenAI) for sentiment analysis.
    
    TODO: Implement OpenAI API integration
    - Use openai package
    - Read OPENAI_API_KEY from .env (repo root)
    - Batch process sources
    - Return sentiment: {label: positive|negative|neutral, score: float, confidence: float}
    """
    print("TODO: Implement GPT sentiment analysis")
    return _annotate_with_neutral(sources)


def _annotate_with_google_nlp(sources: List[SourceBlob], config: Dict[str, Any]) -> List[SourceBlob]:
    """
    Use Google Cloud Natural Language API for sentiment analysis.
    
    TODO: Implement Google NLP integration
    - Use google-cloud-language package
    - Reuse Google credentials from credentials.json
    - Batch process sources
    - Return sentiment: {label: positive|negative|neutral, score: float, confidence: float}
    """
    print("TODO: Implement Google NLP sentiment analysis")
    return _annotate_with_neutral(sources)


def _annotate_with_neutral(sources: List[SourceBlob]) -> List[SourceBlob]:
    """
    Default: assign neutral sentiment to all sources.
    """
    for source in sources:
        source.sentiment = {
            "label": "neutral",
            "score": 0.0,
            "confidence": 1.0,
        }
    return sources

