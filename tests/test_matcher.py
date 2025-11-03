"""
Unit Tests for Question Matcher
"""
import pytest
import numpy as np

from src.services.matcher import QuestionMatcher, MatcherError
from src.services.preprocessor import TextPreprocessor
from src.models.faq import FAQ, FAQDatabase, FAQCategory
from src.config import MatcherConfig


class TestQuestionMatcher:
    """Tests for QuestionMatcher."""
    
    @pytest.fixture
    def sample_faqs(self) -> list[FAQ]:
        """Fixture providing sample FAQs."""
        return [
            FAQ(
                id="test_001",
                question="What is Python?",
                answer="Python is a programming language.",
                category=FAQCategory.TECHNICAL,
                keywords=["python", "programming"],
                alternate_questions=["Tell me about Python", "Explain Python"]
            ),
            FAQ(
                id="test_002",
                question="How do I apply?",
                answer="Visit our website to apply.",
                category=FAQCategory.GENERAL,
                keywords=["apply", "application"],
                alternate_questions=["Application process", "How to apply"]
            ),
            FAQ(
                id="test_003",
                question="What is machine learning?",
                answer="Machine learning is a subset of AI.",
                category=FAQCategory.TECHNICAL,
                keywords=["machine learning", "ml", "ai"],
                alternate_questions=["Explain ML", "What is ML"]
            ),
        ]
    
    @pytest.fixture
    def faq_database(self, sample_faqs: list[FAQ]) -> FAQDatabase:
        """Fixture providing FAQ database."""
        return FAQDatabase(faqs=sample_faqs)
    
    @pytest.fixture
    def preprocessor(self) -> TextPreprocessor:
        """Fixture providing preprocessor."""
        return TextPreprocessor()
    
    @pytest.fixture
    def matcher(
        self,
        faq_database: FAQDatabase,
        preprocessor: TextPreprocessor
    ) -> QuestionMatcher:
        """Fixture providing question matcher."""
        return QuestionMatcher(faq_database, preprocessor)
    
    def test_matcher_initialization(self, matcher: QuestionMatcher) -> None:
        """Test matcher initializes correctly."""
        assert matcher is not None
        assert matcher.faq_database is not None
        assert matcher.preprocessor is not None
        assert len(matcher.corpus_questions) > 0
    
    def test_corpus_building(self, matcher: QuestionMatcher) -> None:
        """Test FAQ corpus is built correctly."""
        # Should have main + alternate questions
        assert len(matcher.corpus_questions) >= 3
        assert len(matcher.corpus_faqs) == len(matcher.corpus_questions)
        assert len(matcher.corpus_original_questions) == len(matcher.corpus_questions)
    
    def test_exact_match(self, matcher: QuestionMatcher) -> None:
        """Test exact question matching."""
        result = matcher.match("What is Python?")
        
        assert result is not None
        assert result.faq.id == "test_001"
        assert result.similarity_score > 0.5
    
    def test_similar_match(self, matcher: QuestionMatcher) -> None:
        """Test matching similar questions."""
        result = matcher.match("Tell me about Python programming")
        
        assert result is not None
        assert result.faq.id == "test_001"
    
    def test_alternate_question_match(self, matcher: QuestionMatcher) -> None:
        """Test matching with alternate questions."""
        result = matcher.match("Tell me about Python")
        
        assert result is not None
        assert result.faq.id == "test_001"
    
    def test_no_match(self, matcher: QuestionMatcher) -> None:
        """Test no match for irrelevant query."""
        config = MatcherConfig(similarity_threshold=0.8)
        matcher = QuestionMatcher(
            matcher.faq_database,
            matcher.preprocessor,
            config
        )
        
        result = matcher.match("How to cook pasta?")
        
        # Should either be None or have very low similarity
        if result is not None:
            assert result.similarity_score < 0.5
    
    def test_empty_query(self, matcher: QuestionMatcher) -> None:
        """Test empty query returns None."""
        assert matcher.match("") is None
        assert matcher.match("   ") is None
    
    def test_match_with_alternatives(self, matcher: QuestionMatcher) -> None:
        """Test getting match with alternatives."""
        best, alternatives = matcher.match_with_alternatives(
            "What is Python programming language?"
        )
        
        assert best is not None
        assert isinstance(alternatives, list)
        
        # Best match should be test_001
        assert best.faq.id == "test_001"
        
        # Alternatives should not include same FAQ
        for alt in alternatives:
            assert alt.faq.id != best.faq.id
    
    def test_similarity_threshold(self) -> None:
        """Test similarity threshold filtering."""
        faqs = [
            FAQ(
                id="test_001",
                question="Python programming",
                answer="Answer",
                category=FAQCategory.TECHNICAL
            )
        ]
        db = FAQDatabase(faqs=faqs)
        preprocessor = TextPreprocessor()
        
        # High threshold
        config = MatcherConfig(similarity_threshold=0.9)
        matcher = QuestionMatcher(db, preprocessor, config)
        
        result = matcher.match("Java programming")
        # Should not match due to high threshold
        assert result is None or result.similarity_score < 0.9
    
    def test_max_suggestions(self, matcher: QuestionMatcher) -> None:
        """Test max suggestions limit."""
        config = MatcherConfig(max_suggestions=2)
        matcher = QuestionMatcher(
            matcher.faq_database,
            matcher.preprocessor,
            config
        )
        
        best, alternatives = matcher.match_with_alternatives(
            "programming language"
        )
        
        # Should have at most 2 alternatives
        assert len(alternatives) <= 2
    
    def test_is_low_confidence(self, matcher: QuestionMatcher) -> None:
        """Test low confidence detection."""
        result = matcher.match("What is Python?")
        assert result is not None
        
        # Exact match should be high confidence
        assert not matcher.is_low_confidence(result)
        
        # Create low confidence match
        from src.models.faq import MatchResult
        low_match = MatchResult(
            faq=result.faq,
            similarity_score=0.3,
            matched_question=result.matched_question
        )
        
        assert matcher.is_low_confidence(low_match)
    
    def test_get_matches_by_category(self, matcher: QuestionMatcher) -> None:
        """Test filtering matches by category."""
        matches = matcher.get_matches_by_category(
            "programming",
            "technical"
        )
        
        assert all(m.faq.category == FAQCategory.TECHNICAL for m in matches)
    
    def test_get_similarity_matrix(self, matcher: QuestionMatcher) -> None:
        """Test similarity matrix generation."""
        matrix = matcher.get_similarity_matrix()
        
        assert isinstance(matrix, np.ndarray)
        assert matrix.shape[0] == matrix.shape[1]
        assert matrix.shape[0] == len(matcher.corpus_questions)
        
        # Diagonal should be 1.0 (self-similarity)
        for i in range(min(len(matrix), 3)):
            assert abs(matrix[i][i] - 1.0) < 0.01
    
    def test_find_similar_faqs(self, matcher: QuestionMatcher) -> None:
        """Test finding similar FAQs."""
        similar = matcher.find_similar_faqs("test_001", top_n=2)
        
        assert isinstance(similar, list)
        assert len(similar) <= 2
        
        # Each result should be (FAQ, similarity_score)
        for faq, score in similar:
            assert isinstance(faq, FAQ)
            assert isinstance(score, float)
            assert 0 <= score <= 1
            assert faq.id != "test_001"  # Should not include self
    
    def test_get_corpus_statistics(self, matcher: QuestionMatcher) -> None:
        """Test corpus statistics."""
        stats = matcher.get_corpus_statistics()
        
        assert 'total_faqs' in stats
        assert 'total_questions' in stats
        assert 'vocabulary_size' in stats
        
        assert stats['total_faqs'] == 3
        assert stats['total_questions'] >= 3
    
    def test_case_insensitive_matching(self, matcher: QuestionMatcher) -> None:
        """Test matching is case-insensitive."""
        result1 = matcher.match("What is Python?")
        result2 = matcher.match("WHAT IS PYTHON?")
        result3 = matcher.match("what is python?")
        
        # All should match same FAQ
        assert result1 is not None
        assert result2 is not None
        assert result3 is not None
        
        assert result1.faq.id == result2.faq.id == result3.faq.id
    
    def test_empty_database_raises_error(self) -> None:
        """Test empty database raises error."""
        empty_db = FAQDatabase(faqs=[
            FAQ(
                id="test",
                question="test",
                answer="test",
                category=FAQCategory.GENERAL
            )
        ])
        preprocessor = TextPreprocessor()
        
        # Should initialize without error
        matcher = QuestionMatcher(empty_db, preprocessor)
        assert matcher is not None