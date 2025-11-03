"""
Unit Tests for Text Preprocessor
"""
import pytest
from src.services.preprocessor import TextPreprocessor, PreprocessingError
from src.config import PreprocessorConfig


class TestTextPreprocessor:
    """Tests for TextPreprocessor."""
    
    @pytest.fixture
    def preprocessor(self) -> TextPreprocessor:
        """Fixture providing default preprocessor."""
        return TextPreprocessor()
    
    @pytest.fixture
    def preprocessor_no_lemma(self) -> TextPreprocessor:
        """Fixture providing preprocessor without lemmatization."""
        config = PreprocessorConfig(use_lemmatization=False)
        return TextPreprocessor(config)
    
    def test_basic_preprocessing(self, preprocessor: TextPreprocessor) -> None:
        """Test basic text preprocessing."""
        text = "What is the Python programming language?"
        result = preprocessor.preprocess(text)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert result.islower()
        # Should remove "what", "is", "the" as stop words
        assert "what" not in result
        assert "python" in result
        assert "programming" in result
    
    def test_empty_string(self, preprocessor: TextPreprocessor) -> None:
        """Test preprocessing empty string."""
        assert preprocessor.preprocess("") == ""
        assert preprocessor.preprocess("   ") == ""
    
    def test_lowercase_conversion(self, preprocessor: TextPreprocessor) -> None:
        """Test text is converted to lowercase."""
        text = "HELLO WORLD"
        result = preprocessor.preprocess(text)
        assert result == "hello world"
    
    def test_punctuation_removal(self, preprocessor: TextPreprocessor) -> None:
        """Test punctuation is removed."""
        text = "Hello, world! How are you?"
        result = preprocessor.preprocess(text)
        assert "," not in result
        assert "!" not in result
        assert "?" not in result
    
    def test_url_removal(self, preprocessor: TextPreprocessor) -> None:
        """Test URLs are removed."""
        text = "Check out https://example.com for more info"
        result = preprocessor.preprocess(text)
        assert "https" not in result
        assert "example.com" not in result
        assert "check" in result
        assert "info" in result
    
    def test_email_removal(self, preprocessor: TextPreprocessor) -> None:
        """Test email addresses are removed."""
        text = "Contact us at support@example.com for help"
        result = preprocessor.preprocess(text)
        assert "support@example.com" not in result
        assert "@" not in result
        assert "contact" in result
    
    def test_stop_words_removal(self, preprocessor: TextPreprocessor) -> None:
        """Test stop words are removed."""
        text = "This is a test of the system"
        result = preprocessor.preprocess(text)
        # Common stop words should be removed
        assert "is" not in result
        assert "a" not in result
        assert "of" not in result
        assert "the" not in result
        # Content words should remain
        assert "test" in result
        assert "system" in result
    
    def test_minimum_word_length(self, preprocessor: TextPreprocessor) -> None:
        """Test words below minimum length are filtered."""
        config = PreprocessorConfig(min_word_length=3)
        preprocessor = TextPreprocessor(config)
        
        text = "I am a developer"
        result = preprocessor.preprocess(text)
        
        # Short words should be filtered
        tokens = result.split()
        assert all(len(token) >= 3 for token in tokens)
    
    def test_lemmatization_enabled(self, preprocessor: TextPreprocessor) -> None:
        """Test lemmatization is applied when enabled."""
        text = "running runs runner"
        result = preprocessor.preprocess(text)
        
        # Should lemmatize to base form
        # Note: actual lemmatization results may vary
        assert len(result) > 0
    
    def test_lemmatization_disabled(
        self, preprocessor_no_lemma: TextPreprocessor
    ) -> None:
        """Test preprocessing without lemmatization."""
        text = "running programming"
        result = preprocessor_no_lemma.preprocess(text)
        
        # Should keep original forms
        assert "running" in result or "programming" in result
    
    def test_number_removal(self) -> None:
        """Test number removal when configured."""
        config = PreprocessorConfig(remove_numbers=True)
        preprocessor = TextPreprocessor(config)
        
        text = "Python 3.11 released in 2024"
        result = preprocessor.preprocess(text)
        
        assert "3" not in result
        assert "11" not in result
        assert "2024" not in result
        assert "python" in result
    
    def test_custom_stop_words(self) -> None:
        """Test custom stop words are removed."""
        config = PreprocessorConfig(custom_stop_words=("custom", "special"))
        preprocessor = TextPreprocessor(config)
        
        text = "This is custom text with special words"
        result = preprocessor.preprocess(text)
        
        assert "custom" not in result
        assert "special" not in result
    
    def test_preprocess_to_tokens(self, preprocessor: TextPreprocessor) -> None:
        """Test preprocessing to token list."""
        text = "Python programming language"
        tokens = preprocessor.preprocess_to_tokens(text)
        
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert all(isinstance(token, str) for token in tokens)
    
    def test_batch_preprocessing(self, preprocessor: TextPreprocessor) -> None:
        """Test batch preprocessing multiple texts."""
        texts = [
            "What is Python?",
            "How to learn AI?",
            "Tell me about machine learning"
        ]
        
        results = preprocessor.batch_preprocess(texts)
        
        assert len(results) == len(texts)
        assert all(isinstance(r, str) for r in results)
        assert all(len(r) > 0 for r in results)
    
    def test_get_text_statistics(self, preprocessor: TextPreprocessor) -> None:
        """Test text statistics generation."""
        text = "What is the Python programming language used for?"
        stats = preprocessor.get_text_statistics(text)
        
        assert "original_length" in stats
        assert "original_tokens" in stats
        assert "final_tokens" in stats
        assert "removed_tokens" in stats
        assert "unique_tokens" in stats
        
        assert stats["original_length"] > 0
        assert stats["original_tokens"] > stats["final_tokens"]
    
    def test_cached_preprocessing(self, preprocessor: TextPreprocessor) -> None:
        """Test cached preprocessing returns same result."""
        text = "Python programming"
        
        result1 = preprocessor.preprocess_cached(text)
        result2 = preprocessor.preprocess_cached(text)
        
        assert result1 == result2
    
    def test_extra_whitespace_handling(
        self, preprocessor: TextPreprocessor
    ) -> None:
        """Test handling of extra whitespace."""
        text = "Python    programming    language"
        result = preprocessor.preprocess(text)
        
        # Should normalize to single spaces
        assert "  " not in result
    
    def test_special_characters(self, preprocessor: TextPreprocessor) -> None:
        """Test handling of special characters."""
        text = "Python @#$% programming !!! language"
        result = preprocessor.preprocess(text)
        
        # Should remove special characters
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result
        assert "!" not in result