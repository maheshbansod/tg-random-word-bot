import os
import random
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from google import genai
import json
import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

TELEGRAM_CHAT_IDS_STR = os.getenv("TELEGRAM_CHAT_IDS", "")
TELEGRAM_CHAT_IDS = [
    int(cid.strip()) for cid in TELEGRAM_CHAT_IDS_STR.split(",") if cid.strip()
]
print(TELEGRAM_CHAT_IDS)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Path to the dictionary file on most Linux/macOS systems
WORDS_FILE = "/usr/share/dict/words"
NUM_WORDS_TO_SEND = 5
DICTIONARY_API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"


async def get_random_words_from_file(filepath, num_words):
    """
    Reads num_words random lines (words) from a file using reservoir sampling.
    This ensures we don't load the entire file into memory.
    Filters for alphabetic words of reasonable length.
    """
    if not os.path.exists(filepath):
        print(f"Error: Dictionary file not found at {filepath}")
        return []

    selected_words = []
    word_count = 0  # Counter for actual valid words processed
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                word = line.strip().lower()
                # Basic filtering: must be alphabetic and not too short/long
                if not word.isalpha() or len(word) < 3 or len(word) > 20:
                    continue

                word_count += 1

                if len(selected_words) < num_words:
                    selected_words.append(word)
                else:
                    # Reservoir sampling: replace a random word with current word
                    # with probability num_words / word_count
                    j = random.randrange(
                        word_count
                    )  # random.randrange(N) gives 0 to N-1
                    if j < num_words:
                        selected_words[j] = word
    except Exception as e:
        print(f"Error reading dictionary file: {e}")
        return []
    return selected_words


async def get_word_definitions():
    """
    Fetches the definition of a word using Google Gemini 1.5 Flash.
    Returns a formatted string with the word, definition, part of speech, and an example.
    """
    if not GOOGLE_API_KEY:
        return "**\nError: Google API Key not set. Cannot fetch definition from Gemini."

    try:
        # genai.configure(api_key=GOOGLE_API_KEY)
        client = genai.Client(api_key=GOOGLE_API_KEY)

        today = datetime.datetime.now().isoformat()
        random_word = await get_random_words_from_file(WORDS_FILE, 2)

        print(today)
        print(random_word)

        # --- Prompt for Gemini ---
        prompt = f"""
        datetime.now().isoformat() = {today}
        overall theme = {random_word}



        You are a helpful "day start thoughts" assistant.
        Provide 5 good words for us today that will help build our vocabulary.
        Tell words that are not super common, but could be uncommon for non-native
        english speakers.
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
            today_theme: string,
            words: WordData[],
            tamil_word: TamilWord
        }}

        """
        # --- End Prompt ---

        # genai.GenerativeModel.generate_content is a synchronous call.
        # To use it in an async function without blocking the event loop,
        # it should be wrapped with `asyncio.to_thread`.
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        response_text = response.text.strip()
        print(response_text)

        # Attempt to parse the JSON response
        try:
            # Gemini might sometimes include markdown code blocks (e.g., ```json...```),
            # so we need to strip them if present.

            response_data = json.loads(response_text)
            def_list = response_data.get("words")
            today_theme = response_data.get("today_theme")

            message_parts = ["Today's words:\n"]
            for data in def_list:
                word_out = data.get("word").capitalize()
                definition = data.get("definition", "Definition not found.")
                part_of_speech = data.get("part_of_speech")
                example = data.get("example")

                message_parts.append(f"\n\n*{word_out}*")
                if part_of_speech:
                    message_parts.append(f"({part_of_speech})")
                message_parts.append(f"\n{definition}")
                if example:
                    message_parts.append(f"\n_Example: {example}_")

            tamil_word_data = response_data.get("tamil_word")
            tamil_word = tamil_word_data.get("word")
            tamil_word_pronunciation = tamil_word_data.get("pronunciation")
            tamil_word_part_of_speech = tamil_word_data.get("part_of_speech")
            tamil_word_meaning = tamil_word_data.get("meaning")
            message_parts.append(
                f"\n\nToday's Tamil word: *{tamil_word}* ({tamil_word_part_of_speech})"
            )
            message_parts.append(f"\n_{tamil_word_pronunciation}_")
            message_parts.append(f"\n{tamil_word_meaning}")

            message_parts.append(f"\n\nA little about today:\n{today_theme}\n\n")
            message_parts.append("\n\n\nBy Light (@justanotherlight)")
            return " ".join(message_parts)

        except json.JSONDecodeError:
            print(f"Error parsing JSON from Gemini : {response_text}")
            return "Definition not found (JSON parse error from Gemini)."
        except Exception as e:
            print(f"Unexpected error processing Gemini response for: {e}")
            return "Definition not found (processing error from Gemini)."

    except Exception as e:
        print(f"Error fetching definition from Gemini: {e}")
        return f"Could not fetch definition due to Gemini API error: {e}"


