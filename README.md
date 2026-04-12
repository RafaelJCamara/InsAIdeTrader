## Project scope

The purpose of InsAIdeTrader is to monitor the Stock Market and trigger notifications whenever some stocks have price decreases.

It also allows the end user to interact with it, namely for stock purchase simulation purposes.


## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable                         | Description                                                                                  |
|----------------------------------|----------------------------------------------------------------------------------------------|
| `GOOGLE_API_KEY`                 | API key for Google Gemini, used by the AI agents.                                            |
| `POLYGON_API_KEY`                | API key for [Polygon.io](https://polygon.io/), used to fetch stock market data.              |
| `RUN_EVERY_N_MINUTES`            | How often (in minutes) the monitoring agent checks stock prices.                             |
| `RUN_EVEN_WHEN_MARKET_IS_CLOSED` | Set to `True` to run checks even outside market hours.                                       |
| `PRICE_CHANGE_THRESHOLD_PERCENT` | Minimum price change percentage to trigger a notification.                                   |
| `TELEGRAM_TOKEN`                 | Bot token from [BotFather](https://t.me/BotFather) for sending Telegram notifications.      |
| `TELEGRAM_CHAT_ID`              | Telegram chat ID where notifications are sent.                                               |
| `ELEVEN_LABS_API_KEY`            | API key for [ElevenLabs](https://elevenlabs.io/), used for text-to-speech audio generation.  |

## Agents

### Monitor/Tracking agent

This agent is responsible for tracking the stock prices and trigger follow up actions when they go higher/below a certain value.