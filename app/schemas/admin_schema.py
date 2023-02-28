from pydantic import BaseModel, EmailStr, constr

from app.models.user_model import UserRoleEnum
from app.schemas.base_schema import ULID
from app.schemas.user_schema import rgx_user_alias


class AdminCreateUser(BaseModel):
	email: EmailStr
	alias: constr(min_length=3, max_length=20, regex=rgx_user_alias)
	password: constr(min_length=6, max_length=200)
	role: UserRoleEnum
	confirmed: bool = True


class AdminSetUserRole(BaseModel):
	user_id: ULID
	role: UserRoleEnum


class AdminBanUser(BaseModel):
	user_id: ULID
	reason: constr(min_length=6, max_length=50) | None = None
