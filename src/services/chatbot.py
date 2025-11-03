"""
Main Chatbot Service
Orchestrates preprocessing, matching, and response generation
"""
from typing import List, Optional, Tuple
from dataclasses import dataclass

from src.models.faq import FAQ, FAQDatabase, MatchResult, ChatMessage, FAQCategory
from src.services.preprocessor import TextPreprocessor
from src.services.matcher import QuestionMatcher
from src.services.data_loader import FAQDataLoader
from src.config import config, MatcherConfig, PreprocessorConfig


@dataclass
class ChatbotResponse:
    """
    Represents a chatbot response.
    
    Attributes:
        message: Response message
        match_result: Match result if found
        alternatives: Alternative suggestions
        is_fallback: Whether this is a fallback response
    """
    message: str
    match_result: Optional[MatchResult] = None
    alternatives: List[MatchResult] = None
    is_fallback: bool = False
    
    def __post_init__(self) -> None:
        """Initialize alternatives list if None."""
        if self.alternatives is None:
            self.alternatives = []


class Chatbot:
    """
    Main chatbot service for FAQ answering.
    
    Handles user queries, matches them with FAQs, and generates responses.
    """
    
    def __init__(
        self,
        faq_database: Optional[FAQDatabase] = None,
        preprocessor_config: Optional[PreprocessorConfig] = None,
        matcher_config: Optional[MatcherConfig] = None
    ) -> None:
        """
        Initialize chatbot.
        
        Args:
            faq_database: FAQ database. Loads from config if None.
            preprocessor_config: Preprocessing configuration
            matcher_config: Matching configuration
        """
        # Load FAQ database
        if faq_database is None:
            self.faq_database = FAQDataLoader.load_from_json(
                config.faq_data_path
            )
        else:
            self.faq_database = faq_database
        
        # Initialize components
        self.preprocessor = TextPreprocessor(
            preprocessor_config or config.preprocessor
        )
        
        self.matcher = QuestionMatcher(
            faq_database=self.faq_database,
            preprocessor=self.preprocessor,
            config=matcher_config or config.matcher
        )
        
        # Conversation history
        self.conversation_history: List[ChatMessage] = []
    
    def ask(self, user_query: str) -> ChatbotResponse:
        """
        Process user query and generate response.
        
        Args:
            user_query: User's question
            
        Returns:
            ChatbotResponse with answer and match information
        """
        # Add user message to history
        self._add_to_history("user", user_query)
        
        # Handle empty query
        if not user_query or not user_query.strip():
            response = self._generate_empty_query_response()
            self._add_to_history("assistant", response.message)
            return response
        
        # Match query with FAQs
        best_match, alternatives = self.matcher.match_with_alternatives(
            user_query
        )
        
        # Generate response
        if best_match is None:
            response = self._generate_no_match_response()
        elif self.matcher.is_low_confidence(best_match):
            response = self._generate_low_confidence_response(
                best_match,
                alternatives
            )
        else:
            response = self._generate_answer_response(
                best_match,
                alternatives
            )
        
        # Add assistant response to history
        self._add_to_history(
            "assistant",
            response.message,
            response.match_result
        )
        
        return response
    
    def _generate_answer_response(
        self,
        match: MatchResult,
        alternatives: List[MatchResult]
    ) -> ChatbotResponse:
        """Generate response with matched answer."""
        message = match.faq.answer
        
        return ChatbotResponse(
            message=message,
            match_result=match,
            alternatives=alternatives,
            is_fallback=False
        )
    
    def _generate_low_confidence_response(
        self,
        match: MatchResult,
        alternatives: List[MatchResult]
    ) -> ChatbotResponse:
        """Generate response for low-confidence matches."""
        message = (
            f"I think you're asking about: **{match.faq.question}**\n\n"
            f"{match.faq.answer}\n\n"
            f"*Note: I'm only {match.confidence_percentage}% confident about this answer.*"
        )
        
        if alternatives:
            message += "\n\n**Did you mean one of these?**\n"
            for i, alt in enumerate(alternatives[:3], 1):
                message += f"{i}. {alt.faq.question}\n"
        
        return ChatbotResponse(
            message=message,
            match_result=match,
            alternatives=alternatives,
            is_fallback=False
        )
    
    def _generate_no_match_response(self) -> ChatbotResponse:
        """Generate response when no match is found."""
        message = (
            "I'm sorry, I couldn't find an answer to your question in my knowledge base. "
            "Please try rephrasing your question or contact support:\n\n"
            "📧 Email: services@codealpha.tech\n"
            "💬 WhatsApp: +91 8052293611\n"
            "🌐 Website: www.codealpha.tech"
        )
        
        # Suggest browsing categories
        categories = self.faq_database.categories
        if categories:
            message += "\n\n**Or browse these categories:**\n"
            for cat in sorted(categories, key=lambda x: x.value):
                count = len(self.faq_database.get_by_category(cat))
                message += f"- {cat.value.capitalize()} ({count} FAQs)\n"
        
        return ChatbotResponse(
            message=message,
            match_result=None,
            alternatives=[],
            is_fallback=True
        )
    
    def _generate_empty_query_response(self) -> ChatbotResponse:
        """Generate response for empty queries."""
        message = (
            "Hi! I'm here to help answer your questions about CodeAlpha internships. "
            "Feel free to ask me anything!"
        )
        
        return ChatbotResponse(
            message=message,
            match_result=None,
            alternatives=[],
            is_fallback=True
        )
    
    def _add_to_history(
        self,
        role: str,
        content: str,
        match_result: Optional[MatchResult] = None
    ) -> None:
        """Add message to conversation history."""
        message = ChatMessage(
            role=role,
            content=content,
            match_result=match_result
        )
        self.conversation_history.append(message)
    
    def get_faqs_by_category(self, category: FAQCategory) -> List[FAQ]:
        """Get all FAQs in a specific category."""
        return self.faq_database.get_by_category(category)
    
    def get_all_categories(self) -> List[FAQCategory]:
        """Get all available FAQ categories."""
        return sorted(self.faq_database.categories, key=lambda x: x.value)
    
    def search_by_keyword(self, keyword: str) -> List[FAQ]:
        """Search FAQs by keyword."""
        return self.faq_database.search_keywords(keyword)
    
    def get_conversation_history(self) -> List[ChatMessage]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def get_random_faq(self) -> FAQ:
        """Get a random FAQ for suggestions."""
        import random
        return random.choice(self.faq_database.faqs)
    
    def get_statistics(self) -> dict[str, any]:
        """
        Get chatbot statistics.
        
        Returns:
            Dictionary with various statistics
        """
        return {
            'total_faqs': self.faq_database.total_faqs,
            'total_categories': len(self.faq_database.categories),
            'conversation_turns': len(self.conversation_history),
            'matcher_stats': self.matcher.get_corpus_statistics(),
        }