"""
Configuration Management
Centralized configuration for the FAQ Chatbot
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Final


# Project paths
PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
ASSETS_DIR: Final[Path] = PROJECT_ROOT / "assets"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class MatcherConfig:
    """Configuration for question matching."""

    # Minimum similarity score (0-1) to consider a match valid
    similarity_threshold: float = 0.3

    # Maximum number of alternative suggestions to show
    max_suggestions: int = 3

    # Low confidence threshold - below this, show alternatives
    low_confidence_threshold: float = 0.5

    # TF-IDF parameters
    max_features: int = 1000
    ngram_range: tuple[int, int] = (1, 2)  # unigrams and bigrams


@dataclass(frozen=True)
class PreprocessorConfig:
    """Configuration for text preprocessing."""

    # Minimum word length to keep
    min_word_length: int = 2

    # Whether to use lemmatization (slower but better)
    use_lemmatization: bool = True

    # Whether to remove numbers
    remove_numbers: bool = False

    # Custom stop words to add (domain-specific)
    custom_stop_words: tuple[str, ...] = ()


@dataclass(frozen=True)
class AppConfig:
    """Main application configuration."""

    # Application metadata
    app_name: str = "FAQ Chatbot"
    app_version: str = "0.1.0"
    app_description: str = "AI-powered FAQ Chatbot using NLP"

    # Data file paths
    faq_data_path: Path = DATA_DIR / "faqs.json"

    # Component configurations
    matcher: MatcherConfig = MatcherConfig()
    preprocessor: PreprocessorConfig = PreprocessorConfig()

    # UI Configuration
    page_title: str = "FAQ Chatbot"
    page_icon: str = "🤖"
    layout: str = "centered"

    # Session state keys
    SESSION_MESSAGES: str = "messages"
    SESSION_CHATBOT: str = "chatbot"


# Global configuration instance
config: Final[AppConfig] = AppConfig()
