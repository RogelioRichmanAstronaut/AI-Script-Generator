import re
from typing import List, Optional

class TextProcessor:
    """Handles text preprocessing and cleaning"""
    
    def __init__(self):
        """Initialize text processor"""
        self.sentence_endings = r'[.!?]'
        self.word_pattern = r'\b\w+\b'
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text to clean
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        # Normalize punctuation
        text = self._normalize_punctuation(text)
        
        return text.strip()
    
    def split_into_sections(self, text: str) -> List[str]:
        """
        Split text into logical sections based on content
        
        Args:
            text: Input text to split
            
        Returns:
            List[str]: List of text sections
        """
        # Split on double newlines or section markers
        sections = re.split(r'\n\s*\n|\n(?=[A-Z][^a-z]*:)', text)
        return [s.strip() for s in sections if s.strip()]
    
    def count_words(self, text: str) -> int:
        """
        Count words in text
        
        Args:
            text: Input text
            
        Returns:
            int: Word count
        """
        words = re.findall(self.word_pattern, text)
        return len(words)
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors"""
        replacements = {
            r'[|]': 'I',  # Vertical bar to I
            r'0': 'O',    # Zero to O where appropriate
            r'1': 'l',    # One to l where appropriate
            r'\s+': ' '   # Multiple spaces to single space
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        return text
    
    def _normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation marks"""
        # Replace multiple periods with single period
        text = re.sub(r'\.{2,}', '.', text)
        
        # Add space after punctuation if missing
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.!?,])', r'\1', text)
        
        return text 