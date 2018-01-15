from datetime import datetime, timedelta
from random import SystemRandom

import boto3
from passlib.hash import pbkdf2_sha256
from pyramid.settings import asbool
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from messaging_service.serialization import MissingFieldsError
from messaging_service.models.friend import Friend
from messaging_service.models.message import Message
from messaging_service.models.meta import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    email = Column(Text)
    password = Column(Text)
    mobile_number = Column(Text)
    name = Column(Text)

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

    verifications = relationship(
        "UserVerification",
        backref="user",
        cascade="all, delete-orphan",
    )

    def __json__(self, request):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'mobileNumber': self.mobile_number,
            'name': self.name,
        }

    def hash_password(self):
        self.password = pbkdf2_sha256.hash(self.password)

    def has_test_mobile_number(self):
        return self.mobile_number == "0005550000"

    def verify_password(self, incoming_password):
        return pbkdf2_sha256.verify(incoming_password, self.password)

    @classmethod
    def from_json(cls, json_user):
        missing_fields = []
        fields = {}

        # Required fields
        fields['username'] = json_user.get('username')
        fields['password'] = json_user.get('password')
        fields['mobile_number'] = ''.join(
            c for c in json_user.get('mobileNumber', '') if c in "0123456789"
        )

        if fields['username'] is None:
            missing_fields.append('username')

        if fields['password'] is None:
            missing_fields.append('password')

        if not fields['mobile_number']:
            missing_fields.append('mobileNumber')

        if missing_fields:
            raise MissingFieldsError(User, *missing_fields)

        # Optional fields
        fields['name'] = json_user.get('name')
        fields['email'] = json_user.get('email')

        return cls(**fields)


class UserVerification(Base):
    __tablename__ = 'user_verifications'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    code = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    def __init__(self, user):
        self.user = user
        self.timestamp = datetime.now()
        self.code = str(SystemRandom().randint(100000, 999999))

    @property
    def expired(self):
        current_time = datetime.now()
        too_old = current_time - timedelta(hours=24)
        return too_old >= self.timestamp

    @property
    def unhashed_code(self):
        try:
            return self._unhashed_code
        except AttributeError:
            return self.code

    def hash_code(self):
        self._unhashed_code = self.code
        self.code = pbkdf2_sha256.hash(self.code)

    def verify_code(self, incoming_code):
        return pbkdf2_sha256.verify(incoming_code, self.code) or \
            self.user.has_test_mobile_number()

    def send_code(self, request):
        send_sms = asbool(request.registry.settings.get('verifications.send_sms'))
        real_mobile_number = not self.user.has_test_mobile_number()

        if send_sms and real_mobile_number:
            client = boto3.client('sns', region_name='us-west-2')
            client.publish(
                PhoneNumber="+1{}".format(self.user.mobile_number),
                Message=self.unhashed_code,
            )
        elif real_mobile_number:
            print(self.code)
