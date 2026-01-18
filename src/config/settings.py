from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str = Field(
        ..., description="Telegram bot token from BotFather"
    )
    telegram_chat_ids_str: str = Field(
        default="", description="Comma-separated list of Telegram chat IDs"
    )
    openrouter_api_key: str = Field(..., description="OpenRouter API key")
    openrouter_model: str = Field(
        default="z-ai/glm-4.5-air:free",
        description="OpenRouter model to use",
    )
    words_file_path: str = Field(
        default="/usr/share/dict/words", description="Path to system dictionary file"
    )
    num_words_to_send: int = Field(
        default=5, description="Number of words to send daily"
    )
    log_level: str = Field(default="INFO", description="Logging level")

    @property
    def telegram_chat_ids(self) -> list[int]:
        if not self.telegram_chat_ids_str.strip():
            return []
        return [
            int(cid.strip())
            for cid in self.telegram_chat_ids_str.split(",")
            if cid.strip()
        ]

    class Config:
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
