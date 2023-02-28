from datetime import datetime
from fastapi import Depends, status, HTTPException, APIRouter
from loguru import logger

from app import crud
from app.api import deps
from app.models.user_model import User, UserRoleEnum
from app.schemas.admin_schema import (AdminSetUserRole, AdminBanUser)
from app.schemas.response_schema import (
	create_response, )

router = APIRouter()


@router.post("/ban-user", status_code=status.HTTP_200_OK)  # POST /admin/ban-user
async def ban_user(
	data: AdminBanUser,
	current_user: User = Depends(
	deps.get_current_user(required_roles=[UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR])),
) -> None:
	"""Bans a user."""
	user = await crud.user.get(id=data.user_id)
	if not user:
		raise HTTPException(status_code=404, detail="user does not exist")

	await crud.user.update(obj=user,
		new={
		"role": UserRoleEnum.BANNED,
		"revoked_at": datetime.utcnow()
		})

	message = f"'{current_user.alias}' ({current_user.id}) has banned user: '{user.alias}' - reason: {data.reason}"
	logger.success(message)
	return create_response(message=message, data=None)


@router.post("/set-role", status_code=status.HTTP_200_OK)  # POST /admin/set-role
async def set_user_role(
	data: AdminSetUserRole,
	current_user: User = Depends(deps.get_current_user(required_roles=[UserRoleEnum.ADMIN])),
) -> None:
	"""Sets a user's role."""
	if data.role == UserRoleEnum.BANNED:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
			detail=f"use the /admin/ban-user route instead")

	user = await crud.user.get(id=data.user_id)
	if not user:
		raise HTTPException(status_code=404, detail="user does not exist")

	await crud.user.update(obj=user, new={
		"role": data.role,
	})

	logger.success(
		f"'{current_user.alias}' ({current_user.id}) has set user role: '{user.alias}' -> {data.role}"
	)
	return create_response(message="role updated", data=None)