from aiogram import Router, F
from aiogram.filters import CommandStart, Command

import handlers.commands as cm
from handlers.commands import Reg, Token, Category, Link

def setup() -> Router:
    router = Router()
    router.message.register(cm.start_command_handler, CommandStart())
    router.message.register(cm.help_command_handler, F.text == 'Help')
    router.message.register(cm.main_menu, F.text == 'Return to Main Menu')

    router.message.register(cm.reg_firstname, F.text == 'Register')
    router.message.register(cm.reg_lastname, Reg.first_name)
    router.message.register(cm.reg_phone, Reg.last_name)
    router.message.register(cm.reg_notion_token, Reg.phone_number, F.contact)
    router.message.register(cm.reg_database_id, Reg.notion_token)
    router.message.register(cm.reg_finish, Reg.database_id)

    router.message.register(cm.set_token, Command('settoken'))
    router.message.register(cm.get_token_and_db_id, Command('gettoken'))
    router.message.register(cm.token_finish, Token.notion_token)

    router.message.register(cm.get_categories, F.text == 'Categories')
    router.callback_query.register(cm.create_category, F.data == 'create_category')
    router.callback_query.register(cm.get_category_items, F.data.startswith('category_items_'))
    router.callback_query.register(cm.get_category_item_details, F.data.startswith('category_item_'))
    router.message.register(cm.set_category_name, Category.name)

    router.message.register(cm.save_link, F.text.contains('Save new link'))
    router.message.register(cm.save_link_title_and_url, Link.title)
    router.callback_query.register(cm.choose_link_title, F.data.startswith('save_title_'), Link.title)
    router.callback_query.register(cm.save_link_url, F.data.startswith('link_option_'), Link.url)
    router.callback_query.register(cm.save_link_category, Link.category)
    router.callback_query.register(cm.save_link_priority, F.data.startswith('priority_'))

    router.message.register(cm.get_saved_links, F.text == 'List of links')
    router.callback_query.register(cm.sort_links_by_title, F.data.startswith('sort_'))

    return router