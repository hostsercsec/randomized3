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

    except Exception as e:
        await message.answer(
            "❌ Не удалось отправить розыгрыш в канал.\n\n"
            "Проверь:\n"
            "• правильность username канала;\n"
            "• бот является администратором;\n"
            "• у бота есть право отправлять сообщения."
        )

        print(e)

    await state.clear()


# =========================
# УЧАСТИЕ
# =========================

@router.callback_query(F.data.startswith("join_"))
async def join_giveaway(
    callback: CallbackQuery
):
    giveaway_id = callback.data.replace("join_", "")

    if giveaway_id not in giveaways:
        await callback.answer(
            "❌ Розыгрыш не найден",
            show_alert=True
        )
        return

    user = callback.from_user

    if user.id in participants[giveaway_id]:
        await callback.answer(
            "⚠️ Ты уже участвуешь!",
            show_alert=True
        )
        return

    participants[giveaway_id].append(user.id)

    await callback.answer(
        "✅ Ты участвуешь в розыгрыше!"
    )


# =========================
# ВЫБОР ПОБЕДИТЕЛЯ
# =========================

@router.callback_query(F.data == "choose_winner")
async def choose_winner(
    callback: CallbackQuery
):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "❌ У тебя нет доступа",
            show_alert=True
        )
        return

    if not giveaways:
        await callback.message.answer(
            "❌ Пока нет созданных розыгрышей."
        )
        await callback.answer()
        return

    buttons = []

    for giveaway_id, giveaway in giveaways.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"🎁 {giveaway['prize']}",
                callback_data=f"winner_{giveaway_id}"
            )
        ])

    await callback.message.answer(
        "🏆 Выбери розыгрыш:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )

    await callback.answer()


# =========================
# СПИСОК УЧАСТНИКОВ
# =========================

@router.callback_query(F.data.startswith("winner_"))
async def winner_list(
    callback: CallbackQuery,
    bot: Bot
):
    giveaway_id = callback.data.replace("winner_", "")

    if giveaway_id not in giveaways:
        await callback.answer(
            "❌ Розыгрыш не найден",
            show_alert=True
        )
        return

    users = participants[giveaway_id]

    if not users:
        await callback.message.answer(
            "❌ В этом розыгрыше пока нет участников."
        )
        await callback.answer()
        return

    buttons = []

    for user_id in users:
        try:
            user = await bot.get_chat(user_id)

            username = (
                f"@{user.username}"
                if user.username
                else user.first_name
            )

        except Exception:
            username = str(user_id)

        buttons.append([
            InlineKeyboardButton(
                text=f"🏆 {username}",
                callback_data=f"setwinner_{giveaway_id}_{user_id}"
            )
        ])

    await callback.message.answer(
        f"🏆 <b>Выбор победителя</b>\n\n"
        f"🎁 Приз: <b>{giveaways[giveaway_id]['prize']}</b>\n"
        f"👥 Участников: <b>{len(users)}</b>\n\n"
        "Нажми на участника, которого хочешь сделать победителем:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )

    await callback.answer()


# =========================
# НАЗНАЧИТЬ ПОБЕДИТЕЛЯ
# =========================

@router.callback_query(F.data.startswith("setwinner_"))
async def set_winner(
    callback: CallbackQuery,
    bot: Bot
):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            "❌ Нет доступа",
            show_alert=True
        )
        return

    parts = callback.data.split("_")

    giveaway_id = parts[1]
    winner_id = int(parts[2])

    if giveaway_id not in giveaways:
        await callback.answer(
            "❌ Розыгрыш не найден",
            show_alert=True
        )
        return

    giveaway = giveaways[giveaway_id]

    try:
        winner = await bot.get_chat(winner_id)

        username = (
            f"@{winner.username}"
            if winner.username
            else winner.first_name
        )

    except Exception:
        username = str(winner_id)

    result_text = (
        "🏆 <b>ИТОГИ РОЗЫГРЫША</b>\n\n"
        f"🎁 Приз: <b>{giveaway['prize']}</b>\n\n"
        f"🥇 Победитель: <b>{username}</b>\n\n"
        "🎉 Поздравляем!"
    )

    try:
        await bot.send_message(
            chat_id=giveaway["channel"],
            text=result_text,
            parse_mode="HTML"
        )

        await callback.message.answer(
            "✅ Победитель выбран!\n\n"
            f"🥇 {username}\n"
            f"🎁 Приз: {giveaway['prize']}"
        )

    except Exception as e:
        await callback.message.answer(
            "❌ Не удалось отправить итоги в канал."
        )
        print(e)

    await callback.answer()