# async def get_word_definition(word):
#     """Fetches the definition of a word from the dictionary API."""
#     try:
#         # requests is not async, but for a small number of words (5), it's acceptable.
#         # For a larger scale, consider an async HTTP client like aiohttp.
#         response = requests.get(
#             f"{DICTIONARY_API_URL}{word}", timeout=10
#         )  # Add a timeout
#         response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
#         data = response.json()
#
#         if isinstance(data, list) and data:
#             # The API returns a list of entries for a word.
#             # We'll try to get the first definition of the first meaning of the first entry.
#             meanings = data[0].get("meanings")
#             if meanings:
#                 for (
#                     meaning
#                 ) in meanings:  # Iterate through meanings to find a definition
#                     definitions = meaning.get("definitions")
#                     if definitions:
#                         definition = definitions[0].get("definition")
#                         if definition:
#                             return definition
#         return "Definition not found."
#     except requests.exceptions.Timeout:
#         return "Definition request timed out."
#     except requests.exceptions.ConnectionError:
#         return "Could not connect to dictionary API."
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching definition for '{word}': {e}")
#         return "Could not fetch definition due to API error."
#     except (KeyError, IndexError, TypeError) as e:
#         print(f"Error parsing definition for '{word}': {e}")
#         return "Definition structure unexpected."


async def send_telegram_message(bot_token, chat_id, message):
    """Sends a message to a specific Telegram chat."""
    if not bot_token:
        print("Telegram bot token is not set. Cannot send message.")
        return
    if not chat_id:
        print("Telegram chat ID is not set. Cannot send message.")
        return

    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        print(f"Message sent successfully to chat {chat_id}")
    except TelegramError as e:
        print(f"Error sending message to chat {chat_id}: {e}")
    except Exception as e:
        print(
            f"An unexpected error occurred while sending message to chat {chat_id}: {e}"
        )


async def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Please set the TELEGRAM_BOT_TOKEN environment variable.")
        print("You can get a token from BotFather on Telegram.")
        return
    if not TELEGRAM_CHAT_IDS:
        print(
            "Please set the TELEGRAM_CHAT_IDS environment variable (comma-separated list of IDs)."
        )
        print(
            "You can get your user ID from @userinfobot. For group IDs, add the bot to the group and use @getidsbot."
        )
        return

    # print(f"Attempting to fetch {NUM_WORDS_TO_SEND} random words from {WORDS_FILE}...")
    messages_parts = []

    print("Fetching definitions...")
    definitions = await get_word_definitions()
    # for d in definitions:
    #     word = d["word"]
    #     definition = d["definition"]
    messages_parts.append(definitions)

    full_message = "\n\n".join(
        messages_parts
    )  # Add double newline for better separation

    print(f"Sending message to {len(TELEGRAM_CHAT_IDS)} Telegram chat(s)...")
    tasks = [
        send_telegram_message(TELEGRAM_BOT_TOKEN, chat_id, full_message)
        for chat_id in TELEGRAM_CHAT_IDS
    ]
    await asyncio.gather(*tasks)
    print("All messages sent (or attempted).")


if __name__ == "__main__":
    asyncio.run(main())
