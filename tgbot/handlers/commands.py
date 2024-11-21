from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardRemove
import datetime

import keyboards.keyboards as kb 
import database.requests as rq

class Reg(StatesGroup):
    first_name = State()
    last_name = State()
    tg_username = State()
    tg_id = State()
    phone_number = State()
    notion_token = State()

async def start_command_handler(message: types.Message, state: FSMContext):
    from_user = message.from_user
    greeting_text = f"Hello, {from_user.full_name}!"
    await message.answer(greeting_text, reply_markup=kb.main)

async def reg_firstname(message: Message, state: FSMContext):
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(tg_username=message.from_user.username)
    await state.set_state(Reg.first_name)
    await message.answer("Enter your first name", reply_markup=ReplyKeyboardRemove())

async def reg_lastname(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await state.set_state(Reg.last_name)
    await message.answer("Enter your last name")

async def reg_phone(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await state.set_state(Reg.phone_number)
    await message.answer("Enter your phone number", reply_markup=kb.share_contact)

async def reg_notion_token(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.contact.phone_number)
    await state.set_state(Reg.notion_token)
    await message.answer("Enter your notion token", reply_markup=ReplyKeyboardRemove())

# @router.message(Reg.number)
async def reg_finish(message: Message, state: FSMContext):
    await state.update_data(notion_token=message.text)
    data = await state.get_data()
    await message.answer(f'You have successfully registered.\nFirstname: <b>{data["first_name"]}</b>\nLastname: {data["last_name"]}\nPhone number: {data["phone_number"]}\nTelegram ID: {data["tg_id"]}\nTelegram username: @{data["tg_username"]}\nNotion token: {data["notion_token"]}')
    data['created_date']=datetime.datetime.now()
    await rq.register_user(data)
    await state.clear()

# <blockquote></blockquote>
# <spoiler></spoiler>