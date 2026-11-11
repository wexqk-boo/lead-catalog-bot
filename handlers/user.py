from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from config import config
from database.db import add_lead, get_all_items, get_item_by_id
from keyboards.builders import (
    get_catalog_kb,
    get_item_card_kb,
    get_main_menu_kb,
    get_phone_kb,
    get_admin_lead_kb,
)
from states.order import OrderFSM

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Я бот для заказа IT-услуг и разработки.\n"
        "Выбери нужный раздел в меню ниже:",
        reply_markup=get_main_menu_kb(),
        parse_mode="HTML",
    )


@router.message(F.text == "ℹ️ Обо мне")
async def about_me(message: Message):
    await message.answer(
        "👨‍💻 <b>О разработчике:</b>\n\n"
        "Делаю надежных Telegram-ботов на <b>Python (aiogram 3)</b> и парсеры данных (Playwright/BS4).\n"
        "Чистый код, базы данных, деплой на сервер под ключ.",
        parse_mode="HTML",
    )


@router.message(F.text == "📞 Контакты")
async def contacts(message: Message):
    await message.answer(
        "📩 <b>Связь со мной:</b>\n\n"
        "Telegram: @wrx1k\n"
        "GitHub: https://github.com/wexqk-boo",
        parse_mode="HTML",
    )


@router.message(F.text == "🛍 Каталог услуг")
async def show_catalog(message: Message):
    items = await get_all_items()
    await message.answer(
        "📋 <b>Каталог доступных услуг:</b>\n"
        "Нажмите на интересующую позицию для подробностей:",
        reply_markup=get_catalog_kb(items),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "back_to_catalog")
async def back_to_catalog(callback: CallbackQuery):
    items = await get_all_items()
    await callback.message.edit_text(
        "📋 <b>Каталог доступных услуг:</b>\n"
        "Нажмите на интересующую позицию для подробностей:",
        reply_markup=get_catalog_kb(items),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data.startswith("item_"))
async def show_item(callback: CallbackQuery):
    item_id = int(callback.data.split("_")[1])
    item = await get_item_by_id(item_id)

    if not item:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    text = (
        f"🏷 <b>{item['title']}</b>\n\n"
        f"📝 {item['description']}\n\n"
        f"💰 <b>Стоимость:</b> от {item['price']} ₽"
    )
    await callback.message.edit_text(
        text, reply_markup=get_item_card_kb(item_id), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_"))
async def start_order(callback: CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split("_")[1])
    item = await get_item_by_id(item_id)

    await state.update_data(item_title=item["title"])
    await state.set_state(OrderFSM.waiting_for_name)

    await callback.message.answer(
        f"Вы выбрали: <b>{item['title']}</b>.\n\n"
        "Как к вам обращаться? (Введите ваше имя):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer(
        "Оформление заявки отменено.", reply_markup=get_main_menu_kb()
    )


@router.message(OrderFSM.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Пожалуйста, отправьте имя текстом.")
        return

    await state.update_data(client_name=message.text)
    await state.set_state(OrderFSM.waiting_for_phone)

    await message.answer(
        "Отлично! Теперь укажите ваш номер телефона для связи.\n"
        "Можно нажать кнопку внизу или ввести номер вручную:",
        reply_markup=get_phone_kb(),
    )

@router.message(OrderFSM.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    else:
        await message.answer(
            "Пожалуйста, отправьте контакт кнопкой или введите номер сообщением."
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(OrderFSM.waiting_for_comment)

    await message.answer(
        "Напишите кратко суть задачи или пожелания к проекту\n"
        "(или напишите «нет», если хотите обсудить лично):"
    )


@router.message(OrderFSM.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    comment = message.text if message.text else "Без комментария"
    data = await state.get_data()

    lead_id = await add_lead(
        user_id=message.from_user.id,
        username=message.from_user.username,
        item_title=data["item_title"],
        client_name=data["client_name"],
        phone=data["phone"],
        comment=comment,
    )

    await message.answer(
        "✅ <b>Ваша заявка принята!</b>\n"
        "Я свяжусь с вами в ближайшее время для уточнения деталей.",
        reply_markup=get_main_menu_kb(),
        parse_mode="HTML",
    )
    username_text = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "скрыт"
    )
    admin_card = (
        f"🔥 <b>НОВАЯ ЗАЯВКА #{lead_id}!</b>\n\n"
        f"📌 <b>Услуга:</b> {data['item_title']}\n"
        f"👤 <b>Имя:</b> {data['client_name']}\n"
        f"📱 <b>Телефон:</b> {data['phone']}\n"
        f"💬 <b>Telegram:</b> {username_text} (ID: <code>{message.from_user.id}</code>)\n"
        f"📝 <b>Комментарий:</b> {comment}"
    )

    await message.bot.send_message(
        chat_id=config.admin_id,
        text=admin_card,
        reply_markup=get_admin_lead_kb(
            lead_id=lead_id,
            client_user_id=message.from_user.id,
            client_username=message.from_user.username,
            status="new",
        ),
        parse_mode="HTML",
    )

    await state.clear()
