from typing import Any, Dict, Generic, Type, TypeVar
from fastapi import HTTPException, status

from app.models.base_model import Base
from app.schemas.base_schema import ULID

ModelType = TypeVar("ModelType", bound=Base)


class ContentNoChangeException(HTTPException):

	def __init__(
		self,
		detail: Any = None,
		headers: Dict[str, Any] | None = None,
	) -> None:
		super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
			detail=detail,
			headers=headers)


class IdNotFoundException(HTTPException, Generic[ModelType]):

	def __init__(
		self,
		model: Type[ModelType],
		id: ULID | str | None = None,
		headers: Dict[str, Any] | None = None,
	) -> None:
		if id:
			super().__init__(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"unable to find the {model.__name__.lower()} with id {id}",
				headers=headers,
			)
			return

		super().__init__(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"{model.__name__} id not found",
			headers=headers,
		)


class NameNotFoundException(HTTPException, Generic[ModelType]):

	def __init__(
		self,
		model: Type[ModelType],
		name: str | None = None,
		headers: Dict[str, Any] | None = None,
	) -> None:
		if name:
			super().__init__(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"unable to find the {model.__name__.lower()} named {name}",
				headers=headers,
			)
		else:
			super().__init__(
				status_code=status.HTTP_404_NOT_FOUND,
				detail=f"{model.__name__} name not found",
				headers=headers,
			)


class NameExistsException(HTTPException, Generic[ModelType]):

	def __init__(
		self,
		model: Type[ModelType],
		name: str | None = None,
		headers: Dict[str, Any] | None = None,
	) -> None:
		if name:
			super().__init__(
				status_code=status.HTTP_409_CONFLICT,
				detail=f"the {model.__name__.lower()} name {name} already exists",
				headers=headers,
			)
			return

		super().__init__(
			status_code=status.HTTP_409_CONFLICT,
			detail=f"the {model.__name__.lower()} name already exists",
			headers=headers,
		)
