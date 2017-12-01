from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
)

from .meta import Base


class User(Base):
    __tablename__ = 'base'
    id = Column(Integer, primary_key=True)
    username = Column(Text)
    email = Column(Text)
    password = Column(Text) # TODO: Hash this.
