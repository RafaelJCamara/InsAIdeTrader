import asyncio
import os
from dotenv import load_dotenv
from tools.market.market import is_market_open
from custom_agents.monitoring import Monitor

load_dotenv(override=True)

RUN_EVERY_N_MINUTES = int(os.getenv("RUN_EVERY_N_MINUTES", "60"))

RUN_EVEN_WHEN_MARKET_IS_CLOSED = (
    os.getenv("RUN_EVEN_WHEN_MARKET_IS_CLOSED", "false").strip().lower() == "true"
)

async def run_every_n_minutes():
    monitor_agent = Monitor()
    await monitor_agent.run()
    print("Finished running Monitor agent...")
    # while True:
    #     if RUN_EVEN_WHEN_MARKET_IS_CLOSED or is_market_open():
    #         print("Market is open, running Monitor agent")
    #         await monitor_agent.run()
    #     else:
    #         print("Market is closed, skipping run")
        
    #     print(f"***** Sleeping for {RUN_EVERY_N_MINUTES} minutes... *****")
    #     await asyncio.sleep(RUN_EVERY_N_MINUTES * 60)

if __name__ == "__main__":
    print(f"***** Starting scheduler to run every {RUN_EVERY_N_MINUTES} minutes *****")
    asyncio.run(run_every_n_minutes())