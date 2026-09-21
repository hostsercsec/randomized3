from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

router = Router()


# =========================
# НАСТРОЙКИ
# =========================

ADMIN_ID = 123456789

# Username твоего бота БЕЗ @
BOT_USERNAME = "YOUR_BOT_USERNAME"


# =========================
# ДАННЫЕ В ПАМЯТИ
# =========================

giveaway_active = False
giveaway_id = 0
giveaway_title = ""

participants = {}


# =========================
# КНОПКА УЧАСТИЯ
# =========================

def giveaway_button():
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


# =========================
# /START
# =========================

@router.message(CommandStart())
async def start_handler(message: Message):
    global giveaway_active

    args = message.text.split(maxsplit=1)

    # Если человек пришёл по кнопке розыгрыша
    if len(args) > 1 and args[1].startswith("join_"):

        if not giveaway_active:
            await message.answer(
                "❌ Сейчас нет активного розыгрыша."
            )
            return

        try:
            joined_id = int(args[1].replace("join_", ""))
        except ValueError:
            await message.answer("❌ Неверная ссылка на розыгрыш.")
            return

        if joined_id != giveaway_id:
            await message.answer(
                "❌ Этот розыгрыш уже неактивен."
            )
            return

        user_id = message.from_user.id

        if user_id in participants:
            await message.answer(
                "ℹ️ Вы уже участвуете в этом розыгрыше!"
            )
            return

        username = message.from_user.username

        if username:
            name = f"@{username}"
        else:
            name = message.from_user.full_name

        participants[user_id] = name

        await message.answer(
            "✅ <b>Теперь вы участвуете в розыгрыше!</b>\n\n"
            f"🎁 Розыгрыш: <b>{giveaway_title}</b>\n\n"
            "Удачи! 🍀"
        )

        return

    # Обычный /start
    await message.answer(
        "👋 Привет!\n\n"
        "Здесь проходят розыгрыши."
    )


# =========================
# ПРОВЕРКА АДМИНА
# =========================

def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


# =========================
# СОЗДАНИЕ РОЗЫГРЫША
# =========================

@router.message(Command("create"))
async def create_giveaway(message: Message):
    global giveaway_active
    global giveaway_id
    global giveaway_title
    global participants

    if not is_admin(message):
        await message.answer("❌ У вас нет доступа.")
        return

    # После /create берём название
    text = message.text.replace("/create", "", 1).strip()

    if not text:
        await message.answer(
            "❗ Напиши название розыгрыша после команды.\n\n"
            "Пример:\n"
            "<code>/create Розыгрыш на Яд</code>"
        )
        return

    giveaway_id += 1
    giveaway_title = text
    giveaway_active = True
    participants = {}

    await message.answer(
        "✅ <b>Розыгрыш создан!</b>\n\n"
        f"🎁 Название: <b>{giveaway_title}</b>\n"
        f"🆔 ID: <code>{giveaway_id}</code>\n\n"
        "Добавь эту кнопку в пост канала:\n"
        f"https://t.me/{BOT_USERNAME}?start=join_{giveaway_id}"
    )


# =========================
# ПОКАЗАТЬ КНОПКУ
# =========================

@router.message(Command("button"))
async def send_button(message: Message):

    if not is_admin(message):
        await message.answer("❌ У вас нет доступа.")
        return

    if not giveaway_active:
        await message.answer(
            "❌ Сначала создай розыгрыш через /create"
        )
        return
    await message.answer(
        f"🎁 <b>{giveaway_title}</b>\n\n"
        "Нажми кнопку ниже, чтобы принять участие 👇",
        reply_markup=giveaway_button()
    )


# =========================
# КОЛИЧЕСТВО УЧАСТНИКОВ
# =========================

@router.message(Command("participants"))
async def show_participants(message: Message):

    if not is_admin(message):
        await message.answer("❌ У вас нет доступа.")
        return

    if not giveaway_active:
        await message.answer("❌ Нет активного розыгрыша.")
        return

    if not participants:
        await message.answer(
            "👥 Участников пока нет."
        )
        return

    text = "👥 <b>Участники:</b>\n\n"

    for number, username in enumerate(participants.values(), 1):
        text += f"{number}. {username}\n"

    text += f"\nВсего участников: <b>{len(participants)}</b>"

    await message.answer(text)


# =========================
# ВЫБОР ПОБЕДИТЕЛЯ ВРУЧНУЮ
# =========================

@router.message(Command("winner"))
async def choose_winner(message: Message):
    global giveaway_active

    if not is_admin(message):
        await message.answer("❌ У вас нет доступа.")
        return

    if not giveaway_active:
        await message.answer(
            "❌ Нет активного розыгрыша."
        )
        return

    text = message.text.replace("/winner", "", 1).strip()

    if not text:
        await message.answer(
            "❗ Укажи победителя.\n\n"
            "Пример:\n"
            "<code>/winner @username</code>"
        )
        return

    winner = text

    await message.answer(
        "🏆 <b>РОЗЫГРЫШ ЗАВЕРШЁН!</b>\n\n"
        f"🎁 Приз: <b>{giveaway_title}</b>\n\n"
        f"🥇 Победитель: <b>{winner}</b>\n\n"
        "🎉 Поздравляем!"
    )

    giveaway_active = False


# =========================
# ОСТАНОВИТЬ РОЗЫГРЫШ
# =========================

@router.message(Command("stop"))
async def stop_giveaway(message: Message):
    global giveaway_active

    if not is_admin(message):
        await message.answer("❌ У вас нет доступа.")
        return

    if not giveaway_active:
        await message.answer(
            "❌ Нет активного розыгрыша."
        )
        return

    giveaway_active = False

    await message.answer(
        "🛑 <b>Розыгрыш остановлен.</b>"
    )


# =========================
# ПОКАЗАТЬ ТЕКУЩИЙ РОЗЫГРЫШ
# =========================

@router.message(Command("status"))
async def status(message: Message):

    if not is_admin(message):
        await message.answer("❌ У вас нет доступа.")
        return

    if not giveaway_active:
        await message.answer(
            "❌ Сейчас нет активного розыгрыша."
        )
        return

    await message.answer(
        "📊 <b>Текущий розыгрыш</b>\n\n"
        f"🎁 Приз: <b>{giveaway_title}</b>\n"
        f"🆔 ID: <code>{giveaway_id}</code>\n"
        f"👥 Участников: <b>{len(participants)}</b>"
    )
   