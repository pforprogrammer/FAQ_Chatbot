"""
Unit Tests for Text Utilities
"""
import pytest
from src.services.text_utils import (
    extract_keywords,
    calculate_text_similarity,
    remove_special_patterns,
    normalize_whitespace,
    split_into_sentences,
    get_word_frequency,
    truncate_text,
    expand_contractions,
    remove_repeated_chars
)


class TestTextUtils:
    """Tests for text utility functions."""
    
    def test_extract_keywords(self) -> None:
        """Test keyword extraction."""
        text = "python python programming code code code"
        keywords = extract_keywords(text, top_n=2)
        
        assert len(keywords) <= 2
        assert "code" in keywords  # Most frequent
    
    def test_calculate_text_similarity(self) -> None:
        """Test Jaccard similarity calculation."""
        text1 = "python programming language"
        text2 = "python coding language"
        
        similarity = calculate_text_similarity(text1, text2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0  # Should have some overlap
        
        # Identical texts
        assert calculate_text_similarity(text1, text1) == 1.0
        
        # Completely different texts
        sim = calculate_text_similarity("aaa bbb", "ccc ddd")
        assert sim == 0.0
    
    def test_remove_special_patterns(self) -> None:
        """Test removal of hashtags and mentions."""
        text = "Check out #python and @developer for more!"
        result = remove_special_patterns(text)
        
        assert "#python" not in result
        assert "@developer" not in result
        assert "check" in result.lower()
    
    def test_normalize_whitespace(self) -> None:
        """Test whitespace normalization."""
        text = "Python    programming   \n\t  language"
        result = normalize_whitespace(text)
        
        assert "  " not in result
        assert "\n" not in result
        assert "\t" not in result
        assert result == "Python programming language"
    
    def test_split_into_sentences(self) -> None:
        """Test sentence splitting."""
        text = "Python is great. AI is amazing! What about ML?"
        sentences = split_into_sentences(text)
        
        assert len(sentences) == 3
        assert "Python is great" in sentences
        assert "AI is amazing" in sentences
    
    def test_get_word_frequency(self) -> None:
        """Test word frequency calculation."""
        text = "python python ai ai ai"
        freq = get_word_frequency(text)
        
        assert freq["python"] == 2
        assert freq["ai"] == 3
    
    def test_truncate_text(self) -> None:
        """Test text truncation."""
        text = "This is a long text that needs truncation"
        result = truncate_text(text, max_length=20)
        
        assert len(result) <= 20
        assert result.endswith("...")
        
        # Short text should not be truncated
        short = "Short"
        assert truncate_text(short, max_length=20) == "Short"
    
    def test_expand_contractions(self) -> None:
        """Test contraction expansion."""
        text = "I'm learning AI and it's amazing. Don't stop!"
        result = expand_contractions(text)
        
        assert "i am" in result.lower()
        assert "it is" in result.lower()
        assert "do not" in result.lower()
        assert "'" not in result or result.count("'") < text.count("'")
    
    def test_remove_repeated_chars(self) -> None:
        """Test repeated character removal."""
        text = "Hellooooo woooorld!!!"
        result = remove_repeated_chars(text, max_repeats=2)
        
        assert "ooo" not in result
        assert result == "Helloo woorld!!"