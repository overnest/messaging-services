from datetime import datetime

from passlib.hash import pbkdf2_sha256
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from messaging_service.serialization import MissingFieldsError
from messaging_service.models.contact_method import ContactMethod
from messaging_service.models.friend import Friend
from messaging_service.models.message import Message
from messaging_service.models.meta import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    default_username = Column(Text, unique=True)
    password = Column(Text)

    verified = Column(
        Boolean(name="ck_user_verified"),
        nullable=False,
        default=False,
    )

    initiated_friendships = relationship(
        "Friend",
        backref="initiator",
        foreign_keys=[Friend.initiator_id],
        cascade="all, delete-orphan",
    )

    targeted_friendships = relationship(
        "Friend",
        backref="target",
        foreign_keys=[Friend.target_id],
        cascade="all, delete-orphan",
    )

    sent_messages = relationship(
        "Message",
        backref="from_user",
        foreign_keys=[Message.from_id],
        cascade="all, delete-orphan",
    )

    received_messages = relationship(
        "Message",
        backref="to_user",
        foreign_keys=[Message.to_id],
        cascade="all, delete-orphan",
    )

    def __json__(self, request):
        return {
            'id': self.id,
            'defaultUsername': self.default_username,
        }

    def hash_password(self):
        self.password = pbkdf2_sha256.hash(self.password)

    def verify_password(self, incoming_password):
        return pbkdf2_sha256.verify(incoming_password, self.password)

    @classmethod
    def from_json(cls, json_user):
        missing_fields = []
        fields = {}

        # Required fields
        fields['username'] = json_user.get('username')
        fields['password'] = json_user.get('password')

        if fields['username'] is None:
            missing_fields.append('username')

        if fields['password'] is None:
            missing_fields.append('password')

        if missing_fields:
            raise MissingFieldsError(User, *missing_fields)

        # Optional fields
        fields['name'] = json_user.get('name')

        return cls(**fields)

    def create_email(self, value):
        return ContactMethod.email(self, value)

    def create_mobile_phone(self, value):
        return ContactMethod.mobile_phone(self, value)
