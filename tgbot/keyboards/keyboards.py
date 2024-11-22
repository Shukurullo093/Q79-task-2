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
     KeyboardButton(text="How to find Notion Database ID")]],
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
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
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
        InlineKeyboardButton(text='Title A->Z', callback_data = 'title_a_z'), 
        InlineKeyboardButton(text='Title Z->A', callback_data = 'title_z_a')
    ],
    [
        InlineKeyboardButton(text='Priority low to high', callback_data = 'priority_l_h'),
        InlineKeyboardButton(text='Priority high to low', callback_data = 'priority_h_l')
    ]
])