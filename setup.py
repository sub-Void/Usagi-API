from pathlib import Path
from setuptools import setup, find_packages

DESCRIPTION = ("FastAPI Async App Base")
APP_ROOT = Path(__file__).parent
README = (APP_ROOT / "README.md").read_text()
AUTHOR = "sub-Void"
AUTHOR_EMAIL = "subvoid@mailfence.com"
PROJECT_URLS = {
	"Documentation": "",
	"Bug Tracker": "",
	"Source Code": "",
}
INSTALL_REQUIRES = [
	"fastapi_pagination",
	"python-multipart",
	"SQLAlchemy",
	"FastAPI",
	"urllib3",
	"alembic",
	"loguru",
	"uvicorn",
	"pydantic",
	"email_validator",
	"fastapi_async_sqlalchemy",
	"asyncpg",
	"fastapi-cache2",
	"python-jose",
	"passlib",
	"ulid-py",
	#"sqlalchemy-utils",  #*
	#"async-timeout",  #*
	#"anyio",  #*
	#"python-dateutil", #*
	#"httpx",  #*
]
EXTRAS_REQUIRE = {
	"dev": [
	"yapf",
	"pydocstyle",
	"pytest",
	"pytest-clarity",
	"pytest-dotenv",
	"tox",
	"toml",
	]
}

setup(
	name="usagi-api-base",
	description=DESCRIPTION,
	long_description=README,
	long_description_content_type="text/markdown",
	version="0.1",
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	maintainer=AUTHOR,
	maintainer_email=AUTHOR_EMAIL,
	license="MIT",
	url="",
	project_urls=PROJECT_URLS,
	packages=find_packages(),
	python_requires=">=3.10",
	install_requires=INSTALL_REQUIRES,
	extras_require=EXTRAS_REQUIRE,
)