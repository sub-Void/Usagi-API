from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime
import ulid

Base = declarative_base()


def gen_ulid():
	return ulid.new().str


class utcnow(expression.FunctionElement):
	type = DateTime()
	inherit_cache = True


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
	return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
