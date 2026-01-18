from typing import Dict, Any, List

from ..utils.logging import get_logger

logger = get_logger(__name__)


class MessageFormatter:
    """Formats AI response into Telegram message."""
    
    def format_daily_words_message(self, response_data: Dict[str, Any]) -> str:
        """
        Format AI response into a readable Telegram message.
        
        Args:
            response_data: Dictionary containing AI response
            
        Returns:
            Formatted message string
        """
        try:
            message_parts = ["Today's words:\n"]
            
            # Format English words
            words = response_data.get("words", [])
            for word_data in words:
                word = word_data.get("word", "").capitalize()
                definition = word_data.get("definition", "Definition not found.")
                part_of_speech = word_data.get("part_of_speech")
                example = word_data.get("example")
                
                message_parts.append(f"\n\n*{word}*")
                if part_of_speech:
                    message_parts.append(f"({part_of_speech})")
                message_parts.append(f"\n{definition}")
                if example:
                    message_parts.append(f"\n_Example: {example}_")
            
            # Format Tamil word
            tamil_word_data = response_data.get("tamil_word", {})
            if tamil_word_data:
                tamil_word = tamil_word_data.get("word", "")
                tamil_pronunciation = tamil_word_data.get("pronunciation", "")
                tamil_pos = tamil_word_data.get("part_of_speech", "")
                tamil_meaning = tamil_word_data.get("meaning", "")
                
                message_parts.append(
                    f"\n\nToday's Tamil word: *{tamil_word}* ({tamil_pos})"
                )
                message_parts.append(f"\n_{tamil_pronunciation}_")
                message_parts.append(f"\n{tamil_meaning}")
            
            # Add today's theme
            today_theme = response_data.get("today_theme", "")
            if today_theme:
                message_parts.append(f"\n\nA little about today:\n{today_theme}\n\n")
            
            # Add signature
            message_parts.append("\n\n\nBy Light (@justanotherlight)")
            
            formatted_message = " ".join(message_parts)
            logger.info("Successfully formatted message", message_length=len(formatted_message))
            
            return formatted_message
            
        except Exception as e:
            logger.error("Error formatting message", error=str(e))
            raise