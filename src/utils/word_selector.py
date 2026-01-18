import os
import random
from typing import List

from ..utils.exceptions import WordSelectionError


class WordSelector:
    """Handles selection of random words from dictionary file."""
    
    def __init__(self, words_file_path: str):
        self.words_file_path = words_file_path
    
    async def get_random_words(self, num_words: int) -> List[str]:
        """
        Get random words from file using reservoir sampling.
        
        Args:
            num_words: Number of words to select
            
        Returns:
            List of randomly selected words
            
        Raises:
            WordSelectionError: If file reading fails
        """
        if not os.path.exists(self.words_file_path):
            raise WordSelectionError(f"Dictionary file not found at {self.words_file_path}")

        selected_words = []
        word_count = 0
        
        try:
            with open(self.words_file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    word = line.strip().lower()
                    
                    # Filter: alphabetic only, reasonable length
                    if not word.isalpha() or len(word) < 3 or len(word) > 20:
                        continue

                    word_count += 1

                    if len(selected_words) < num_words:
                        selected_words.append(word)
                    else:
                        # Reservoir sampling
                        j = random.randrange(word_count)
                        if j < num_words:
                            selected_words[j] = word
                            
        except Exception as e:
            raise WordSelectionError(f"Error reading dictionary file: {e}")
            
        return selected_words