from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Integer

from data import config

engine = create_async_engine(url=config.DATABASE_URL)

async_session = async_sessionmaker(engine)

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class User(Base):
    __tablename__ = "users"

    tg_id = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    tg_username: Mapped[str] = mapped_column(String(30))
    phone_number: Mapped[str] = mapped_column(String(13))
    notion_token: Mapped[str] = mapped_column(String(50))
    created_date = mapped_column(DateTime(timezone=True), nullable=False) # datetime.now()

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # print("Connected to DB")