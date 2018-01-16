from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship

from .meta import Base


class Friend(Base):
    __tablename__ = 'friends'

    initiator_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    target_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    verified = Column(
        Boolean(name="ck_friendship_verified"),
        nullable=False,
        default=False,
    )
    initiator_public_key = Column(Text, nullable=False)
    target_public_key = Column(Text, nullable=True)

    def other_user(self, user_id):
        """Given a ``User``, return the other user associated with this
        friendship. Raise a ValueError if they are not associated with this
        friendship at all.
        """
        other_user = None

        if self.initiator_id == user_id:
            other_user = self.target

        if self.target_id == user_id:
            other_user = self.initiator

        if other_user is None:
            raise ValueError(
                "The user_id {} is not associated with this friendship."
                .format(user_id)
            )

        return other_user

    def key_for(self, user_id):
        """Given a ``User``, return the ``*_public_key`` associated with them
        for this friendship.
        """
        if user_id == self.initiator_id:
            return self.initiator_public_key

        if user_id == self.target_id:
            return self.target_public_key

    def set_key_for(self, user_id, key_value):
        """Given a ``user_id`` and a public key value, update the public key
        for that user to match the new value.
        """
        if user_id == self.initiator_id:
            self.initiator_public_key = key_value
        elif user_id == self.target_id:
            self.target_public_key = key_value
        else:
            raise ValueError("Provided user_id does not belong to this friendhsip.")
