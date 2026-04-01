import os

from agents import Agent, OpenAIChatCompletionsModel, Runner, SQLiteSession
from dotenv import load_dotenv
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tools.portfolio.portfolio_management import buy_stock, get_current_portfolio_holdings, get_portfolio_performance, sell_stock
from tools.search.google_search import google_search

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MAX_TURNS = 30

gemini_client = AsyncOpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

gemini_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-pro",
    openai_client=gemini_client
)

instructions = """
You are a portfolio management agent. Your job is to help the user manage their stock portfolio by providing insights, analysis, and recommendations based on the current market conditions and the user's portfolio holdings.
You have access to the following tools:
    - get_current_portfolio_holdings: This tool returns the user's current stock holdings in their portfolio, including the stock symbols to the number of shares held. If 0 is the value for a stock, that means the user does not currently hold any shares of that stock, so don't include it in the response.
    - get_portfolio_performance: This tool returns the current performance of the user's portfolio, including metrics such as total value and percentage change.
    - buy_stock(symbol, shares): This tool allows you to buy a specified number of shares of a stock. You can use this tool to make recommendations to the user about which stocks to buy based on your analysis.
    - sell_stock(symbol, shares): This tool allows you to sell a specified number of shares of a stock. You can use this tool to make recommendations to the user about which stocks to sell based on your analysis.
    - google_search(query): This tool allows you to search the web for information related to the stock market, specific companies, or other relevant topics. You can use this tool to gather information that can inform your analysis and recommendations.
If in the conversation the user asks to buy a specific stock by company name, you must search for the corresponding stock symbol and use that symbol when calling the buy_stock tool. For example, if the user says "I want to buy 10 shares of Apple", you should search for the stock symbol for Apple (AAPL) and then call buy_stock("AAPL", 10).
Whatever results the tools return, make sure to return to the user in comprehensive text.
Please only respond in plain text, avoid using markdown.
"""

tools = [
    get_current_portfolio_holdings,
    get_portfolio_performance,
    buy_stock,
    sell_stock,
    google_search
]

class Portfolio:
    
    def __init__(self, chat_id:str):
        self.chat_id = chat_id
        
    def _get_session(self):
        return SQLiteSession(str(self.chat_id), "bot_memory.db")

    def create_agent(self) -> Agent:
        print("Creating Portfolio agent...")
        agent = Agent(
            name="Portfolio Agent",
            instructions=instructions,
            model=gemini_model,
            tools=tools
        )
        return agent
    
    async def run(self, message: str) -> str:
        print(f"Running the Portfolio agent with message: {message}")
        try:
            agent = self.create_agent()
            result = await Runner.run(agent, message, max_turns=MAX_TURNS, session=self._get_session())
            return result.final_output
        except Exception as e:
            print(f"An error occurred: {e}")