"""
Text Preprocessing Service
Handles all text cleaning, normalization, and preprocessing using NLTK
"""
import re
import string
from typing import List, Set, Optional
from functools import lru_cache

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from src.config import PreprocessorConfig


class PreprocessingError(Exception):
    """Raised when text preprocessing fails."""
    pass


class TextPreprocessor:
    """
    Text preprocessing service using NLTK.
    
    Provides text cleaning, tokenization, lemmatization,
    and stop word removal for NLP tasks.
    """
    
    def __init__(self, config: Optional[PreprocessorConfig] = None) -> None:
        """
        Initialize text preprocessor.
        
        Args:
            config: Preprocessing configuration. Uses default if None.
        """
        self.config = config or PreprocessorConfig()
        
        # Initialize NLTK components
        try:
            self._lemmatizer = WordNetLemmatizer()
            self._stop_words = self._load_stop_words()
        except LookupError as e:
            raise PreprocessingError(
                f"NLTK data not found. Please run: python src/setup_nltk.py\n"
                f"Error: {e}"
            )
    
    def _load_stop_words(self) -> Set[str]:
        """
        Load stop words from NLTK.
        
        Returns:
            Set of stop words in lowercase
        """
        try:
            base_stop_words = set(stopwords.words('english'))
        except LookupError:
            # Fallback to basic stop words if NLTK data not available
            base_stop_words = {
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
                'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
                'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
                'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
                'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
                'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
                'against', 'between', 'into', 'through', 'during', 'before',
                'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
                'out', 'on', 'off', 'over', 'under', 'again', 'further',
                'then', 'once'
            }
        
        # Add custom stop words from config
        if self.config.custom_stop_words:
            base_stop_words.update(
                word.lower() for word in self.config.custom_stop_words
            )
        
        return base_stop_words
    
    def preprocess(self, text: str) -> str:
        """
        Complete preprocessing pipeline.
        
        Args:
            text: Raw input text
            
        Returns:
            Preprocessed text as a single string
            
        Example:
            >>> preprocessor = TextPreprocessor()
            >>> preprocessor.preprocess("What's the Python programming language?")
            'python programming language'
        """
        if not text or not text.strip():
            return ""
        
        # Step 1: Clean text
        cleaned = self._clean_text(text)
        
        # Step 2: Tokenize
        tokens = self._tokenize(cleaned)
        
        # Step 3: Remove stop words
        tokens = self._remove_stop_words(tokens)
        
        # Step 4: Filter by length
        tokens = self._filter_by_length(tokens)
        
        # Step 5: Lemmatize (if enabled)
        if self.config.use_lemmatization:
            tokens = self._lemmatize(tokens)
        
        # Step 6: Join back to string
        return ' '.join(tokens)
    
    def preprocess_to_tokens(self, text: str) -> List[str]:
        """
        Complete preprocessing pipeline returning tokens.
        
        Args:
            text: Raw input text
            
        Returns:
            List of preprocessed tokens
        """
        preprocessed = self.preprocess(text)
        return preprocessed.split() if preprocessed else []
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Steps:
        1. Convert to lowercase
        2. Remove URLs
        3. Remove email addresses
        4. Remove special characters (optional: keep numbers)
        5. Remove extra whitespace
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove numbers if configured
        if self.config.remove_numbers:
            text = re.sub(r'\d+', '', text)
        
        # Remove punctuation (keep spaces)
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Cleaned text
            
        Returns:
            List of tokens
        """
        try:
            tokens = word_tokenize(text)
        except LookupError:
            # Fallback to simple split if NLTK tokenizer not available
            tokens = text.split()
        
        return tokens
    
    def _remove_stop_words(self, tokens: List[str]) -> List[str]:
        """
        Remove stop words from token list.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens without stop words
        """
        return [
            token for token in tokens 
            if token not in self._stop_words
        ]
    
    def _filter_by_length(self, tokens: List[str]) -> List[str]:
        """
        Filter tokens by minimum length.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens meeting length requirement
        """
        return [
            token for token in tokens 
            if len(token) >= self.config.min_word_length
        ]
    
    def _lemmatize(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens to their base form.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Lemmatized tokens
        """
        return [
            self._lemmatizer.lemmatize(token)
            for token in tokens
        ]
    
    @lru_cache(maxsize=1000)
    def preprocess_cached(self, text: str) -> str:
        """
        Cached version of preprocess for frequently used queries.
        
        Args:
            text: Raw input text
            
        Returns:
            Preprocessed text
        """
        return self.preprocess(text)
    
    def batch_preprocess(self, texts: List[str]) -> List[str]:
        """
        Preprocess multiple texts efficiently.
        
        Args:
            texts: List of raw texts
            
        Returns:
            List of preprocessed texts
        """
        return [self.preprocess(text) for text in texts]
    
    def get_text_statistics(self, text: str) -> dict[str, int]:
        """
        Get statistics about text preprocessing.
        
        Args:
            text: Raw input text
            
        Returns:
            Dictionary with preprocessing statistics
        """
        original_tokens = self._tokenize(self._clean_text(text))
        preprocessed = self.preprocess(text)
        final_tokens = preprocessed.split() if preprocessed else []
        
        return {
            'original_length': len(text),
            'original_tokens': len(original_tokens),
            'final_tokens': len(final_tokens),
            'removed_tokens': len(original_tokens) - len(final_tokens),
            'unique_tokens': len(set(final_tokens))
        }