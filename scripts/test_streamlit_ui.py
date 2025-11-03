"""
Streamlit UI Testing Script
Validates UI components and functionality
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.chatbot import Chatbot
from src.config import config


def test_imports() -> bool:
    """Test that all UI components can be imported."""
    print("Testing imports...")
    try:
        from src.ui.components import (
            initialize_session_state,
            apply_custom_styles,
            render_header,
            render_chat_interface,
            render_sidebar,
        )
        print("✓ All UI components imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_chatbot_initialization() -> bool:
    """Test chatbot can be initialized."""
    print("\nTesting chatbot initialization...")
    try:
        chatbot = Chatbot()
        print(f"✓ Chatbot initialized with {chatbot.faq_database.total_faqs} FAQs")
        return True
    except Exception as e:
        print(f"✗ Chatbot initialization failed: {e}")
        return False


def test_session_state_structure() -> bool:
    """Test session state keys are properly defined."""
    print("\nTesting session state structure...")
    try:
        assert hasattr(config, 'SESSION_MESSAGES')
        assert hasattr(config, 'SESSION_CHATBOT')
        print("✓ Session state keys defined")
        return True
    except AssertionError:
        print("✗ Session state keys not found in config")
        return False


def test_response_generation() -> bool:
    """Test response generation works."""
    print("\nTesting response generation...")
    try:
        chatbot = Chatbot()
        response = chatbot.ask("What is CodeAlpha?")
        
        assert response.message is not None
        assert len(response.message) > 0
        print(f"✓ Response generated: {response.message[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Response generation failed: {e}")
        return False


def test_category_browser() -> bool:
    """Test category browsing functionality."""
    print("\nTesting category browser...")
    try:
        chatbot = Chatbot()
        categories = chatbot.get_all_categories()
        
        assert len(categories) > 0
        
        for category in categories:
            faqs = chatbot.get_faqs_by_category(category)
            print(f"  {category.value.capitalize()}: {len(faqs)} FAQs")
        
        print("✓ Category browser working")
        return True
    except Exception as e:
        print(f"✗ Category browser failed: {e}")
        return False


def test_keyword_search() -> bool:
    """Test keyword search functionality."""
    print("\nTesting keyword search...")
    try:
        chatbot = Chatbot()
        results = chatbot.search_by_keyword("python")
        
        print(f"✓ Keyword search found {len(results)} result(s)")
        return True
    except Exception as e:
        print(f"✗ Keyword search failed: {e}")
        return False


def test_statistics() -> bool:
    """Test statistics generation."""
    print("\nTesting statistics...")
    try:
        chatbot = Chatbot()
        stats = chatbot.get_statistics()
        
        assert 'total_faqs' in stats
        assert 'total_categories' in stats
        assert 'conversation_turns' in stats
        
        print(f"✓ Statistics generated:")
        print(f"  Total FAQs: {stats['total_faqs']}")
        print(f"  Total Categories: {stats['total_categories']}")
        return True
    except Exception as e:
        print(f"✗ Statistics generation failed: {e}")
        return False


def main() -> None:
    """Run all tests."""
    print("=" * 70)
    print("Streamlit UI Testing")
    print("=" * 70)
    
    tests = [
        test_imports,
        test_chatbot_initialization,
        test_session_state_structure,
        test_response_generation,
        test_category_browser,
        test_keyword_search,
        test_statistics,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓ All tests passed! Ready to run Streamlit app.")
        print("\nRun the app with:")
        print("  streamlit run src/main.py")
    else:
        print("\n✗ Some tests failed. Please fix issues before running the app.")
        sys.exit(1)


if __name__ == "__main__":
    main()