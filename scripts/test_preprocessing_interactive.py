"""
Interactive Preprocessing Test
Allows testing preprocessing with custom inputs
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.preprocessor import TextPreprocessor
from src.services.preprocessing_pipeline import PreprocessingPipeline
from src.config import PreprocessorConfig


def print_separator(char: str = "=", length: int = 70) -> None:
    """Print a separator line."""
    print(char * length)


def display_menu() -> None:
    """Display the main menu."""
    print_separator()
    print("Interactive Preprocessing Test")
    print_separator()
    print("\nOptions:")
    print("1. Test basic preprocessing")
    print("2. Test advanced pipeline")
    print("3. Compare preprocessing methods")
    print("4. View preprocessing statistics")
    print("5. Test with sample FAQ questions")
    print("6. Exit")
    print()


def test_basic_preprocessing() -> None:
    """Test basic preprocessing."""
    preprocessor = TextPreprocessor()
    
    print_separator("-")
    print("Basic Preprocessing Test")
    print_separator("-")
    
    text = input("\nEnter text to preprocess: ").strip()
    
    if not text:
        print("❌ Empty input!")
        return
    
    result = preprocessor.preprocess(text)
    
    print(f"\nOriginal:     {text}")
    print(f"Preprocessed: {result}")
    
    stats = preprocessor.get_text_statistics(text)
    print(f"\nStatistics:")
    print(f"  Original tokens:  {stats['original_tokens']}")
    print(f"  Final tokens:     {stats['final_tokens']}")
    print(f"  Removed tokens:   {stats['removed_tokens']}")
    print(f"  Unique tokens:    {stats['unique_tokens']}")


def test_advanced_pipeline() -> None:
    """Test advanced preprocessing pipeline."""
    pipeline = PreprocessingPipeline(enable_advanced=True)
    
    print_separator("-")
    print("Advanced Pipeline Test")
    print_separator("-")
    
    text = input("\nEnter text to preprocess: ").strip()
    
    if not text:
        print("❌ Empty input!")
        return
    
    result = pipeline.process(text)
    
    print(f"\nOriginal:     {text}")
    print(f"Preprocessed: {result}")
    
    print(f"\nPipeline steps:")
    for i, step in enumerate(pipeline.get_enabled_steps(), 1):
        print(f"  {i}. {step}")


def compare_methods() -> None:
    """Compare different preprocessing methods."""
    print_separator("-")
    print("Compare Preprocessing Methods")
    print_separator("-")
    
    text = input("\nEnter text to preprocess: ").strip()
    
    if not text:
        print("❌ Empty input!")
        return
    
    print(f"\nOriginal: {text}\n")
    
    # Method 1: Basic
    preprocessor_basic = TextPreprocessor()
    result_basic = preprocessor_basic.preprocess(text)
    print(f"1. Basic:            {result_basic}")
    
    # Method 2: No lemmatization
    config_no_lemma = PreprocessorConfig(use_lemmatization=False)
    preprocessor_no_lemma = TextPreprocessor(config_no_lemma)
    result_no_lemma = preprocessor_no_lemma.preprocess(text)
    print(f"2. No Lemmatization: {result_no_lemma}")
    
    # Method 3: Advanced pipeline
    pipeline = PreprocessingPipeline(enable_advanced=True)
    result_pipeline = pipeline.process(text)
    print(f"3. Advanced Pipeline:{result_pipeline}")
    
    # Method 4: Remove numbers
    config_no_numbers = PreprocessorConfig(remove_numbers=True)
    preprocessor_no_numbers = TextPreprocessor(config_no_numbers)
    result_no_numbers = preprocessor_no_numbers.preprocess(text)
    print(f"4. Remove Numbers:   {result_no_numbers}")


def view_statistics() -> None:
    """View detailed preprocessing statistics."""
    preprocessor = TextPreprocessor()
    
    print_separator("-")
    print("Preprocessing Statistics")
    print_separator("-")
    
    text = input("\nEnter text to analyze: ").strip()
    
    if not text:
        print("❌ Empty input!")
        return
    
    stats = preprocessor.get_text_statistics(text)
    
    print(f"\nOriginal text:")
    print(f"  '{text}'")
    print(f"\nPreprocessed text:")
    print(f"  '{preprocessor.preprocess(text)}'")
    print(f"\nDetailed statistics:")
    print(f"  Original length:      {stats['original_length']} characters")
    print(f"  Original tokens:      {stats['original_tokens']}")
    print(f"  Final tokens:         {stats['final_tokens']}")
    print(f"  Removed tokens:       {stats['removed_tokens']}")
    print(f"  Removal rate:         {stats['removed_tokens']/max(stats['original_tokens'],1)*100:.1f}%")
    print(f"  Unique tokens:        {stats['unique_tokens']}")
    print(f"  Uniqueness ratio:     {stats['unique_tokens']/max(stats['final_tokens'],1)*100:.1f}%")


def test_sample_questions() -> None:
    """Test with sample FAQ questions."""
    preprocessor = TextPreprocessor()
    
    sample_questions = [
        "What is CodeAlpha?",
        "How do I apply for the internship?",
        "What are the task requirements?",
        "Can I use Python for the projects?",
        "Will I get a certificate after completion?",
    ]
    
    print_separator("-")
    print("Sample FAQ Questions Test")
    print_separator("-")
    
    for i, question in enumerate(sample_questions, 1):
        result = preprocessor.preprocess(question)
        print(f"\n{i}. {question}")
        print(f"   → {result}")


def main() -> None:
    """Main interactive loop."""
    while True:
        display_menu()
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == "1":
            test_basic_preprocessing()
        elif choice == "2":
            test_advanced_pipeline()
        elif choice == "3":
            compare_methods()
        elif choice == "4":
            view_statistics()
        elif choice == "5":
            test_sample_questions()
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid option! Please choose 1-6.")
        
        input("\nPress Enter to continue...")
        print("\n" * 2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)