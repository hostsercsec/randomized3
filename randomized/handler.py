from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import uuid


router = Router()


# =========================================================
# НАСТРОЙКИ
# =========================================================

ADMIN_ID = 8127860525

# Username бота БЕЗ @
randomized = "randomized_473_bot"


# =========================================================
# РОЗЫГРЫШИ В ПАМЯТИ
# =========================================================

giveaways = {}

# Формат:
#
# giveaways[giveaway_id] = {
#     "title": "...",
#     "channel": "...",
#     "participants": {
#         user_id: "@username"
#     },
#     "active": True
# }


# =========================================================
# СОСТОЯНИЯ СОЗДАНИЯ
# =========================================================

class CreateGiveaway(StatesGroup):
    text = State()
    channel = State()


# =========================================================
# СОСТОЯНИЯ ИТОГОВ
# =========================================================

class Results(StatesGroup):
    giveaway_id = State()
    winner = State()
    channel = State()


# =========================================================
# КНОПКА УЧАСТИЯ
# =========================================================

def giveaway_keyboard(giveaway_id: str):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎟 Участвовать",
                    url=f"https://t.me/{BOT_USERNAME}?start=join_{giveaway_id}"
                )
            ]
        ]
    )


# =========================================================
# ПРОВЕРКА АДМИНА
# =========================================================

def is_admin(message: Message):

    return message.from_user.id == ADMIN_ID


# =========================================================
# /START
# =========================================================

@router.message(CommandStart())
async def start_handler(
    message: Message,
    command: CommandObject
):

    # Если человек пришёл по кнопке участия
    if command.args and command.args.startswith("join_"):

        giveaway_id = command.args.replace("join_", "", 1)

        # Проверяем существование
        if giveaway_id not in giveaways:

            await message.answer(
                "❌ Розыгрыш не найден или уже завершён."
            )
            return

        giveaway = giveaways[giveaway_id]

        # Проверяем активность
        if not giveaway["active"]:

            await message.answer(
                "❌ Этот розыгрыш уже завершён."
            )
            return

        user_id = message.from_user.id

        # Проверяем повторное участие
        if user_id in giveaway["participants"]:

            await message.answer(
                "ℹ️ Вы уже участвуете в этом розыгрыше!"
            )
            return

        # Получаем username
        if message.from_user.username:

            username = f"@{message.from_user.username}"

        else:

            username = message.from_user.full_name

        # Добавляем участника
        giveaway["participants"][user_id] = username

        await message.answer(
            "✅ <b>Теперь вы участвуете в розыгрыше!</b>\n\n"
            f"🎁 Розыгрыш: <b>{giveaway['title']}</b>\n\n"
            "Удачи! 🍀",
            parse_mode="HTML"
        )

        return

    # Обычный /start

    await message.answer(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Это бот для проведения розыгрышей.\n\n"
        "🎁 Здесь можно создавать розыгрыши "
        "и смотреть участников.",
        parse_mode="HTML"
    )


# =========================================================
# /createkon
# =========================================================

@router.message(Command("createkon"))
async def create_giveaway(
    message: Message,
    state: FSMContext
):

    if not is_admin(message):

        await message.answer(
            "❌ У вас нет доступа."
        )
        return

    await message.answer(
        "🎁 <b>Создание розыгрыша</b>\n\n"
        "Введите текст/название розыгрыша.\n\n"
        "Например:\n"
        "<code>Розыгрыш на Яд</code>",
        parse_mode="HTML"
    )

    await state.set_state(CreateGiveaway.text)


# =========================================================
# ПОЛУЧАЕМ ТЕКСТ
# =========================================================

@router.message(CreateGiveaway.text)
async def giveaway_text(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        text=message.text
    )

    await message.answer(
        "📢 Теперь отправь username канала.\n\n"
        "Например:\n"
        "<code>@blox_fight</code>\n\n"
        "⚠️ Бот должен быть администратором канала.",
        parse_mode="HTML"
    )

    await state.set_state(CreateGiveaway.channel)


