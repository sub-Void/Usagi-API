from typing import List
from fastapi import Depends, HTTPException, status

from app.core.exceptions import RevokedTokenException
from app.schemas.user_schema import UserCreateIn
from app import crud
from app.core.security import AuthRefreshCookie, AuthAccessBearer, validate_token
from app.models.user_model import User
from app.utils.time_util import compare_datetimes

auth_cookie = AuthRefreshCookie(tokenUrl="/auth/login")  #docs
auth_bearer = AuthAccessBearer(tokenUrl="/auth/access-token")


async def user_doesnt_exist(new_user: UserCreateIn) -> UserCreateIn:
	"""Ensures an existing user email or alias doesn't already exist."""

	user = await crud.user.get_by_email(email=new_user.email)
	if user:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="a user with this email address already exists",
		)
	user = await crud.user.get_by_alias(alias=new_user.alias)
	if user:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="a user with this alias already exists",
		)
	return new_user


def get_current_user(required_roles: List[str] = None) -> User:
	"""Retrieves the current user's data via access_token payload"""

	async def current_user(token: str = Depends(auth_bearer)) -> User:
		payload = validate_token(token)
		user_id = payload.sub
		user: User = await crud.user.get(id=user_id)
		if not user:
			raise HTTPException(status_code=404, detail="user does not exist")

		if user.revoked_at and compare_datetimes(payload.iat, '<', user.revoked_at):
			raise RevokedTokenException(token_type="access_token")

		if required_roles:
			valid_role = False
			for role in required_roles:
				if role == user.role:
					valid_role = True
			if not valid_role:
				raise HTTPException(
					status_code=403,
					detail=f"a {user.role.lower()} cannot perform this action",
				)

		return user

	return current_user
