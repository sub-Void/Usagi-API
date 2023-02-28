from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_pagination import add_pagination
from fastapi_async_sqlalchemy import db, SQLAlchemyMiddleware
from fastapi.openapi.docs import get_redoc_html
from loguru import logger

from app.core.config import config, config_mode
from app.core.logging import setup_logger_from_config
from app.api.v1.api import api_router as api_v1

async_db_url = f"postgresql+asyncpg://{config.DB_USER}:{config.DB_PASS}@{config.DB_HOST}/{config.DB_NAME}"
openapi_url = f"{config.API_V1_STR}/openapi.json"

app = FastAPI(
	title=config.PROJECT_NAME,
	version=config.API_VERSION,
	openapi_url=openapi_url,
	docs_url=None,
	redoc_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# db access via middleware
app.add_middleware(
	SQLAlchemyMiddleware,
	db_url=async_db_url,
	engine_args={
	"echo": False,
	"pool_pre_ping": True,
	"pool_size": config.DB_POOL_SIZE,
	"max_overflow": config.DB_MAX_OVERFLOW,
	},
)

if config.BACKEND_CORS_ORIGINS:
	app.add_middleware(
		CORSMiddleware,
		allow_origins=[str(origin) for origin in config.BACKEND_CORS_ORIGINS],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

app.include_router(api_v1, prefix=config.API_V1_STR)
add_pagination(app)


@app.on_event("startup")
async def on_startup():
	logger.success(f"Starting server...")
	if config_mode:
		logger.success(f"Config loaded: {config_mode}")


@app.on_event("shutdown")
async def on_startup():
	logger.warning("Shutting down...")


# overrides redoc without tiangolo server ping
@app.get("/redoc", include_in_schema=False)
def overridden_redoc():
	return get_redoc_html(openapi_url=openapi_url,
		title="FastAPI",
		redoc_favicon_url="/static/favicon64.png")


setup_logger_from_config()