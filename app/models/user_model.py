import enum

from sqlalchemy import (
	Column,
	DateTime,
	String,
	Boolean,
	Enum,
)
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.base_model import Base, gen_ulid, utcnow
import ulid


class UserRoleEnum(str, enum.Enum):
	USER = 'USER'
	MODERATOR = 'MODERATOR'
	ADMIN = 'ADMIN'
	BANNED = 'BANNED'

	@classmethod
	def _missing_(cls, value):
		for member in cls:
			if member.value == value.upper():
				return member


class User(Base):
	__tablename__ = "app_users"

	# Let's see what func.now does with timezone false.
	id = Column(String(26), primary_key=True, nullable=False, default=gen_ulid)
	email = Column(String(100), nullable=False, unique=True)
	alias = Column(String(20), nullable=False, unique=True)  #XXX - Index disabled for resting
	password = Column(String(200), nullable=False)
	last_login = Column(DateTime(timezone=False), nullable=False, server_default=utcnow())
	revoked_at = Column(DateTime(timezone=False))
	confirmed = Column(Boolean, nullable=False, default=False)
	role = Column(Enum(UserRoleEnum),
		nullable=False,
		default=UserRoleEnum.USER.value,
		server_default=UserRoleEnum.USER.value)

	@property
	def registered_on(self):
		return ulid.parse(self.id).timestamp().datetime

	def __repr__(self):
		return (
			f"<User email={self.email}, id={self.id}, alias={self.alias}, role={self.role}>")
