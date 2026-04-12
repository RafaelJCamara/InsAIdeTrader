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

## API

The project exposes a FastAPI server that n8n (or any HTTP client) can call to interact with the portfolio.

### Running the API

```bash
cd insaide-trader
uv run python api.py
```

The server starts on `http://localhost:8000`. Interactive docs are available at `http://localhost:8000/docs`.

### Endpoints

| Method | Path                    | Description                                                        |
|--------|-------------------------|--------------------------------------------------------------------|
| `POST` | `/portfolio/chat`       | Send a natural-language message to the Portfolio agent              |
| `GET`  | `/portfolio/holdings`   | List current portfolio holdings                                    |
| `GET`  | `/portfolio/performance`| Get portfolio performance metrics                                  |
| `POST` | `/portfolio/buy`        | Buy shares of a stock (`{ "symbol": "AAPL", "shares": 5 }`)       |
| `POST` | `/portfolio/sell`       | Sell shares of a stock (`{ "symbol": "AAPL", "shares": 2 }`)      |
| `GET`  | `/health`               | Health check                                                       |

The `/portfolio/chat` endpoint accepts a JSON body with `message` (required) and an optional `chat_id` for session memory:

```json
{ "message": "Buy 10 shares of Apple", "chat_id": "my-session" }
```

## Agents

### Monitor/Tracking agent

This agent is responsible for tracking the stock prices and trigger follow up actions when they go higher/below a certain value.