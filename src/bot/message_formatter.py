from typing import Dict, Any, List

from ..utils.logging import get_logger

logger = get_logger(__name__)


class MessageFormatter:
    """Formats AI response into Telegram message."""
    
    def format_daily_words_message(self, ai_text: str) -> str:
        """
        Format AI response into a readable Telegram message.
        
        Args:
            ai_text: Raw text response from AI
            
        Returns:
            Formatted message string
        """
        try:
            # The AI should provide well-formatted text, so we just need to add our signature
            # and ensure proper formatting for Telegram
            formatted_message = ai_text.strip()
            
            # Ensure there's a nice header
            if not formatted_message.startswith("Today's") and not formatted_message.startswith("**Today's"):
                formatted_message = "Today's words:\n\n" + formatted_message
            
            # Add signature at the end
            if not formatted_message.endswith("By Light"):
                formatted_message += "\n\n\nBy Light (@justanotherlight)"
            
            logger.info("Successfully formatted message", message_length=len(formatted_message))
            
            return formatted_message
            
        except Exception as e:
            logger.error("Error formatting message", error=str(e))
            raise