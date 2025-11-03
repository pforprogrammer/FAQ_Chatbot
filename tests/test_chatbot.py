"""
Unit Tests for Chatbot Service
"""
import pytest

from src.services.chatbot import Chatbot, ChatbotResponse
from src.models.faq import FAQ, FAQDatabase, FAQCategory, ChatMessage


class TestChatbot:
    """Tests for Chatbot service."""
    
    @pytest.fixture
    def sample_faqs(self) -> list[FAQ]:
        """Fixture providing sample FAQs."""
        return [
            FAQ(
                id="test_001",
                question="What is CodeAlpha?",
                answer="CodeAlpha is a software development company.",
                category=FAQCategory.GENERAL,
                keywords=["codealpha", "company"],
                alternate_questions=["Tell me about CodeAlpha"]
            ),
            FAQ(
                id="test_002",
                question="How to apply?",
                answer="Visit www.codealpha.tech to apply.",
                category=FAQCategory.GENERAL,
                keywords=["apply", "application"]
            ),
            FAQ(
                id="test_003",
                question="What is Python?",
                answer="Python is a programming language.",
                category=FAQCategory.TECHNICAL,
                keywords=["python", "programming"]
            ),
        ]
    
    @pytest.fixture
    def chatbot(self, sample_faqs: list[FAQ]) -> Chatbot:
        """Fixture providing chatbot instance."""
        database = FAQDatabase(faqs=sample_faqs)
        return Chatbot(faq_database=database)
    
    def test_chatbot_initialization(self, chatbot: Chatbot) -> None:
        """Test chatbot initializes correctly."""
        assert chatbot is not None
        assert chatbot.faq_database is not None
        assert chatbot.preprocessor is not None
        assert chatbot.matcher is not None
        assert len(chatbot.conversation_history) == 0
    
    def test_ask_basic_question(self, chatbot: Chatbot) -> None:
        """Test asking a basic question."""
        response = chatbot.ask("What is CodeAlpha?")
        
        assert isinstance(response, ChatbotResponse)
        assert response.message is not None
        assert "CodeAlpha" in response.message
        assert response.match_result is not None
        assert not response.is_fallback

    def test_ask_empty_query(self, chatbot: Chatbot) -> None:
        """Test asking empty query."""
        response = chatbot.ask("")
        
        assert isinstance(response, ChatbotResponse)
        assert response.is_fallback
        assert response.match_result is None
    
    def test_ask_no_match(self, chatbot: Chatbot) -> None:
        """Test query with no matching FAQ."""
        response = chatbot.ask("How to cook pasta?")
        
        assert isinstance(response, ChatbotResponse)
        assert response.is_fallback
        assert response.match_result is None
        assert "couldn't find an answer" in response.message.lower()
    
    def test_conversation_history(self, chatbot: Chatbot) -> None:
        """Test conversation history is maintained."""
        assert len(chatbot.conversation_history) == 0
        
        chatbot.ask("What is CodeAlpha?")
        assert len(chatbot.conversation_history) == 2  # user + assistant
        
        chatbot.ask("How to apply?")
        assert len(chatbot.conversation_history) == 4
        
        # Check message roles
        history = chatbot.get_conversation_history()
        assert history[0].role == "user"
        assert history[1].role == "assistant"
        assert history[2].role == "user"
        assert history[3].role == "assistant"
    
    def test_clear_history(self, chatbot: Chatbot) -> None:
        """Test clearing conversation history."""
        chatbot.ask("What is CodeAlpha?")
        chatbot.ask("How to apply?")
        
        assert len(chatbot.conversation_history) > 0
        
        chatbot.clear_history()
        assert len(chatbot.conversation_history) == 0
    
    def test_get_faqs_by_category(self, chatbot: Chatbot) -> None:
        """Test getting FAQs by category."""
        technical_faqs = chatbot.get_faqs_by_category(FAQCategory.TECHNICAL)
        
        assert len(technical_faqs) > 0
        assert all(faq.category == FAQCategory.TECHNICAL for faq in technical_faqs)
    
    def test_get_all_categories(self, chatbot: Chatbot) -> None:
        """Test getting all categories."""
        categories = chatbot.get_all_categories()
        
        assert len(categories) > 0
        assert all(isinstance(cat, FAQCategory) for cat in categories)
    
    def test_search_by_keyword(self, chatbot: Chatbot) -> None:
        """Test keyword search."""
        results = chatbot.search_by_keyword("python")
        
        assert len(results) > 0
        assert any("python" in faq.keywords for faq in results)
    
    def test_get_random_faq(self, chatbot: Chatbot) -> None:
        """Test getting random FAQ."""
        faq = chatbot.get_random_faq()
        
        assert isinstance(faq, FAQ)
        assert faq.id in [f.id for f in chatbot.faq_database.faqs]
    
    def test_get_statistics(self, chatbot: Chatbot) -> None:
        """Test getting chatbot statistics."""
        chatbot.ask("What is CodeAlpha?")
        
        stats = chatbot.get_statistics()
        
        assert 'total_faqs' in stats
        assert 'total_categories' in stats
        assert 'conversation_turns' in stats
        assert 'matcher_stats' in stats
        
        assert stats['total_faqs'] == 3
        assert stats['conversation_turns'] == 2
    
    def test_low_confidence_response(self, chatbot: Chatbot) -> None:
        """Test low confidence match generates appropriate response."""
        # Query that might match but with low confidence
        response = chatbot.ask("Tell me something about software")
        
        assert isinstance(response, ChatbotResponse)
        # Response should either be a match or fallback
        assert response.message is not None
    
    def test_alternatives_in_response(self, chatbot: Chatbot) -> None:
        """Test alternatives are provided when available."""
        response = chatbot.ask("What is programming?")
        
        # Should have either a match with alternatives or fallback
        if response.match_result:
            assert isinstance(response.alternatives, list)
    
    def test_multiple_conversations(self, chatbot: Chatbot) -> None:
        """Test multiple conversation turns."""
        response1 = chatbot.ask("What is CodeAlpha?")
        response2 = chatbot.ask("How to apply?")
        response3 = chatbot.ask("What is Python?")
        
        assert all(isinstance(r, ChatbotResponse) for r in [response1, response2, response3])
        assert len(chatbot.conversation_history) == 6  # 3 user + 3 assistant
    
    def test_chat_message_with_match_result(self, chatbot: Chatbot) -> None:
        """Test chat messages store match results."""
        chatbot.ask("What is CodeAlpha?")
        
        history = chatbot.get_conversation_history()
        assistant_message = history[1]
        
        assert assistant_message.role == "assistant"
        # Should have match result for successful match
        if not "couldn't find" in assistant_message.content.lower():
            assert assistant_message.match_result is not None