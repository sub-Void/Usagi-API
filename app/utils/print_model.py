from typing import TypeVar
from fastapi.encoders import jsonable_encoder

from app.models.base_model import Base

ModelType = TypeVar("ModelType", bound=Base)


def print_model(text: str = "", model: ModelType = []):
	"""Prints out sqlalchemy relationship models."""
	return print(text, jsonable_encoder(model))