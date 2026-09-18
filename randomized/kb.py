from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Участвовать', url='tg://resolve?domain=randomized_473_bot&start=kon25289583')]
    ]
)
admin = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Написать администратору', url='https://t.me/smaliz')]
    ]
)