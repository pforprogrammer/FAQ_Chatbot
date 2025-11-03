"""
NLTK Data Setup Script
Downloads required NLTK datasets for the chatbot
"""

import nltk
from typing import List


def download_nltk_data() -> None:
    """Download all required NLTK datasets."""
    datasets: List[str] = [
        "punkt",  # Tokenizer
        "stopwords",  # Stop words
        "wordnet",  # Lemmatization
        "omw-1.4",  # Wordnet multilingual
        "averaged_perceptron_tagger",  # POS tagging
    ]

    print("Downloading NLTK datasets...")
    for dataset in datasets:
        try:
            nltk.download(dataset, quiet=False)
            print(f"✓ Downloaded: {dataset}")
        except Exception as e:
            print(f"✗ Failed to download {dataset}: {e}")

    print("\n✓ NLTK setup complete!")


if __name__ == "__main__":
    download_nltk_data()
