from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

import random

router = Router()

participants = []
giveaway_active = False


def make_table(winner):
    username = f"@{winner}" if not winner.startswith("@") else winner
    username = username[:16].rjust(16)

    return (
        "┌─────┬──────────────────┐\n"
        "│  №  │        Username  │\n"
        "├─────┼──────────────────┤\n"
        f"│  1  │ {username} │\n"
        "└─────┴──────────────────┘"
    )


@router.message(Command("start"))
async def start(message: Message):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🎁 Создать розыгрыш",
        callback_data="create_giveaway"
    )

    keyboard.button(
        text="👥 Участники",
        callback_data="participants"
    )

    keyboard.adjust(1)

    await message.answer(
        "🎉 <b>Розыгрыш</b>\n\n"
        "Выбери действие:",
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(F.data == "create_giveaway")
async def create_giveaway(callback: CallbackQuery):
    global giveaway_active

    giveaway_active = True
    participants.clear()

    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🎟 Участвовать",
        callback_data="join_giveaway"
    )

    keyboard.button(
        text="🏆 Выбрать победителя",
        callback_data="choose_winner"
    )

    keyboard.adjust(1)

    await callback.message.edit_text(
        "🎁 <b>Розыгрыш создан!</b>\n\n"
        "Нажми кнопку ниже, чтобы принять участие.",
        reply_markup=keyboard.as_markup()
    )

    await callback.answer()


@router.callback_query(F.data == "join_giveaway")
async def join_giveaway(callback: CallbackQuery):
    if not giveaway_active:
        await callback.answer(
            "❌ Сейчас нет активного розыгрыша.",
            show_alert=True
        )
        return

    username = callback.from_user.username

    if not username:
        username = callback.from_user.full_name

    if username not in participants:
        participants.append(username)

        await callback.answer(
            "✅ Ты участвуешь в розыгрыше!"
        )
    else:
        await callback.answer(
            "ℹ️ Ты уже участвуешь.",
            show_alert=True
        )


@router.callback_query(F.data == "participants")
async def show_participants(callback: CallbackQuery):
    if not participants:
        await callback.answer(
            "Пока никто не участвует.",
            show_alert=True
        )
        return

    lines = [
        "┌─────┬──────────────────┐",
        "│  №  │        Username  │",
        "├─────┼──────────────────┤"
    ]

    for i, username in enumerate(participants, 1):
        username = f"@{username}" if not username.startswith("@") else username
        username = username[:16].rjust(16)

        lines.append(
            f"│ {i:^3} │ {username} │"
        )

    lines.append(
        "└─────┴──────────────────┘"
    )

    table = "\n".join(lines)

    await callback.message.answer(
        "👥 <b>Участники</b>\n\n"
        f"<pre>{table}</pre>"
    )

    await callback.answer()


@router.callback_query(F.data == "choose_winner")
async def choose_winner(callback: CallbackQuery):
    global giveaway_active

    if not participants:
        await callback.answer(
            "❌ Нет участников!",
            show_alert=True
        )
        return

    winner = random.choice(participants)

    giveaway_active = False

    table = make_table(winner)

    await callback.message.edit_text(
        "🏆 <b>ИТОГИ РОЗЫГРЫША</b>\n\n"
        f"<pre>{table}</pre>\n\n"
        "🎉 Поздравляем победителя!"
    )

    await callback.answer(
        "🏆 Победитель выбран!"
    )


@router.message(Command("add"))
async def add_participant(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "❌ Используй:\n"
            "<code>/add username</code>"
        )
        return

    username = args[1].strip()

    if username not in participants:
        participants.append(username)

        await message.answer(
            f"✅ <b>{username}</b> добавлен!"
        )
    else:
        await message.answer(
            "ℹ️ Этот пользователь уже есть в списке."
        )


@router.message(Command("list"))
async def participant_list(message: Message):
    if not participants:
        await message.answer(
            "👥 Участников пока нет."
        )
        return

    lines = [
        "┌─────┬──────────────────┐",
        "│  №  │        Username  │",
        "├─────┼──────────────────┤"
    ]

    for i, username in enumerate(participants, 1):
        username = f"@{username}" if not username.startswith("@") else username
        username = username[:16].rjust(16)

        lines.append(
            f"│ {i:^3} │ {username} │"
        )

    lines.append(
        "└─────┴──────────────────┘"
    )

    table = "\n".join(lines)

    await message.answer(
        "👥 <b>Список участников</b>\n\n"
        f"<pre>{table}</pre>"
    )