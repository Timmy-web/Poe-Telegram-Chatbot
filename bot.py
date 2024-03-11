import asyncio
import fastapi_poe as fp
from telegram import Update, constants, error
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import logging
import os

class GetUpdatesFilter(logging.Filter):
    def filter(self, record):
        return "api.telegram.org" not in record.getMessage()
    
class CustomHandler(logging.Handler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addFilter(GetUpdatesFilter())

    def emit(self, record):
        if not self.filter(record):
            return
        print(self.format(record))

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[CustomHandler()])

# Replace <api_key> with your actual API key, ensuring it is a string.
api_key = os.environ["POE_API_KEY"]
bot_names = {
    'gpt4': 'GPT-4',
    'claude3': 'Claude-3-Opus'
}
default_bot_name = bot_names['claude3']
user_tasks = {}
user_context = {}

async def get_responses(api_key, messages, response_list, done, bot_name):
    async for chunk in fp.get_bot_response(messages=messages, bot_name=bot_name, api_key=api_key):
        response_list.append(chunk.text)
    done.set()
    
async def update_telegram_message(update, context, response_list, done, response_text, update_interval=1):
    response_message = None
    last_response_text = ""

    while not done.is_set():
        if response_list:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=constants.ChatAction.TYPING)

            response_text[0] += "".join(response_list)
            response_list.clear()

            if response_text[0].strip() != last_response_text.strip():
                response_message = await send_response_message(context, update.effective_chat.id, response_text[0], response_message)
                last_response_text = response_text[0]

        await asyncio.sleep(update_interval)

    if response_list:
        response_text[0] += "".join(response_list)
        response_list.clear()

        if response_text[0].strip() != last_response_text.strip():
            await send_response_message(context, update.effective_chat.id, response_text[0], response_message)

async def handle_user_request(user_id, update, context):
    if user_id in user_context and user_context[user_id]['messages']:
        response_list = []
        done = asyncio.Event()
        response_text = [""]
        api_task = asyncio.create_task(get_responses(api_key, user_context[user_id]['messages'], response_list, done, user_context[user_id]['bot_name']))
        telegram_task = asyncio.create_task(update_telegram_message(update, context, response_list, done, response_text))

        await asyncio.gather(api_task, telegram_task)

        # Add the bot's response to the context
        user_context[user_id]['messages'].append(fp.ProtocolMessage(role="bot", content=response_text[0]))

async def handle_message(update: Update, context):
    user_id = update.effective_user.id
    logging.info(f"开始处理用户 {user_id} 的请求")
    user_input = update.message.text
    message = fp.ProtocolMessage(role="user", content=user_input)

    # 获取用户上下文
    if user_id not in user_context:
        user_context[user_id] = {'messages': [message], 'bot_name': default_bot_name}
    else:
        user_context[user_id]['messages'].append(message)

    # 检查用户是否已有对应的任务,如果没有则创建一个新任务
    if user_id not in user_tasks or user_tasks[user_id].done():
        user_tasks[user_id] = asyncio.create_task(handle_user_request(user_id, update, context))

async def send_response_message(context, chat_id, response_text, response_message=None):
    if response_text.strip():
        try:
            if response_message is None:
                response_message = await context.bot.send_message(chat_id=chat_id, text=response_text, parse_mode="Markdown")
            else:
                await response_message.edit_text(response_text, parse_mode="Markdown")
        except error.BadRequest:
            if response_message is None:
                response_message = await context.bot.send_message(chat_id=chat_id, text=response_text)
            else:
                await response_message.edit_text(response_text)
    return response_message

async def start(update: Update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="欢迎使用Poe AI助手! 请输入您的问题。[Write by Claude-3-Opus-200k]")

async def new_conversation(update: Update, context):
    user_id = update.effective_user.id
    bot_name = default_bot_name
    if user_id in user_context:
        bot_name = user_context[user_id]['bot_name']
        user_context[user_id] = {'messages': [], 'bot_name': bot_name}
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"====== 新的对话开始（{bot_name}） ======")

async def gpt4(update: Update, context):
    user_id = update.effective_user.id
    bot_name = bot_names['gpt4']
    await switch_model(user_id, bot_name, update, context)

async def claude3(update: Update, context):
    user_id = update.effective_user.id
    bot_name = bot_names['claude3']
    await switch_model(user_id, bot_name, update, context)

async def switch_model(user_id, bot_name, update, context):
    if user_id not in user_context or user_context[user_id]['bot_name'] != bot_name:
        user_context[user_id] = {'messages': [], 'bot_name': bot_name}
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"已切换到 {bot_name} 模型,并清空上下文。")
        await new_conversation(update, context)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"当前已经是 {bot_name} 模型。")

def main():
    application = Application.builder().token(os.environ["TELEGRAM_BOT_TOKEN"]).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    new_handler = CommandHandler('new', new_conversation)
    application.add_handler(new_handler)

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    application.add_handler(message_handler)

    gpt4_handler = CommandHandler('gpt4', gpt4)
    application.add_handler(gpt4_handler)

    claude3_handler = CommandHandler('claude3', claude3)
    application.add_handler(claude3_handler)

    # 运行
    application.run_polling()

if __name__ == '__main__':
    main()
