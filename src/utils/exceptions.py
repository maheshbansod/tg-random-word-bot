class RandomWordBotError(Exception):
    """Base exception for the random word bot."""


class ConfigurationError(RandomWordBotError):
    """Raised when there's a configuration problem."""


class AIServiceError(RandomWordBotError):
    """Raised when AI service encounters an error."""


class TelegramBotError(RandomWordBotError):
    """Raised when Telegram bot encounters an error."""


class WordSelectionError(RandomWordBotError):
    """Raised when word selection fails."""