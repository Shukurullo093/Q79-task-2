from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.sql import func
import enum

from data import config

engine = create_async_engine(url=config.DATABASE_URL)
async_session = async_sessionmaker(engine)

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

class User(Base):
    __tablename__ = "users"

    tg_id = mapped_column(BigInteger, unique=True, nullable=False)
    tg_username: Mapped[str] = mapped_column(String(30))
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    phone_number: Mapped[str] = mapped_column(String(13))
    notion_token: Mapped[str] = mapped_column(String())
    database_id: Mapped[str] = mapped_column(String())
    # created_date = mapped_column(DateTime(timezone=True), nullable=False) 
    created_date = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now()) 

class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String())
    owner: Mapped[int] = mapped_column(ForeignKey('users.id'))

class Priority(enum.Enum):
    low = 1
    middle = 2
    high = 3

# class Source(Base):
#     __tablename__ = "sources"

#     forward_from: Mapped[str] = mapped_column(String(30))
#     forward_user: Mapped[int] = mapped_column()

# class Link(Base):
#     __tablename__ = "links"

#     title: Mapped[str] = mapped_column(String())
#     category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
#     priority = mapped_column(Enum(Priority))
#     created_date = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now()) 

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # print("Connected to DB")