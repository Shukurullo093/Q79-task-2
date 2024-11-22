from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from database.requests import get_categories

main = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text="Register")]],
    resize_keyboard = True, input_field_placeholder="Please register"
)

share_contact = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text="Share phone number", request_contact=True)]],
    resize_keyboard = True
)

main_menu = ReplyKeyboardMarkup(keyboard= [
    [KeyboardButton(text="Save new link"), KeyboardButton(text="List of links")],
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