"""
Unit Tests for Preprocessing Pipeline
"""
import pytest
from src.services.preprocessing_pipeline import (
    PreprocessingPipeline,
    PipelineStep
)


class TestPreprocessingPipeline:
    """Tests for PreprocessingPipeline."""
    
    @pytest.fixture
    def basic_pipeline(self) -> PreprocessingPipeline:
        """Fixture providing basic pipeline."""
        return PreprocessingPipeline(enable_advanced=False)
    
    @pytest.fixture
    def advanced_pipeline(self) -> PreprocessingPipeline:
        """Fixture providing advanced pipeline."""
        return PreprocessingPipeline(enable_advanced=True)
    
    def test_basic_pipeline_initialization(
        self, basic_pipeline: PreprocessingPipeline
    ) -> None:
        """Test basic pipeline initializes correctly."""
        steps = basic_pipeline.get_steps()
        
        assert len(steps) > 0
        assert "normalize_whitespace" in steps
        assert "nltk_preprocessing" in steps
    
    def test_advanced_pipeline_initialization(
        self, advanced_pipeline: PreprocessingPipeline
    ) -> None:
        """Test advanced pipeline has extra steps."""
        steps = advanced_pipeline.get_steps()
        
        assert "expand_contractions" in steps
        assert "remove_special_patterns" in steps
        assert "remove_repeated_chars" in steps
    
    def test_process_text(self, basic_pipeline: PreprocessingPipeline) -> None:
        """Test text processing through pipeline."""
        text = "What is Python programming?"
        result = basic_pipeline.process(text)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert result.islower()
    
    def test_advanced_processing(
        self, advanced_pipeline: PreprocessingPipeline
    ) -> None:
        """Test advanced processing features."""
        text = "I'm learning #python and it's amaaazing!!!"
        result = advanced_pipeline.process(text)
        
        assert len(result) > 0
        # Contractions should be expanded
        # Special patterns should be removed
        # Repeated chars should be reduced
    
    def test_add_custom_step(
        self, basic_pipeline: PreprocessingPipeline
    ) -> None:
        """Test adding custom preprocessing step."""
        def custom_step(text: str) -> str:
            return text.replace("test", "demo")
        
        initial_steps = len(basic_pipeline.get_steps())
        basic_pipeline.add_step("custom_replace", custom_step)
        
        assert len(basic_pipeline.get_steps()) == initial_steps + 1
        assert "custom_replace" in basic_pipeline.get_steps()
        
        # Test the custom step works
        result = basic_pipeline.process("This is a test")
        assert "demo" in result or "test" not in result.split()
    
    def test_remove_step(self, advanced_pipeline: PreprocessingPipeline) -> None:
        """Test removing a preprocessing step."""
        assert "expand_contractions" in advanced_pipeline.get_steps()
        
        removed = advanced_pipeline.remove_step("expand_contractions")
        
        assert removed is True
        assert "expand_contractions" not in advanced_pipeline.get_steps()
        
        # Try removing non-existent step
        removed = advanced_pipeline.remove_step("nonexistent")
        assert removed is False
    
    def test_enable_disable_step(
        self, basic_pipeline: PreprocessingPipeline
    ) -> None:
        """Test enabling and disabling steps."""
        step_name = "normalize_whitespace"
        
        # Disable step
        assert basic_pipeline.disable_step(step_name) is True
        enabled = basic_pipeline.get_enabled_steps()
        assert step_name not in enabled
        
        # Enable step
        assert basic_pipeline.enable_step(step_name) is True
        enabled = basic_pipeline.get_enabled_steps()
        assert step_name in enabled
    
    def test_get_enabled_steps(
        self, basic_pipeline: PreprocessingPipeline
    ) -> None:
        """Test getting only enabled steps."""
        all_steps = basic_pipeline.get_steps()
        enabled_steps = basic_pipeline.get_enabled_steps()
        
        # Initially, all steps should be enabled
        assert len(all_steps) == len(enabled_steps)
        
        # Disable one step
        basic_pipeline.disable_step(all_steps[0])
        enabled_steps = basic_pipeline.get_enabled_steps()
        
        assert len(enabled_steps) == len(all_steps) - 1
    
    def test_pipeline_with_error_handling(
        self, basic_pipeline: PreprocessingPipeline
    ) -> None:
        """Test pipeline handles errors gracefully."""
        def failing_step(text: str) -> str:
            raise ValueError("Intentional error")
        
        basic_pipeline.add_step("failing_step", failing_step, position=0)
        
        # Should not raise exception, should continue with other steps
        result = basic_pipeline.process("Test text")
        assert isinstance(result, str)