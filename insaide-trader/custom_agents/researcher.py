from datetime import date
import os
from agents import Agent, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tools.market.market import get_market_for_prior_date
from tools.notification.telegram_notification import send_notification
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

monitor_tools = [
    google_search
]

class Researcher:
    def create_agent(self) -> Agent:
        instructions = f"""
        You're a seasoned financial analyst specializing in finding the catalysts and reasons behind stock price movements.
        When a stock has a significant price change, your job is to research and identify what caused it.
        Focus on finding recent news, events, earnings reports, market catalysts, regulatory changes, or other factors that could explain why the stock moved.
        You should look for specific, recent information that directly caused or influenced the price change - not general company information.
        Present your findings in a clear, concise manner that explains the connection between the event/news and the stock price movement.
        For reference this is today's date: {date.today().isoformat()}.
        """
        print("Creating Researcher agent...")
        agent = Agent(
            name="Researcher Agent",
            instructions=instructions,
            model=gemini_model,
            tools=monitor_tools
        )
        return agent
    
    async def run(self, company: str):
        print(f"Researching company: {company}")
        try:
            agent = await self.create_agent()
            research_message = f"""
                Investigate why the following stock moved recently and find the catalysts or reasons behind the price change:
                {company}
                Search for recent news, earnings reports, product announcements, regulatory changes, market events, or other specific factors that could have caused this stock price movement.
                Provide a clear explanation of what caused the stock to move.
            """
            await Runner.run(agent, research_message, max_turns=MAX_TURNS)
        except Exception as e:
            print(f"An error occurred: {e}")