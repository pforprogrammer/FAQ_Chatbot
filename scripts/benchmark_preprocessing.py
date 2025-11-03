"""
Preprocessing Performance Benchmark
Measures preprocessing speed and efficiency
"""
import time
import sys
from pathlib import Path
from typing import List, Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.preprocessor import TextPreprocessor
from src.services.preprocessing_pipeline import PreprocessingPipeline
from src.config import PreprocessorConfig


# Sample test texts
SAMPLE_TEXTS: List[str] = [
    "What is Python programming language?",
    "How do I apply for the AI internship at CodeAlpha?",
    "Tell me about machine learning and artificial intelligence.",
    "Can you explain natural language processing in simple terms?",
    "What are the requirements for the chatbot project?",
    "I'm interested in learning about deep learning and neural networks.",
    "How long does it take to complete the internship tasks?",
    "What is the difference between supervised and unsupervised learning?",
    "Where can I find resources for learning computer vision?",
    "Please explain the concept of transfer learning in AI.",
]


def benchmark_preprocessor(iterations: int = 100) -> Dict[str, float]:
    """
    Benchmark text preprocessor performance.
    
    Args:
        iterations: Number of iterations to run
        
    Returns:
        Dictionary with benchmark results
    """
    preprocessor = TextPreprocessor()
    
    # Warm-up
    for text in SAMPLE_TEXTS[:3]:
        preprocessor.preprocess(text)
    
    # Benchmark single text processing
    start = time.time()
    for _ in range(iterations):
        for text in SAMPLE_TEXTS:
            preprocessor.preprocess(text)
    single_time = time.time() - start
    
    # Benchmark batch processing
    start = time.time()
    for _ in range(iterations):
        preprocessor.batch_preprocess(SAMPLE_TEXTS)
    batch_time = time.time() - start
    
    # Benchmark cached processing
    start = time.time()
    for _ in range(iterations):
        for text in SAMPLE_TEXTS:
            preprocessor.preprocess_cached(text)
    cached_time = time.time() - start
    
    return {
        "single": single_time,
        "batch": batch_time,
        "cached": cached_time,
        "texts_per_second_single": (iterations * len(SAMPLE_TEXTS)) / single_time,
        "texts_per_second_batch": (iterations * len(SAMPLE_TEXTS)) / batch_time,
        "texts_per_second_cached": (iterations * len(SAMPLE_TEXTS)) / cached_time,
    }


def benchmark_pipeline(iterations: int = 100) -> Dict[str, float]:
    """
    Benchmark preprocessing pipeline performance.
    
    Args:
        iterations: Number of iterations to run
        
    Returns:
        Dictionary with benchmark results
    """
    basic_pipeline = PreprocessingPipeline(enable_advanced=False)
    advanced_pipeline = PreprocessingPipeline(enable_advanced=True)
    
    # Benchmark basic pipeline
    start = time.time()
    for _ in range(iterations):
        for text in SAMPLE_TEXTS:
            basic_pipeline.process(text)
    basic_time = time.time() - start
    
    # Benchmark advanced pipeline
    start = time.time()
    for _ in range(iterations):
        for text in SAMPLE_TEXTS:
            advanced_pipeline.process(text)
    advanced_time = time.time() - start
    
    return {
        "basic": basic_time,
        "advanced": advanced_time,
        "texts_per_second_basic": (iterations * len(SAMPLE_TEXTS)) / basic_time,
        "texts_per_second_advanced": (iterations * len(SAMPLE_TEXTS)) / advanced_time,
    }


def analyze_preprocessing_impact() -> None:
    """Analyze the impact of preprocessing on text."""
    preprocessor = TextPreprocessor()
    
    print("\n" + "=" * 70)
    print("Preprocessing Impact Analysis")
    print("=" * 70)
    
    for i, text in enumerate(SAMPLE_TEXTS[:5], 1):
        print(f"\n{i}. Original: {text}")
        preprocessed = preprocessor.preprocess(text)
        print(f"   Processed: {preprocessed}")
        
        stats = preprocessor.get_text_statistics(text)
        print(f"   Stats: {stats['original_tokens']} → {stats['final_tokens']} tokens "
              f"({stats['removed_tokens']} removed)")


def compare_configurations() -> None:
    """Compare different preprocessing configurations."""
    configs = {
        "Default": PreprocessorConfig(),
        "No Lemma": PreprocessorConfig(use_lemmatization=False),
        "Min Length 3": PreprocessorConfig(min_word_length=3),
        "Remove Numbers": PreprocessorConfig(remove_numbers=True),
    }
    
    test_text = "I'm learning Python 3.11 and AI in 2024!"
    
    print("\n" + "=" * 70)
    print("Configuration Comparison")
    print("=" * 70)
    print(f"\nOriginal: {test_text}\n")
    
    for name, config in configs.items():
        preprocessor = TextPreprocessor(config)
        result = preprocessor.preprocess(test_text)
        print(f"{name:15s}: {result}")


def main() -> None:
    """Run all benchmarks."""
    print("=" * 70)
    print("Text Preprocessing Performance Benchmark")
    print("=" * 70)
    
    iterations = 100
    print(f"\nRunning benchmarks with {iterations} iterations...")
    print(f"Sample texts: {len(SAMPLE_TEXTS)}")
    print(f"Total operations: {iterations * len(SAMPLE_TEXTS)}")
    
    # Benchmark preprocessor
    print("\n" + "-" * 70)
    print("TextPreprocessor Benchmark")
    print("-" * 70)
    
    results = benchmark_preprocessor(iterations)
    
    print(f"\nSingle processing:  {results['single']:.3f}s "
          f"({results['texts_per_second_single']:.1f} texts/sec)")
    print(f"Batch processing:   {results['batch']:.3f}s "
          f"({results['texts_per_second_batch']:.1f} texts/sec)")
    print(f"Cached processing:  {results['cached']:.3f}s "
          f"({results['texts_per_second_cached']:.1f} texts/sec)")
    
    speedup_batch = results['single'] / results['batch']
    speedup_cached = results['single'] / results['cached']
    
    print(f"\nSpeedup (batch vs single):  {speedup_batch:.2f}x")
    print(f"Speedup (cached vs single): {speedup_cached:.2f}x")
    
    # Benchmark pipeline
    print("\n" + "-" * 70)
    print("PreprocessingPipeline Benchmark")
    print("-" * 70)
    
    pipeline_results = benchmark_pipeline(iterations)
    
    print(f"\nBasic pipeline:    {pipeline_results['basic']:.3f}s "
          f"({pipeline_results['texts_per_second_basic']:.1f} texts/sec)")
    print(f"Advanced pipeline: {pipeline_results['advanced']:.3f}s "
          f"({pipeline_results['texts_per_second_advanced']:.1f} texts/sec)")
    
    overhead = (pipeline_results['advanced'] - pipeline_results['basic']) / \
               pipeline_results['basic'] * 100
    print(f"\nAdvanced pipeline overhead: {overhead:.1f}%")
    
    # Analysis
    analyze_preprocessing_impact()
    compare_configurations()
    
    print("\n" + "=" * 70)
    print("✓ Benchmark complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()