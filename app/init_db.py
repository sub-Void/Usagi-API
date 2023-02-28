import asyncio
from sqlalchemy import text

from app.db.init_data import init_data
from app.db.session import SessionLocal, engine
from app.models import Base


async def create_init_data() -> None:
	async with SessionLocal() as session:
		await init_data(session)


async def create_all():
	async with engine.begin() as conn:
		print("-- Dropping Tables --")
		await conn.run_sync(Base.metadata.drop_all)
		print("-- Creating Tables --")
		await conn.run_sync(Base.metadata.create_all)


async def create_extensions():
	async with engine.begin() as conn:
		try:
			await conn.execute(text("CREATE EXTENSION pg_trgm;"))
			await conn.execute(text("CREATE EXTENSION btree_gin;"))
		except Exception as e:
			print(e)


async def create_indexes():
	async with engine.connect() as conn:
		await conn.execution_options(isolation_level="AUTOCOMMIT")
		query = "CREATE INDEX CONCURRENTLY ix_app_users_trgm_alias ON app_users USING gin (alias gin_trgm_ops);"
		await conn.execute(text(query))


async def main() -> None:
	print("== Initializing database ==")
	await create_all()

	print("== Creating PSQL extensions ==")
	await create_extensions()

	print("== Creating PSQL indexes ==")
	await create_indexes()

	print("== Creating initial data ==")
	await create_init_data()


if __name__ == "__main__":
	asyncio.run(main())