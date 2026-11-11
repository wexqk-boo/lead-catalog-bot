import aiosqlite

DB_NAME = "database.db"


async def init_db():
    """Создает таблицы при первом запуске и добавляет тестовые товары, если пусто."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица товаров/услуг
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                price INTEGER NOT NULL
            )
        """
        )

        # Таблица заявок
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                item_title TEXT NOT NULL,
                client_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                comment TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Проверяем, есть ли уже товары. Если нет — добавим демо-услуги
        async with db.execute("SELECT COUNT(*) FROM items") as cursor:
            count = (await cursor.fetchone())[0]
            if count == 0:
                demo_items = [
                    (
                        "Telegram-бот визитка",
                        "Простой бот с кнопками, контактами и каталогом услуг.",
                        5000,
                    ),
                    (
                        "Бот с приемом заявок",
                        "Сбор лидов через FSM-анкету, валидация и отправка менеджеру.",
                        12000,
                    ),
                    (
                        "Парсер данных",
                        "Скрипт на Playwright/BS4 со сбором данных и выгрузкой в Excel.",
                        8000,
                    ),
                ]
                await db.executemany(
                    "INSERT INTO items (title, description, price) VALUES (?, ?, ?)",
                    demo_items,
                )

        await db.commit()


async def get_all_items():
    """Возвращает все товары из каталога."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, title, description, price FROM items"
        ) as cursor:
            return await cursor.fetchall()


async def get_item_by_id(item_id: int):
    """Находит один товар по ID."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, title, description, price FROM items WHERE id = ?",
            (item_id,),
        ) as cursor:
            return await cursor.fetchone()


async def add_lead(
    user_id: int,
    username: str | None,
    item_title: str,
    client_name: str,
    phone: str,
    comment: str | None,
):
    """Сохраняет новую заявку в базу."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO leads (user_id, username, item_title, client_name, phone, comment)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (user_id, username, item_title, client_name, phone, comment),
        )
        await db.commit()

async def update_lead_status(lead_id: int, new_status: str):
    """Обновляет статус заявки (new -> in_progress -> completed)."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE leads SET status = ? WHERE id = ?", (new_status, lead_id)
        )
        await db.commit()


async def update_lead_status(lead_id: int, new_status: str):
    """Обновляет статус заявки (new -> in_progress -> completed)."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE leads SET status = ? WHERE id = ?", (new_status, lead_id)
        )
        await db.commit()


async def get_all_leads():
    """Возвращает все заявки для экспорта."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, user_id, username, item_title, client_name, phone, comment, status, created_at FROM leads ORDER BY id DESC"
        ) as cursor:
            return await cursor.fetchall()


# И немного обнови функцию add_lead, чтобы она возвращала ID новой строки:
async def add_lead(
    user_id: int,
    username: str | None,
    item_title: str,
    client_name: str,
    phone: str,
    comment: str | None,
) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            INSERT INTO leads (user_id, username, item_title, client_name, phone, comment)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (user_id, username, item_title, client_name, phone, comment),
        )
        await db.commit()
        return cursor.lastrowid
