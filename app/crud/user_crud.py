from sqlalchemy import func, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from pydantic import EmailStr
from fastapi_async_sqlalchemy import db

from app.core.exceptions import UserIsBannedException
from app.crud.base_crud import CRUDBase
from app.schemas.user_schema import UserCreateIn, UserUpdateIn
from app.models.user_model import User, UserRoleEnum
from app.core.security import verify_hash, hash_pass
from app.utils.time_util import utc_now


class CRUDUser(CRUDBase[User, UserCreateIn, UserUpdateIn]):  #

	async def get_by_email(self, *, email: str,
		db_session: None | AsyncSession = None) -> User | None:
		db_session = db_session or db.session
		users = await db_session.execute(
			select(User).where(func.lower(User.email) == email.lower()))
		return users.scalar_one_or_none()

	async def get_by_alias(self, *, alias: str,
		db_session: None | AsyncSession = None) -> User | None:
		db_session = db_session or db.session
		users = await db_session.execute(select(User).where(User.alias == alias))
		return users.scalar_one_or_none()

	async def create_user(self, *, data: UserCreateIn,
		db_session: None | AsyncSession = None) -> User | None:
		db_session = db_session or db.session
		user_obj = User(
			email=data.email,
			alias=data.alias,
			password=hash_pass(data.password),
		)
		db_session.add(user_obj)
		await db_session.commit()
		await db_session.refresh(user_obj)
		return user_obj

	async def verify(self, *, email: EmailStr, password: str) -> User | None:
		""" Verifies a users login credentials """
		user = await self.get_by_email(email=email)
		if not user:
			return None
		if user.role == UserRoleEnum.BANNED:
			raise UserIsBannedException()
		if not verify_hash(password, user.password):
			return None
		return user

	async def update_password(self, *, user: User, new_pass: str):
		user.password = hash_pass(new_pass)
		db.session.add(user)
		await db.session.commit()

	async def revoke_access(self, *, user: User):
		user.revoked_at = utc_now()
		db.session.add(user)
		await db.session.commit()

	async def stamp_login(self, *, user: User):
		user.last_login = utc_now()
		db.session.add(user)
		await db.session.commit()


user = CRUDUser(User)
