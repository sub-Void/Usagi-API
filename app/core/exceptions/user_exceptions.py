from typing import Any, Dict
from fastapi import HTTPException, status


class UserIsBannedException(HTTPException):

	def __init__(
		self,
		headers: Dict[str, Any] | None = None,
	) -> None:
		super().__init__(
			status_code=status.HTTP_418_IM_A_TEAPOT,
			detail="this user is banned!",
			headers=headers,
		)


class UserSelfDeleteException(HTTPException):

	def __init__(
		self,
		headers: Dict[str, Any] | None = None,
	) -> None:
		super().__init__(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="users may not delete themselves",
			headers=headers,
		)