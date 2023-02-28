from math import ceil
from typing import Any, Dict, Generic, Sequence, TypeVar
from pydantic.generics import GenericModel
from fastapi_pagination import Params, Page
from fastapi_pagination.bases import AbstractPage, AbstractParams

DataType = TypeVar("DataType")
T = TypeVar("T")


class PageBase(Page[T], Generic[T]):
	pages: int
	next_page: int | None
	previous_page: int | None


class ResponseBase(GenericModel, Generic[T]):
	message: str = ""
	meta: Dict = {}
	data: T | None


class ResponsePage(AbstractPage[T], Generic[T]):
	message: str = ""
	meta: Dict = {}
	data: PageBase[T]

	__params_type__ = Params

	@classmethod
	def create(
		cls,
		items: Sequence[T],
		total: int,
		params: AbstractParams,
	) -> PageBase[T] | None:
		if params.size is not None and total is not None and params.size != 0:
			pages = ceil(total / params.size)
		else:
			pages = 0

		return cls(data=PageBase(
			items=items,
			page=params.page,
			size=params.size,
			total=total,
			pages=pages,
			next_page=params.page + 1 if params.page < pages else None,
			previous_page=params.page - 1 if params.page > 1 else None,
		))


class GetResponseBase(ResponseBase[DataType], Generic[DataType]):
	message: str = "data retrieved"


class GetResponsePaginated(ResponsePage[DataType], Generic[DataType]):
	message: str = "data retrieved"


class PostResponseBase(ResponseBase[DataType], Generic[DataType]):
	message: str = "success"


class PutResponseBase(ResponseBase[DataType], Generic[DataType]):
	message: str = "data updated"


class DeleteResponseBase(ResponseBase[DataType], Generic[DataType]):
	message: str = "data deleted"


def create_response(
	data: DataType | None,
	message: str | None = None,
	meta: Dict | Any = {},
) -> Dict[str, DataType] | DataType:
	if isinstance(data, ResponsePage):  # if paginated object
		data.message = f"paginated collection retrieved" if not message else message
		data.meta = meta
		return data
	body_response = {"data": data, "message": message, "meta": meta}
	# Returns a dictionary to avoid double validation https://github.com/tiangolo/fastapi/issues/3021
	return {k: v for k, v in body_response.items() if v is not None}
