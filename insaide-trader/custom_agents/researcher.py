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
        
        Your research must always include:
        1. Company background: What they do, their industry, key products/services (keep it brief, 1-2 sentences)
        2. Price movement catalyst: Recent news, events, earnings reports, product announcements, regulatory changes, market events, or other specific factors
        
        IMPORTANT:
        - If you find catalysts/news explaining the move, clearly state what is causing the stock to trend today
        - If you cannot find any recent news or specific catalyst, state this professionally and honestly (e.g., "No specific recent news catalysts detected driving this price movement at this time")
        - Always provide the company background regardless of whether you find news
        
        Present your findings in a clear, concise manner that combines both the company context and what caused (or did not cause identifiably) the stock price movement.
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
                Investigate the following stock price movement and provide complete analysis:
                {company}
                
                Please research and provide:
                1. Company background: Brief description of what this company does, their industry, and key products/services
                2. Why this stock is trending: Search for recent news, earnings reports, product announcements, regulatory changes, market events, or other specific factors causing the price movement
                
                IMPORTANT: If you cannot find specific recent news or catalysts driving the price movement, state this clearly and professionally in your response.
                
                Provide a comprehensive but concise analysis that explains both who the company is and why their stock is moving today.
            """
            await Runner.run(agent, research_message, max_turns=MAX_TURNS)
        except Exception as e:
            print(f"An error occurred: {e}")