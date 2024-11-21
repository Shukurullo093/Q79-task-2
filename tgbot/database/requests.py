from models.models import async_session
from models.models import User
from sqlalchemy import select
import datetime

async def register_user(reg) -> None:
    async with async_session() as session:
        # print(reg)
        # print(reg['tg_id'])
        user = await session.scalar(select(User).where(User.tg_id == int(reg['tg_id'])))

        if not user:
            # print('enter------------')
            new_user = User(tg_id=reg['tg_id'], 
                            first_name=reg['first_name'],
                            last_name=reg['last_name'],
                            phone_number=reg['phone_number'],
                            tg_username=reg['tg_username'],
                            notion_token=reg['notion_token'],
                            created_date=datetime.datetime.now())
            session.add(new_user)
            # session.add(User(tg_id = reg['tg_id'], User(created_date=datetime.datetime.now()))) 
            # session.add(User(tg_username=reg['tg_username']))
            # session.add(User(first_name=reg['first_name']))
            # session.add(User(last_name=reg['last_name']))
            # session.add(User(phone_number=reg['phone_number']))
            # session.add(User(notion_token=reg['notion_token']))
            # session.add(User(created_date=datetime.datetime.now()))

            await session.commit()
"""
async def set_user(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id = tg_id))
            await session.commit()

async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))
    
async def get_category_item(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category == int(category_id)))
    
async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == int(item_id)))
"""