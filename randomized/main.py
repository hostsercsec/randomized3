import asyncio
from aiogram import Dispatcher, Bot
from handler import router

bot = Bot(token="8407452828:AAElvoYfmhGeTdHXlbK1RcK8ZQ0KrAhWCZI")

dp = Dispatcher()
dp.include_router(router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "main":
    asyncio.run(main())