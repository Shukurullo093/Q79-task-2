from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
import re

import keyboards.keyboards as kb 
import database.requests as rq

class Token(StatesGroup):
    tg_id=State()
    notion_token=State()

class Category(StatesGroup):
    tg_id=State()
    name=State()

class Reg(StatesGroup):
    first_name = State()
    last_name = State()
    tg_username = State()
    tg_id = State()
    phone_number = State()
    notion_token = State()

async def start_command_handler(message: types.Message):
    from_user = message.from_user
    greeting_text = f"Hello, {from_user.full_name}!"
    # print(await rq.has_user(message.from_user.id))
    if not await rq.has_user(message.from_user.id):
        await message.answer(greeting_text, reply_markup=kb.main)
    else: await message.answer(greeting_text, reply_markup=kb.main_menu)

async def help_command_handler(message: types.Message):
    await message.reply(text=f"This bot helps you to save useful links into Notion account. You must register to use bot.")

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
    answer = """Enter your notion token\n\nHint.\n<blockquote>To find a Notion integration token, you can: 
Go to the <a href="https://www.notion.so/my-integrations">My integrations</a> page 
Click + New Integration 
Create the integration 
Navigate to Settings & members in your sidebar 
Select the Connections tab 
Click the ••• menu next to the connection you want to link 
Click Copy internal integration token</blockquote>"""
    await message.answer(answer, reply_markup=ReplyKeyboardRemove())

async def reg_finish(message: Message, state: FSMContext):
    await state.update_data(notion_token=message.text)
    data = await state.get_data()
    response = await rq.register_user(data)
    if response:
        await message.answer(f'You have successfully registered.\nFirstname: <b>{data["first_name"]}</b>\nLastname: {data["last_name"]}\nPhone number: {data["phone_number"]}\nTelegram ID: {data["tg_id"]}\nTelegram username: @{data["tg_username"]}\nNotion token: {data["notion_token"]}', reply_markup=kb.main_menu)
    else: await message.answer("You have already registered")
    await state.clear()

async def set_token(message: Message, state: FSMContext):
    await state.set_state(Token.tg_id)
    await state.update_data(tg_id=message.from_user.id)
    await state.set_state(Token.notion_token)
    await message.answer("Enter your notion token")

async def token_finish(message: Message, state: FSMContext):
    await state.update_data(notion_token=message.text)
    data = await state.get_data()
    await rq.set_token(data)
    await message.answer('Your Notion token has saved.')
    await state.clear()

async def get_categories(message: Message):
    all_categories = await rq.get_categories(message.from_user.id)
    if all_categories: 
        await message.answer('List of categories', reply_markup=await kb.categories(all_categories))
    else:
        await message.answer('You don\'t have any saved category', reply_markup=kb.create_category)

async def create_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(tg_id=callback.from_user.id)
    await state.set_state(Category.name)
    await callback.message.answer('Enter new category name')

async def set_category_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    await rq.create_category(data)
    await message.answer('New category has created')
    await state.clear()

async def any_message(message: Message):
    if message.forward_origin is not None:
        # print(message.forward_origin)
        if message.forward_origin.type != 'hidden_user':
            print(message.forward_origin.sender_user.username)
        print(message)
        # print(re.findall("(?P<url>https?://[^\s]+)", message.text)[0])

        # print(message.forward_from_chat)
        # print(message.forward_sender_name)

        # message_sender = message.forward_from.username or message.forward_from.full_name
        # print(message_sender)


# <blockquote></blockquote>
# <spoiler></spoiler>