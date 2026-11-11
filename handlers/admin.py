import csv
import io
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from config import config
from database.db import get_all_leads, update_lead_status

router = Router()

router.message.filter(F.from_user.id == config.admin_id)
router.callback_query.filter(F.from_user.id == config.admin_id)


@router.callback_query(F.data.startswith("status_progress_"))
async def mark_in_progress(callback: CallbackQuery):
    lead_id = int(callback.data.split("_")[2])
    await update_lead_status(lead_id, "in_progress")

    old_text = callback.message.html_text
    new_text = old_text + "\n\n🟡 <i>Статус: В работе</i>"

    from keyboards.builders import get_admin_lead_kb

    client_url = callback.message.reply_markup.inline_keyboard[0][0].url
    builder = callback.message.reply_markup.inline_keyboard

    await callback.message.edit_text(
        new_text,
        reply_markup=get_admin_lead_kb(lead_id, 0, None, status="in_progress"),
        parse_mode="HTML",
    )
    await callback.answer("Заявка взята в работу!")


@router.callback_query(F.data.startswith("status_done_"))
async def mark_completed(callback: CallbackQuery):
    lead_id = int(callback.data.split("_")[2])
    await update_lead_status(lead_id, "completed")

    new_text = (
        callback.message.html_text.replace(
            "🟡 <i>Статус: В работе</i>", ""
        ).strip()
        + "\n\n✅ <b>Заявка выполнена!</b>"
    )
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    client_button = callback.message.reply_markup.inline_keyboard[0][0]
    builder = InlineKeyboardBuilder()
    builder.button(text=client_button.text, url=client_button.url)

    await callback.message.edit_text(
        new_text, reply_markup=builder.as_markup(), parse_mode="HTML"
    )
    await callback.answer("Заявка закрыта!")


@router.message(Command("export"))
async def export_leads(message: Message):
    leads = await get_all_leads()

    if not leads:
        await message.answer("В базе пока нет заявок.")
        return

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(
        [
            "ID",
            "Дата",
            "Услуга",
            "Имя",
            "Телефон",
            "Telegram",
            "Комментарий",
            "Статус",
        ]
    )

    for row in leads:
        writer.writerow(
            [
                row["id"],
                row["created_at"],
                row["item_title"],
                row["client_name"],
                row["phone"],
                f"@{row['username']}" if row["username"] else str(row["user_id"]),
                row["comment"],
                row["status"],
            ]
        )

    csv_bytes = output.getvalue().encode("utf-8-sig")
    document = BufferedInputFile(csv_bytes, filename="leads_export.csv")

    await message.answer_document(
        document=document,
        caption=f"📊 Выгрузка базы: всего <b>{len(leads)}</b> заявок.",
        parse_mode="HTML",
    )
