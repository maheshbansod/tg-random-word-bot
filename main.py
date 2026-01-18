import asyncio
import sys

from src.config.settings import settings
from src.utils.logging import configure_logging, get_logger
from src.utils.exceptions import RandomWordBotError, ConfigurationError
from src.ai.openrouter_client import OpenRouterClient
from src.utils.word_selector import WordSelector
from src.bot.telegram_client import TelegramClient
from src.bot.message_formatter import MessageFormatter


logger = get_logger(__name__)


class RandomWordBot:
    """Main bot orchestrator."""
    
    def __init__(self):
        self.word_selector = WordSelector(settings.words_file_path)
        self.ai_client = OpenRouterClient()
        self.telegram_client = TelegramClient()
        self.message_formatter = MessageFormatter()
    
    async def run(self) -> None:
        """Run the daily word generation and sending process."""
        try:
            logger.info("Starting Random Word Bot")
            
            # Get random words for theme
            logger.info("Selecting random words", count=2)
            random_words = await self.word_selector.get_random_words(2)
            logger.info("Selected random words", words=random_words)
            
            # Generate daily words using AI
            logger.info("Generating daily words with AI")
            ai_response = await self.ai_client.generate_daily_words(random_words)
            
            # Format message
            logger.info("Formatting message")
            message = self.message_formatter.format_daily_words_message(ai_response)
            
            # Send to Telegram
            logger.info("Sending message to Telegram")
            await self.telegram_client.send_message(message)
            
            logger.info("Random Word Bot completed successfully")
            
        except RandomWordBotError as e:
            logger.error("Bot error occurred", error=str(e))
            sys.exit(1)
        except Exception as e:
            logger.error("Unexpected error", error=str(e))
            sys.exit(1)


async def main():
    """Main entry point."""
    # Configure logging
    configure_logging(settings.log_level)
    
    # Validate configuration
    if not settings.telegram_bot_token:
        raise ConfigurationError("TELEGRAM_BOT_TOKEN is required")
    
    if not settings.openrouter_api_key:
        raise ConfigurationError("OPENROUTER_API_KEY is required")
    
    if not settings.telegram_chat_ids:
        raise ConfigurationError("TELEGRAM_CHAT_IDS is required")
    
    # Run the bot
    bot = RandomWordBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())