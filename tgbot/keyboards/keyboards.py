from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from models.models import Priority

main = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text="Register")]],
    resize_keyboard = True, input_field_placeholder="Please register"
)

help = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text="How to find Notion Token(API Key)"),
     KeyboardButton(text="How to find Notion Database ID")],
    [KeyboardButton(text="Return to Main Menu")]],
    resize_keyboard = True
)

share_contact = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text="Share phone number", request_contact=True)]],
    resize_keyboard = True
)

main_menu = ReplyKeyboardMarkup(keyboard= [
    [KeyboardButton(text="🆕 Save new link 🔗"), KeyboardButton(text="List of links")],
    [KeyboardButton(text="Categories"), KeyboardButton(text="Help")],
], resize_keyboard=True)

async def categories(all_categories):
    keyboard = InlineKeyboardBuilder()    
    keyboard.add(InlineKeyboardButton(text="Create New 🆕", callback_data="create_category"))
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_items_{category.name}"))
    return keyboard.adjust(1).as_markup()

async def get_categories(all_categories):
    keyboard = InlineKeyboardBuilder()    
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
    return keyboard.adjust(1).as_markup()

async def get_category_items(links):
    keyboard = InlineKeyboardBuilder()  
    for link in links:
        keyboard.add(InlineKeyboardButton(text=link['Title'], callback_data=f"category_item_{link['id']}"))
    return keyboard.adjust(1).as_markup()

create_category = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text='Create New 🆕', callback_data = 'create_category')] 
])

async def priorities():
    keyboard = InlineKeyboardBuilder()    
    for priority in (Priority):
        keyboard.add(InlineKeyboardButton(text=priority.name, callback_data=f"priority_{priority.value}"))
    return keyboard.adjust(1).as_markup()

links_btm = InlineKeyboardMarkup(inline_keyboard = [
    [
        InlineKeyboardButton(text='Title ⬆️', callback_data = 'sort_title'), 
        InlineKeyboardButton(text='Category 🔼', callback_data = 'sort_category'),
        InlineKeyboardButton(text='Priority ↗️', callback_data = 'sort_priority'),
    ],
    [
        InlineKeyboardButton(text='Title ⬇️', callback_data = 'sort_reverse_title'),
        InlineKeyboardButton(text='Category 🔽', callback_data = 'sort_reverse_category'),
        InlineKeyboardButton(text='Priority ↘️', callback_data = 'sort_reverse_priority')
    ],
    [InlineKeyboardButton(text='⚫️ Default ⚫️', callback_data = 'sort_default')]
])

save_title = InlineKeyboardMarkup(inline_keyboard = [
    [InlineKeyboardButton(text='Yes, I want', callback_data = 'save_title_yes')],
    [InlineKeyboardButton(text='No, Please, use url\'s title', callback_data = 'save_title_no')],
    [InlineKeyboardButton(text='I want to create a new title', callback_data = 'save_title_manually')]
])

async def option_links_to_save(links):
    keyboard = InlineKeyboardBuilder() 
    count = 1   
    for link in links:
        keyboard.add(InlineKeyboardButton(text=link, callback_data=f"link_option_{link}"))
        count += 1
    return keyboard.adjust(1).as_markup()