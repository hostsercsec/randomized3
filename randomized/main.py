from aiogram import Dispatcher, Bot, Router
from handler import router

bot = Bot(token='8407452828:AAElvoYfmhGeTdHXlbK1RcK8ZQ0KrAhWCZI')
dp = Dispatcher()
dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

