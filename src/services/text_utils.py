"""
Text Utility Functions
Additional text processing and analysis utilities
"""
import re
from typing import List, Dict, Tuple
from collections import Counter


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract most common keywords from text.
    
    Args:
        text: Input text
        top_n: Number of top keywords to return
        
    Returns:
        List of top keywords
    """
    # Simple word frequency
    words = text.lower().split()
    word_counts = Counter(words)
    return [word for word, _ in word_counts.most_common(top_n)]


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate simple Jaccard similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def remove_special_patterns(text: str) -> str:
    """
    Remove special patterns like hashtags, mentions, etc.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Remove hashtags
    text = re.sub(r'#\w+', '', text)
    
    # Remove mentions
    text = re.sub(r'@\w+', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[!?]{2,}', '', text)
    
    return text.strip()


def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace to single spaces.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    return ' '.join(text.split())


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences (basic implementation).
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def get_word_frequency(text: str) -> Dict[str, int]:
    """
    Get word frequency distribution.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary mapping words to their frequencies
    """
    words = text.lower().split()
    return dict(Counter(words))


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix


def expand_contractions(text: str) -> str:
    """
    Expand common English contractions.
    
    Args:
        text: Input text with contractions
        
    Returns:
        Text with expanded contractions
    """
    contractions = {
        "don't": "do not",
        "doesn't": "does not",
        "didn't": "did not",
        "can't": "cannot",
        "couldn't": "could not",
        "wouldn't": "would not",
        "shouldn't": "should not",
        "won't": "will not",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not",
        "haven't": "have not",
        "hasn't": "has not",
        "hadn't": "had not",
        "i'm": "i am",
        "you're": "you are",
        "he's": "he is",
        "she's": "she is",
        "it's": "it is",
        "we're": "we are",
        "they're": "they are",
        "i've": "i have",
        "you've": "you have",
        "we've": "we have",
        "they've": "they have",
        "i'll": "i will",
        "you'll": "you will",
        "he'll": "he will",
        "she'll": "she will",
        "we'll": "we will",
        "they'll": "they will",
        "i'd": "i would",
        "you'd": "you would",
        "he'd": "he would",
        "she'd": "she would",
        "we'd": "we would",
        "they'd": "they would",
    }
    
    # Create pattern for all contractions
    pattern = re.compile(
        r'\b(' + '|'.join(re.escape(key) for key in contractions.keys()) + r')\b',
        re.IGNORECASE
    )
    
    def replace(match: re.Match) -> str:
        return contractions[match.group(0).lower()]
    
    return pattern.sub(replace, text)


def remove_repeated_chars(text: str, max_repeats: int = 2) -> str:
    """
    Remove repeated characters (e.g., 'helllllo' -> 'hello').
    
    Args:
        text: Input text
        max_repeats: Maximum allowed repetitions
        
    Returns:
        Text with reduced character repetitions
    """
    pattern = re.compile(r'(.)\1{' + str(max_repeats) + r',}')
    return pattern.sub(r'\1' * max_repeats, text)