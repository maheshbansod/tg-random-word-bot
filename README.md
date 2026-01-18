# Random Word Bot

A clean, production-quality Telegram bot that sends daily vocabulary words with definitions using OpenRouter AI. The bot provides 5 English words with definitions, parts of speech, examples, and a Tamil word of the day, all themed around the current date's significance.

## Features

- **Daily Vocabulary**: 5 carefully selected English words with definitions
- **Tamil Word of the Day**: Common Tamil words with pronunciation and meaning
- **Date Analysis**: Numerology, historical events, and psychological insights
- **AI-Powered**: Uses OpenRouter with Dolphin Mistral model for intelligent content
- **Clean Architecture**: Modular, maintainable codebase with proper separation of concerns
- **Structured Logging**: JSON-formatted logs for production monitoring
- **Type Safety**: Full type annotations with Pydantic validation

## Architecture

```
src/
├── bot/                 # Telegram bot functionality
│   ├── telegram_client.py
│   └── message_formatter.py
├── ai/                  # AI service integration
│   └── openrouter_client.py
├── config/              # Configuration management
│   └── settings.py
└── utils/               # Shared utilities
    ├── word_selector.py
    ├── exceptions.py
    └── logging.py
```

## Setup

### Prerequisites

- Python 3.12+
- Telegram Bot Token
- OpenRouter API Key
- System dictionary file (`/usr/share/dict/words` on Linux/macOS)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd random-word-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Configuration

Create a `.env` file with the following variables:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_IDS=chat_id_1,chat_id_2,chat_id_3

# OpenRouter AI Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=cognitivecomputations/dolphin-mistral-24b-venice-edition:free

# Application Configuration
WORDS_FILE_PATH=/usr/share/dict/words
NUM_WORDS_TO_SEND=5
LOG_LEVEL=INFO
```

#### Getting Required Tokens

1. **Telegram Bot Token**:
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Copy the provided token

2. **Telegram Chat IDs**:
   - For personal chat: Message @userinfobot
   - For group chat: Add bot to group, then message @getidsbot

3. **OpenRouter API Key**:
   - Sign up at [OpenRouter.ai](https://openrouter.ai)
   - Get your API key from the dashboard

## Usage

### Running the Bot

```bash
python main.py
```

The bot will:
1. Select random words for theme inspiration
2. Generate daily content using OpenRouter AI
3. Format the message for Telegram
4. Send to all configured chat IDs

### Scheduling

For daily execution, use a scheduler like cron:

```bash
# Run daily at 8 AM
0 8 * * * cd /path/to/random-word-bot && source .venv/bin/activate && python main.py
```

Or use systemd timer for more robust scheduling.

## Development

### Code Quality

The project follows these best practices:
- **Type Hints**: Full type annotations throughout
- **Error Handling**: Custom exceptions with proper error recovery
- **Logging**: Structured JSON logging with contextual information
- **Configuration**: Pydantic-based settings with validation
- **Async/Await**: Proper async patterns for I/O operations

### Project Structure

- **Modular Design**: Each component has a single responsibility
- **Dependency Injection**: Configuration passed to components
- **Error Boundaries**: Custom exceptions for different error types
- **Logging Integration**: Structured logging throughout the application

### Dependencies

- `openai`: OpenRouter API client
- `python-telegram-bot`: Telegram bot framework
- `pydantic`: Data validation and settings management
- `pydantic-settings`: Environment-based configuration
- `structlog`: Structured logging

## Monitoring

The bot outputs structured JSON logs that can be easily monitored:

```json
{
  "timestamp": "2024-01-18T08:00:00.000Z",
  "level": "info",
  "logger": "main",
  "message": "Starting Random Word Bot",
  "chat_count": 2,
  "model": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"
}
```

## Troubleshooting

### Common Issues

1. **Dictionary file not found**:
   - Ensure `/usr/share/dict/words` exists
   - On macOS: Install with `brew install words`
   - Or set `WORDS_FILE_PATH` to your dictionary location

2. **Telegram API errors**:
   - Verify bot token is correct
   - Check chat IDs are valid
   - Ensure bot has permission to send messages

3. **OpenRouter API errors**:
   - Verify API key is valid
   - Check model name is correct
   - Monitor rate limits

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the logs for error details