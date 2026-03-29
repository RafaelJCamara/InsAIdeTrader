from datetime import date
import os
from agents import Agent, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tools.market.market import get_market_for_prior_date
from tools.notification.telegram_notification import send_notification

load_dotenv(override=True)

PRICE_CHANGE_THRESHOLD_PERCENT = float(os.getenv("PRICE_CHANGE_THRESHOLD_PERCENT"))

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

instructions = f"""
You are a market monitor agent.
Your job is to check the current share price of a stock and compare it to the last saved share price in the database.
If the price has changed by more than {PRICE_CHANGE_THRESHOLD_PERCENT}%, you should send a notification to the user. This price decrease can be both positive or negative. 
As an example:
    - If the last saved price was $100 and the current price is $104, that is a 4% increase, which is more than a 1% change, so you should send a notification. 
    - If the last saved price was $100 and the current price is $98, that is a 2% decrease, which is more than a 1% change, so you should send a notification. 
    - If the last saved price was $100 and the current price is $100.50, that is a 0.5% increase, which is not more than a 1% change, so you should not send a notification.

From all the stocks that have changed over the threshold, please select only the top 5 stocks with the highest percentage change to continue your processing.

The notification message should include the stock symbol, the current price, the previous price, and the percentage change in the notification message.

You have at your disposal the following tools:
- get_market_for_prior_date(today): Gets the market data information for the prior date from the data passed. The function will get the market data for the prior date. It returns a dictionary mapping stock symbols to their prices.
- send_notification(notification): Sends a notification to the user. The notification message should include the stock symbol, the current price, the previous price, and the percentage change in the notification message.

For reference this is today's date: {date.today().isoformat()}.
"""

monitor_message = f"""
Based on the provided market for the current and previous day, determine if any stock has changed in price by more than {PRICE_CHANGE_THRESHOLD_PERCENT} percentage compared to the last saved price. 
If so, send a notification with the relevant details.

For reference this is today's date: {date.today().isoformat()}.
"""

monitor_mcp_servers = []

monitor_tools = [
    get_market_for_prior_date,
    send_notification
]

monitor_handoffs = [
    
]

class Monitor:
    async def create_agent(self) -> Agent:
        print("Creating Monitor agent...")
        agent = Agent(
            name="Monitor Agent",
            instructions=instructions,
            model=gemini_model,
            tools=monitor_tools
        )
        return agent
    
    async def run(self):
        print(f"Using price change threshold of {PRICE_CHANGE_THRESHOLD_PERCENT}%")
        print("Running Monitor agent...")
        try:
            agent = await self.create_agent()
            await Runner.run(agent, monitor_message, max_turns=MAX_TURNS)
        except Exception as e:
            print(f"An error occurred: {e}")