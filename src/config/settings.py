from typing import List
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
    available_models: List[str] = Field(
        default=[
            "z-ai/glm-4.5-air:free",
            "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "microsoft/phi-3-medium-128k-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free",
        ],
        description="List of available OpenRouter models for random selection",
    )
    enable_model_rotation: bool = Field(
        default=True, description="Enable random model selection"
    )
    max_retry_attempts: int = Field(
        default=3, description="Maximum retry attempts with different models"
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
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
