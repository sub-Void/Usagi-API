from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr


class LogIn(BaseModel):
	email: EmailStr
	password: str


class UpdatePassIn(BaseModel):
	current_pass: str
	new_pass: str
	confirm_pass: str


class TokenType(str, Enum):
	ACCESS = "access_token"
	REFRESH = "refresh_token"


class TokenPayload(BaseModel):
	iat: datetime
	exp: datetime
	sub: str
	type: TokenType  # "access_token" or "refresh_token"


class TokenOut(BaseModel):
	access_token: str | None
	token_type: str  # "bearer" or "cookie"


class TokensOut(BaseModel):
	access_token: str | None
	token_type: str = "bearer"
	refresh_token: str | None
	refresh_token_type: str = "cookie"  # "bearer" or "cookie"