"""
Command-Line Chatbot Test Interface
Interactive CLI for testing the chatbot
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.chatbot import Chatbot
from src.config import config


def print_separator(char: str = "=", length: int = 70) -> None:
    """Print a separator line."""
    print(char * length)


def print_response(response) -> None:
    """Print chatbot response nicely formatted."""
    print_separator("-")
    print("🤖 Assistant:")
    print_separator("-")
    print(response.message)
    
    if response.match_result:
        print(f"\n📊 Confidence: {response.match_result.confidence_percentage}% "
              f"({response.match_result.confidence_level})")
        print(f"📝 Matched: {response.match_result.matched_question}")
        print(f"🏷️  Category: {response.match_result.faq.category.value}")
        
        if response.alternatives:
            print(f"\n💡 {len(response.alternatives)} alternative(s) available")
    
    print_separator("-")


def display_help() -> None:
    """Display help information."""
    print("\n📖 Available Commands:")
    print("  /help       - Show this help message")
    print("  /stats      - Show chatbot statistics")
    print("  /history    - Show conversation history")
    print("  /clear      - Clear conversation history")
    print("  /categories - List all FAQ categories")
    print("  /search     - Search FAQs by keyword")
    print("  /quit       - Exit the chatbot")
    print()


def display_stats(chatbot: Chatbot) -> None:
    """Display chatbot statistics."""
    stats = chatbot.get_statistics()
    
    print_separator("-")
    print("📊 Chatbot Statistics")
    print_separator("-")
    print(f"Total FAQs:          {stats['total_faqs']}")
    print(f"Total Categories:    {stats['total_categories']}")
    print(f"Conversation Turns:  {stats['conversation_turns']}")
    print(f"Vocabulary Size:     {stats['matcher_stats']['vocabulary_size']}")
    print(f"Total Questions:     {stats['matcher_stats']['total_questions']}")
    print_separator("-")


def display_history(chatbot: Chatbot) -> None:
    """Display conversation history."""
    history = chatbot.get_conversation_history()
    
    if not history:
        print("\n📭 No conversation history yet.")
        return
    
    print_separator("-")
    print("📜 Conversation History")
    print_separator("-")
    
    for i, message in enumerate(history, 1):
        icon = "👤" if message.role == "user" else "🤖"
        print(f"\n{i}. {icon} {message.role.capitalize()}:")
        print(f"   {message.content[:100]}...")
        if message.match_result:
            print(f"   (Confidence: {message.match_result.confidence_percentage}%)")
    
    print_separator("-")


def display_categories(chatbot: Chatbot) -> None:
    """Display all FAQ categories with counts."""
    categories = chatbot.get_all_categories()
    
    print_separator("-")
    print("🏷️  FAQ Categories")
    print_separator("-")
    
    for category in categories:
        faqs = chatbot.get_faqs_by_category(category)
        print(f"  {category.value.capitalize():15s} - {len(faqs)} FAQs")
    
    print_separator("-")


def search_faqs(chatbot: Chatbot) -> None:
    """Search FAQs by keyword."""
    keyword = input("\n🔍 Enter keyword to search: ").strip()
    
    if not keyword:
        print("❌ Empty keyword!")
        return
    
    results = chatbot.search_by_keyword(keyword)
    
    print_separator("-")
    print(f"🔍 Search Results for '{keyword}'")
    print_separator("-")
    
    if not results:
        print(f"No FAQs found with keyword '{keyword}'")
    else:
        print(f"Found {len(results)} FAQ(s):\n")
        for i, faq in enumerate(results, 1):
            print(f"{i}. {faq.question}")
            print(f"   Category: {faq.category.value}")
            print(f"   Answer: {faq.answer[:80]}...")
            print()
    
    print_separator("-")


def main() -> None:
    """Main CLI loop."""
    print_separator()
    print("🤖 CodeAlpha FAQ Chatbot - Interactive CLI")
    print_separator()
    
    # Check if FAQ data exists
    if not config.faq_data_path.exists():
        print(f"❌ Error: FAQ data file not found at {config.faq_data_path}")
        print("Please ensure data/faqs.json exists.")
        return
    
    # Initialize chatbot
    print("\n⏳ Initializing chatbot...")
    try:
        chatbot = Chatbot()
        print("✅ Chatbot initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        return
    
    # Display initial stats
    stats = chatbot.get_statistics()
    print(f"📚 Loaded {stats['total_faqs']} FAQs in {stats['total_categories']} categories")
    print("\nType /help for available commands or start asking questions!")
    print("Type /quit to exit\n")
    
    # Main conversation loop
    while True:
        print_separator()
        try:
            user_input = input("👤 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Handle commands
        if user_input.startswith('/'):
            command = user_input.lower()
            
            if command == '/quit' or command == '/exit':
                print("\n👋 Goodbye!")
                break
            elif command == '/help':
                display_help()
            elif command == '/stats':
                display_stats(chatbot)
            elif command == '/history':
                display_history(chatbot)
            elif command == '/clear':
                chatbot.clear_history()
                print("✅ Conversation history cleared!")
            elif command == '/categories':
                display_categories(chatbot)
            elif command == '/search':
                search_faqs(chatbot)
            else:
                print(f"❌ Unknown command: {command}")
                print("Type /help for available commands")
        else:
            # Process user query
            try:
                response = chatbot.ask(user_input)
                print()
                print_response(response)
            except Exception as e:
                print(f"\n❌ Error processing query: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)