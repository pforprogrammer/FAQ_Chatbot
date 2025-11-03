"""
Unit Tests for FAQ Data Models
"""

import pytest
from src.models.faq import (
    FAQ,
    FAQCategory,
    FAQDatabase,
    MatchResult,
    ChatMessage,
)


class TestFAQ:
    """Tests for FAQ model."""

    def test_faq_creation_valid(self) -> None:
        """Test creating a valid FAQ."""
        faq = FAQ(
            id="test_001",
            question="What is Python?",
            answer="Python is a programming language.",
            category=FAQCategory.TECHNICAL,
            keywords=["python", "programming"],
            alternate_questions=["Tell me about Python"],
        )

        assert faq.id == "test_001"
        assert faq.question == "What is Python?"
        assert faq.category == FAQCategory.TECHNICAL
        assert len(faq.keywords) == 2

    def test_faq_empty_id_raises_error(self) -> None:
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="id cannot be empty"):
            FAQ(
                id="",
                question="Test question",
                answer="Test answer",
                category=FAQCategory.GENERAL,
            )

    def test_faq_empty_question_raises_error(self) -> None:
        """Test that empty question raises ValueError."""
        with pytest.raises(ValueError, match="question cannot be empty"):
            FAQ(
                id="test_001",
                question="",
                answer="Test answer",
                category=FAQCategory.GENERAL,
            )

    def test_faq_all_questions_property(self) -> None:
        """Test all_questions property."""
        faq = FAQ(
            id="test_001",
            question="Main question",
            answer="Answer",
            category=FAQCategory.GENERAL,
            alternate_questions=["Alt 1", "Alt 2"],
        )

        all_q = faq.all_questions
        assert len(all_q) == 3
        assert all_q[0] == "Main question"
        assert "Alt 1" in all_q

    def test_faq_matches_keyword(self) -> None:
        """Test keyword matching."""
        faq = FAQ(
            id="test_001",
            question="Test",
            answer="Answer",
            category=FAQCategory.GENERAL,
            keywords=["python", "coding"],
        )

        assert faq.matches_keyword("Python")
        assert faq.matches_keyword("CODING")
        assert not faq.matches_keyword("java")


class TestMatchResult:
    """Tests for MatchResult model."""

    def test_match_result_creation(self) -> None:
        """Test creating a valid MatchResult."""
        faq = FAQ(
            id="test_001",
            question="Test?",
            answer="Answer",
            category=FAQCategory.GENERAL,
        )

        result = MatchResult(faq=faq, similarity_score=0.85, matched_question="Test?")

        assert result.similarity_score == 0.85
        assert result.confidence_level == "High"

    def test_match_result_invalid_score(self) -> None:
        """Test that invalid similarity score raises error."""
        faq = FAQ(
            id="test_001",
            question="Test?",
            answer="Answer",
            category=FAQCategory.GENERAL,
        )

        with pytest.raises(ValueError, match="between 0 and 1"):
            MatchResult(faq=faq, similarity_score=1.5, matched_question="Test?")

    def test_confidence_levels(self) -> None:
        """Test confidence level categorization."""
        faq = FAQ(
            id="test_001",
            question="Test?",
            answer="Answer",
            category=FAQCategory.GENERAL,
        )

        high = MatchResult(faq=faq, similarity_score=0.8, matched_question="Test?")
        assert high.confidence_level == "High"

        medium = MatchResult(faq=faq, similarity_score=0.6, matched_question="Test?")
        assert medium.confidence_level == "Medium"

        low = MatchResult(faq=faq, similarity_score=0.3, matched_question="Test?")
        assert low.confidence_level == "Low"


class TestChatMessage:
    """Tests for ChatMessage model."""

    def test_chat_message_user(self) -> None:
        """Test creating user message."""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_chat_message_invalid_role(self) -> None:
        """Test that invalid role raises error."""
        with pytest.raises(ValueError, match="must be 'user' or 'assistant'"):
            ChatMessage(role="bot", content="Hello")

    def test_chat_message_empty_content(self) -> None:
        """Test that empty content raises error."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            ChatMessage(role="user", content="")


class TestFAQDatabase:
    """Tests for FAQDatabase model."""

    def test_database_creation(self) -> None:
        """Test creating FAQ database."""
        faqs = [
            FAQ(
                id="test_001", question="Q1", answer="A1", category=FAQCategory.GENERAL
            ),
            FAQ(
                id="test_002",
                question="Q2",
                answer="A2",
                category=FAQCategory.TECHNICAL,
            ),
        ]

        db = FAQDatabase(faqs=faqs)
        assert db.total_faqs == 2
        assert len(db.categories) == 2

    def test_database_empty_raises_error(self) -> None:
        """Test that empty FAQ list raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            FAQDatabase(faqs=[])

    def test_database_duplicate_ids_raises_error(self) -> None:
        """Test that duplicate IDs raise error."""
        faqs = [
            FAQ(
                id="test_001", question="Q1", answer="A1", category=FAQCategory.GENERAL
            ),
            FAQ(
                id="test_001",  # Duplicate
                question="Q2",
                answer="A2",
                category=FAQCategory.TECHNICAL,
            ),
        ]

        with pytest.raises(ValueError, match="duplicate IDs"):
            FAQDatabase(faqs=faqs)

    def test_get_by_id(self) -> None:
        """Test getting FAQ by ID."""
        faqs = [
            FAQ(
                id="test_001", question="Q1", answer="A1", category=FAQCategory.GENERAL
            ),
            FAQ(
                id="test_002",
                question="Q2",
                answer="A2",
                category=FAQCategory.TECHNICAL,
            ),
        ]

        db = FAQDatabase(faqs=faqs)
        faq = db.get_by_id("test_001")

        assert faq is not None
        assert faq.id == "test_001"
        assert faq.question == "Q1"

        # Test non-existent ID
        assert db.get_by_id("test_999") is None

    def test_get_by_category(self) -> None:
        """Test getting FAQs by category."""
        faqs = [
            FAQ(
                id="test_001", question="Q1", answer="A1", category=FAQCategory.GENERAL
            ),
            FAQ(
                id="test_002", question="Q2", answer="A2", category=FAQCategory.GENERAL
            ),
            FAQ(
                id="test_003",
                question="Q3",
                answer="A3",
                category=FAQCategory.TECHNICAL,
            ),
        ]

        db = FAQDatabase(faqs=faqs)
        general_faqs = db.get_by_category(FAQCategory.GENERAL)

        assert len(general_faqs) == 2
        assert all(faq.category == FAQCategory.GENERAL for faq in general_faqs)

    def test_search_keywords(self) -> None:
        """Test searching FAQs by keyword."""
        faqs = [
            FAQ(
                id="test_001",
                question="Q1",
                answer="A1",
                category=FAQCategory.GENERAL,
                keywords=["python", "coding"],
            ),
            FAQ(
                id="test_002",
                question="Q2",
                answer="A2",
                category=FAQCategory.TECHNICAL,
                keywords=["java", "programming"],
            ),
        ]

        db = FAQDatabase(faqs=faqs)
        results = db.search_keywords("python")

        assert len(results) == 1
        assert results[0].id == "test_001"
