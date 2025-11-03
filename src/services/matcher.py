"""
Question Matching Service
Uses TF-IDF and cosine similarity to match user queries with FAQ questions
"""
from typing import List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.models.faq import FAQ, FAQDatabase, MatchResult
from src.services.preprocessor import TextPreprocessor
from src.config import MatcherConfig


class MatcherError(Exception):
    """Raised when question matching fails."""
    pass


class QuestionMatcher:
    """
    Question matching service using TF-IDF and cosine similarity.
    
    Matches user queries against FAQ questions to find the most relevant answer.
    """
    
    def __init__(
        self,
        faq_database: FAQDatabase,
        preprocessor: TextPreprocessor,
        config: Optional[MatcherConfig] = None
    ) -> None:
        """
        Initialize question matcher.
        
        Args:
            faq_database: Database of FAQ entries
            preprocessor: Text preprocessor instance
            config: Matcher configuration. Uses default if None.
            
        Raises:
            MatcherError: If initialization fails
        """
        self.faq_database = faq_database
        self.preprocessor = preprocessor
        self.config = config or MatcherConfig()
        
        # Initialize vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.config.max_features,
            ngram_range=self.config.ngram_range,
            lowercase=True,
            strip_accents='unicode'
        )
        
        # Build FAQ corpus and fit vectorizer
        self._build_corpus()
    
    def _build_corpus(self) -> None:
        """
        Build and preprocess FAQ question corpus.
        
        Creates vectors for all FAQ questions including alternates.
        """
        self.corpus_questions: List[str] = []
        self.corpus_faqs: List[FAQ] = []
        self.corpus_original_questions: List[str] = []
        
        # Collect all questions (main + alternates)
        for faq in self.faq_database.faqs:
            for question in faq.all_questions:
                # Store original question
                self.corpus_original_questions.append(question)
                
                # Preprocess and store
                preprocessed = self.preprocessor.preprocess(question)
                self.corpus_questions.append(preprocessed)
                
                # Map back to FAQ
                self.corpus_faqs.append(faq)
        
        if not self.corpus_questions:
            raise MatcherError("No questions found in FAQ database")
        
        # Fit vectorizer on preprocessed corpus
        try:
            self.corpus_vectors = self.vectorizer.fit_transform(
                self.corpus_questions
            )
        except Exception as e:
            raise MatcherError(f"Failed to vectorize FAQ corpus: {e}")
    
    def match(self, user_query: str) -> Optional[MatchResult]:
        """
        Find the best matching FAQ for a user query.
        
        Args:
            user_query: User's question
            
        Returns:
            MatchResult if a good match is found, None otherwise
        """
        if not user_query or not user_query.strip():
            return None
        
        # Preprocess user query
        preprocessed_query = self.preprocessor.preprocess(user_query)
        
        if not preprocessed_query:
            return None
        
        # Get all matches above threshold
        matches = self._get_all_matches(preprocessed_query)
        
        if not matches:
            return None
        
        # Return best match
        return matches[0]
    
    def match_with_alternatives(
        self,
        user_query: str
    ) -> Tuple[Optional[MatchResult], List[MatchResult]]:
        """
        Find best match and alternative suggestions.
        
        Args:
            user_query: User's question
            
        Returns:
            Tuple of (best_match, alternatives)
            - best_match: Best matching result or None
            - alternatives: List of alternative matches
        """
        if not user_query or not user_query.strip():
            return None, []
        
        # Preprocess user query
        preprocessed_query = self.preprocessor.preprocess(user_query)
        
        if not preprocessed_query:
            return None, []
        
        # Get all matches
        all_matches = self._get_all_matches(preprocessed_query)
        
        if not all_matches:
            return None, []
        
        # Best match
        best_match = all_matches[0]
        
        # Get alternatives (excluding duplicates of best match)
        alternatives: List[MatchResult] = []
        seen_faq_ids = {best_match.faq.id}
        
        for match in all_matches[1:]:
            if match.faq.id not in seen_faq_ids:
                alternatives.append(match)
                seen_faq_ids.add(match.faq.id)
                
                if len(alternatives) >= self.config.max_suggestions:
                    break
        
        return best_match, alternatives
    
    def _get_all_matches(self, preprocessed_query: str) -> List[MatchResult]:
        """
        Get all matches above similarity threshold, sorted by score.
        
        Args:
            preprocessed_query: Preprocessed user query
            
        Returns:
            List of MatchResult objects sorted by similarity (highest first)
        """
        # Vectorize query
        try:
            query_vector = self.vectorizer.transform([preprocessed_query])
        except Exception as e:
            raise MatcherError(f"Failed to vectorize query: {e}")
        
        # Calculate cosine similarities
        similarities = cosine_similarity(
            query_vector,
            self.corpus_vectors
        )[0]
        
        # Create match results
        matches: List[MatchResult] = []
        
        for idx, similarity in enumerate(similarities):
            # Filter by threshold
            if similarity >= self.config.similarity_threshold:
                match = MatchResult(
                    faq=self.corpus_faqs[idx],
                    similarity_score=float(similarity),
                    matched_question=self.corpus_original_questions[idx]
                )
                matches.append(match)
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return matches
    
    def get_matches_by_category(
        self,
        user_query: str,
        category: str
    ) -> List[MatchResult]:
        """
        Get matches filtered by category.
        
        Args:
            user_query: User's question
            category: FAQ category to filter by
            
        Returns:
            List of matches in the specified category
        """
        preprocessed_query = self.preprocessor.preprocess(user_query)
        
        if not preprocessed_query:
            return []
        
        all_matches = self._get_all_matches(preprocessed_query)
        
        # Filter by category
        return [
            match for match in all_matches
            if match.faq.category.value == category
        ]
    
    def is_low_confidence(self, match_result: MatchResult) -> bool:
        """
        Check if a match has low confidence.
        
        Args:
            match_result: Match result to check
            
        Returns:
            True if confidence is below threshold
        """
        return match_result.similarity_score < self.config.low_confidence_threshold
    
    def get_similarity_matrix(self) -> np.ndarray:
        """
        Get similarity matrix for all FAQ questions.
        
        Returns:
            Numpy array of similarities between all questions
        """
        return cosine_similarity(self.corpus_vectors, self.corpus_vectors)
    
    def find_similar_faqs(self, faq_id: str, top_n: int = 5) -> List[Tuple[FAQ, float]]:
        """
        Find FAQs similar to a given FAQ.
        
        Args:
            faq_id: ID of the FAQ to find similar questions for
            top_n: Number of similar FAQs to return
            
        Returns:
            List of (FAQ, similarity_score) tuples
        """
        # Find the index of the FAQ
        target_indices = [
            i for i, faq in enumerate(self.corpus_faqs)
            if faq.id == faq_id
        ]
        
        if not target_indices:
            return []
        
        # Use first occurrence
        target_idx = target_indices[0]
        
        # Get similarities
        similarities = cosine_similarity(
            self.corpus_vectors[target_idx:target_idx+1],
            self.corpus_vectors
        )[0]
        
        # Get top N (excluding self)
        similar_indices = np.argsort(similarities)[::-1][1:top_n+1]
        
        results: List[Tuple[FAQ, float]] = []
        seen_ids = {faq_id}
        
        for idx in similar_indices:
            faq = self.corpus_faqs[idx]
            if faq.id not in seen_ids:
                results.append((faq, float(similarities[idx])))
                seen_ids.add(faq.id)
        
        return results[:top_n]
    
    def get_corpus_statistics(self) -> dict[str, int]:
        """
        Get statistics about the FAQ corpus.
        
        Returns:
            Dictionary with corpus statistics
        """
        return {
            'total_faqs': self.faq_database.total_faqs,
            'total_questions': len(self.corpus_questions),
            'avg_questions_per_faq': len(self.corpus_questions) / max(self.faq_database.total_faqs, 1),
            'vocabulary_size': len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0,
            'max_features': self.config.max_features,
        }