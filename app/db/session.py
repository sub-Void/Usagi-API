from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.config import config

connect_args = {"check_same_thread": False}

async_db_uri = f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}/{config.DB_NAME}"
print(f"database url: async_db_uri")

engine = create_async_engine(
	async_db_uri,
	echo=True,
	future=True,
	pool_size=config.DB_POOL_SIZE,
	max_overflow=config.DB_MAX_OVERFLOW,
)

SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine,
	class_=AsyncSession,
	expire_on_commit=False,
)