# =========================================================
# ПОЛУЧАЕМ КАНАЛ И СОЗДАЁМ
# =========================================================

@router.message(CreateGiveaway.channel)
async def giveaway_channel(
    message: Message,
    state: FSMContext,
    bot: Bot
):

    channel = message.text.strip()

    if not channel.startswith("@"):

        await message.answer(
            "❌ Username канала должен начинаться с @\n\n"
            "Например: <code>@blox_fight</code>",
            parse_mode="HTML"
        )
        return

    data = await state.get_data()

    title = data["text"]

    # Создаём ID
    giveaway_id = uuid.uuid4().hex[:8]

    # Сохраняем в память
    giveaways[giveaway_id] = {
        "title": title,
        "channel": channel,
        "participants": {},
        "active": True
    }

    # Отправляем розыгрыш в канал
    try:

        await bot.send_message(
            chat_id=channel,
            text=(
                f"🎁 <b>{title}</b>\n\n"
                "Чтобы принять участие, нажмите кнопку ниже 👇"
            ),
            parse_mode="HTML",
            reply_markup=giveaway_keyboard(giveaway_id)
        )

    except Exception as e:

        # Если не получилось отправить
        del giveaways[giveaway_id]

        await message.answer(
            "❌ Не удалось отправить сообщение в канал.\n\n"
            "Проверь:\n"
            "• бот добавлен в канал\n"
            "• бот является администратором\n"
            "• username канала указан правильно\n\n"
            f"Ошибка: <code>{e}</code>",
            parse_mode="HTML"
        )

        await state.clear()
        return

    await message.answer(
        "✅ <b>Розыгрыш создан!</b>\n\n"
        f"🎁 Приз: <b>{title}</b>\n"
        f"🆔 ID: <code>{giveaway_id}</code>\n"
        f"📢 Канал: {channel}\n"
        "👥 Участники: 0",
        parse_mode="HTML"
    )

    await state.clear()


# =========================================================
# /participants
# =========================================================

