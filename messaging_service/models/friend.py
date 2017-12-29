from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Text,
)

from .meta import Base


class Friend(Base):
    __tablename__ = 'friends'

    initiator_id = Column(Integer, ForeignKey("users.id"), nullable=False, primary_key=True,)
    target_id = Column(Integer, ForeignKey("users.id"), nullable=False, primary_key=True,)
    verified = Column(Boolean(name="ck_friendship_verified"), nullable=False, default=False)

    initiator_public_key = Column(Text, nullable=False)
    target_public_key = Column(Text, nullable=True)
