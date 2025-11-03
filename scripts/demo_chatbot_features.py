"""
Chatbot Features Demo
Demonstrates all chatbot capabilities
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.chatbot import Chatbot
from src.config import config


def print_section(title: str) -> None:
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_basic_queries(chatbot: Chatbot) -> None:
    """Demo basic question answering."""
    print_section("1. Basic Question Answering")
    
    queries = [
        "What is CodeAlpha?",
        "How do I apply for the internship?",
        "What certificates will I receive?",
    ]
    
    for query in queries:
        print(f"\n👤 User: {query}")
        response = chatbot.ask(query)
        print(f"🤖 Bot: {response.message[:150]}...")
        if response.match_result:
            print(f"   Confidence: {response.match_result.confidence_percentage}%")


def demo_similar_questions(chatbot: Chatbot) -> None:
    """Demo handling similar questions."""
    print_section("2. Similar Question Handling")
    
    chatbot.clear_history()
    
    similar_queries = [
        "What is CodeAlpha?",
        "Tell me about CodeAlpha",
        "Who is CodeAlpha?",
        "Explain CodeAlpha to me",
    ]
    
    print("\nAsking similar questions...")
    for query in similar_queries:
        print(f"\n👤 User: {query}")
        response = chatbot.ask(query)
        if response.match_result:
            print(f"🤖 Matched: {response.match_result.faq.question}")
            print(f"   Confidence: {response.match_result.confidence_percentage}%")


def demo_no_match(chatbot: Chatbot) -> None:
    """Demo handling queries with no match."""
    print_section("3. No Match Handling")
    
    chatbot.clear_history()
    
    query = "How to cook pasta?"
    print(f"\n👤 User: {query}")
    response = chatbot.ask(query)
    print(f"🤖 Bot: {response.message[:200]}...")
    print(f"   Is Fallback: {response.is_fallback}")


def demo_alternatives(chatbot: Chatbot) -> None:
    """Demo alternative suggestions."""
    print_section("4. Alternative Suggestions")
    
    chatbot.clear_history()
    
    query = "programming language"
    print(f"\n👤 User: {query}")
    response = chatbot.ask(query)
    
    if response.alternatives:
        print(f"\n🤖 Found {len(response.alternatives)} alternative(s):")
        for i, alt in enumerate(response.alternatives[:3], 1):
            print(f"   {i}. {alt.faq.question} ({alt.confidence_percentage}%)")


def demo_categories(chatbot: Chatbot) -> None:
    """Demo category browsing."""
    print_section("5. Category Browsing")
    
    categories = chatbot.get_all_categories()
    print(f"\nAvailable categories: {len(categories)}")
    
    for category in categories:
        faqs = chatbot.get_faqs_by_category(category)
        print(f"\n📁 {category.value.capitalize()}: {len(faqs)} FAQs")
        for i, faq in enumerate(faqs[:2], 1):
            print(f"   {i}. {faq.question}")


def demo_keyword_search(chatbot: Chatbot) -> None:
    """Demo keyword search."""
    print_section("6. Keyword Search")
    
    keywords = ["python", "certificate", "task"]
    
    for keyword in keywords:
        results = chatbot.search_by_keyword(keyword)
        print(f"\n🔍 Searching for '{keyword}': {len(results)} result(s)")
        for faq in results[:2]:
            print(f"   - {faq.question}")


def demo_conversation_history(chatbot: Chatbot) -> None:
    """Demo conversation history."""
    print_section("7. Conversation History")
    
    chatbot.clear_history()
    
    # Have a conversation
    queries = [
        "What is CodeAlpha?",
        "How many tasks do I need to complete?",
    ]
    
    for query in queries:
        chatbot.ask(query)
    
    history = chatbot.get_conversation_history()
    print(f"\nConversation has {len(history)} messages:")
    
    for i, message in enumerate(history, 1):
        role_icon = "👤" if message.role == "user" else "🤖"
        print(f"\n{i}. {role_icon} {message.role.capitalize()}:")
        print(f"   {message.content[:100]}...")


def demo_statistics(chatbot: Chatbot) -> None:
    """Demo statistics."""
    print_section("8. Chatbot Statistics")
    
    stats = chatbot.get_statistics()
    
    print(f"\nTotal FAQs:           {stats['total_faqs']}")
    print(f"Total Categories:     {stats['total_categories']}")
    print(f"Conversation Turns:   {stats['conversation_turns']}")
    print(f"Vocabulary Size:      {stats['matcher_stats']['vocabulary_size']}")
    print(f"Total Questions:      {stats['matcher_stats']['total_questions']}")
    print(f"Avg Q per FAQ:        {stats['matcher_stats']['avg_questions_per_faq']:.2f}")


def main() -> None:
    """Run all demos."""
    print("=" * 70)
    print("  CodeAlpha FAQ Chatbot - Feature Demonstration")
    print("=" * 70)
    
    # Check FAQ data
    if not config.faq_data_path.exists():
        print(f"\n❌ Error: FAQ data not found at {config.faq_data_path}")
        return
    
    # Initialize chatbot
    print("\n⏳ Initializing chatbot...")
    try:
        chatbot = Chatbot()
        print("✅ Chatbot initialized successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Run demos
    try:
        demo_basic_queries(chatbot)
        demo_similar_questions(chatbot)
        demo_no_match(chatbot)
        demo_alternatives(chatbot)
        demo_categories(chatbot)
        demo_keyword_search(chatbot)
        demo_conversation_history(chatbot)
        demo_statistics(chatbot)
        
        print("\n" + "=" * 70)
        print("  ✅ All demos completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")


if __name__ == "__main__":
    main()