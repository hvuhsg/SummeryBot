import logging

from bot.bot import run_bot
from bot.handler import save_message, start, summarize

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    run_bot(save_message, start, summarize)
