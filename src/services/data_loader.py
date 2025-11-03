"""
FAQ Data Loader
Handles loading and validation of FAQ data from JSON files
"""

import json
from pathlib import Path
from typing import Any

from src.models.faq import FAQ, FAQCategory, FAQDatabase


class DataLoadError(Exception):
    """Raised when FAQ data cannot be loaded."""

    pass


class FAQDataLoader:
    """Loads and validates FAQ data from JSON files."""

    @staticmethod
    def load_from_json(file_path: Path) -> FAQDatabase:
        """
        Load FAQ database from JSON file.

        Args:
            file_path: Path to JSON file containing FAQ data

        Returns:
            FAQDatabase instance with all loaded FAQs

        Raises:
            DataLoadError: If file cannot be loaded or data is invalid
        """
        if not file_path.exists():
            raise DataLoadError(f"FAQ data file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON in FAQ data file: {e}")
        except Exception as e:
            raise DataLoadError(f"Error reading FAQ data file: {e}")

        return FAQDataLoader._parse_faq_data(data)

    @staticmethod
    def _parse_faq_data(data: dict[str, Any]) -> FAQDatabase:
        """
        Parse FAQ data dictionary into FAQDatabase.

        Args:
            data: Dictionary containing FAQ data

        Returns:
            FAQDatabase instance

        Raises:
            DataLoadError: If data format is invalid
        """
        if "faqs" not in data:
            raise DataLoadError("FAQ data must contain 'faqs' key")

        faqs: list[FAQ] = []

        for idx, faq_data in enumerate(data["faqs"]):
            try:
                faq = FAQDataLoader._parse_faq_entry(faq_data)
                faqs.append(faq)
            except Exception as e:
                raise DataLoadError(f"Error parsing FAQ entry at index {idx}: {e}")

        metadata = data.get("metadata", {})

        try:
            return FAQDatabase(faqs=faqs, metadata=metadata)
        except ValueError as e:
            raise DataLoadError(f"Invalid FAQ database: {e}")

    @staticmethod
    def _parse_faq_entry(faq_data: dict[str, Any]) -> FAQ:
        """
        Parse a single FAQ entry.

        Args:
            faq_data: Dictionary containing single FAQ data

        Returns:
            FAQ instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ["id", "question", "answer", "category"]
        for field in required_fields:
            if field not in faq_data:
                raise ValueError(f"Missing required field: {field}")

        # Parse category
        try:
            category = FAQCategory(faq_data["category"])
        except ValueError:
            raise ValueError(
                f"Invalid category '{faq_data['category']}'. "
                f"Must be one of: {[c.value for c in FAQCategory]}"
            )

        # Create FAQ instance
        return FAQ(
            id=faq_data["id"],
            question=faq_data["question"],
            answer=faq_data["answer"],
            category=category,
            keywords=faq_data.get("keywords", []),
            alternate_questions=faq_data.get("alternate_questions", []),
        )

    @staticmethod
    def save_to_json(database: FAQDatabase, file_path: Path) -> None:
        """
        Save FAQ database to JSON file.

        Args:
            database: FAQDatabase instance to save
            file_path: Path where to save the JSON file

        Raises:
            DataLoadError: If file cannot be written
        """
        data = {
            "metadata": database.metadata,
            "faqs": [
                {
                    "id": faq.id,
                    "question": faq.question,
                    "answer": faq.answer,
                    "category": faq.category.value,
                    "keywords": faq.keywords,
                    "alternate_questions": faq.alternate_questions,
                }
                for faq in database.faqs
            ],
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise DataLoadError(f"Error writing FAQ data file: {e}")
