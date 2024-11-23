from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove
from notion_client import Client
from aiogram import Bot
import re
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from operator import itemgetter

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

async def start_command_handler(message: types.Message, state: FSMContext):
    await state.clear()
    from_user = message.from_user
    greeting_text = f"Hello, {from_user.full_name}!"
    if not await rq.has_user(message.from_user.id):
        await message.answer(greeting_text, reply_markup=kb.main)
    else: await message.answer(greeting_text, reply_markup=kb.main_menu)

async def help_command_handler(message: types.Message):
    await message.answer(text=f"FAQ", reply_markup=kb.help)

async def main_menu(message: types.Message):
    await message.answer(text=f"Main Menu", reply_markup=kb.main_menu)

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

async def reg_database_id(message: Message, state: FSMContext, bot: Bot):
    try:
        # animation = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fgifer.com%2Fen%2Fgifs%2Fwait&psig=AOvVaw129VUyJTWajLiM4J-mGqNr&ust=1732465982821000&source=images&cd=vfe&opi=89978449&ved=0CBMQjRxqFwoTCICS8vDw8okDFQAAAAAdAAAAABAE"
        # msg = await message.answer_animation(animation, caption="Please wait, fetching data...")
        client = Client(auth=message.text)
        user=client.users.me()
        import time
        time.sleep(5)
        await state.update_data(notion_token=message.text)
        await state.set_state(Reg.database_id)
        answer = "Enter your Notion database ID"
        # await bot.delete_message(msg.from_user.id, msg.message.message_id)
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())
    except:
        await state.set_state(Reg.notion_token)
        answer = "Your token is invalid\nEnter your Notion token again"
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())

async def reg_finish(message: Message, state: FSMContext):
    try:
        token = await state.get_value('notion_token')
        client = Client(auth=token)
        db = client.databases.retrieve(message.text)
        await state.update_data(database_id=message.text)
        data = await state.get_data()
        response = await rq.register_user(data)
        if response:
            await message.answer(f'You have successfully registered.\nFirstname: <b>{data["first_name"]}</b>\nLastname: {data["last_name"]}\nPhone number: {data["phone_number"]}\nDatabase ID: {data["database_id"]}\nNotion token: {data["notion_token"]}', reply_markup=kb.main_menu)
        else: await message.answer("You have already registered", reply_markup=kb.main_menu)
        await state.clear()
    except: 
        await state.set_state(Reg.database_id)
        answer = "Your database ID is invalid\nEnter your database ID again"
        await message.answer(answer, reply_markup=ReplyKeyboardRemove())

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

