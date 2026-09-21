from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

router = Router()

# =========================
# НАСТРОЙКИ
# =========================

ADMIN_ID = 8127860525 


# =========================
# ВРЕМЕННЫЕ ДАННЫЕ
# =========================

giveaways = {}
participants = {}


# =========================
# СОСТОЯНИЯ
# =========================

class CreateGiveaway(StatesGroup):
    prize = State()
    channel = State()


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎁 Создать розыгрыш",
                    callback_data="create_giveaway"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏆 Выбрать победителя",
                    callback_data="choose_winner"
                )
            ]
        ]
    )


# =========================
# КНОПКА УЧАСТИЯ
# =========================

def participate_button(giveaway_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎁 Участвовать",
                    callback_data=f"join_{giveaway_id}"
                )
            ]
        ]
    )


# =========================
# /START
# =========================

@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "👋 Привет!\n\n"
        "🎁 Это бот для проведения розыгрышей.\n\n"
        "Выбери действие:",
        reply_markup=main_menu()
    )


# =========================
# СОЗДАНИЕ РОЗЫГРЫША
# =========================

@router.callback_query(F.data == "create_giveaway")
async def create_giveaway(
    callback: CallbackQuery,
    state: FSMContext
):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "❌ У тебя нет доступа",
            show_alert=True
        )
        return

    await callback.message.answer(
        "🎁 Напиши приз для розыгрыша:\n\n"
        "Например:\n"
        "Dark Blade\n"
        "Kitsune\n"
        "1000 Robux"
    )

    await state.set_state(CreateGiveaway.prize)
    await callback.answer()


# =========================
# ПРИЗ
# =========================

@router.message(CreateGiveaway.prize)
async def giveaway_prize(
    message: Message,
    state: FSMContext
):
    await state.update_data(prize=message.text)

    await message.answer(
        "📢 Теперь отправь username канала,\n"
        "например:\n\n"
        "@blox_fight\n\n"
        "⚠️ Бот должен быть администратором канала."
    )

    await state.set_state(CreateGiveaway.channel)


# =========================
# КАНАЛ
# =========================

@router.message(CreateGiveaway.channel)
async def giveaway_channel(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    data = await state.get_data()

    prize = data["prize"]
    channel = message.text.strip()

    giveaway_id = str(message.from_user.id) + "_" + str(
        len(giveaways) + 1
    )

    giveaways[giveaway_id] = {
        "prize": prize,
        "channel": channel,
        "creator": message.from_user.id,
        "participants": []
    }

    participants[giveaway_id] = []

    text = (
        "🎉 <b>РОЗЫГРЫШ</b> 🎉\n\n"
        f"🎁 Приз: <b>{prize}</b>\n\n"
        "👇 Нажми кнопку ниже, чтобы принять участие!"
    )

    try:
        await bot.send_message(
            chat_id=channel,
            text=text,
            parse_mode="HTML",
            reply_markup=participate_button(giveaway_id)
        )

        await message.answer(
            "✅ Розыгрыш создан!\n\n"
            f"🎁 Приз: {prize}\n"
            f"📢 Канал: {channel}\n\n"
            "Участники могут нажимать кнопку «Участвовать»."
        )