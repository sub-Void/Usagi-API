import os
from pydantic import BaseSettings, validator, EmailStr, AnyHttpUrl
from pathlib import Path
from enum import Enum

# optionally load a different env file -> .env.<CONFIG_MODE>
config_mode = os.getenv("CONFIG_MODE")
env_filename = ".env" if config_mode is None else ".env."+config_mode

if config_mode and not os.path.isfile(env_filename):
	raise FileNotFoundError(f"Config file '{env_filename}' was not found. CONFIG_MODE={config_mode}")


class BaseConfig(BaseSettings):
	# Shell environment variables will have precedence
	API_VERSION: str = "v1"
	PROJECT_NAME: str = "Usagi API"
	ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 1  # 1 hour
	REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 100  # 100 days
	DB_USER: str
	DB_PASS: str
	DB_HOST: str
	DB_PORT: int | str
	DB_NAME: str

	DB_POOL_SIZE: int = 5 
	DB_MAX_OVERFLOW = 10

	INIT_ADMIN_EMAIL: EmailStr = "Reisen@admin.net"
	INIT_ADMIN_ALIAS: str = "Reisen"
	INIT_ADMIN_PASSWORD: str = "lunar123"

	SECRET_KEY: str
	ENCRYPT_KEY: str

	BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl] = ["http://localhost", "http://localhost:8080"]

	@validator("BACKEND_CORS_ORIGINS", pre=True)
	def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
		if isinstance(v, str) and not v.startswith("["):
			return [i.strip() for i in v.split(",")]
		elif isinstance(v, (list, str)):
			return v
		raise ValueError(v)


	class Config:
		case_sensitive=False
		env_file = env_filename

config = BaseConfig()

class LoggingLevel(str, Enum):
	"""
	Allowed log levels for the application
	"""

	CRITICAL: str = "CRITICAL"
	ERROR: str = "ERROR"
	WARNING: str = "WARNING"
	SUCCESS: str = "SUCCESS"
	INFO: str = "INFO"
	DEBUG: str = "DEBUG"
	TRACE: str = "TRACE"


class LoggingConfig(BaseSettings):
	"""Configure your service logging using a LoggingSettings instance.

	All arguments are optional.

	Arguments:

		level (str): the minimum log-level to log. (default: "DEBUG")
		format (str): the logformat to use. (default: "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>")
		filepath (Path): the path where to store the logfiles. (default: None)
		rotation (str): when to rotate the logfile. (default: "1 days")
		retention (str): when to remove logfiles. (default: "1 months")
		backtrace (bool): whether the formatted exception trace should be extended entirely
		diagnose (bool): whether variables should be displayed during exception handling - should be enabled only for bebugging.

	"""

	level: LoggingLevel = "DEBUG" 
	format: str = (
		"<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
		"<level>{level: <8}</level> | "
		"<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
		"<level>{message}</level>"
	)
	filepath: Path | None = None
	rotation: str = "1 days"
	retention: str = "1 months"
	backtrace: bool = True
	diagnose: bool = False

	class Config:
		env_prefix = "logging_" 
		env_file = env_filename