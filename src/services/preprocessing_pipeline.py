"""
Preprocessing Pipeline
Orchestrates multiple preprocessing steps with configuration
"""
from typing import List, Optional, Callable
from dataclasses import dataclass

from src.services.preprocessor import TextPreprocessor
from src.services.text_utils import (
    expand_contractions,
    remove_special_patterns,
    normalize_whitespace,
    remove_repeated_chars
)
from src.config import PreprocessorConfig


@dataclass
class PipelineStep:
    """Represents a single preprocessing step."""
    name: str
    function: Callable[[str], str]
    enabled: bool = True


class PreprocessingPipeline:
    """
    Flexible preprocessing pipeline with configurable steps.
    
    Allows adding, removing, and reordering preprocessing steps.
    """
    
    def __init__(
        self,
        config: Optional[PreprocessorConfig] = None,
        enable_advanced: bool = False
    ) -> None:
        """
        Initialize preprocessing pipeline.
        
        Args:
            config: Preprocessing configuration
            enable_advanced: Enable advanced preprocessing steps
        """
        self.config = config or PreprocessorConfig()
        self.preprocessor = TextPreprocessor(self.config)
        self.steps: List[PipelineStep] = []
        
        # Initialize default pipeline
        self._initialize_pipeline(enable_advanced)
    
    def _initialize_pipeline(self, enable_advanced: bool) -> None:
        """Initialize the preprocessing pipeline with default steps."""
        # Basic steps (always enabled)
        self.steps = [
            PipelineStep(
                name="normalize_whitespace",
                function=normalize_whitespace,
                enabled=True
            ),
        ]
        
        # Advanced steps (optional)
        if enable_advanced:
            self.steps.extend([
                PipelineStep(
                    name="expand_contractions",
                    function=expand_contractions,
                    enabled=True
                ),
                PipelineStep(
                    name="remove_special_patterns",
                    function=remove_special_patterns,
                    enabled=True
                ),
                PipelineStep(
                    name="remove_repeated_chars",
                    function=lambda text: remove_repeated_chars(text, 2),
                    enabled=True
                ),
            ])
        
        # Core NLP preprocessing (always last)
        self.steps.append(
            PipelineStep(
                name="nltk_preprocessing",
                function=self.preprocessor.preprocess,
                enabled=True
            )
        )
    
    def process(self, text: str) -> str:
        """
        Process text through all enabled pipeline steps.
        
        Args:
            text: Raw input text
            
        Returns:
            Fully preprocessed text
        """
        result = text
        
        for step in self.steps:
            if step.enabled:
                try:
                    result = step.function(result)
                except Exception as e:
                    # Log error but continue pipeline
                    print(f"Warning: Step '{step.name}' failed: {e}")
        
        return result
    
    def add_step(
        self,
        name: str,
        function: Callable[[str], str],
        position: Optional[int] = None
    ) -> None:
        """
        Add a custom preprocessing step.
        
        Args:
            name: Step name
            function: Processing function
            position: Position to insert (None = end)
        """
        step = PipelineStep(name=name, function=function, enabled=True)
        
        if position is None:
            self.steps.append(step)
        else:
            self.steps.insert(position, step)
    
    def remove_step(self, name: str) -> bool:
        """
        Remove a preprocessing step by name.
        
        Args:
            name: Step name to remove
            
        Returns:
            True if step was removed, False if not found
        """
        for i, step in enumerate(self.steps):
            if step.name == name:
                self.steps.pop(i)
                return True
        return False
    
    def enable_step(self, name: str) -> bool:
        """Enable a preprocessing step."""
        for step in self.steps:
            if step.name == name:
                step.enabled = True
                return True
        return False
    
    def disable_step(self, name: str) -> bool:
        """Disable a preprocessing step."""
        for step in self.steps:
            if step.name == name:
                step.enabled = False
                return True
        return False
    
    def get_steps(self) -> List[str]:
        """Get list of all step names."""
        return [step.name for step in self.steps]
    
    def get_enabled_steps(self) -> List[str]:
        """Get list of enabled step names."""
        return [step.name for step in self.steps if step.enabled]