"""
FAQ Data Models
Type-safe data structures for FAQ entries and matching results
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class FAQCategory(str, Enum):
    """Predefined FAQ categories."""

    PRODUCT = "product"
    TECHNICAL = "technical"
    BILLING = "billing"
    ACCOUNT = "account"
    GENERAL = "general"
    SHIPPING = "shipping"
    RETURNS = "returns"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class FAQ:
    """
    Represents a single FAQ entry.

    Attributes:
        id: Unique identifier for the FAQ
        question: The question text
        answer: The answer text
        category: FAQ category
        keywords: Optional list of keywords for better matching
        alternate_questions: Similar ways to ask the same question
    """

    id: str
    question: str
    answer: str
    category: FAQCategory
    keywords: list[str] = field(default_factory=list)
    alternate_questions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate FAQ data after initialization."""
        if not self.id or not self.id.strip():
            raise ValueError("FAQ id cannot be empty")

        if not self.question or not self.question.strip():
            raise ValueError(f"FAQ {self.id}: question cannot be empty")

        if not self.answer or not self.answer.strip():
            raise ValueError(f"FAQ {self.id}: answer cannot be empty")

    @property
    def all_questions(self) -> list[str]:
        """Get all questions including alternates."""
        return [self.question] + self.alternate_questions

    def matches_keyword(self, keyword: str) -> bool:
        """Check if FAQ contains a specific keyword."""
        keyword_lower = keyword.lower()
        return any(keyword_lower in kw.lower() for kw in self.keywords)


@dataclass(frozen=True)
class MatchResult:
    """
    Represents a question matching result.

    Attributes:
        faq: The matched FAQ entry
        similarity_score: Confidence score (0-1)
        matched_question: Which question variant was matched
    """

    faq: FAQ
    similarity_score: float
    matched_question: str

    def __post_init__(self) -> None:
        """Validate match result data."""
        if not 0 <= self.similarity_score <= 1:
            raise ValueError(
                f"Similarity score must be between 0 and 1, "
                f"got {self.similarity_score}"
            )

    @property
    def confidence_level(self) -> str:
        """Get human-readable confidence level."""
        if self.similarity_score >= 0.7:
            return "High"
        elif self.similarity_score >= 0.5:
            return "Medium"
        else:
            return "Low"

    @property
    def confidence_percentage(self) -> int:
        """Get confidence as percentage."""
        return int(self.similarity_score * 100)


@dataclass
class ChatMessage:
    """
    Represents a chat message in the conversation.

    Attributes:
        role: 'user' or 'assistant'
        content: Message text
        match_result: Optional matching result for assistant messages
    """

    role: str  # 'user' or 'assistant'
    content: str
    match_result: Optional[MatchResult] = None

    def __post_init__(self) -> None:
        """Validate chat message data."""
        if self.role not in ("user", "assistant"):
            raise ValueError(f"Role must be 'user' or 'assistant', got '{self.role}'")

        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")


@dataclass
class FAQDatabase:
    """
    Container for all FAQ entries.

    Attributes:
        faqs: List of all FAQ entries
        metadata: Optional metadata about the database
    """

    faqs: list[FAQ]
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate FAQ database."""
        if not self.faqs:
            raise ValueError("FAQ database cannot be empty")

        # Check for duplicate IDs
        ids = [faq.id for faq in self.faqs]
        if len(ids) != len(set(ids)):
            raise ValueError("FAQ database contains duplicate IDs")

    def get_by_id(self, faq_id: str) -> Optional[FAQ]:
        """Get FAQ by ID."""
        for faq in self.faqs:
            if faq.id == faq_id:
                return faq
        return None

    def get_by_category(self, category: FAQCategory) -> list[FAQ]:
        """Get all FAQs in a specific category."""
        return [faq for faq in self.faqs if faq.category == category]

    def search_keywords(self, keyword: str) -> list[FAQ]:
        """Search FAQs by keyword."""
        return [faq for faq in self.faqs if faq.matches_keyword(keyword)]

    @property
    def total_faqs(self) -> int:
        """Get total number of FAQs."""
        return len(self.faqs)

    @property
    def categories(self) -> set[FAQCategory]:
        """Get all unique categories in the database."""
        return {faq.category for faq in self.faqs}
