from datetime import timedelta
from fastapi import Depends, status, HTTPException, APIRouter, Response
from loguru import logger

from app import crud
from app.api import deps
from app.core.exceptions import RevokedTokenException, IdNotFoundException
from app.models.user_model import User
from app.core.security import create_token, validate_token, verify_hash
from app.core.config import config
from app.schemas.auth_schema import TokenOut, TokensOut, LogIn, UpdatePassIn
from app.schemas.user_schema import (
	UserCreateIn, )
from app.schemas.response_schema import (
	GetResponseBase,
	PostResponseBase,
	create_response,
)
from app.utils.time_util import compare_datetimes

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)  # POST /auth/register
async def create_user(
	response: Response, new_user: UserCreateIn = Depends(deps.user_doesnt_exist)
) -> PostResponseBase[TokensOut]:
	"""Register a new user."""
	if new_user.password != new_user.pass_confirm:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"password and confirmation must match")

	user = await crud.user.create_user(data=new_user)
	logger.success(f"ew user created: {user.email}:{new_user.alias}")

	access_token = create_token(user.id, token_type="access_token")
	refresh_token = create_token(user.id, token_type="refresh_token")
	response.set_cookie(key="refresh_token", value=f"Bearer {refresh_token}", httponly=True)

	return create_response(
		message=f"user {user.alias} was successfully registered",
		data={
		"access_token": access_token,
		"refresh_token": refresh_token
		},
	)


@router.post("/login")  # POST /auth/login
async def login(
	response: Response,
	data: LogIn,
) -> PostResponseBase[TokensOut]:
	"""Generate access & refresh tokens for valid users."""
	user = await crud.user.verify(email=data.email, password=data.password)
	if not user:
		raise HTTPException(status_code=400, detail="incorrect email or password")

	access_token = create_token(user.id, token_type="access_token")
	refresh_token = create_token(user.id, token_type="refresh_token")
	response.set_cookie(key="refresh_token", value=f"Bearer {refresh_token}", httponly=True)

	await crud.user.stamp_login(user=user)

	return create_response(
		message=f"login succeeded",
		data={
		"access_token": access_token,
		"refresh_token": refresh_token
		},
	)


@router.post("/access-token")  # POST /auth/access-token
async def get_access_token(data: LogIn) -> PostResponseBase[TokenOut]:
	"""Optional access-only login for direct API usage."""
	user = await crud.user.verify(email=data.email, password=data.password)
	if not user:
		raise HTTPException(status_code=400, detail="incorrect email or password")
	access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_token(user.id,
		token_type="access_token",
		expires_delta=access_token_expires)

	await crud.user.stamp_login(user=user)

	return create_response(
		message=f"token granted",
		data={
		"access_token": access_token,
		"token_type": "bearer",
		},
	)


@router.get("/refresh-access")  # POST /auth/refresh-access
async def get_new_access_token(
	response: Response,
	refresh_token: str = Depends(deps.auth_cookie),
	continuous: bool = "False",
) -> GetResponseBase[TokensOut]:
	"""
	Generate a new access_token for any user bearing a refresh cookie.
	Optionally refreshes both tokens.
	"""
	payload = validate_token(refresh_token)
	user_id = payload.sub
	user = await crud.user.get(id=user_id)
	if not user:
		raise IdNotFoundException(User, id=user_id)

	if user.revoked_at and compare_datetimes(payload.iat, '<', user.revoked_at):
		raise RevokedTokenException(token_type="refresh_token")

	access_token = create_token(user_id, token_type="access_token")
	message = "access token refreshed"

	refresh_token = None
	if continuous:
		refresh_token = create_token(user_id, token_type="refresh_token")
		response.set_cookie(key="refresh_token", value=f"Bearer {refresh_token}", httponly=True)
		await crud.user.stamp_login(user=user)
		message = "both tokens refreshed"

	return create_response(
		message=message,
		data={
		"access_token": access_token,
		"refresh_token": refresh_token
		},
	)


@router.delete("/tokens")  # DELETE /auth/tokens
async def revoke_tokens(current_user: User = Depends(deps.get_current_user()), ) -> None:
	"""Allows a user to log out from all sessions by invalidating any previously issued tokens."""
	# A regular front-end login route could simply delete the cookie for that session.
	await crud.user.revoke_access(user=current_user)
	logger.info(f"user logged out: {current_user.alias}")

	return create_response(message=f"tokens revoked", data=None)


@router.post("/update-password")  # POST /auth/update-password
async def update_password(
		data: UpdatePassIn,
		current_user: User = Depends(deps.get_current_user()),
) -> None:
	"""Change the logged-in user's password. Revokes all previously issued tokens."""
	if not verify_hash(data.current_pass, current_user.password):
		raise HTTPException(status_code=400, detail="current password is incorrect")

	if data.new_pass != data.confirm_pass:
		raise HTTPException(status_code=400,
			detail="confirmation does not match the desired password")

	await crud.user.update_password(user=current_user, new_pass=data.new_pass)
	await crud.user.revoke_access(user=current_user)
	logger.success(f"user {current_user.alias} has update their password")

	# Could be a RedirectResponse to the front-end login
	return create_response(message=f"password updated - please log in again", data=None)
