import re
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr

from app.models.user_model import UserRoleEnum
from app.schemas.base_schema import ULID

rgx_user_alias = r"^[A-Za-z][A-Za-z0-9]{1,18}[A-Za-z0-9]$"


# -~-~ input ~-~-
class UserAlias(str):
	"""Validates a user alias against our regex and returns a readable message."""

	@classmethod
	def __get_validators__(cls):
		yield cls.validate

	@classmethod
	def validate(cls, v):
		if not isinstance(v, str):
			raise TypeError('alias must be a string')
		match = re.match(r"^[0-9]", v)
		if match:
			raise ValueError("an alias cannot begin with a number.")
		match = re.match(rgx_user_alias, v)
		if match is None:
			raise ValueError(
				"an alias must must be between 3-20 characters and contain only letters and numbers."
			)
		return v


# CRUDUser
class UserCreateIn(BaseModel):
	email: EmailStr
	alias: UserAlias
	password: constr(min_length=6, max_length=200)
	pass_confirm: constr(min_length=6, max_length=200)


# CRUDUser
class UserUpdateIn(BaseModel):
	email: EmailStr
	alias: UserAlias
	password: constr(min_length=6, max_length=100)


class UserLogIn(BaseModel):
	email: EmailStr
	password: constr(min_length=6, max_length=200)


class UserUpdatePasswordIn(BaseModel):
	current_password: constr(min_length=6, max_length=200)
	desired_password: constr(min_length=6, max_length=200)
	password_confirm: constr(min_length=6, max_length=200)


# -~-~ output ~-~-
class UserOut(BaseModel):
	id: ULID
	alias: str
	role: UserRoleEnum
	registered_on: datetime
	last_login: datetime

	class Config:
		orm_mode = True  #*


class UserOutFull(BaseModel):
	id: ULID
	email: EmailStr
	alias: str
	role: UserRoleEnum
	last_login: datetime
	registered_on: datetime
	revoked_at: datetime | None

	class Config:
		orm_mode = True  #*
