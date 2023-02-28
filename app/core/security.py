from datetime import timedelta
from typing import Any, Dict
from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from app.core.config import config
from app.schemas.auth_schema import TokenPayload, TokenType
from app.utils.time_util import utc_now

pwd_context = CryptContext(schemes=["pbkdf2_sha512"], deprecated="auto")
TOKEN_ALGORITHM = "HS256"

class AuthAccessBearer(OAuth2):
	def __init__(
		self,
		tokenUrl: str,
		scheme_name: str | None = None,
		scopes: Dict[str, str] | None = None,
		description: str | None = None,
		auto_error: bool = True,
	):
		if not scopes:
			scopes = {}
		flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
		super().__init__(
			flows=flows,
			scheme_name=scheme_name,
			description=description,
			auto_error=auto_error,
		)

	async def __call__(self, request: Request) -> str | None:
		authorization = request.headers.get("Authorization")
		scheme, param = get_authorization_scheme_param(authorization)
		if not authorization or scheme.lower() != "bearer":
			if self.auto_error:
					raise HTTPException(
						status_code=status.HTTP_401_UNAUTHORIZED,
						detail="not authenticated",
						headers={"WWW-Authenticate": "Bearer"},
					)
			else:
					return None
		return param


class AuthRefreshCookie(OAuth2):
	def __init__(
		self,
		tokenUrl: str,
		scheme_name: str | None = None,
		scopes: Dict[str, str] | None = None,
		description: str | None = None,
		auto_error: bool = True,
	):
		if not scopes:
			scopes = {}
		flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
		super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error, description=description,)

	async def __call__(self, request: Request) -> str | None:
		authorization: str = request.cookies.get("refresh_token")
		
		scheme, param = get_authorization_scheme_param(authorization)
		if not authorization or scheme.lower() != "bearer":
			if self.auto_error:
					raise HTTPException( 
						status_code=status.HTTP_401_UNAUTHORIZED,
						detail="no refresh token",
						headers={"WWW-Authenticate": "cookie"},
					)
			else:
					return None
		return param


def create_token(
	subject: str | Any, token_type: TokenType, expires_delta: timedelta = None, 
) -> str:
	"""Encode a JSON Web Token"""

	if expires_delta:
		expire = utc_now() + expires_delta
	elif token_type == TokenType.ACCESS:
		expire = utc_now() + timedelta(
			minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
		)
	elif token_type == TokenType.REFRESH:
		expire = utc_now() + timedelta(
			minutes=config.REFRESH_TOKEN_EXPIRE_MINUTES
		)
	to_encode = {"iat": utc_now(), "exp": expire, "sub": str(subject), "type": token_type}
	encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=TOKEN_ALGORITHM)

	return encoded_jwt


def validate_token(
	token: str) -> TokenPayload:
	"""Validates a token and returns the payload."""

	try: 
		data = jwt.decode(token, config.SECRET_KEY, algorithms=[TOKEN_ALGORITHM])
		payload = TokenPayload(**data) 
		
	except (jwt.JWTError, ValidationError):
		raise HTTPException(
					status_code=status.HTTP_403_FORBIDDEN,
					detail="invalid access token",
			)
	
	return payload

def verify_hash(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)

def hash_pass(password: str) -> str:
	return pwd_context.hash(password)


