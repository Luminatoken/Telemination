import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv('BOT_TOKEN', '8003276937:AAH_3STTw5r2UBnzCGYjCtjpz3TEBrvDcf4')
MAX_PLAYERS = 500
current_round = 1
players = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player_id = str(user.id)
    player_number = str(len(players) + 1).zfill(3)
    
    players[player_id] = {
        "name": user.full_name,
        "number": player_number,
        "round": current_round
    }
    
    await update.message.reply_html(
        f"💀 <b>PLAYER {player_number} REGISTERED</b> 💀\n\n"
        f"Welcome {user.mention_html()}!\nRound: {current_round}\n"
        f"Players: {len(players)}/{MAX_PLAYERS}\n\n"
        "Type /join to confirm"
    )

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player_id = str(user.id)
    
    if player_id not in players:
        await update.message.reply_text("⚠️ Please /start first!")
        return
        
    if len(players) >= MAX_PLAYERS:
        await update.message.reply_text("🚨 ROUND FULL! Next round starts soon")
        return
        
    await update.message.reply_text(
        f"✅ ENTRY CONFIRMED!\n"
        f"Number: #{players[player_id]['number']}\n"
        f"Players ready: {len(players)}/{MAX_PLAYERS}"
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    logger.info("Telemination bot starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
