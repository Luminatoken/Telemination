import logging
from typing import Dict, Any
from dotenv import load_dotenv
import os

from telegram import Update, User
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

# Load environment variables from .env file
load_dotenv()

# Config (read BOT_TOKEN from environment variable)
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "@revrec2")
MAX_PLAYERS: int = 500

# Game state (in-memory)
current_round: int = 1
players: Dict[int, Dict[str, Any]] = {}
player_counter: int = 1

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def get_display_name(user: User) -> str:
    """Get the user's display name for registration."""
    if user.full_name:
        return user.full_name
    if user.username:
        return f"@{user.username}"
    return f"ID:{user.id}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Register the user with a unique number for the current round."""
    global player_counter

    user = update.effective_user
    user_id = user.id

    if user_id in players and players[user_id]["round"] == current_round:
        # Already registered, resend info
        player_num = players[user_id]["number"]
    elif len(players) >= MAX_PLAYERS:
        await update.message.reply_text("🚨 ROUND FULL! Next round soon")
        return
    else:
        # Register new player for this round
        player_num = player_counter
        players[user_id] = {
            "name": get_display_name(user),
            "number": player_num,
            "round": current_round,
            "confirmed": False,
        }
        player_counter += 1

    await update.message.reply_text(
        f"💀 PLAYER {player_num:03d} REGISTERED 💀\n"
        f"Welcome {get_display_name(user)}!\n"
        f"Round: {current_round}\n"
        f"Players: {len(players)}/{MAX_PLAYERS}\n"
        f"Type /join to confirm"
    )
    logger.info(f"User {user_id} registered as {player_num:03d} for round {current_round}")

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirm the user's participation as an active contestant."""
    user = update.effective_user
    user_id = user.id

    if len(players) >= MAX_PLAYERS and (user_id not in players or players[user_id]["round"] != current_round):
        await update.message.reply_text("🚨 ROUND FULL! Next round soon")
        return

    if user_id not in players or players[user_id]["round"] != current_round:
        await update.message.reply_text("You must /start to register first.")
        return

    if players[user_id].get("confirmed"):
        await update.message.reply_text(
            f"✅ CONFIRMED!\nNumber: #{players[user_id]['number']:03d}\nStatus: Active contestant\nPlayers: {len(players)}/{MAX_PLAYERS}"
        )
        return

    players[user_id]["confirmed"] = True
    await update.message.reply_text(
        f"✅ CONFIRMED!\nNumber: #{players[user_id]['number']:03d}\nStatus: Active contestant\nPlayers: {len(players)}/{MAX_PLAYERS}"
    )
    logger.info(
    f"User {user_id} confirmed participation as #{players[user_id]['number']:03d} in round {current_round})"
    )

async def players_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin-only: List all players for the current round."""
    user = update.effective_user
    if (user.username and f"@{user.username}" == ADMIN_USERNAME) or (user.mention_html() == ADMIN_USERNAME):
        lines = [
            f"👥 PLAYERS (Round {current_round})",
            f"Total: {len(players)}/{MAX_PLAYERS}",
            ""
        ]
        sorted_players = sorted(players.values(), key=lambda p: p["number"])
        for p in sorted_players:
            lines.append(f"{p['number']:03d}: {p['name']}")
        await update.message.reply_text("\n".join(lines))
        logger.info("Admin requested player list.")
    else:
        await update.message.reply_text("❌ You are not authorized to use this command.")

def reset_round() -> None:
    """Increment the round and reset all player data."""
    global current_round, players, player_counter
    current_round += 1
    players.clear()
    player_counter = 1
    logger.info(f"Round reset. Now starting round {current_round}.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors from Telegram API."""
    logger.error(f"Exception while handling update: {context.error}")
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("⚠️ An error occurred. Please try again later.")
        except TelegramError:
            pass  # Don't crash if we can't send a message

def main() -> None:
    # If you use a hardcoded token, this check is just a sanity check.
    if not BOT_TOKEN or BOT_TOKEN.strip() == "":
        logger.error("BOT_TOKEN is not set. Please set it in the code or as an environment variable.")
        raise RuntimeError("BOT_TOKEN is not set.")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join)
    application.add_handler(CommandHandler("players", players_cmd))

    application.add_error_handler(error_handler)

    logger.info("Bot started.")
    application.run_polling()

if __name__ == "__main__":
    main()
