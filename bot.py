import logging
from typing import Dict, Any
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

BOT_TOKEN: str = "8003276937:AAH_3STTw5r2UBnzCGYjCtjpz3TEBrvDcf4"
MAX_PLAYERS: int = 500
ADMIN_USERNAME: str = "@revrec2"

current_round: int = 1
players: Dict[int, Dict[str, Any]] = {}
assigned_numbers: set[int] = set()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("telemination-bot")

def get_next_number() -> int:
    for num in range(1, MAX_PLAYERS + 1):
        if num not in assigned_numbers:
            return num
    return -1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        player_id = user.id
        if player_id in players:
            await update.message.reply_text(
                f"💀 PLAYER {players[player_id]['number']:03d} REGISTERED 💀\n"
                f"Welcome {user.full_name}!\n"
                f"Round: {current_round}\n"
                f"Players: {len(players)}/{MAX_PLAYERS}"
            )
            return
        if len(players) >= MAX_PLAYERS:
            await update.message.reply_text("🚨 ROUND FULL! Next round starts soon")
            return
        number = get_next_number()
        if number == -1:
            await update.message.reply_text("🚨 ROUND FULL! Next round starts soon")
            return
        assigned_numbers.add(number)
        players[player_id] = {
            "name": user.full_name,
            "number": number,
            "confirmed": False,
        }
        await update.message.reply_text(
            f"💀 PLAYER {number:03d} REGISTERED 💀\n"
            f"Welcome {user.full_name}!\n"
            f"Round: {current_round}\n"
            f"Players: {len(players)}/{MAX_PLAYERS}"
        )
    except TelegramError as e:
        logger.error(f"Telegram API error in /start: {e}")

async def join(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        player_id = user.id
        if player_id not in players:
            await update.message.reply_text("Please use /start to register first.")
            return
        if players[player_id]["confirmed"]:
            await update.message.reply_text(
                f"✅ CONFIRMED!\nNumber: #{players[player_id]['number']:03d}\n"
                f"Players: {len(players)}/{MAX_PLAYERS}"
            )
            return
        if len(players) > MAX_PLAYERS:
            await update.message.reply_text("🚨 ROUND FULL! Next round starts soon")
            return
        players[player_id]["confirmed"] = True
        await update.message.reply_text(
            f"✅ CONFIRMED!\nNumber: #{players[player_id]['number']:03d}\n"
            f"Players: {len(players)}/{MAX_PLAYERS}"
        )
        if sum(1 for p in players.values() if p["confirmed"]) >= MAX_PLAYERS:
            await reset_round(context)
    except TelegramError as e:
        logger.error(f"Telegram API error in /join: {e}")

async def players_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = update.effective_user
        if user.username != ADMIN_USERNAME.lstrip("@"):
            return
        player_list = [
            f"{p['number']:03d}: {p['name']}" for p in sorted(players.values(), key=lambda x: x["number"])
        ]
        msg = f"👥 PLAYERS: {len(players)}/{MAX_PLAYERS}\n" + ", ".join(player_list)
        await update.message.reply_text(msg)
    except TelegramError as e:
        logger.error(f"Telegram API error in /players: {e}")

async def reset_round(context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_round, players, assigned_numbers
    current_round += 1
    players = {}
    assigned_numbers = set()
    logger.info(f"Round reset. Now at round {current_round}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception: {context.error}")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("join", join))
    application.add_handler(CommandHandler("players", players_command))
    application.add_error_handler(error_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
