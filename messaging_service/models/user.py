from sqlalchemy import (
    Column,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .friend import Friend
from .message import Message
from .meta import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text)
    email = Column(Text)
    password = Column(Text)  # TODO: Hash this.

    initiated_friendships = relationship(
        "Friend",
        backref="initiator",
        foreign_keys=[Friend.initiator_id],
    )

    targeted_friendships = relationship(
        "Friend",
        backref="target",
        foreign_keys=[Friend.target_id],
    )

    sent_messages = relationship(
        "Message",
        backref="from",
        foreign_keys=[Message.from_id],
    )

    received_messages = relationship(
        "Message",
        backref="to",
        foreign_keys=[Message.to_id],
    )

    def __json__(self, request):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

    @classmethod
    def from_json(cls, json_user):
        return cls(
            username=json_user['username'],
            email=json_user['email'],
            password=json_user['password'],
        )
