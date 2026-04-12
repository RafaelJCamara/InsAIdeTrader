import os

from agents import Agent, OpenAIChatCompletionsModel, Runner, SQLiteSession
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tools.portfolio.portfolio_management import (
    buy_stock,
    sell_stock,
    get_current_portfolio_holdings,
    get_wallet_balance,
    deposit_money,
)
from tools.search.stock_search import get_company_name_from_ticker, get_ticker_from_name

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MAX_TURNS = 30

gemini_client = AsyncOpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

gemini_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=gemini_client
)

instructions = """
You are a portfolio management agent. Your job is to help the user manage their stock portfolio by providing insights, analysis, and recommendations based on the current market conditions and the user's portfolio holdings.

IMPORTANT CONCEPTS:
- The user has a cash wallet. Before buying stocks they must have enough money in their wallet.
- To add money, the user can deposit funds using the deposit_money tool.
- Buying stocks deducts money from the wallet at the current market price.
- Selling stocks credits the proceeds back into the wallet.
- The user cannot buy stocks if their wallet balance is too low.
- The user cannot sell more shares than they currently hold.

You have access to the following tools:
    - get_wallet_balance: Returns the current cash balance in the wallet.
    - deposit_money(amount): Deposits money into the wallet. Use when the user wants to add funds.
    - get_current_portfolio_holdings: Returns the user's current stock holdings with shares, average cost, current market value, P&L, and wallet balance. IMPORTANT: After calling this tool, you MUST call get_company_name_from_ticker for each stock ticker to get the company name, then present both the company name and ticker symbol to the user (e.g., "Apple (AAPL): 10 shares").
    - buy_stock(symbol, shares): Buys shares at the current market price. The cost is deducted from the wallet. Will fail if the wallet balance is insufficient.
    - sell_stock(symbol, shares): Sells shares at the current market price. The proceeds are added to the wallet. Will fail if the user doesn't hold enough shares.
    - get_ticker_from_name(company_name): Searches for a stock ticker symbol by company name.
    - get_company_name_from_ticker(ticker): Searches for a company name by ticker symbol.

If the user asks to buy a stock by company name, first look up the ticker with get_ticker_from_name, then call buy_stock with that ticker.
If a buy or sell fails (insufficient funds or shares), relay the error clearly and suggest alternatives (e.g., deposit more money, sell fewer shares).
Whatever results the tools return, make sure to return to the user in comprehensive text.
Please only respond in plain text, avoid using markdown.
"""

tools = [
    get_wallet_balance,
    deposit_money,
    get_current_portfolio_holdings,
    buy_stock,
    sell_stock,
    get_ticker_from_name,
    get_company_name_from_ticker,
]


class Portfolio:

    def __init__(self, chat_id: str):
        self.chat_id = chat_id

    def _get_session(self):
        return SQLiteSession(str(self.chat_id), "bot_memory.db")

    def create_agent(self) -> Agent:
        print("Creating Portfolio agent...")
        agent = Agent(
            name="Portfolio Agent",
            instructions=instructions,
            model=gemini_model,
            tools=tools,
        )
        return agent

    async def run(self, message: str) -> str:
        print(f"Running the Portfolio agent with message: {message}")
        try:
            agent = self.create_agent()
            result = await Runner.run(
                agent, message, max_turns=MAX_TURNS, session=self._get_session()
            )
            return result.final_output
        except Exception as e:
            print(f"An error occurred: {e}")
