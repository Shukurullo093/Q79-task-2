from aiogram import Router, F
from aiogram.filters import CommandStart, Command

import handlers.commands as cm
from handlers.commands import Reg, Token, Category

def setup() -> Router:
    router = Router()
    router.message.register(cm.start_command_handler, CommandStart())
    router.message.register(cm.help_command_handler, Command('help'))

    router.message.register(cm.reg_firstname, F.text == 'Register')
    router.message.register(cm.reg_lastname, Reg.first_name)
    router.message.register(cm.reg_phone, Reg.last_name)
    router.message.register(cm.reg_notion_token, Reg.phone_number, F.contact)
    router.message.register(cm.reg_finish, Reg.notion_token)

    router.message.register(cm.set_token, Command('settoken'))
    router.message.register(cm.token_finish, Token.notion_token)

    router.message.register(cm.get_categories, F.text == 'Categories')
    router.callback_query.register(cm.create_category, F.data == 'create_category')
    router.message.register(cm.set_category_name, Category.name)

    return router