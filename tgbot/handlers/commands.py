from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
import re
import requests

import keyboards.keyboards as kb 
import database.requests as rq

class Reg(StatesGroup):
    first_name = State()
    last_name = State()
    tg_username = State()
    tg_id = State()
    phone_number = State()
    notion_token = State()
    database_id = State()

class Token(StatesGroup):
    tg_id=State()
    notion_token=State()

class Category(StatesGroup):
    tg_id=State()
    name=State()

class Link(StatesGroup):
    tg_id=State()
    title = State()
    url = State()
    category = State()
    priority = State()

async def start_command_handler(message: types.Message):
    from_user = message.from_user
    greeting_text = f"Hello, {from_user.full_name}!"
    # print(await rq.has_user(message.from_user.id))
    if not await rq.has_user(message.from_user.id):
        await message.answer(greeting_text, reply_markup=kb.main)
    else: await message.answer(greeting_text, reply_markup=kb.main_menu)

async def help_command_handler(message: types.Message):
    await message.answer(text=f"FAQ", reply_markup=kb.help)

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
    answer = "Enter your Notion token"
    await message.answer(answer, reply_markup=ReplyKeyboardRemove())

async def reg_database_id(message: Message, state: FSMContext):
    await state.update_data(notion_token=message.text)
    await state.set_state(Reg.database_id)
    answer = "Enter your Notion database ID"
    await message.answer(answer, reply_markup=ReplyKeyboardRemove())

async def reg_finish(message: Message, state: FSMContext):
    await state.update_data(database_id=message.text)
    data = await state.get_data()
    response = await rq.register_user(data)
    if response:
        await message.answer(f'You have successfully registered.\nFirstname: <b>{data["first_name"]}</b>\nLastname: {data["last_name"]}\nPhone number: {data["phone_number"]}\nDatabase ID: @{data["database_id"]}\nNotion token: {data["notion_token"]}', reply_markup=kb.main_menu)
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
        # print()

        # print(message.forward_from_chat)
        # print(message.forward_sender_name)

        # message_sender = message.forward_from.username or message.forward_from.full_name
        # print(message_sender)

async def save_link(message: Message, state: FSMContext):
    all_categories = await rq.get_categories(message.from_user.id)
    if all_categories:
        await state.update_data(tg_id = message.from_user.id)
        await state.set_state(Link.title)
        await message.answer('Send me url or (title & url)')
    else:
        await message.answer("You cannot save new link.\nBecause you don't have any category to choose\nPlease, At first, create new category in categories menu")

async def save_link_title_and_url(message: Message, state: FSMContext):
    content = (message.text or message.caption)
    if len(re.findall("(?P<url>https?://[^\s]+)", content)) > 0:
        url = re.findall("(?P<url>https?://[^\s]+)", content)[0]
        # title = re.match(r'^'+url, content)
        # print(title)
        page = requests.get(url)
        # print(page.status_code)
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(page.text, 'html.parser')
        await state.update_data(title = soup.find('title').string)
        await state.update_data(url = url)
        await state.set_state(Link.category)
        # print(message.from_user.id)
        all_categories = await rq.get_categories(message.from_user.id)
        # print(all_categories)
        await message.answer('Choose the category', reply_markup=await kb.categories(all_categories))
    else: 
        await state.clear()
        await message.answer('Sizning xabaringizda url manzil topilmadi')

async def save_link_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category = int(callback.data.split('_')[1]))
    await state.set_state(Link.priority)
    await callback.message.answer('Choose the priority', reply_markup=await kb.priorities())

priorities_name = {1: 'low', 2: 'middle', 3: 'high'}
async def save_link_priority(callback: CallbackQuery, state: FSMContext):
    priority_name = priorities_name[int(callback.data.split('_')[1])]
    await state.update_data(priority = priority_name)
    data = await state.get_data()
    # extracted_info = tldextract.extract(data['url'])
    # domain = f"{extracted_info.subdomain}.{extracted_info.domain}.{extracted_info.suffix}"
    domain = ''
    data.update({'category': (await rq.get_category(int(data['category']))).name})
    await callback.message.answer(f"Link saved\n\nTitle: {data['title']}\nURL: {data['url']}\nURL source: {domain}\nCategory: {data['category']}\nPriority: {data['priority']}")
    user = await rq.get_token_and_db_id(callback.from_user.id)
    await save_link_to_notion_db(user, data)
    await state.clear()

# ------------------------------------------------------------
async def save_link_to_notion_db(user, link):
    print(user.notion_token, link)
    headers = {
        'Authorization': f"Bearer {user.notion_token}",
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    data = {
        'Title': {'title': [{'text': {'content': link['title']}}]},
        'Category': {'rich_text': [{'text': {'content': str(link['category'])}}]},
        'URL': {'url': link['url']},
        'Priority': {'rich_text': [{'text': {'content': link['priority']}}]}
    }
    
    await create_page(headers, data, user.database_id)

async def create_page(headers, data: dict, db_id):
    create_url = "https://api.notion.com/v1/pages"
    print(db_id)
    payload = {"parent": {"database_id": db_id}, "properties": data}
    res = requests.post(create_url, headers=headers, json=payload)
    print(res.status_code)
    return res

# ------------------------------------------------------------
async def get_saved_links(message: Message):
    user = await rq.get_token_and_db_id(message.from_user.id)
    headers = {
        'Authorization': f"Bearer {user.notion_token}",
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }
    pages = await get_pages(user.database_id, headers, 100)
    count = 1 ##️⃣
    # new_table = {}
    answer = []
    msg = ''
    for page in pages:
        page = page['properties']
        row = {}
        for table_header in page.keys():
            type = page[table_header]['type']
            type_value = page[table_header][type]
            if isinstance(type_value, list):
                col = type_value[0]['text']['content']
                # column = []
                # if table_header in new_table:
                #     column = new_table[table_header]
                #     column.append(col)
                row[table_header] = col
                # msg += f"{table_header}: {col}\n"
                #     new_table.update({table_header: column})
                # else:
                #     column.append(col)
                #     row[table_header] = col
                #     new_table[table_header] = list(column)
            else: 
                col = type_value
                # column = []
                # if table_header in new_table:
                #     column = new_table[table_header]
                #     column.append(col)
                row[table_header] = col
                # msg += f"{table_header}: {col}\n"
                    # new_table.update({table_header: column})
                # else:
                #     column.append(col)
                #     row[table_header] = col
                    # msg += f"{table_header}: {col}\n"
                    # new_table[table_header] = list(column)
        answer.append(row)
    
    for link in answer:
        msg += f"\n🔢 {count}\n"
        count+=1
        if 'Title' in link:
            msg += f"Title: {link['Title']}\n"
        if 'URL' in link:
            msg += f"URL: {link['URL']}\n"
        if 'Category' in link:
            msg += f"Category: {link['Category']}\n"
        if 'Priority' in link:
            msg += f"Priority: {link['Priority']}\n"
    
    await message.answer(msg.strip(), reply_markup=kb.links_btm)

async def get_pages(db_id, headers, num_pages=None):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}    
    response = requests.post(url, json=payload, headers=headers)
    # print(response.status_code)
    data = response.json()
    # import json
    # with open('db.json', 'w', encoding='utf8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)
    return data['results']

# ------------------------------------------------------------
async def get_token_and_db_id(message: Message):
    await rq.get_token_and_db_id(message.from_user.id)