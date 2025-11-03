#!/bin/bash

echo "=================================="
echo "Step 3: Text Preprocessing Tests"
echo "=================================="
echo ""

# Run unit tests
echo "Running unit tests..."
pytest tests/test_preprocessor.py -v --cov=src/services/preprocessor
pytest tests/test_text_utils.py -v --cov=src/services/text_utils
pytest tests/test_preprocessing_pipeline.py -v --cov=src/services/preprocessing_pipeline

echo ""
echo "Running all preprocessing tests with coverage..."
pytest tests/test_preprocessor.py tests/test_text_utils.py tests/test_preprocessing_pipeline.py \
    -v --cov=src/services --cov-report=term-missing --cov-report=html

echo ""
echo "Running type checking..."
mypy src/services/preprocessor.py
mypy src/services/text_utils.py
mypy src/services/preprocessing_pipeline.py

echo ""
echo "Running code quality checks..."
black --check src/services/
ruff check src/services/

echo ""
echo "=================================="
echo "✓ All tests complete!"
echo "=================================="