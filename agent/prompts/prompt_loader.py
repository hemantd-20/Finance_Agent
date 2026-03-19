"""Centralized prompt registry for loading and managing prompt templates."""

from pathlib import Path
from typing import Dict


class PromptRegistry:
    """Registry for managing prompt templates."""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent
        self._cache: Dict[str, str] = {}
    
    def load_prompt(self, prompt_name: str) -> str:
        """
        Load a prompt template from file.
        
        Args:
            prompt_name: Name of the prompt file (without .txt extension)
            
        Returns:
            Prompt template as string
        """
        if prompt_name in self._cache:
            return self._cache[prompt_name]
        
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_template = f.read()
        
        self._cache[prompt_name] = prompt_template
        return prompt_template
    
    def format_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        Load and format a prompt template with provided variables.
        
        Args:
            prompt_name: Name of the prompt file (without .txt extension)
            **kwargs: Variables to format into the template
            
        Returns:
            Formatted prompt string
        """
        template = self.load_prompt(prompt_name)
        return template.format(**kwargs)


# Global registry instance
prompt_registry = PromptRegistry()
