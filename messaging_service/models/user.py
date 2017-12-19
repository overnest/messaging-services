from passlib.hash import pbkdf2_sha256
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
    password = Column(Text)
    mobile_number = Column(Text)

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
        backref="from_user",
        foreign_keys=[Message.from_id],
    )

    received_messages = relationship(
        "Message",
        backref="to_user",
        foreign_keys=[Message.to_id],
    )

    def __json__(self, request):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'mobileNumber': self.mobile_number,
        }

    def hash_password(self):
        self.password = pbkdf2_sha256.hash(self.password)

    def verify_password(self, incoming_password):
        return pbkdf2_sha256.verify(incoming_password, self.password)

    @classmethod
    def from_json(cls, json_user):
        return cls(
            username=json_user['username'],
            email=json_user['email'],
            password=json_user['password'],
            mobile_number=''.join(
                c for c in json_user['mobileNumber'] if c in "0123456789"
            ),
        )
