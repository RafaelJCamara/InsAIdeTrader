import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

load_dotenv(override=True)

from custom_agents.portfolio import Portfolio
from tools.market.market import get_share_price
from tools.portfolio.database import (
    execute_buy,
    execute_sell,
    execute_deposit,
    get_all_holdings,
    get_balance,
    get_transactions,
)


DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("InsAIdeTrader API is starting up...")
    yield
    print("InsAIdeTrader API is shutting down...")


app = FastAPI(
    title="InsAIdeTrader API",
    description="API for managing the InsAIdeTrader portfolio, callable from n8n or any HTTP client.",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(..., description="Natural-language instruction for the portfolio agent")
    chat_id: str | int | None = Field(
        None,
        description="Session ID for conversation memory (defaults to TELEGRAM_CHAT_ID)",
    )


class ChatResponse(BaseModel):
    response: str


class TradeRequest(BaseModel):
    symbol: str = Field(..., description="Stock ticker symbol (e.g. AAPL)")
    shares: int = Field(..., gt=0, description="Number of shares")


class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Dollar amount to deposit")


class BalanceResponse(BaseModel):
    balance: float


class HoldingsResponse(BaseModel):
    holdings: dict[str, dict]
    balance: float


class TradeResponse(BaseModel):
    status: str
    balance: float
    holdings: dict[str, dict]


class DepositResponse(BaseModel):
    status: str
    balance: float


# ---------------------------------------------------------------------------
# Chat endpoint – delegates to the Portfolio agent
# ---------------------------------------------------------------------------

@app.post("/portfolio/chat", response_model=ChatResponse)
async def portfolio_chat(request: ChatRequest):
    """Send a natural-language message to the Portfolio agent and get a response."""
    chat_id = str(request.chat_id) if request.chat_id is not None else DEFAULT_CHAT_ID
    agent = Portfolio(chat_id)
    result = await agent.run(request.message)
    if result is None:
        raise HTTPException(status_code=500, detail="Agent returned no response")
    return ChatResponse(response=result)


# ---------------------------------------------------------------------------
# Direct endpoints – fast, deterministic, no agent overhead
# ---------------------------------------------------------------------------

@app.get("/portfolio/balance", response_model=BalanceResponse)
async def wallet_balance():
    """Return the current wallet cash balance."""
    return BalanceResponse(balance=get_balance())


@app.post("/portfolio/deposit", response_model=DepositResponse)
async def deposit(req: DepositRequest):
    """Deposit money into the wallet."""
    try:
        new_balance = execute_deposit(req.amount)
        return DepositResponse(
            status=f"Deposited ${req.amount:.2f}",
            balance=new_balance,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/portfolio/holdings", response_model=HoldingsResponse)
async def get_holdings():
    """Return the current portfolio holdings and wallet balance."""
    return HoldingsResponse(holdings=get_all_holdings(), balance=get_balance())


@app.post("/portfolio/buy", response_model=TradeResponse)
async def buy_stock(trade: TradeRequest):
    """Buy shares of a stock at the current market price."""
    symbol = trade.symbol.upper()
    price = get_share_price(symbol)
    if price <= 0:
        raise HTTPException(status_code=400, detail=f"Could not get a valid price for {symbol}")

    try:
        result = execute_buy(symbol, trade.shares, price)
        return TradeResponse(
            status=(
                f"Bought {result['shares_bought']} shares of {symbol} "
                f"at ${result['price_per_share']:.2f}/share "
                f"(total ${result['total_cost']:.2f})"
            ),
            balance=result["remaining_balance"],
            holdings=get_all_holdings(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/portfolio/sell", response_model=TradeResponse)
async def sell_stock(trade: TradeRequest):
    """Sell shares of a stock at the current market price."""
    symbol = trade.symbol.upper()
    price = get_share_price(symbol)
    if price <= 0:
        raise HTTPException(status_code=400, detail=f"Could not get a valid price for {symbol}")

    try:
        result = execute_sell(symbol, trade.shares, price)
        return TradeResponse(
            status=(
                f"Sold {result['shares_sold']} shares of {symbol} "
                f"at ${result['price_per_share']:.2f}/share "
                f"(total ${result['total_proceeds']:.2f})"
            ),
            balance=result["remaining_balance"],
            holdings=get_all_holdings(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/portfolio/transactions")
async def list_transactions(limit: int = 50):
    """Return recent transaction history."""
    return {"transactions": get_transactions(limit)}


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