@router.message(Command("participants"))
async def participants_handler(
    message: Message
):

    if not is_admin(message):

        await message.answer(
            "❌ У вас нет доступа."
        )
        return

    active = [
        (gid, data)
        for gid, data in giveaways.items()
        if data["active"]
    ]

    if not active:

        await message.answer(
            "❌ Активных розыгрышей нет."
        )
        return

    text = "👥 <b>Участники:</b>\n\n"

    for giveaway_id, giveaway in active:

        text += (
            f"🎁 <b>{giveaway['title']}</b>\n"
            f"🆔 ID: <code>{giveaway_id}</code>\n"
            f"👥 Участников: "
            f"<b>{len(giveaway['participants'])}</b>\n\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


# =========================================================
# /status
# =========================================================

@router.message(Command("status"))
async def status_handler(
    message: Message
):

    if not is_admin(message):

        await message.answer(
            "❌ У вас нет доступа."
        )
        return

    active = [
        (gid, data)
        for gid, data in giveaways.items()
        if data["active"]
    ]

    if not active:

        await message.answer(
            "❌ Сейчас нет активных розыгрышей."
        )
        return

    text = "📊 <b>Активные розыгрыши:</b>\n\n"

    for giveaway_id, giveaway in active:

        text += (
            f"🎁 {giveaway['title']}\n"
            f"🆔 <code>{giveaway_id}</code>\n"
            f"👥 {len(giveaway['participants'])} участников\n\n"
        )

    await message.answer(
        text,
        parse_mode="HTML"
    )


# =========================================================
# /itogi
# =========================================================

@router.message(Command("itogi"))
async def results_start(
    message: Message,
    state: FSMContext
):

    if not is_admin(message):

        await message.answer(
            "❌ У вас нет доступа."
        )
        return

    await message.answer(
        "🏆 Введите ID конкурса.\n\n"
        "Например:\n"
        "<code>a82f91cd</code>",
        parse_mode="HTML"
    )

    await state.set_state(
        Results.giveaway_id
    )


# =========================================================
# ПОЛУЧАЕМ ID
# =========================================================

@router.message(Results.giveaway_id)
async def results_id(
    message: Message,
    state: FSMContext
):

    giveaway_id = message.text.strip()

    if giveaway_id not in giveaways:

        await message.answer(
            "❌ Розыгрыш с таким ID не найден.\n\n"
            "Попробуй ещё раз."
        )
        return

    giveaway = giveaways[giveaway_id]

    if not giveaway["participants"]:

        await message.answer(
            "❌ В этом розыгрыше нет участников."
        )
        return

    await state.update_data(
        giveaway_id=giveaway_id
    )

    await message.answer(
        "🥇 Введи username победителя.\n\n"
        "Например:\n"
        "<code>@username</code>",
        parse_mode="HTML"
    )

    await state.set_state(
        Results.winner
    )


# =========================================================
# ПОЛУЧАЕМ ПОБЕДИТЕЛЯ
# =========================================================

@router.message(Results.winner)
async def results_winner(
    message: Message,
    state: FSMContext
):

    winner = message.text.strip()

    await state.update_data(
        winner=winner
    )

    await message.answer(
        "📢 Введи username канала, куда отправить итоги.\n\n"
        "Например:\n"
        "<code>@blox_fight</code>",
        parse_mode="HTML"
    )

    await state.set_state(
        Results.channel
    )


# =========================================================
# ОТПРАВЛЯЕМ ИТОГИ
# =========================================================

@router.message(Results.channel)
async def results_channel(
    message: Message,
    state: FSMContext,
    bot: Bot
):

    channel = message.text.strip()

    if not channel.startswith("@"):

        await message.answer(
            "❌ Username канала должен начинаться с @."
        )
        return

    data = await state.get_data()

    giveaway_id = data["giveaway_id"]
    winner = data["winner"]

    giveaway = giveaways[giveaway_id]

    # Текстовая таблица
    results_text = (
        f"🏆 <b>ИТОГИ КОНКУРСА #{giveaway_id}</b>\n\n"
        f"🎁 Приз: <b>{giveaway['title']}</b>\n\n"
        "┌──────────┬────────────────────┐\n"
        "│ Место    │ Username           │\n"
        "├──────────┼────────────────────┤\n"
        f"│ 🥇 1      │ {winner:<18} │\n"
        "└──────────┴────────────────────┘\n\n"
        "⏰ Отпишите в течение 1 часа "
        "нашему администратору или же приз сгорит!\n\n"
        "🎉 Поздравляем победителя!"
    )

    try:

       await bot.send_message(
            chat_id=channel,
            text=results_text,
            parse_mode="HTML"
        )

    except Exception as e:

        await message.answer(
            "❌ Не удалось отправить итоги.\n\n"
            f"Ошибка: <code>{e}</code>",
            parse_mode="HTML"
        )
        return

    # Завершаем розыгрыш
    giveaway["active"] = False
    giveaway["winner"] = winner

    await message.answer(
        "✅ <b>Итоги были отправлены!</b>\n\n"
        f"🥇 Победитель: {winner}\n"
        f"🎁 Приз: {giveaway['title']}",
        parse_mode="HTML"
    )

    await state.clear()


# =========================================================
# /stop
# =========================================================

@router.message(Command("stop"))
async def stop_giveaway(
    message: Message
):

    if not is_admin(message):

        await message.answer(
            "❌ У вас нет доступа."
        )
        return

    active = [
        (gid, data)
        for gid, data in giveaways.items()
        if data["active"]
    ]

    if not active:

        await message.answer(
            "❌ Активных розыгрышей нет."
        )
        return

    giveaway_id, giveaway = active[-1]

    giveaway["active"] = False

    await message.answer(
        "🛑 <b>Розыгрыш остановлен.</b>\n\n"
        f"🎁 {giveaway['title']}\n"
        f"🆔 <code>{giveaway_id}</code>",
        parse_mode="HTML"
    )