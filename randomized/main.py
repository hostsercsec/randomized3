impoimport asyncio
import os

from aiohttp import web
from aiogram import Bot, Dispatcher

from handler import router


TOKEN = "8407452828:AAElvoYfmhGeTdHXlbK1RcK8ZQ0KrAhWCZI"

bot = Bot(TOKEN)
dp = Dispatcher()

dp.include_router(router)


async def health_check(request):
    return web.Response(text="Bot is running!")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)

    port = int(os.environ.get("PORT", 10000))

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(f"Web server started on port {port}")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    await start_web_server()

    print("Bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())