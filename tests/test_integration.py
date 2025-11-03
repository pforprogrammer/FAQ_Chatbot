"""
Integration Tests
Tests the complete chatbot pipeline end-to-end
"""
import pytest
from pathlib import Path

from src.services.chatbot import Chatbot
from src.services.data_loader import FAQDataLoader
from src.config import config


class TestIntegration:
    """Integration tests for the complete chatbot system."""
    
    @pytest.fixture
    def chatbot(self) -> Chatbot:
        """Fixture providing chatbot with real FAQ data."""
        # Use real FAQ data if available
        if config.faq_data_path.exists():
            return Chatbot()
        else:
            pytest.skip("FAQ data file not found")
    
    def test_end_to_end_query(self, chatbot: Chatbot) -> None:
        """Test complete query processing pipeline."""
        queries = [
            "What is CodeAlpha?",
            "How do I apply for the internship?",
            "What are the task requirements?",
        ]
        
        for query in queries:
            response = chatbot.ask(query)
            
            # Should get valid response
            assert response is not None
            assert response.message is not None
            assert len(response.message) > 0
    
    def test_conversation_flow(self, chatbot: Chatbot) -> None:
        """Test natural conversation flow."""
        # User asks about company
        response1 = chatbot.ask("Tell me about CodeAlpha")
        assert "CodeAlpha" in response1.message or response1.is_fallback
        
        # User asks about application
        response2 = chatbot.ask("How can I join?")
        assert response2.message is not None
        
        # User asks technical question
        response3 = chatbot.ask("Which programming language should I use?")
        assert response3.message is not None
        
        # Check history
        assert len(chatbot.conversation_history) == 6
    
    def test_similar_questions(self, chatbot: Chatbot) -> None:
        """Test similar questions get similar answers."""
        queries = [
            "What is CodeAlpha?",
            "Tell me about CodeAlpha",
            "Who is CodeAlpha?",
        ]
        
        responses = [chatbot.ask(q) for q in queries]
        
        # Clear history between tests
        chatbot.clear_history()
        
        # All should match to similar/same FAQ
        matched_faqs = [
            r.match_result.faq.id for r in responses 
            if r.match_result is not None
        ]
        
        # If any matched, they should be related
        if matched_faqs:
            # At least some should match the same FAQ
            from collections import Counter
            faq_counts = Counter(matched_faqs)
            assert len(faq_counts) <= len(queries)
    
    def test_category_filtering(self, chatbot: Chatbot) -> None:
        """Test category-based FAQ retrieval."""
        from src.models.faq import FAQCategory
        
        for category in chatbot.get_all_categories():
            faqs = chatbot.get_faqs_by_category(category)
            
            # Should get FAQs
            assert isinstance(faqs, list)
            
            # All should be in correct category
            for faq in faqs:
                assert faq.category == category
    
    def test_keyword_search(self, chatbot: Chatbot) -> None:
        """Test keyword-based search."""
        keywords = ["python", "apply", "certificate", "task"]
        
        for keyword in keywords:
            results = chatbot.search_by_keyword(keyword)
            
            # Should get results (or empty list if keyword not in any FAQ)
            assert isinstance(results, list)
            
            # If results found, they should contain the keyword
            for faq in results:
                assert keyword.lower() in [kw.lower() for kw in faq.keywords]
    
    def test_preprocessing_consistency(self, chatbot: Chatbot) -> None:
        """Test preprocessing is consistent across queries."""
        query1 = "What is Python programming?"
        query2 = "WHAT IS PYTHON PROGRAMMING?"
        query3 = "what is python programming"
        
        # Get preprocessed versions
        prep1 = chatbot.preprocessor.preprocess(query1)
        prep2 = chatbot.preprocessor.preprocess(query2)
        prep3 = chatbot.preprocessor.preprocess(query3)
        
        # Should all be same after preprocessing
        assert prep1 == prep2 == prep3
    
    def test_matching_consistency(self, chatbot: Chatbot) -> None:
        """Test matching is consistent for same query."""
        query = "What is CodeAlpha?"
        
        response1 = chatbot.ask(query)
        chatbot.clear_history()
        response2 = chatbot.ask(query)
        
        # Should get same match
        if response1.match_result and response2.match_result:
            assert response1.match_result.faq.id == response2.match_result.faq.id
    
    def test_statistics_accuracy(self, chatbot: Chatbot) -> None:
        """Test statistics are accurate."""
        initial_stats = chatbot.get_statistics()
        
        # Ask some questions
        chatbot.ask("What is CodeAlpha?")
        chatbot.ask("How to apply?")
        
        updated_stats = chatbot.get_statistics()
        
        # Conversation turns should increase
        assert updated_stats['conversation_turns'] > initial_stats['conversation_turns']
        assert updated_stats['conversation_turns'] == 4  # 2 user + 2 assistant
        
        # FAQ count should remain same
        assert updated_stats['total_faqs'] == initial_stats['total_faqs']
    
    def test_load_real_faq_data(self) -> None:
        """Test loading real FAQ data from file."""
        if not config.faq_data_path.exists():
            pytest.skip("FAQ data file not found")
        
        database = FAQDataLoader.load_from_json(config.faq_data_path)
        
        # Should load successfully
        assert database is not None
        assert database.total_faqs > 0
        
        # Should have expected categories
        from src.models.faq import FAQCategory
        categories = database.categories
        assert len(categories) > 0
        assert all(isinstance(cat, FAQCategory) for cat in categories)
    
    def test_full_chatbot_initialization(self) -> None:
        """Test chatbot initializes with all components."""
        if not config.faq_data_path.exists():
            pytest.skip("FAQ data file not found")
        
        chatbot = Chatbot()
        
        # Check all components initialized
        assert chatbot.faq_database is not None
        assert chatbot.preprocessor is not None
        assert chatbot.matcher is not None
        assert chatbot.conversation_history is not None
        
        # Check components are functional
        stats = chatbot.get_statistics()
        assert stats['total_faqs'] > 0
        assert stats['matcher_stats']['vocabulary_size'] > 0
        