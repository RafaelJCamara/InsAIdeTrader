from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, OpenAIChatCompletionsModel, function_tool
from agents.mcp import MCPServerStdio
import os
from datetime import datetime

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

gemini_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

gemini_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-pro",
    openai_client=gemini_client
)


@function_tool
async def google_search(query: str) -> str:
    """Searches the web for information related to the query and returns a brief summary of the takeaways.

    Args:
        query (str): The search query to research.
    Returns:
        str: A brief summary of the takeaways from the web search.
    """
    print(f"Performing web search for query: {query}")
    
    env = {"GEMINI_API_KEY": os.getenv("GOOGLE_API_KEY"), "GEMINI_MODEL": "gemini-2.5-pro"}
    params = {"command": "npx","args": ["-y", "mcp-gemini-google-search"],"env": env}
    async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as server:
        instructions = "You are able to search the web for information and briefly summarize the takeaways."
        request = f"Please research the latest news on Amazon stock price and briefly summarize its outlook. \
            For context, the current date is {datetime.now().strftime('%Y-%m-%d')}"
    agent = Agent(
        name="web_researcher", 
        instructions=instructions, 
        model=gemini_model,
        mcp_servers=[server]
        )
    result = await Runner.run(agent, request)
    print("Final output: ", result.final_output)
    
    return f"Summary of web search results for query: {query}"