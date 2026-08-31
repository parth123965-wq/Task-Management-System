from app.core.config import setting
from sqlalchemy.ext.asyncio import create_async_engine , async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = create_async_engine(url=setting.DATABASE_URL,echo=True)
async_session_maker = async_sessionmaker(bind=engine,expire_on_commit=True)


async def get_db():
    async with async_session_maker() as session:
        yield session