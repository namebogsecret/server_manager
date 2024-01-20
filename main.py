#!/usr/bin/env python3
import sys
import os
from os.path import dirname, abspath
if getattr(sys, 'frozen', False):
    src_path = sys._MEIPASS
else:
    src_path = dirname(abspath(__file__))
sys.path.append(src_path)
import asyncio
import nest_asyncio
from handlers_async import  gpt_chat, voice_to_text, BotStates, callback_query_handler, service_management_handler

from aiogram import Bot, Dispatcher #, types

#from aiogram.types import ParseMode
#from aiogram.utils import executor
from dotenv import load_dotenv
load_dotenv()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
nest_asyncio.apply()

def set_affinity(cores):
    """ Устанавливает аффинность (привязку) процесса к определенным ядрам. """
    pid = os.getpid()
    os.sched_setaffinity(pid, cores)
    print("done")
set_affinity([1])

async def my_telegram_bot() -> None:
    api = os.getenv("TELEGRAM_API")
    bot = Bot(token=api)
    dp = Dispatcher(bot)

    # Register your async handlers here, for example:
    dp.register_message_handler(gpt_chat, content_types=['text'])
    dp.register_message_handler(voice_to_text, content_types=['voice'])
    #dp.register_callback_query_handler(callback_query_handler, state='*')
    #dp.register_message_handler(service_management_handler, state=BotStates.service_management)

    
    try:
        await dp.start_polling()
    finally:
        await bot.close()

async def main():
    await my_telegram_bot()

if __name__ == "__main__":
    asyncio.run(main())
