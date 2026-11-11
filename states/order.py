from aiogram.fsm.state import State, StatesGroup


class OrderFSM(StatesGroup):
    waiting_for_name = State()  # Ждем ввода имени
    waiting_for_phone = State()  # Ждем телефон (кнопкой или текстом)
    waiting_for_comment = State()  # Ждем пожелания к заказу
