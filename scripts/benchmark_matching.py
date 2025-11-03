"""
Question Matching Performance Benchmark
Measures matching speed and accuracy
"""
import time
import sys
from pathlib import Path
from typing import List, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.chatbot import Chatbot
from src.config import config


def print_separator(char: str = "=", length: int = 70) -> None:
    """Print separator line."""
    print(char * length)


def benchmark_query_speed(chatbot: Chatbot, queries: List[str], iterations: int = 100) -> Dict[str, float]:
    """
    Benchmark query processing speed.
    
    Args:
        chatbot: Chatbot instance
        queries: List of test queries
        iterations: Number of iterations
        
    Returns:
        Dictionary with benchmark results
    """
    # Warm-up
    for query in queries[:3]:
        chatbot.ask(query)
    
    chatbot.clear_history()
    
    # Benchmark
    start = time.time()
    for _ in range(iterations):
        for query in queries:
            chatbot.ask(query)
        chatbot.clear_history()
    
    total_time = time.time() - start
    avg_time = total_time / (iterations * len(queries))
    queries_per_sec = (iterations * len(queries)) / total_time
    
    return {
        'total_time': total_time,
        'avg_time_per_query': avg_time,
        'queries_per_second': queries_per_sec,
        'total_queries': iterations * len(queries)
    }


def benchmark_matching_accuracy(chatbot: Chatbot) -> Dict[str, float]:
    """
    Benchmark matching accuracy with test cases.
    
    Args:
        chatbot: Chatbot instance
        
    Returns:
        Dictionary with accuracy metrics
    """
    # Test cases: (query, expected_faq_id_contains)
    test_cases = [
        ("What is CodeAlpha?", "intern_001"),
        ("How to apply?", "intern_002"),
        ("How many tasks?", "intern_003"),
        ("What certificates?", "intern_004"),
        ("Programming language?", "tech_001"),
        ("Submit project?", "tech_002"),
        ("Contact support?", "account_001"),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for query, expected_id_part in test_cases:
        response = chatbot.ask(query)
        if response.match_result and expected_id_part in response.match_result.faq.id:
            correct += 1
    
    chatbot.clear_history()
    
    accuracy = (correct / total) * 100 if total > 0 else 0
    
    return {
        'correct': correct,
        'total': total,
        'accuracy': accuracy
    }


def analyze_confidence_distribution(chatbot: Chatbot, queries: List[str]) -> Dict[str, int]:
    """
    Analyze confidence score distribution.
    
    Args:
        chatbot: Chatbot instance
        queries: List of test queries
        
    Returns:
        Dictionary with confidence distribution
    """
    high_conf = 0
    medium_conf = 0
    low_conf = 0
    no_match = 0
    
    for query in queries:
        response = chatbot.ask(query)
        if response.match_result:
            score = response.match_result.similarity_score
            if score >= 0.7:
                high_conf += 1
            elif score >= 0.5:
                medium_conf += 1
            else:
                low_conf += 1
        else:
            no_match += 1
    
    chatbot.clear_history()
    
    return {
        'high_confidence': high_conf,
        'medium_confidence': medium_conf,
        'low_confidence': low_conf,
        'no_match': no_match,
        'total': len(queries)
    }


def main() -> None:
    """Run all benchmarks."""
    print_separator()
    print("Question Matching Performance Benchmark")
    print_separator()
    
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
    
    # Test queries
    test_queries = [
        "What is CodeAlpha?",
        "How do I apply for the internship?",
        "What are the task requirements?",
        "Which programming language should I use?",
        "How do I submit my project?",
        "Will I get a certificate?",
        "Can I get a recommendation letter?",
        "What tasks are available?",
        "Do I need AI experience?",
        "How to contact support?",
    ]
    
    # 1. Speed Benchmark
    print("\n" + "-" * 70)
    print("1. Query Processing Speed")
    print("-" * 70)
    
    iterations = 50
    print(f"\nRunning {iterations} iterations with {len(test_queries)} queries...")
    
    speed_results = benchmark_query_speed(chatbot, test_queries, iterations)
    
    print(f"\nResults:")
    print(f"  Total Time:           {speed_results['total_time']:.2f}s")
    print(f"  Total Queries:        {speed_results['total_queries']}")
    print(f"  Avg Time per Query:   {speed_results['avg_time_per_query']*1000:.2f}ms")
    print(f"  Queries per Second:   {speed_results['queries_per_second']:.1f}")
    
    # 2. Accuracy Benchmark
    print("\n" + "-" * 70)
    print("2. Matching Accuracy")
    print("-" * 70)
    
    accuracy_results = benchmark_matching_accuracy(chatbot)
    
    print(f"\nResults:")
    print(f"  Correct Matches:      {accuracy_results['correct']}/{accuracy_results['total']}")
    print(f"  Accuracy:             {accuracy_results['accuracy']:.1f}%")
    
    # 3. Confidence Distribution
    print("\n" + "-" * 70)
    print("3. Confidence Distribution")
    print("-" * 70)
    
    conf_results = analyze_confidence_distribution(chatbot, test_queries)
    
    print(f"\nResults:")
    print(f"  High Confidence:      {conf_results['high_confidence']} "
          f"({conf_results['high_confidence']/conf_results['total']*100:.1f}%)")
    print(f"  Medium Confidence:    {conf_results['medium_confidence']} "
          f"({conf_results['medium_confidence']/conf_results['total']*100:.1f}%)")
    print(f"  Low Confidence:       {conf_results['low_confidence']} "
          f"({conf_results['low_confidence']/conf_results['total']*100:.1f}%)")
    print(f"  No Match:             {conf_results['no_match']} "
          f"({conf_results['no_match']/conf_results['total']*100:.1f}%)")
    
    # 4. Corpus Statistics
    print("\n" + "-" * 70)
    print("4. Corpus Statistics")
    print("-" * 70)
    
    stats = chatbot.get_statistics()
    matcher_stats = stats['matcher_stats']
    
    print(f"\nFAQ Database:")
    print(f"  Total FAQs:           {matcher_stats['total_faqs']}")
    print(f"  Total Questions:      {matcher_stats['total_questions']}")
    print(f"  Avg Q per FAQ:        {matcher_stats['avg_questions_per_faq']:.2f}")
    print(f"  Vocabulary Size:      {matcher_stats['vocabulary_size']}")
    print(f"  Max Features:         {matcher_stats['max_features']}")
    
    # 5. Performance Summary
    print("\n" + "=" * 70)
    print("Performance Summary")
    print("=" * 70)
    
    print(f"\n✅ Speed:      {speed_results['queries_per_second']:.1f} queries/sec")
    print(f"✅ Accuracy:   {accuracy_results['accuracy']:.1f}%")
    print(f"✅ Avg Time:   {speed_results['avg_time_per_query']*1000:.2f}ms per query")
    
    # Performance rating
    if speed_results['queries_per_second'] > 100:
        speed_rating = "Excellent"
    elif speed_results['queries_per_second'] > 50:
        speed_rating = "Good"
    else:
        speed_rating = "Acceptable"
    
    if accuracy_results['accuracy'] > 80:
        accuracy_rating = "Excellent"
    elif accuracy_results['accuracy'] > 60:
        accuracy_rating = "Good"
    else:
        accuracy_rating = "Needs Improvement"
    
    print(f"\n📊 Speed Rating:       {speed_rating}")
    print(f"📊 Accuracy Rating:    {accuracy_rating}")
    
    print("\n" + "=" * 70)
    print("✓ Benchmark complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()