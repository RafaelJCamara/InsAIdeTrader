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
        instructions = """
        You're a seasoned financial researcher with a talent for finding the most relevant information about a given company.
        Known for your ability to find the most relevant
        information and present it in a clear and concise manner.

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
                Research the following company: {company}.
                Find the most relevant information about this company that could be useful for an investor.
            """
            await Runner.run(agent, research_message, max_turns=MAX_TURNS)
        except Exception as e:
            print(f"An error occurred: {e}")