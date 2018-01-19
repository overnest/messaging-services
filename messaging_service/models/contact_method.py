from datetime import datetime
import enum
import hashlib
from random import SystemRandom

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
)

from messaging_service.models.meta import Base


class _ContactType(enum.Enum):
    email = 1
    mobile_phone = 2


class ContactMethod(Base):
    """A ``ContactMethod`` is a way of contacting a user, such as by mobile
    phone or email. It is tied to a user identity and verified, when possible,
    by a previously-verified method.
    """
    __tablename__ = 'contact_methods'

    id = Column(Integer, primary_key=True)
    type = Column(Enum(_ContactType))
    value = Column(Text)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    verified = Column(
        Boolean(name="ck_cm_verified"),
        nullable=False,
        default=False,
    )
    verification_code = Column(Text, nullable=False)
    verification_code_date = Column(DateTime, nullable=False)

    def __init__(self, user, type, value):
        self.user = user
        self.type = type
        self.value = value

        self.verification_code = self._generate_verification_code()
        self.verification_code_date = datetime.now()

    def _generate_verification_code(self):
        code = SystemRandom().randint(2**17, 2**50)

        if self.type == _ContactType.mobile_phone:
            code %= 1000000

        code = str(code).encode('utf-8')

        if self.type == _ContactType.email:
            code = hashlib.md5(code).hexdigest()

        return code

    @classmethod
    def email(cls, user, value):
        return cls(user, _ContactType.email, value)

    @classmethod
    def mobile_phone(cls, user, value):
        return cls(user, _ContactType.mobile_phone, value)

    def verify(self, request):
        if self.type == _ContactType.email:
            verify_email(self, request)

def verify_email(contact, request):
    pass

