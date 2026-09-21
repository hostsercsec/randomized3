import asyncio
from aiogram import Bot, Dispatcher
from handler import router

bot = Bot(token="8407452828:AAElvoYfmhGeTdHXlbK1RcK8ZQ0KrAhWCZI")

dp = Dispatcher()
dp.include_router(router)

async def main():
    print("1. main запущен")

    await bot.delete_webhook(drop_pending_updates=True)
    print("2. webhook удалён")

    print("3. запускаю polling")
    await dp.start_polling(bot)

if name == "main":
    print("4. запускаю asyncio")
    asyncio.run(main())
