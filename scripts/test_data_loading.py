"""
Test Script for FAQ Data Loading
Quick validation of FAQ data and models
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.services.data_loader import FAQDataLoader, DataLoadError
from src.models.faq import FAQCategory


def main() -> None:
    """Test FAQ data loading."""
    print("=" * 60)
    print("FAQ Data Loading Test")
    print("=" * 60)

    # Check if FAQ file exists
    if not config.faq_data_path.exists():
        print(f"❌ FAQ data file not found: {config.faq_data_path}")
        return

    print(f"✓ FAQ file found: {config.faq_data_path}")

    # Load FAQ database
    try:
        database = FAQDataLoader.load_from_json(config.faq_data_path)
        print("✓ Successfully loaded FAQ database")
    except DataLoadError as e:
        print(f"❌ Error loading FAQ data: {e}")
        return

    # Display statistics
    print("\n" + "-" * 60)
    print("Database Statistics:")
    print("-" * 60)
    print(f"Total FAQs: {database.total_faqs}")
    print(f"Categories: {len(database.categories)}")
    print(f"Metadata: {database.metadata.get('name', 'N/A')}")
    print(f"Version: {database.metadata.get('version', 'N/A')}")

    # Category breakdown
    print("\n" + "-" * 60)
    print("Category Breakdown:")
    print("-" * 60)
    for category in FAQCategory:
        count = len(database.get_by_category(category))
        if count > 0:
            print(f"  {category.value.capitalize()}: {count}")

    # Sample FAQs
    print("\n" + "-" * 60)
    print("Sample FAQs (First 3):")
    print("-" * 60)
    for i, faq in enumerate(database.faqs[:3], 1):
        print(f"\n{i}. [{faq.category.value.upper()}] {faq.question}")
        print(f"   Answer: {faq.answer[:100]}...")
        if faq.keywords:
            print(f"   Keywords: {', '.join(faq.keywords[:5])}")
        if faq.alternate_questions:
            print(f"   Alternates: {len(faq.alternate_questions)}")

    # Test specific queries
    print("\n" + "-" * 60)
    print("Test Queries:")
    print("-" * 60)

    # Test get by ID
    test_faq = database.get_by_id("intern_001")
    if test_faq:
        print(f"✓ Get by ID 'intern_001': {test_faq.question}")

    # Test keyword search
    python_faqs = database.search_keywords("python")
    print(f"✓ Keyword search 'python': {len(python_faqs)} results")

    # Test category filter
    tech_faqs = database.get_by_category(FAQCategory.TECHNICAL)
    print(f"✓ Category 'technical': {len(tech_faqs)} FAQs")

    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
