import json
import datetime
from typing import Dict, Any, List
from openai import OpenAI

from ..config.settings import settings
from ..utils.exceptions import AIServiceError
from ..utils.logging import get_logger
from .model_selector import ModelSelector

logger = get_logger(__name__)


class OpenRouterClient:
    """Client for interacting with OpenRouter AI service."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openrouter_api_key, base_url="https://openrouter.ai/api/v1"
        )
        self.model_selector = ModelSelector(settings)

    def _create_prompt(self, today: str, random_words: List[str]) -> str:
        """Create the prompt for the AI model."""
        return f"""
        datetime.now().isoformat() = {today}
        overall theme = {random_words}

        You are a helpful "day start thoughts" assistant.
        Provide 5 good words for us today that will help build our vocabulary.
        Tell words that are not super common, but could be uncommon for non-native
        english speakers. The overall theme contains some randomly picked words 
        the Operating System's words directory. You may use that as inspiration
        to come up with the 5 words. Find literary words, words that you might
        read in a novel, or sometimes find technical words. Stay close to the
        theme and think about the psychological profile and stuff. you got this.
        Let the date of the day affect your word selection choice a lot as well
        so that there is uniqueness every single day.
        Provide the definition for each given word in a structured JSON format.

        For each word, you will return WordData containing the following keys:
        - "word": The word itself.
        - "definition": A concise definition of the word.
        - "part_of_speech": The primary part of speech (e.g., "noun", "verb", "adjective").
        - "example": An example sentence using the word (if available and appropriate).

        If you cannot find a definition, return a JSON with "definition": "Definition not found." and other fields as null or empty.

        You also need to give me a tamil word of the day. Since the user barely
        knows any Tamil, you need to give common words related to any of the 
        English words you have chosen, or related to the "today_theme"
        The TamilWord should have the following keys:
        - word (in Tamil script)
        - pronunciation (in English)
        - part_of_speech
        - meaning (in English)

        Before giving the output, you need to write about today's theme.
        i.e. first analyze the date and find out what is significant about today's date.

        You need to analyze today from the following perspectives and include the "overall theme" in some way in this. Write this in markdown.
        - Significance of the numbers (from a numerology perspective)
        - Significance of today's date (i.e. any important events in the past on the same day?)
        - Significance about any past recent or future recent event/festivities around this
        - The psychological make up of people around this date

        After you are done with today's theme, tell me 5 words and their WordData that maybe in some way or the other
        relate to the day's themes as well.
        It's important the words are related to the day and the overall theme

        Don't mention the overall theme, but you may mention it's synonyms in your output if you want and don't mention that it is the overall theme though.

        Here's the full response format you need to follow:
        {{
            "today_theme": string,
            "words": WordData[],
            "tamil_word": TamilWord
        }}
        """

    async def generate_daily_words(self, random_words: List[str]) -> Dict[str, Any]:
        """
        Generate daily words with definitions using OpenRouter AI.

        Args:
            random_words: List of random words for theme inspiration

        Returns:
            Dictionary containing today's theme, words, and Tamil word

        Raises:
            AIServiceError: If AI service fails
        """
        today = datetime.datetime.now().isoformat()
        prompt = self._create_prompt(today, random_words)
        used_models = []
        
        while len(used_models) < settings.max_retry_attempts:
            model = None
            try:
                model = self.model_selector.get_random_model(exclude_models=used_models)
                used_models.append(model)

                logger.info(
                    "Generating daily words",
                    model=model,
                    words_count=len(random_words),
                    attempt=len(used_models),
                )

                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    # response_format={"type": "json_object"},
                )

                response_text = response.choices[0].message.content
                if response_text is None:
                    raise ValueError("Received empty response from AI")
                    
                logger.info("Received AI response", response_length=len(response_text))

                # Parse JSON response
                try:
                    response_data = json.loads(response_text)
                    logger.info(
                        "Successfully parsed AI response",
                        model=model,
                        usage_stats=self.model_selector.get_usage_stats()
                    )
                    return response_data
                except json.JSONDecodeError as e:
                    logger.error(
                        "Failed to parse AI response as JSON",
                        error=str(e),
                        response=response_text,
                        model=model,
                    )
                    self.model_selector.mark_model_failed(model, e)
                    continue

            except Exception as e:
                logger.error(
                    "AI service error with model",
                    error=str(e),
                    model=model or 'unknown',
                    attempt=len(used_models),
                )
                if model:
                    self.model_selector.mark_model_failed(model, e)
                
                # Try next model if available
                next_model = self.model_selector.get_model_for_retry(used_models)
                if next_model is None:
                    break
                continue

        # All models failed
        logger.error(
            "All models failed to generate daily words",
            used_models=used_models,
            failed_models=list(self.model_selector.failed_models),
            max_attempts=settings.max_retry_attempts,
        )
        raise AIServiceError("All available models failed to generate daily words")
