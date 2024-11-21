from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State

# from handlers.commands import start_command_handler
import handlers.commands as cm
from handlers.commands import Reg

def setup() -> Router:
    router = Router()
    router.message.register(cm.start_command_handler, CommandStart())
    router.message.register(cm.reg_firstname, F.text == 'Register')
    router.message.register(cm.reg_lastname, Reg.first_name)
    router.message.register(cm.reg_phone, Reg.last_name)
    router.message.register(cm.reg_notion_token, Reg.phone_number, F.contact)
    router.message.register(cm.reg_finish, Reg.notion_token)

    return router