async def get_category_items(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    user = await rq.get_token_and_db_id(callback.from_user.id)
    links = await get_saved_links_from_notion(user.database_id, user.notion_token, 100)
    new_links = list(filter(lambda link: link['Category'] == callback.data[len('category_items_'):], links))
    # answer = await link_list_to_answer(new_links)
    await callback.message.answer("Saved links related to the category", reply_markup=await kb.get_category_items(new_links))

async def get_category_item_details(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    user = await rq.get_token_and_db_id(callback.from_user.id)
    links = await get_saved_links_from_notion(user.database_id, user.notion_token, 100)
    link = list(filter(lambda link: link['id'] == int(callback.data[len('category_item_'):]), links))
    answer = await link_list_to_answer(list(link))
    await callback.message.answer(answer)

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
        await state.set_state(Link.title)
        await message.answer('Send me url or (title & url)', reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("You cannot save new link.\nBecause you don't have any category to choose\nPlease, At first, create new category in categories menu")

async def save_link_title_and_url(message: Message, state: FSMContext):
    content = (message.text or message.caption)
    all_categories = await rq.get_categories(message.from_user.id)
    await state.update_data(tg_id = message.from_user.id)
    url = await state.get_value('url')
    if url != None:
        print("#1 [save_link_title_and_url]; url topildi")
        await state.update_data(title = message.text)
        await state.set_state(Link.category)
        await message.answer('Choose the category', reply_markup=await kb.get_categories(all_categories))
    else:
        print("#1 [save_link_title_and_url]; url topilmadi")
        title_and_urls = await extract_text_and_urls(content)
        if len(title_and_urls['urls']) > 0:
            print("#1 [save_link_title_and_url]; url topilmadi -> url bor")
            await state.update_data(title = title_and_urls['title'])
            urls = title_and_urls['urls']
            if len(urls) > 1:
                print("#1 [save_link_title_and_url]; url topilmadi -> url bor -> url ko'p")
                await state.set_state(Link.url)
                await message.answer("Multiple URLs were detected in the message you sent.\nWhich link do you want to save?", reply_markup=await kb.option_links_to_save(urls))
            else:
                if not title_and_urls['title']:
                    print("#1 [save_link_title_and_url]; url topilmadi -> url bor -> url bitta -> title yo'q")
                    # page = requests.get(urls[0])
                    # soup = BeautifulSoup(page.text, 'html.parser')
                    await state.update_data(title = await get_title_from_url(urls[0]))
                    await state.update_data(url = urls[0])
                    await state.set_state(Link.category)
                    # print(message.from_user.id)
                    # print(all_categories)
                    await message.answer('Choose the category', reply_markup=await kb.get_categories(all_categories))
                else:
                    print("#1 [save_link_title_and_url]; url topilmadi -> url bor -> url bitta -> title bor")
                    await state.set_state(Link.title)
                    title = title_and_urls['title']
                    answer = f"The following text was found in the message you sent.\n<blockquote>{title}</blockquote>\nDo you want to save it as a <b>TITLE</b>?\n"
                    await state.update_data(url = urls[0])
                    await message.answer(text=answer, reply_markup=kb.save_title)
        else: 
            await state.clear()
            await message.answer('Sizning xabaringizda url manzil topilmadi')

async def extract_text_and_urls(text):
    url_pattern = r'https?://\S+|www\.\S+'
    
    urls = re.findall(url_pattern, text)
    
    text_without_urls = re.sub(url_pattern, '', text)
    
    plain_text = re.sub(r'\s+', ' ', text_without_urls).strip()
    
    return {
        'title': plain_text,
        'urls': urls
    }

async def save_link_url(callback: CallbackQuery, state: FSMContext):
    # print(callback.data[len('link_option_'):])
    await state.update_data(url = callback.data[len('link_option_'):])
    await state.set_state(Link.title)
    title = await state.get_value('title')
    answer = f"The following text was found in the message you sent.\n<blockquote>{title}</blockquote>\nDo you want to save it as a <b>title</b>?\n"
    await callback.message.answer(text=answer, reply_markup=kb.save_title)

async def choose_link_title(callback: CallbackQuery, state: FSMContext):
    option = callback.data[len('save_title_'):]
    if option == 'yes':
        await state.set_state(Link.category)
        all_categories = await rq.get_categories(callback.from_user.id)
        await callback.message.answer('Choose the category', reply_markup=await kb.get_categories(all_categories))
    elif option == 'no':
        url = await state.get_value('url')
        await state.update_data(title = await get_title_from_url(url))
        await state.set_state(Link.category)
        all_categories = await rq.get_categories(callback.from_user.id)
        await callback.message.answer('Choose the category', reply_markup=await kb.get_categories(all_categories))
    else:
        await state.set_state(Link.title)
        await callback.message.answer('Enter the new title')

async def save_link_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category = int(callback.data.split('_')[1]))
    await state.set_state(Link.priority)
    await callback.message.answer('Choose the priority', reply_markup=await kb.priorities())

priorities_name = {1: 'low', 2: 'middle', 3: 'high'}
async def save_link_priority(callback: CallbackQuery, state: FSMContext):
    priority_name = priorities_name[int(callback.data.split('_')[1])]
    await state.update_data(priority = priority_name)
    data = await state.get_data()
    data.update({'category': (await rq.get_category(int(data['category']))).name})
    await callback.message.answer(f"Link saved\n\nTitle: {data['title']}\nURL: {data['url']}\nCategory: {data['category']}\nPriority: {data['priority']}", reply_markup=kb.main_menu)
    user = await rq.get_token_and_db_id(callback.from_user.id)
    await save_link_to_notion_db(user, data)
    await state.clear()

async def get_title_from_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup.find('title').string
# ------------------------------------------------------------

async def save_link_to_notion_db(user, link):
    # print(user.notion_token, link)
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
    # print(db_id)
    payload = {"parent": {"database_id": db_id}, "properties": data}
    res = requests.post(create_url, headers=headers, json=payload)
    # print(res.status_code)
    return res

# ------------------------------------------------------------
async def get_saved_links(message: Message):
    user = await rq.get_token_and_db_id(message.from_user.id)
    links = await get_saved_links_from_notion(user.database_id, user.notion_token, 100)
    answer = await link_list_to_answer(links)
    await message.answer(answer, reply_markup=kb.links_btm)

async def get_saved_links_from_notion(db_id, notion_token, num_pages=None):
    headers = {
        'Authorization': f"Bearer {notion_token}",
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

    url = f"https://api.notion.com/v1/databases/{db_id}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}    
    response = requests.post(url, json=payload, headers=headers)
    # print(response.status_code)
    data = response.json()
    # return data['results']
    
    answer = []
    count = 1
    for page in data['results']:
        page = page['properties']
        row = {}
        row['id'] = count
        count += 1
        for table_header in page.keys():
            type = page[table_header]['type']
            type_value = page[table_header][type]
            if isinstance(type_value, list):
                col = type_value[0]['text']['content']
                row[table_header] = col
            else: 
                col = type_value
                if type == 'created_time':
                    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
                    date_object = datetime.strptime(col, date_format)
                    created_time = f"{date_object.day}-{date_object.month}-{date_object.year} {date_object.hour+5}:{date_object.minute}"
                    # print("time zone ", date_object)
                    row[table_header] = created_time
                else: row[table_header] = col
        answer.append(row)
    return answer

async def link_list_to_answer(list: list):
    count = 1
    msg = ''
    for link in list:
        msg += f"\n🔢 {count}\n"
        count += 1
        if 'Title' in link:
            msg += f"<blockquote><b><i>Title</i></b>: {link['Title']}\n"
        if 'URL' in link:
            msg += f"<b><i>URL</i></b>: {link['URL']}\n"
        if 'Category' in link:
            msg += f"<b><i>Category</i></b>: {link['Category']}\n"
        if 'Priority' in link:
            msg += f"<b><i>Priority</i></b>: {link['Priority']}\n"
        if 'Created Time' in link:
            msg += f"<b><i>Created Time</i></b>: {link['Created Time']} </blockquote> \n"
    return msg.strip()

async def sort_list_by_arg(list: list, key: str, reverse = False):
    return sorted(list, key = itemgetter(key), reverse = reverse)

async def sort_links_by_title(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    user = await rq.get_token_and_db_id(callback.from_user.id)
    links = await get_saved_links_from_notion(user.database_id, user.notion_token, 100)
    if callback.data != 'sort_default':
        key = callback.data[len('sort_reverse_'):] if callback.data.startswith('sort_reverse_') else callback.data[len('sort_'):]
        links = await sort_list_by_arg(links, key.capitalize(), callback.data.startswith('sort_reverse_'))

    answer = await link_list_to_answer(links)
    await callback.message.answer(answer, reply_markup=kb.links_btm)

# ------------------------------------------------------------
async def get_token_and_db_id(message: Message):
    await rq.get_token_and_db_id(message.from_user.id)