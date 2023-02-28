from fastapi import (APIRouter, Depends, Query)
from fastapi_pagination import Params
from sqlalchemy import func, select
from loguru import logger

from app import crud
from app.models import User
from app.api import deps
from app.core.exceptions import (IdNotFoundException, UserSelfDeleteException)
from app.models.user_model import UserRoleEnum
from app.schemas.base_schema import OrderEnum, ULID
from app.schemas.response_schema import (
	GetResponseBase,
	create_response,
	GetResponsePaginated,
	DeleteResponseBase,
)
from app.schemas.user_schema import (UserOut, UserOutFull)

router = APIRouter()


@router.get("s")  #GET /users/
async def list_users(
	params: Params = Depends(),
	search_string: str | None = Query(default=None, min_length=3, max_length=20),
) -> GetResponsePaginated[UserOut]:
	"""Retrieve a list users. Requires admin or moderator role."""
	if search_string:
		query = (select(User).filter(func.similarity(User.alias, search_string) > 0.4)
					)  # using tgrm
		users = await crud.user.get_multi_paginated(query=query, params=params)
	else:
		users = await crud.user.get_multi_paginated(params=params)

	message = "user(s) retrieved" if users.data.total else "no users found"
	return create_response(data=users, message=message, meta={"search_string": search_string})


@router.get("s/new")  #GET /users/new
async def list_new_users(params: Params = Depends(), ) -> GetResponsePaginated[UserOut]:
	"""Retrieve a paginated list of the newest users."""
	users = await crud.user.get_multi_paginated_ordered(params=params,
		order_by="id",
		order=OrderEnum.DESC)  #ULID is sortable

	message = "user(s) retrieved" if users.data.total else "no users found"
	return create_response(data=users, message=message)


@router.get("s/{role_name}")  #GET /users/:ROLE
async def list_users_by_role_name(
	role_name: UserRoleEnum,
	params: Params = Depends(),
	current_user: User = Depends(
	deps.get_current_user(required_roles=[UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR])),
) -> GetResponsePaginated[UserOutFull]:
	"""Retrieve a list users by role. Requires admin or moderator role."""
	query = (select(User).filter(User.role == role_name))
	users = await crud.user.get_multi_paginated(query=query, params=params)

	message = "user(s) retrieved" if users.data.total else "no users found"
	return create_response(data=users, message=message)


@router.get("/count")  # GET /user/count
async def get_user_count() -> GetResponseBase:
	"""Retrieve the total number of users."""
	user_count = await crud.user.get_count()
	return create_response(data=user_count, message="user count retrieved")


@router.get("/{user_id}")  # GET /user/:ID
async def get_user_by_id(user_id: ULID, ) -> GetResponseBase[UserOut]:
	"""Retrieve a user"""
	if user := await crud.user.get(id=user_id):
		return create_response(data=user, message="user retrieved")
	else:
		raise IdNotFoundException(User, id=user_id)


@router.delete("/{user_id}")  # DELETE /user/:ID
async def remove_user(
	user_id: ULID,
	current_user: User = Depends(deps.get_current_user(required_roles=[UserRoleEnum.ADMIN])),
) -> DeleteResponseBase[UserOutFull]:
	"""Delete a user."""
	user = await crud.user.get(id=user_id)

	if not user:
		raise IdNotFoundException(User, id=user_id)
	if current_user.id == user_id:
		raise UserSelfDeleteException()

	await crud.user.remove(id=user_id)
	logger.success(f"'{current_user.alias}' ({current_user.id}) deleted user: '{user.alias}'")
	return create_response(data=user, message=f"User {user.alias} removed.")
