import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from database.db import init_db
from handlers.admin import router as admin_router
from handlers.user import router as user_router

logging.basicConfig(level=logging.INFO)


async def main():
    # 1. Инициализируем базу
    await init_db()
    print("📦 База данных готова!")

    # 2. Создаем бота и диспетчер
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    # 3. Регистрируем роутеры (admin первым, чтобы перехватывать админские действия)
    dp.include_router(admin_router)
    dp.include_router(user_router)

    print("🚀 Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
