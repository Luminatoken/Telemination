import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
MAX_PLAYERS = 500
ADMIN_USERNAME = "@revrec2"
current_round = 1
players = {}
player_counter = 1

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global player_counter
    user = update.effective_user
    player_id = str(user.id)
    
    if player_id in players:
        await update.message.reply_text("⚠️ You're already registered!")
        return
        
    # Assign unique player number
    player_number = str(player_counter).zfill(3)
    player_counter += 1
    
    # Track player
    players[player_id] = {
        "name": user.full_name,
        "number": player_number,
        "round": current_round
    }
    
    await update.message.reply_html(
        f"💀 <b>PLAYER {player_number} REGISTERED</b> 💀\n\n"
        f"Welcome {user.mention_html()}!\n"
        f"Round: {current_round}\n"
        f"Players: {len(players)}/{MAX_PLAYERS}\n\n"
        "Type <b>/join</b> to confirm entry"
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
        
    player_data = players[player_id]
    await update.message.reply_text(
        f"✅ ENTRY CONFIRMED!\n"
        f"Player Number: #{player_data['number']}\n"
        f"Status: Active contestant\n"
        f"Players ready: {len(players)}/{MAX_PLAYERS}"
    )

async def players_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME[1:]:
        await update.message.reply_text("⛔ Admin access required!")
        return
        
    player_list = "\n".join(
        f"{data['number']}: {data['name']}" 
        for data in players.values()
    )
    
    await update.message.reply_text(
        f"👥 ACTIVE PLAYERS (Round {current_round})\n"
        f"Total: {len(players)}/{MAX_PLAYERS}\n\n"
        f"{player_list}"
    )

def reset_round():
    global current_round, players, player_counter
    current_round += 1
    players = {}
    player_counter = 1
    logger.info(f"Round reset to {current_round}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("players", players_cmd))
    
    logger.info("Telemination bot starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
