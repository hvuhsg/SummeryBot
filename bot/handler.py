from typing import List
import logging
import os
import uuid

import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.message import Message

__all__ = ["save_message", "start", "summarize"]

MAX_MESSAGES_IN_STORAGE = 50
MIN_MESSAGES_FOR_SUMMARY = 5


async def summarize_messages(messages):
    # Authenticate with OpenAI API
    openai_api_key = os.environ.get("OPENAI_KEY")

    # Build prompt
    prompt = "Summarize the following messages:\n"
    prompt += "\n".join([str(message) for message in messages])

    # Send prompt to GPT-3
    async with aiohttp.ClientSession() as session:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        }
        payload = {"prompt": prompt, "temperature": 0.5, "max_tokens": 1024, "n": 1}
        async with session.post(
            "https://api.openai.com/v1/engines/text-davinci-003/completions",
            json=payload,
            headers=headers,
        ) as response:
            data = await response.json()

    if "error" in data:
        raise ConnectionError(data["error"])

    # Extract summary from GPT-3 response
    summary = data["choices"][0]["text"].strip()

    return summary


def initiate_chat_storage(chat_storage: dict):
    if "messages" not in chat_storage:
        chat_storage["messages"] = []


def add_message_to_storage(message: Message, chat_storage: dict):
    chat_storage["messages"].append(message)

    if len(chat_storage["messages"]) > MAX_MESSAGES_IN_STORAGE:
        chat_storage.pop(0)


def get_saved_messages(chat_storage: dict) -> List[Message]:
    return chat_storage.get("messages", [])


def create_keyboard(sum_id: str):
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Summery", url=f"https://t.me/SummySumBot?start={sum_id}")]
        ]
    )

    return keyboard


async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_storage = context.chat_data
    initiate_chat_storage(chat_storage)

    text = update.message.text
    message_id = update.message.id
    sender = update.effective_user.name
    sent_at = update.message.date
    member = await update.effective_chat.get_member(update.effective_user.id)
    is_admin = member.status in (member.ADMINISTRATOR, member.ADMINISTRATOR)

    message = Message(text, sender, sent_at, is_admin, message_id)
    add_message_to_storage(message, chat_storage)

    logging.info(
        f"Message from {sender} at chat {update.effective_chat.title} saved to storage."
    )


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == update.effective_chat.PRIVATE:
        await update.message.reply_text("Add me to the group and send /sum command to get the summary.")
        return

    chat_storage = context.chat_data
    messages = get_saved_messages(chat_storage)

    if len(messages) < MIN_MESSAGES_FOR_SUMMARY:
        await update.message.reply_text("I have not seen enghph messages to create a summery send a few more messages and try again.")
        return

    cache_id = f"{update.effective_chat.id}{messages[-1]}"

    # Try cache
    sum_id = context.bot_data.get("cache", {}).get(cache_id)
    if sum_id:
        await update.message.reply_text("See summery here", reply_markup=create_keyboard(sum_id))
        return

    # Create summary
    try:
        summary = await summarize_messages(messages)
    except ConnectionError as e:
        logging.error(e)
        await update.message.reply_text(
            "Error summarizing, we are on it!")
        return

    sum_id = str(uuid.uuid4())
    context.bot_data[sum_id] = summary

    if "cache" not in context.bot_data:
        context.bot_data["cache"] = {}

    context.bot_data["cache"][cache_id] = sum_id

    await update.message.reply_text("See summery here", reply_markup=create_keyboard(sum_id))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text
    start_link_id = command.removeprefix("/start ") if command != "/start" else None

    if not start_link_id:
        await update.message.reply_text(
            "Hi, I am SummyBot. I will create a summary of your group messages. Anyone joining in the middle of the conversation will be brought up to speed in no time."
        )
        await update.message.reply_text(
            "Just add me to the group and send /sum (in the group chat) at any point to get summary of the conversation."
        )
        return

    summary = context.bot_data.get(start_link_id)
    if summary:
        await update.message.reply_text(summary)
        return

    await update.message.reply_text("Summary not found")
