from aiogram.filters import CommandStart, Command, CommandObject
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import kb
from aiogram.types import InputRichMessage, InputRichBlockParagraph, InputRichBlockTable, RichBlockTableCell


class Form(StatesGroup):
    textt = State()
    username = State()

class It(StatesGroup):
    idkon = State()
    usern = State()
    userk = State()


router = Router()


@router.message(CommandStart())
async def main(message: Message, command: CommandObject):
    if command.args == 'kon25289583':
         await message.answer('(!) Теперь вы участвуете в розыгрыше!')
         return
    await message.answer('Добро пожаловать в бот randomize!\nЭто бот для проведения разных розыгрышей!')

@router.message(Command('createkon'))
async def create(message: Message, state: FSMContext):
    if message.from_user.id == 8127860525:
        await message.answer('Введите текст для розыгрыша')
        await state.set_state(Form.textt)
    else:
        return

@router.message(Form.textt)
async def text(message: Message, state: FSMContext):
    await state.update_data(textt = message.text)
    await message.answer("Введите username канала в какой надо отправить текст(Бот должен быть администратором в этом канале!)")
    await state.set_state(Form.username)

@router.message(Form.username)
async def user(message: Message, state: FSMContext, bot: Bot):
     await state.update_data(username = message.text)
     data = await state.get_data()
     await bot.send_message(
          chat_id=message.text,
          text=data["textt"],
          reply_markup=kb.kb
     )
     await message.answer('Розыгрыш был создан!')
     await state.clear()

@router.message(Command('itogi'))
async def ito(message: Message, state: FSMContext):
    if message.from_user.id == 8127860525:
         await message.answer('Введите id конкурса')
         await state.set_state(It.idkon)
    else:
         return

@router.message(It.idkon)
async def itoid(message: Message, state: FSMContext):
     await state.update_data(idkon = message.text)
     await message.answer('Введите username победителя')
     await state.set_state(It.usern)

@router.message(It.usern)
async def usernn(message: Message, state: FSMContext):
     await state.update_data(usern = message.text)
     await message.answer('Введите username канала в который отправить итоги')
     await state.set_state(It.userk)

@router.message(It.userk)
async def userk(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(userk = message.text)
    data = await state.get_data()
    await bot.send_rich_message(
    chat_id=data["userk"],
    rich_message=InputRichMessage(
        blocks=[
            InputRichBlockParagraph(
                text=f"Итоги конкурса #{data['idkon']}"
            ),

            InputRichBlockTable(
                cells=[
                    [
                        RichBlockTableCell(
                            text="Место",
                            is_header=True,
                            align="center",
                            valign="middle"
                        ),
                        RichBlockTableCell(
                            text="Username",
                            is_header=True,
                            align="center",
                            valign="middle"
                        )
                    ],
                    [
                        RichBlockTableCell(
                            text="1",
                            align="center",
                            valign="middle"
                        ),
                        RichBlockTableCell(
                            text=data["usern"],
                            align="center",
                            valign="middle"
                        )
                    ]
                ],
                is_bordered=True,
                is_striped=True
            ),

            InputRichBlockParagraph(
                text="Отпишите в течении 1 часа нашему администратору или же приз сгорит!"
            )
        ]
    ), reply_markup=kb.admin
)
    await message.answer('итоги были отправлены')