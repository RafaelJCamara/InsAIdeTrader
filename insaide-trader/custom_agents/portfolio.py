import os

from agents import Agent, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv
from dotenv import load_dotenv
from openai import AsyncOpenAI

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

Please only respond in plain text, avoid using markdown.
"""


class Portfolio:
    def create_agent(self) -> Agent:
        print("Creating Portfolio agent...")
        agent = Agent(
            name="Portfolio Agent",
            instructions=instructions,
            model=gemini_model
        )
        return agent
    
    async def run(self, message: str) -> str:
        print(f"Running the Portfolio agent with message: {message}")
        try:
            agent = self.create_agent()
            result = await Runner.run(agent, message, max_turns=MAX_TURNS)
            return result.final_output
        except Exception as e:
            print(f"An error occurred: {e}")