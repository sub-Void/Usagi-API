from enum import Enum
import re

rgx_ulid = r"[0-7][0-9A-HJKMNP-TV-Z]{25}"


class ULID(str):

	@classmethod
	def __get_validators__(cls):
		yield cls.validate

	@classmethod
	def validate(cls, v):
		if not isinstance(v, str):
			raise TypeError('id must be a string')
		match = re.match(rgx_ulid, v)
		if match is None:
			raise ValueError("invalid id")
		return v


class OrderEnum(str, Enum):
	ASC = "asc"
	DESC = "desc"


class TokenType(str, Enum):
	ACCESS = "access_token"
	REFRESH = "refresh_token"


# TODO:: Add an example of a custom @validator that isn't it's own type.
# 	@validator('alias')
# 	def alias_must_match_regex(cls, v):
# 		match = re.match(rgx_user_alias, v)
# 		if (match is None):  #or (len(v) != 10):
# 			raise ValueError("bad alias")
# 		return v