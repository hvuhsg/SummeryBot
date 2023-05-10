import logging
from typing import Callable
import os
from pathlib import Path

from telegram.ext import ApplicationBuilder, MessageHandler, filters, PicklePersistence, CommandHandler

__all__ = ["run_bot"]

TOKEN = os.environ.get("BOT_TOKEN")


def run_bot(on_message: Callable, on_start: Callable, on_sum: Callable):
    if not TOKEN:
        logging.info("Set token in environment variable 'BOT_TOKEN'")
        exit(1)

    current_path = Path(__file__).parent
    persistence_path = current_path.parent / "data" / "persistence.pickle"
    logging.info(
        f"Bot setting up with persistence, state is stored at '{persistence_path.absolute()}'"
    )

    bot = (
        ApplicationBuilder()
        .token(TOKEN)
        .persistence(PicklePersistence(str(persistence_path.absolute())))
        .build()
    )

    # Handlers
    bot.add_handler(CommandHandler("start", on_start))
    bot.add_handler(CommandHandler("sum", on_sum))
    bot.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, on_message))

    logging.info("Starting to read messages")
    bot.run_polling()
