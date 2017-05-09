from datetime import datetime
from sqlalchemy import Column, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base

from lib.utils import tojson

Base = declarative_base()

class PG_Base(object):
    _protected_cols = []

    _created = Column('_created', TIMESTAMP, nullable=False, server_default=text("timezone('utc'::text, now())"))
    _modified = Column('_modified', TIMESTAMP, nullable=False, server_default=text("timezone('utc'::text, now())"), onupdate=datetime.utcnow())

    def as_dict(self):
        def parse_attr(attr):
            # If this is a ORM instance or a list of ORM instances, we need to call as_dict() for this attribute first
            if isinstance(attr, list):
                return map(lambda x: x.as_dict() if isinstance(x, PG_Base) else x, attr)
            else:
                return attr.as_dict() if isinstance(attr, PG_Base) else attr

        return {c.name: parse_attr(getattr(self, c.name)) for c in self.__table__.columns if c.name not in self._protected_cols}

    def to_json(self):
        return tojson(self.as_dict())
