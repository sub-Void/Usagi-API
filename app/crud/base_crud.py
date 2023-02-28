from typing import Any, Dict, Generic, List, Type, TypeVar
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import Select
from sqlalchemy import exc, select, func
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi_async_sqlalchemy import db
from fastapi_pagination import Params, Page
from fastapi.encoders import jsonable_encoder

from app.schemas.base_schema import ULID, OrderEnum
from app.models.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)
T = TypeVar("T", bound=Base)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

	def __init__(self, model: Type[ModelType]):
		"""
		Default generic CRUD methods.
		**Parameters**
		* `model`: A SQLModel model class
		* `schema`: A Pydantic model (schema) class
		"""
		self.model = model

	async def get(self, *, id: ULID,
		db_session: AsyncSession | None = None) -> ModelType | None:
		db_session = db_session or db.session
		query = select(self.model).where(self.model.id == id)
		response = await db_session.execute(query)
		return response.scalar_one_or_none()

	async def get_by_ids(
		self,
		*,
		list_ids: List[str],
		db_session: AsyncSession | None = None,
	) -> List[ModelType] | None:
		db_session = db_session or db.session
		response = await db_session.execute(
			select(self.model).where(self.model.id.in_(list_ids)))
		return response.scalars().all()

	async def get_count(self, db_session: AsyncSession | None = None) -> int | None:
		db_session = db_session or db.session
		response = await db_session.execute(
			select(func.count()).select_from(select(self.model).subquery()))
		return response.scalar_one()

	async def get_multi(
		self,
		*,
		skip: int = 0,
		limit: int = 100,
		query: T | Select[T] | None = None,
		db_session: AsyncSession | None = None,
	) -> List[ModelType]:
		db_session = db_session or db.session
		if query is None:
			query = select(self.model).offset(skip).limit(limit).order_by(self.model.id)
		response = await db_session.execute(query)
		return response.scalars().all()

	async def get_multi_paginated(
		self,
		*,
		params: Params | None = Params(),
		query: T | Select[T] | None = None,
		db_session: AsyncSession | None = None,
	) -> Page[ModelType]:
		db_session = db_session or db.session
		if query is None:
			query = select(self.model)
		return await paginate(db_session, query, params)

	async def get_multi_paginated_ordered(
		self,
		*,
		params: Params | None = Params(),
		order_by: str | None = None,
		order: OrderEnum | None = OrderEnum.ASC,
		query: T | Select[T] | None = None,
		db_session: AsyncSession | None = None,
	) -> Page[ModelType]:
		db_session = db_session or db.session
		columns = self.model.__table__.columns
		if order_by is None or order_by not in columns:
			order_by = self.model.id
		if query is None:
			if order == OrderEnum.ASC:
				query = select(self.model).order_by(columns[order_by].asc())
			else:
				query = select(self.model).order_by(columns[order_by].desc())
		return await paginate(db_session, query, params)

	async def get_multi_ordered(
		self,
		*,
		skip: int = 0,
		limit: int = 100,
		order_by: str | None = None,
		order: OrderEnum | None = OrderEnum.ASC,
		db_session: AsyncSession | None = None,
	) -> List[ModelType]:
		db_session = db_session or db.session

		columns = self.model.__table__.columns

		if order_by is None or order_by not in columns:
			order_by = self.model.id

		if order == OrderEnum.ASC:
			query = (select(self.model).offset(skip).limit(limit).order_by(
				columns[order_by].asc()))
		else:
			query = (select(self.model).offset(skip).limit(limit).order_by(
				columns[order_by].desc()))

		response = await db_session.execute(query)
		return response.scalars().all()

	async def create(
		self,
		*,
		data: CreateSchemaType | ModelType,
		created_by_id: ULID | None = None,
		db_session: AsyncSession | None = None,
	) -> ModelType:
		db_session = db_session or db.session
		obj_data = jsonable_encoder(data)
		obj = self.model(**obj_data)  # type: ignore
		if created_by_id:
			obj.created_by_id = created_by_id

		try:
			db_session.add(obj)
			await db_session.commit()
		except exc.IntegrityError:
			db_session.rollback()
			raise HTTPException(
				status_code=409,
				detail="resource already exists",
			)
		await db_session.refresh(obj)
		return obj

	async def update(
		self,
		*,
		obj: ModelType,
		new: UpdateSchemaType | Dict[str, Any] | ModelType,
		db_session: AsyncSession | None = None,
	) -> ModelType:
		db_session = db_session or db.session
		obj_data = jsonable_encoder(obj)

		if isinstance(new, dict):
			update_data = new
		else:
			update_data = new.dict(
				exclude_unset=True)  # Do not affect values that are not explicitly passed in.
		for field in obj_data:
			if field in update_data:
				setattr(obj, field, update_data[field])

		db_session.add(obj)
		await db_session.commit()
		await db_session.refresh(obj)
		return obj

	async def remove(self, *, id: ULID, db_session: AsyncSession | None = None) -> ModelType:
		db_session = db_session or db.session
		response = await db_session.execute(select(self.model).where(self.model.id == id))
		obj = response.scalar_one()
		await db_session.delete(obj)
		await db_session.commit()
		return obj