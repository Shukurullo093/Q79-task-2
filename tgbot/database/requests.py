from models.models import async_session
from models.models import User, Category
from sqlalchemy import select, update, func
import datetime

async def has_user(tg_id) -> bool:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return True if user else False

async def register_user(reg):
    async with async_session() as session:
        # user = await session.scalar(select(User).where(User.tg_id == int(reg['tg_id'])))
        if not await has_user(reg['tg_id']):
            new_user = User(tg_id = reg['tg_id'], 
                            first_name = reg['first_name'],
                            last_name = reg['last_name'],
                            phone_number = reg['phone_number'],
                            tg_username = reg['tg_username'],
                            notion_token = reg['notion_token'],
                            database_id = reg['database_id'],
                            # created_date = datetime.datetime.now()
                            )
            session.add(new_user)
            await session.commit()
            return True
    return False

async def set_token(token) -> None:
    async with async_session() as session:
        if await has_user(token['tg_id']):
            stmt = update(User).where(User.tg_id == token['tg_id']).values(notion_token = token['notion_token'])
            await session.execute(stmt)
            await session.commit()

async def get_token_and_db_id(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return user
    
async def get_category(category_id) -> Category:
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.id == category_id))
        return category

async def get_categories(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        # print(len(list(await session.execute(select(Category).where(Category.owner == user.id)))))
        return list(await session.scalars(select(Category).where(Category.owner == user.id)))
    
async def create_category(category):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == category['tg_id']))
        new_category = Category(name=category['name'], owner=user.id)
        session.add(new_category)
        await session.commit()
