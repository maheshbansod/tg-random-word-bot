from telegram import Bot
from telegram.error import TelegramError
from typing import List

from ..config.settings import settings
from ..utils.exceptions import TelegramBotError
from ..utils.logging import get_logger

logger = get_logger(__name__)


class TelegramClient:
    """Handles Telegram bot operations."""
    
    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token)
        self.chat_ids = settings.telegram_chat_ids
    
    async def send_message(self, message: str) -> None:
        """
        Send message to all configured Telegram chats.
        
        Args:
            message: Message to send
            
        Raises:
            TelegramBotError: If sending fails
        """
        if not settings.telegram_bot_token:
            raise TelegramBotError("Telegram bot token is not configured")
        
        if not self.chat_ids:
            raise TelegramBotError("No Telegram chat IDs configured")
        
        logger.info("Sending message to Telegram chats", chat_count=len(self.chat_ids))
        
        for chat_id in self.chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id, 
                    text=message, 
                    parse_mode="Markdown"
                )
                logger.info("Message sent successfully", chat_id=chat_id)
            except TelegramError as e:
                logger.error("Failed to send message", chat_id=chat_id, error=str(e))
                raise TelegramBotError(f"Failed to send message to chat {chat_id}: {e}")
            except Exception as e:
                logger.error("Unexpected error sending message", chat_id=chat_id, error=str(e))
                raise TelegramBotError(f"Unexpected error for chat {chat_id}: {e}")
        
        logger.info("All messages sent successfully")