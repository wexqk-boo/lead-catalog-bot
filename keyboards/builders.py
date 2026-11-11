from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🛍 Каталог услуг")],
        [KeyboardButton(text="ℹ️ Обо мне"), KeyboardButton(text="📞 Контакты")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_catalog_kb(items) -> InlineKeyboardMarkup:
    """Инлайн-кнопки со списком товаров из базы данных."""
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(
            text=f"{item['title']} — {item['price']} ₽",
            callback_data=f"item_{item['id']}",
        )
    builder.adjust(1)
    return builder.as_markup()


def get_item_card_kb(item_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📝 Заказать эту услугу", callback_data=f"buy_{item_id}"
    )
    builder.button(text="🔙 Назад в каталог", callback_data="back_to_catalog")
    builder.adjust(1)
    return builder.as_markup()


def get_phone_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📱 Отправить мой номер", request_contact=True)],
        [KeyboardButton(text="❌ Отмена")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb, resize_keyboard=True, one_time_keyboard=True
    )


def get_admin_lead_kb(
    lead_id: int,
    client_user_id: int,
    client_username: str | None,
    status: str = "new",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    url = (
        f"https://t.me/{client_username}"
        if client_username
        else f"tg://user?id={client_user_id}"
    )
    builder.button(text="💬 Написать клиенту", url=url)

    if status == "new":
        builder.button(
            text="⏳ Взять в работу", callback_data=f"status_progress_{lead_id}"
        )
    elif status == "in_progress":
        builder.button(
            text="✅ Завершить", callback_data=f"status_done_{lead_id}"
        )

    builder.adjust(1)
    return builder.as_markup()
