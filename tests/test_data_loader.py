"""
Unit Tests for FAQ Data Loader
"""

import json
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.services.data_loader import FAQDataLoader, DataLoadError
from src.models.faq import FAQCategory


class TestFAQDataLoader:
    """Tests for FAQDataLoader."""

    @pytest.fixture
    def valid_faq_data(self) -> dict:
        """Fixture providing valid FAQ data."""
        return {
            "metadata": {"name": "Test FAQ", "version": "1.0"},
            "faqs": [
                {
                    "id": "test_001",
                    "question": "What is Python?",
                    "answer": "A programming language.",
                    "category": "technical",
                    "keywords": ["python", "programming"],
                    "alternate_questions": ["Tell me about Python"],
                },
                {
                    "id": "test_002",
                    "question": "How to apply?",
                    "answer": "Visit our website.",
                    "category": "general",
                    "keywords": ["apply", "application"],
                    "alternate_questions": [],
                },
            ],
        }

    def test_load_valid_json(self, valid_faq_data: dict) -> None:
        """Test loading valid JSON data."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_faq_data, f)
            temp_path = Path(f.name)

        try:
            database = FAQDataLoader.load_from_json(temp_path)

            assert database.total_faqs == 2
            assert "Test FAQ" in database.metadata.get("name", "")

            faq1 = database.get_by_id("test_001")
            assert faq1 is not None
            assert faq1.question == "What is Python?"
            assert faq1.category == FAQCategory.TECHNICAL
            assert len(faq1.keywords) == 2
        finally:
            temp_path.unlink()

    def test_load_nonexistent_file(self) -> None:
        """Test loading non-existent file raises error."""
        with pytest.raises(DataLoadError, match="not found"):
            FAQDataLoader.load_from_json(Path("nonexistent.json"))

    def test_load_invalid_json(self) -> None:
        """Test loading invalid JSON raises error."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            temp_path = Path(f.name)

        try:
            with pytest.raises(DataLoadError, match="Invalid JSON"):
                FAQDataLoader.load_from_json(temp_path)
        finally:
            temp_path.unlink()

    def test_load_missing_faqs_key(self) -> None:
        """Test loading data without 'faqs' key raises error."""
        data = {"metadata": {"name": "Test"}}

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(DataLoadError, match="must contain 'faqs'"):
                FAQDataLoader.load_from_json(temp_path)
        finally:
            temp_path.unlink()

    def test_load_missing_required_field(self) -> None:
        """Test loading FAQ without required field raises error."""
        data = {
            "faqs": [
                {
                    "id": "test_001",
                    "question": "Test?",
                    # Missing 'answer' and 'category'
                }
            ]
        }

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(DataLoadError, match="Missing required field"):
                FAQDataLoader.load_from_json(temp_path)
        finally:
            temp_path.unlink()

    def test_load_invalid_category(self) -> None:
        """Test loading FAQ with invalid category raises error."""
        data = {
            "faqs": [
                {
                    "id": "test_001",
                    "question": "Test?",
                    "answer": "Answer",
                    "category": "invalid_category",
                }
            ]
        }

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            temp_path = Path(f.name)

        try:
            with pytest.raises(DataLoadError, match="Invalid category"):
                FAQDataLoader.load_from_json(temp_path)
        finally:
            temp_path.unlink()

    def test_save_and_load_roundtrip(self, valid_faq_data: dict) -> None:
        """Test saving and loading produces same data."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_faq_data, f)
            temp_path1 = Path(f.name)

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path2 = Path(f.name)

        try:
            # Load original
            database1 = FAQDataLoader.load_from_json(temp_path1)

            # Save to new file
            FAQDataLoader.save_to_json(database1, temp_path2)

            # Load from new file
            database2 = FAQDataLoader.load_from_json(temp_path2)

            # Compare
            assert database1.total_faqs == database2.total_faqs

            for faq1, faq2 in zip(database1.faqs, database2.faqs):
                assert faq1.id == faq2.id
                assert faq1.question == faq2.question
                assert faq1.answer == faq2.answer
                assert faq1.category == faq2.category
        finally:
            temp_path1.unlink()
            temp_path2.unlink()
