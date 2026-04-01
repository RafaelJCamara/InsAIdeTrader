import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
from custom_agents.portfolio import Portfolio

load_dotenv(override=True)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

#TODO: Save history of chat and send that as well to the LLM
#TODO: While waiting for a response, we should see ... in the chat, indicating some activity
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_text = update.message.text
    
    portfolio_agent = Portfolio()
    
    if str(chat_id) != TELEGRAM_CHAT_ID:
        print(f"Received message from unauthorized chat ID {chat_id}, ignoring.")
        return
    
    print(f"Received message from Telegram: {user_text}")
    
    result = await portfolio_agent.run(user_text)
    print(f"Agent result: {result}")
    
    await context.bot.send_message(chat_id=chat_id, text=result)

def main():    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is actively listening for Telegram messages...")
    app.run_polling()

if __name__ == '__main__':
    main()