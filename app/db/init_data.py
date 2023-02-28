from typing import Dict, List
from sqlalchemy.ext.asyncio.session import AsyncSession

from app import crud
from app.core.config import config
from app.core.security import hash_pass
from app.models.user_model import UserRoleEnum
from app.schemas.admin_schema import AdminCreateUser

dummy_pass = hash_pass(config.INIT_ADMIN_PASSWORD)

users: List[Dict[str, str | AdminCreateUser]] = [
	{
	"data":
	AdminCreateUser(
	email=config.INIT_ADMIN_EMAIL,
	alias=config.INIT_ADMIN_ALIAS,
	password=dummy_pass,
	role=UserRoleEnum.ADMIN,
	confirmed=True,
	),
	},
	{
	"data":
	AdminCreateUser(
	email="nue@mod.net",
	alias="Nue",
	password=dummy_pass,
	role=UserRoleEnum.MODERATOR,
	confirmed=True,
	),
	},
	{
	"data":
	AdminCreateUser(
	email="cirno@user.net",
	alias="cirno",
	password=dummy_pass,
	role=UserRoleEnum.BANNED,
	confirmed=True,
	),
	},
	{
	"data":
	AdminCreateUser(
	email="sakuya@user.net",
	alias="Sakuya",
	password=dummy_pass,
	role=UserRoleEnum.USER,
	confirmed=True,
	),
	},
	{
	"data":
	AdminCreateUser(
	email="junko@user.net",
	alias="junko",
	password=dummy_pass,
	role=UserRoleEnum.USER,
	confirmed=True,
	),
	},
	{
	"data":
	AdminCreateUser(
	email="satori@user.net",
	alias="Satori",
	password=dummy_pass,
	role=UserRoleEnum.USER,
	confirmed=True,
	),
	},
	{
	"data":
	AdminCreateUser(
	email="Okuu@user.net",
	alias="Okuu",
	password=dummy_pass,
	role=UserRoleEnum.USER,
	confirmed=True,
	),
	},
	{
	"data":
	AdminCreateUser(
	email="kokoro@user.net",
	alias="Kokoro",
	password=dummy_pass,
	role=UserRoleEnum.USER,
	confirmed=True,
	),
	},
	{
	"data":
	AdminCreateUser(
	email="kokoro2@user.net",
	alias="Kokoro2",
	password=dummy_pass,
	role=UserRoleEnum.USER,
	confirmed=True,
	),
	},
	{
	"data":
	AdminCreateUser(
	email="kokodoko@user.net",
	alias="kokodoko",
	password=dummy_pass,
	role=UserRoleEnum.USER,
	confirmed=False,
	),
	},
]


async def init_data(db_session: AsyncSession) -> None:

	for user in users:
		current_user = await crud.user.get_by_email(email=user["data"].email,
			db_session=db_session)
		if not current_user:
			await crud.user.create(data=user["data"], db_session=db_session)