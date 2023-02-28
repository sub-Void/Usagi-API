from typing import Any, Dict, TypeVar
from fastapi import HTTPException, status

from app.models.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)


class RevokedTokenException(HTTPException):

	def __init__(self,
		token_type: str = None,
		detail: Any = None,
		headers: Dict[str, Any] | None = None) -> None:
		if token_type:
			super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
				detail=f"this {token_type} has been revoked",
				headers=headers)
			return

		super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
			detail=f"this auth token has been revoked",
			headers=headers)